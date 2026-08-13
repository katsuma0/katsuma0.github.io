#!/usr/bin/env python3
"""Turn an Apple Journal export into entries on the life page.

Usage:
    python3 tools/journal_ingest.py AppleJournalEntries.zip [--summary out.md]

Reads every entry in the export, keeps only the ones whose title starts
with a life@ prefix (forgiving about spacing, case, and repeated letters:
"life@grundy2026", "Life @ Grundy 2026", "life@grundy" all work; the @ is
the one required character, so ordinary journal entries can never leak
onto the site). For each new entry it:

  - takes the first 12 photos (any count is fine; threes fill rows),
  - converts them to web-sized webp pairs under images/life/<slug>/,
  - writes life/data/<slug>.json,
  - regenerates the entry cards in life.html between the journal markers.

Entries already in life/data/ are skipped, so re-running the same export
(Journal always exports everything) only adds what is new. The entry's
date comes from Journal, so a backdated entry sorts into its real place.

Pure Python plus Pillow; no other tooling.
"""

import argparse
import datetime
import html
import json
import pathlib
import re
import shutil
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "life" / "data"
IMAGES = ROOT / "images" / "life"
PAGE = ROOT / "life.html"

START = "<!-- journal:start -->"
END = "<!-- journal:end -->"

MAX_PHOTOS = 12   # photos arrive in threes; four rows is plenty for one entry
FULL_EDGE = 1600   # long edge of the tap-to-zoom image
THUMB_EDGE = 700   # long edge of the card image
IMAGE_EXTS = {".heic", ".jpeg", ".jpg", ".png"}

# life@..., with typos tolerated: any case, any spacing, doubled letters,
# and : or # in place of @. The separator itself is required.
TITLE_RE = re.compile(r"^l+i+f+e*[@:#]+(.+)$")


def strip_tags(fragment):
    text = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(text).replace(" ", " ").strip()


