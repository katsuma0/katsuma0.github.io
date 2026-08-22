# katsuma0.github.io

## What this is

My personal site, served at katsuma.ca. Hand-written HTML pages, no blog engine.

Main pages: `index.html`, `apps.html`, `sewing-projects.html`, `shop.html`, `contact.html`, plus `life.html` (events and a small public log, the landing page for katsuma.life, now also the life tab in the tab bar).

App and project detail pages, all linked from `apps.html`: `tides.html`, `wildlife.html`, `fishing.html`, `camp.html`, `spotify.html`, `used-car.html`, `carbon-cycle.html`, `dsa.html`. They use a `backlink` to Projects, an `Open the app ↗` button for apps, and `h4` section headings. Display names are the brand names (On-Site is `camp.html`, On-Fishing is `fishing.html`, On-Wildlife is `wildlife.html`, Maritides is `tides.html`, Unwrapped is `spotify.html`); the filenames are older than the names and stay.

Road trip pages: `roadtrip.html` is the public trip map for the Markham → Vancouver drive (Leaflet 1.9.4 and OpenStreetMap tiles from CDN, the only pages that load an external library). It probes `trip/days/<YYYY-MM-DD>.json` from its `TRIP_START` constant through today, no manifest, and draws one coloured polyline per day plus a day-by-day log (distance, driving time, `stay`, optional `notes`). `roadtrip-tracker.html` is the phone-side recorder: while open it logs a GPS point about every 100 m to localStorage (accuracy- and jump-filtered, wake lock held, auto-resumes on reload, days keyed by local date), holds the per-day "stayed:" field, and exports each day as `<date>.json` (or GPX for Strava). Publishing is self-serve from the phone: with a fine-grained PAT (this repo only, contents read/write) saved in the tracker's localStorage, it commits `trip/days/<date>.json` to `main` via the GitHub contents API — hourly while recording, on stop, on stay-field change, on day rollover, and via a per-day publish button. That is the owner pushing with the owner's own token from the owner's phone, so the owner-is-the-last-to-push rule holds; the two life workflows still never push to `main`. Fallback publish = drop the exported file in `trip/days/` unchanged and push. Day file shape: `{"date", "stay", "points": [[lat, lon, unixSeconds], ...]}`; a hand-added `"notes"` string also renders. Previewing `roadtrip.html` needs a static server (it fetches), not file://.

Redirect stubs for short URLs: `unwrapped.html` (to `/spotify-unwrapped/`), `nb-tides.html` (to `/maritides/`), and `on-site.html` (to `/camp.html`, kept so old links to the removed On-Site hub page still land somewhere).

`on-stores.html` is the sticker storefront, branded meishi stickers (all physical goods, cards, stickers, wallets, sell under the meishi brand; every sticker sold has an NFC tag inside; prices match Ontario Parks, not undercut). Its circle mockups are pure CSS (`.mockups`/`.mock`), placeholders until commissioned art exists. `business/` holds the private business plan and pitch; it is gitignored and must never be committed to this public repo. Detail pages must never share a name with one of my app repos, because a page named like a repo shadows that repo's project site path on katsuma.ca (that is why the tides detail page is `tides.html`, not `maritides.html`).

## No build step

No static site generator, no npm, no `package.json`. Every file is hand-authored source and served exactly as committed. Do not introduce a build step, a framework, or a package manager.

To preview, open the `.html` file directly or run any throwaway static server (there is a `static-site` entry in `.claude/launch.json` for the preview tools).

## Deploy and domains

GitHub Pages user site from the root of `main`. Pushing to `main` is the deploy. The two workflows, `.github/workflows/journal-ingest.yml` and `.github/workflows/life-post.yml`, are the life page pipelines (see below); both only ever open pull requests, they never push to `main`. The owner merges every life PR by hand; that merge is the approval and the deploy, so nothing lands on the public site without the owner being the last one to push.

Custom domain is `katsuma.ca` via the `CNAME` file. Because of that, every project repo with Pages also serves under it automatically: katsuma.ca/maritides, /on-site, /on-fishing, /on-wildlife, /spotify-unwrapped. Old /on-camp/... addresses fall through to `404.html`, which forwards them to /on-site/... keeping path, search and hash. The other katsuma.* domains forward at GoDaddy: .org and .site to katsuma.ca, .shop and .store to katsuma.ca/shop, .life to katsuma.ca/life.

## Layout

```
*.html                    pages, see above
CNAME
assets/site.css           the only stylesheet: tokens at the top, the document components below
styleguide.html           the design contract page for the resume look, both colour schemes
images/sewing/<slug>/1.jpeg, 2.jpeg, ...        originals, shown by the lightbox
images/sewing/<slug>/1-thumb.jpeg, ...          700px grid thumbnails, made with sips
images/life/<slug>/1.webp, 1-thumb.webp, ...    life photos, written by the journal pipeline
life/data/<slug>.json                           one record per life entry, the pipeline's source of truth
trip/days/<YYYY-MM-DD>.json                     one road trip day, exported by roadtrip-tracker.html
tools/journal_ingest.py                         Apple Journal export -> life entries
.github/workflows/journal-ingest.yml            release published -> ingest -> pull request
```

## Life page pipelines

