#!/usr/bin/env python3
"""Turn a "life" issue into a formatted entry on life.html.

The issue carries everything:
  title    "entry title | place"  (the place is optional)
  body     free text, an optional "date: august 2026" line anywhere,
           and the attached photos (image markdown or img tags)
The entry renders as: month year, title, place, paragraphs, then the
photos in a three-across grid. Photos usually arrive in multiples of
three so the rows land clean, but any count works.
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIFE = os.path.join(ROOT, 'life.html')
IMGDIR = os.path.join(ROOT, 'images', 'life')
MARKER = '<!-- journal:start -->'

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']


def parse_issue():
    raw = os.environ.get('ISSUE_JSON')
    if not raw:
        sys.exit('ISSUE_JSON is not set')
    return json.loads(raw)


def split_title(title):
    if '|' in title:
        t, place = title.split('|', 1)
        return t.strip(), place.strip()
    return title.strip(), ''


def pull_images(body):
    """Collect image URLs and return the body without them."""
    urls = []

    def md(m):
        urls.append(m.group(1))
        return ''

    def tag(m):
        urls.append(m.group(1))
        return ''

    body = re.sub(r'!\[[^\]]*\]\((https?://[^)\s]+)\)', md, body)
    body = re.sub(r'<img[^>]*src="(https?://[^"]+)"[^>]*/?>', tag, body)
    return body, urls


def pull_date(body, created_at):
    m = re.search(r'^\s*date:\s*(.+)$', body, re.IGNORECASE | re.MULTILINE)
    if m:
        body = re.sub(r'^\s*date:\s*.+$', '', body, count=1,
                      flags=re.IGNORECASE | re.MULTILINE)
        return body, m.group(1).strip().lower()
    year = created_at[0:4]
    month = MONTHS[int(created_at[5:7]) - 1]
    return body, month + ' ' + year


def slugify(title, created_at):
    s = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'entry'
    return created_at[0:4] + created_at[5:7] + '-' + s[:40]


def fetch(url, dest):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'life-post',
        'Authorization': 'Bearer ' + os.environ.get('GH_TOKEN', ''),
    })
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, 'wb') as f:
        f.write(r.read())


def convert(src, full, thumb):
    """Full image at 1600px and a 480px thumbnail, both webp. If
    ImageMagick is missing the original bytes are kept under the webp
    names so the page still works."""
    try:
        subprocess.run(['convert', src, '-auto-orient', '-resize', '1600x1600>',
                        '-quality', '82', full], check=True)
        subprocess.run(['convert', src, '-auto-orient', '-resize', '480x480>',
                        '-quality', '75', thumb], check=True)
    except (OSError, subprocess.CalledProcessError):
        for dest in (full, thumb):
            with open(src, 'rb') as a, open(dest, 'wb') as b:
                b.write(a.read())
        print('warning: imagemagick unavailable, images were not resized')


def paragraphs(text):
    out = []
    for block in re.split(r'\n\s*\n', text):
        block = ' '.join(block.split())
        if block:
            out.append('    <p>' + html.escape(block) + '</p>')
    return out


def main():
    issue = parse_issue()
    title, place = split_title(issue['title'])
    body = issue.get('body') or ''
    body, urls = pull_images(body)
    body, date = pull_date(body, issue['created_at'])
    slug = slugify(title, issue['created_at'])

    os.makedirs(IMGDIR, exist_ok=True)
    photos = []
    for i, url in enumerate(urls, 1):
        raw = os.path.join(IMGDIR, slug + '-' + str(i) + '.orig')
        full = os.path.join(IMGDIR, slug + '-' + str(i) + '.webp')
        thumb = os.path.join(IMGDIR, slug + '-' + str(i) + '-thumb.webp')
        fetch(url, raw)
        convert(raw, full, thumb)
        os.remove(raw)
        photos.append('        <img src="images/life/%s-%d-thumb.webp" '
                      'loading="lazy" tabindex="0" alt="%s, photo %d">'
                      % (slug, i, html.escape(title), i))

    lines = ['<article class="entry" id="%s">' % slug,
             '    <h3 class="entry-title"><span>%s</span>'
             '<span class="leader"></span>'
             '<span class="entry-date">%s</span></h3>'
             % (html.escape(title), html.escape(date))]
    if place:
        lines.append('    <div class="entry-place">%s</div>' % html.escape(place))
    lines.extend(paragraphs(body))
    if photos:
        lines.append('    <div class="photos p3">')
        lines.extend(photos)
        lines.append('    </div>')
    lines.append('</article>')
    article = '\n'.join(lines)

    page = open(LIFE, encoding='utf-8').read()
    if MARKER not in page:
        sys.exit('marker missing from life.html')
    page = page.replace(MARKER, MARKER + '\n' + article + '\n', 1)
    page = re.sub(r'last updated: [a-z]+ \d{4}', 'last updated: ' + date, page, count=1)
    open(LIFE, 'w', encoding='utf-8').write(page)
    print('added entry', slug, 'with', len(photos), 'photos')


if __name__ == '__main__':
    main()