def parse_entry(path):
    """One export entry file -> dict, or None if it has no usable date."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if not m:
        return None
    s = path.read_text(encoding="utf-8", errors="replace")

    tm = re.search(r"<div class='title'>(.*?)</div>", s, re.S)
    title = strip_tags(tm.group(1)) if tm else ""

    assets = re.findall(r'<div id="([0-9A-Fa-f-]{36})" class="gridItem', s)

    paras = []
    for pm in re.findall(r'<p class="p2">(.*?)</p>', s, re.S):
        text = strip_tags(pm)
        if text:
            paras.append(text)

    return {"date": m.group(1), "title": title, "assets": assets, "paras": paras}


def life_slug(title):
    """'Life @ Grundy 2026' -> 'grundy2026', or None if not a life@ title."""
    t = re.sub(r"\s+", "", title.lower())
    m = TITLE_RE.match(t)
    if not m:
        return None
    slug = re.sub(r"[^a-z0-9]", "", m.group(1))
    return slug or None


def display_name(slug):
    """'grundy2026' -> 'grundy'; a slug with no trailing year stays whole."""
    name = re.sub(r"(19|20)\d\d$", "", slug)
    return name or slug


def month_year(iso_date):
    d = datetime.date.fromisoformat(iso_date)
    return d.strftime("%B %Y").lower()


def convert_photo(src, dest_dir, index):
    """Write index.webp and index-thumb.webp from one export photo."""
    from PIL import Image, ImageOps
    from pillow_heif import register_heif_opener

    register_heif_opener()
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    dest_dir.mkdir(parents=True, exist_ok=True)
    for edge, suffix, quality in ((FULL_EDGE, "", 80), (THUMB_EDGE, "-thumb", 75)):
        out = im.copy()
        out.thumbnail((edge, edge))
        out.save(dest_dir / f"{index}{suffix}.webp", quality=quality, method=6)


def entry_card(entry):
    """The .entry article for one data record, matching life.html markup.

    Journal-export records carry only a name and render as "life @ name".
    Issue-posted records may carry a display "title" and a "place"; the
    title replaces the life@ form and the place gets its own line."""
    slug = entry["slug"]
    shown = entry.get("title") or "life @ {}".format(entry["name"])
    lines = [
        f'<article class="entry" id="{slug}">',
        '    <h3 class="entry-title"><span>{}</span><span class="leader"></span>'
        '<span class="entry-date">{}</span></h3>'.format(html.escape(shown), month_year(entry["date"])),
    ]
    if entry.get("place"):
        lines.append(f'    <div class="entry-place">{html.escape(entry["place"])}</div>')
    for para in entry["summary"]:
        lines.append(f"    <p>{html.escape(para)}</p>")
    if entry["photos"]:
        lines.append('    <div class="photos">')
        for i in range(1, entry["photos"] + 1):
            lines.append(
                f'        <img src="images/life/{slug}/{i}-thumb.webp" '
                f'alt="photo {i} from {entry["name"]}" loading="lazy" tabindex="0">'
            )
        lines.append("    </div>")
    lines.append("</article>")
    return "\n".join(lines)


def rebuild_page():
    """Regenerate the cards between the journal markers in life.html."""
    records = []
    for f in sorted(DATA.glob("*.json")):
        records.append(json.loads(f.read_text()))
    records.sort(key=lambda r: (r["date"], r["slug"]), reverse=True)

    page = PAGE.read_text()
    if START not in page or END not in page:
        sys.exit(f"life.html is missing the {START} / {END} markers")
    cards = "\n\n".join(entry_card(r) for r in records)
    body = f"{START}\n{cards}\n{END}" if cards else f"{START}\n{END}"
    page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: body, page, flags=re.S)
    PAGE.write_text(page)


def resource_for(resources, uuid):
    for ext in IMAGE_EXTS:
        for candidate in (resources / f"{uuid}{ext}", resources / f"{uuid}{ext.upper()}"):
            if candidate.exists():
                return candidate
    return None


def ingest(export_dir, summary):
    entries_dir = export_dir / "Entries"
    resources = export_dir / "Resources"
    if not entries_dir.is_dir():
        summary.append("- no Entries folder in the export; nothing done")
        return

    added = []
    for path in sorted(entries_dir.glob("*.html")):
        entry = parse_entry(path)
        if entry is None:
            continue
        label = entry["title"] or path.stem
        slug = life_slug(entry["title"])
        if not slug:
            summary.append(f"- skipped {entry['date']} “{label}”: no life@ in the title")
            continue
        if (DATA / f"{slug}.json").exists():
            summary.append(f"- skipped {label}: already on the page as {slug}")
            continue

        photos = 0
        dropped = 0
        for uuid in entry["assets"]:
            src = resource_for(resources, uuid)
            if src is None:
                continue
            if photos == MAX_PHOTOS:
                dropped += 1
                continue
            photos += 1
            convert_photo(src, IMAGES / slug, photos)

        record = {
            "slug": slug,
            "name": display_name(slug),
            "date": entry["date"],
            "summary": entry["paras"],
            "photos": photos,
        }
        DATA.mkdir(parents=True, exist_ok=True)
        (DATA / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n")
        note = f"- added {slug}: {entry['date']}, {photos} photo(s)"
        if dropped:
            note += f" (first {MAX_PHOTOS} kept, {dropped} more in the entry left out)"
        added.append(note)

    summary.extend(added)
    if added:
        rebuild_page()
    else:
        summary.append("- no new life@ entries in this export")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export", help="AppleJournalEntries zip, or an unzipped export folder")
    ap.add_argument("--summary", help="append a markdown summary to this file")
    args = ap.parse_args()

    summary = []
    src = pathlib.Path(args.export)
    if src.is_dir():
        export_dir = src if (src / "Entries").is_dir() else src / "AppleJournalEntries"
        ingest(export_dir, summary)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(src) as z:
                z.extractall(tmp)
            export_dir = pathlib.Path(tmp) / "AppleJournalEntries"
            if not export_dir.is_dir():
                candidates = [p for p in pathlib.Path(tmp).iterdir()
                              if p.is_dir() and (p / "Entries").is_dir()]
                export_dir = candidates[0] if candidates else pathlib.Path(tmp)
            ingest(export_dir, summary)

    text = "\n".join(summary)
    print(text)
    if args.summary:
        with open(args.summary, "a") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