`life.html` is katsuma.life (GoDaddy forward to katsuma.ca/life). Its entry
cards between the `journal:start` / `journal:end` markers are GENERATED from
`life/data/*.json` by `tools/journal_ingest.py` (`rebuild_page()`); edit the
JSON (or the generator), never the generated cards. Hand-written cards live
after the end marker inside `div.entries`. There are two ways in and one
source of truth: the Apple Journal export flow below, and the issue flow
(`.github/workflows/life-post.yml` + `.github/scripts/life_post.py`), where
the owner opens an issue titled `entry title | place` with the text and
photos in the body and a `life` label; the workflow writes the same JSON
record (with optional `title` and `place` fields the export flow does not
set), converts every attached photo to the same webp pairs, regenerates the
page with the shared renderer, and opens a PR. Both flows skip slugs that
already exist, so neither can clobber the other. Photos render three across;
the export flow keeps the first 12, the issue flow takes what is attached.

How a post happens: the owner writes an entry in Apple Journal titled
`life@<place><year>` (for example `life@grundy2026`; matching is forgiving
about case, spacing, doubled letters, and `:`/`#` for `@`, but the separator
is required so private entries can never leak), exports from Journal, and
uploads the export zip as an asset on a new GitHub release. The workflow
unpacks it, keeps only new life@ entries, takes the first 3 photos (0, 1, or
2 are fine), converts them to webp pairs, regenerates `life.html`, and opens
a PR. Journal exports always contain every entry; already-published slugs are
skipped, so re-exports are cheap. The entry's own date (Journal's date, not
upload day) sorts it, newest first, so backdated entries land in their true
spot. Display is title plus month and year only. No captions, no location on
the page, by the owner's choice.

To change or remove a published entry: edit or delete its
`life/data/<slug>.json` (and `images/life/<slug>/`), rerun
`python3 tools/journal_ingest.py <any export> ` or just call
`rebuild_page()`, and PR the result.

## Conventions

- The design is a plain document in the voice of a resume: one column at a 42rem measure, the system sans stack, quiet blue links, section names as small ruled `h2` labels, light and dark via `prefers-color-scheme`. Everything lives in `assets/site.css` (tokens at the top, components below); no hex outside the token block. `styleguide.html` is the contract; keep components matching it. No bars, no tiles, no glass, no app chrome of any kind.
- Everything displays lowercase, enforced by `text-transform: lowercase` on `body` and lowercase `<title>`/meta description text. Not a single uppercase letter anywhere. That is the owner's quirk, do not "fix" it.
- Navigation is text: `header.top` carries the name (the way home) on the left and four links (projects, life, shop, contact) on the right, on every page; the page it names gets `aria-current="page"`. No tab bar, nothing sticky. The redirect stubs (`nb-tides.html`, `on-site.html`, `unwrapped.html`) keep their single `opening … →` row. The homepage is still the hub; its sections link everything.
- Every page ends with the universal footer: name, email, phone, then the manually maintained last-updated line. The footer is pinned to the viewport bottom on short pages (body is a flex column, footer has margin-top auto).
- Page titles are `Page Name · Katsuma Onishi` with a middle dot. `index.html` is just `Katsuma Onishi`.
- Every page has a `meta name="description"` (lowercase).
- Sewing entries: `div.project` with `h3` title, `p.meta` date, `div.photos` grid, then description. Newest first, directly after the lead paragraph.
- Apps entries in `apps.html`: `div.item` with linked `h3`, `p.meta` (`App · Month Year · Claude Code` or `Project · Month Year · Tool`), summary, `More →` button. Newest first.
- Photo grids reference `-thumb.jpeg` files; the lightbox swaps `-thumb.jpeg` back to `.jpeg` for the original. A new photo needs both files. Thumbnail: `sips -Z 700 -s format jpeg -s formatOptions 55 N.jpeg --out N-thumb.jpeg`. The first project's photos load eagerly, everything below gets `loading="lazy"`.
- JavaScript stays inlined at the bottom of the page it belongs to, after the markup it operates on; do not move it to a shared file. There are three pages with any: the ~forty-line lightbox in `sewing-projects.html` (grid images keyboard-focusable, opens on click or Enter/Space, closes on Escape, overlay click, or the Close button, restores focus), and the two road trip pages (`roadtrip.html`, `roadtrip-tracker.html`), which are also the only pages allowed an external library (pinned Leaflet from unpkg, with SRI hashes).
- The emails on `contact.html` are written out literally (katsuma123@gmail.com, katsuma@meishi.shop). That was a deliberate August 2026 decision replacing the old anti-scraper obfuscation; do not re-obfuscate.

## Known issues, not urgent

Listed so you do not "discover" them at me every session. Do not fix these unless I ask.

- `.DS_Store` files are tracked. `.gitignore` exists but only covers `business/`; that is deliberate.
- The `hemsashiko` originals are only 240x320, smaller than every other project's photos, so their thumbs are just copies. Replace with higher-resolution exports when available and regenerate the thumbs.
- Project entries use `h3` titles directly under the page `h1`. Screen reader outline purists would prefer `h2`, but `h3` is the convention here.

## Do not

- Do not add a framework, bundler, or package manager.
- Do not extract the nav or footer into a templating system.
- Do not reformat or prettify the HTML wholesale. Diffs should be small and readable.
- Do not rewrite the copy into marketing voice. It is deliberately plain.
