#!/usr/bin/env python3
"""Turn a "life" issue into an entry on the life page.

The issue carries everything:
  title    "entry title | place"  (the place is optional)
  body     free text, an optional "date: august 2026" line anywhere,
           and the attached photos (image markdown or img tags)

This writes the same life/data/<slug>.json records the Apple Journal
export pipeline writes, then regenerates life.html with the shared
renderer in tools/journal_ingest.py. One source of truth, one renderer:
a later export run keeps issue-posted entries, and an issue post keeps
exported ones. Photos usually arrive in multiples of three so the rows
land clean, but any count works.
"""
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from journal_ingest import DATA, IMAGES, rebuild_page  # noqa: E402

MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]


def parse_issue():
    raw = os.environ.get("ISSUE_JSON")
    if not raw:
        sys.exit("ISSUE_JSON is not set")
    return json.loads(raw)


def split_title(title):
    if "|" in title:
        t, place = title.split("|", 1)
        return t.strip(), place.strip()
    return title.strip(), ""


def pull_images(body):
    """Collect image URLs and return the body without them."""
    urls = []

    def keep(m):
        urls.append(m.group(1))
        return ""

    body = re.sub(r"!\[[^\]]*\]\((https?://[^)\s]+)\)", keep, body)
    body = re.sub(r'<img[^>]*src="(https?://[^"]+)"[^>]*/?>', keep, body)
    return body, urls


def pull_date(body, created_at):
    """An optional "date: august 2026" (or ISO) line overrides the issue
    date; either way the record stores ISO so sorting stays honest."""
    m = re.search(r"^\s*date:\s*(.+)$", body, re.IGNORECASE | re.MULTILINE)
    if m:
        body = re.sub(r"^\s*date:\s*.+$", "", body, count=1,
                      flags=re.IGNORECASE | re.MULTILINE)
        text = m.group(1).strip().lower()
        iso = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?", text)
        if iso:
            return body, "%s-%s-%s" % (iso.group(1), iso.group(2), iso.group(3) or "01")
        my = re.match(r"([a-z]+)\s+(\d{4})", text)
        if my and my.group(1) in MONTHS:
            return body, "%d-%02d-01" % (int(my.group(2)), MONTHS.index(my.group(1)) + 1)
        print("warning: could not read the date line, using the issue date")
    return body, created_at[0:10]


def slugify(title, created_at):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "entry"
    return created_at[0:4] + created_at[5:7] + "-" + s[:40]


class _CrossHostRedirect(urllib.request.HTTPRedirectHandler):
    """GitHub answers an asset request with a redirect to a signed storage
    URL. Forwarding the API token there makes the storage host refuse the
    request (400), so the auth header is dropped the moment a redirect
    leaves the original host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(req.full_url).netloc:
            new.remove_header("Authorization")
        return new


_OPENER = urllib.request.build_opener(_CrossHostRedirect)


def fetch(url, dest):
    req = urllib.request.Request(url, headers={
        "User-Agent": "life-post",
        "Authorization": "Bearer " + os.environ.get("GH_TOKEN", ""),
    })
    with _OPENER.open(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def convert(src, dest_dir, index):
    """The same webp pair the export pipeline writes: index.webp at
    1600px and index-thumb.webp at 700px."""
    from PIL import Image, ImageOps
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    dest_dir.mkdir(parents=True, exist_ok=True)
    for edge, suffix, quality in ((1600, "", 80), (700, "-thumb", 75)):
        out = im.copy()
        out.thumbnail((edge, edge))
        out.save(dest_dir / ("%d%s.webp" % (index, suffix)), quality=quality, method=6)


def paragraphs(text):
    out = []
    for block in re.split(r"\n\s*\n", text):
        block = " ".join(block.split())
        if block:
            out.append(block)
    return out


def main():
    issue = parse_issue()
    title, place = split_title(issue["title"])
    body = issue.get("body") or ""
    body, urls = pull_images(body)
    body, date = pull_date(body, issue["created_at"])
    slug = slugify(title, issue["created_at"])
    if (DATA / (slug + ".json")).exists():
        sys.exit("an entry named %s already exists; retitle the issue" % slug)

    photos = 0
    for url in urls:
        raw = IMAGES / slug / ("dl-%d.orig" % (photos + 1))
        raw.parent.mkdir(parents=True, exist_ok=True)
        fetch(url, raw)
        photos += 1
        convert(raw, IMAGES / slug, photos)
        raw.unlink()

    record = {
        "slug": slug,
        "name": title,
        "date": date,
        "summary": paragraphs(body),
        "photos": photos,
        "title": title,
    }
    if place:
        record["place"] = place
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / (slug + ".json")).write_text(json.dumps(record, indent=2) + "\n")

    rebuild_page()
    # keep the footer's freshness line honest
    page = ROOT / "life.html"
    month = datetime.date.fromisoformat(date).strftime("%B %Y").lower()
    text = page.read_text()
    text = re.sub(r"last updated: [a-z]+ \d{4}", "last updated: " + month, text, count=1)
    page.write_text(text)
    print("added entry", slug, "with", photos, "photos")


if __name__ == "__main__":
    main()
