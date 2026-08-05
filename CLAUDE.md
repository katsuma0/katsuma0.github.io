# katsuma0.github.io

## What this is

My personal site, served at katsuma.ca. Hand-written HTML pages, no blog engine.

Main pages: `index.html`, `apps.html`, `sewing-projects.html`, `shop.html`, `contact.html`, plus `life.html` (events and a small public log, the landing page for katsuma.life, deliberately outside the main nav, it only links back home).

App and project detail pages, all linked from `apps.html`: `tides.html`, `wildlife.html`, `fishing.html`, `camp.html`, `spotify.html`, `used-car.html`, `carbon-cycle.html`, `dsa.html`. They use a `backlink` to Projects, an `Open the app ↗` button for apps, and `h4` section headings. Display names are the brand names (On-Site is `camp.html`, On-Fishing is `fishing.html`, On-Wildlife is `wildlife.html`, Maritides is `tides.html`, Unwrapped is `spotify.html`); the filenames are older than the names and stay.

Redirect stubs for short URLs: `unwrapped.html` (to `/spotify-unwrapped/`), `nb-tides.html` (to `/maritides/`), and `on-site.html` (to `/camp.html`, kept so old links to the removed On-Site hub page still land somewhere).

`on-stores.html` is the sticker storefront (every sticker sold has an NFC tag inside; prices match Ontario Parks, not undercut). Its circle mockups are pure CSS (`.mockups`/`.mock`), placeholders until commissioned art exists. `business/` holds the private business plan and pitch; it is gitignored and must never be committed to this public repo. Detail pages must never share a name with one of my app repos, because a page named like a repo shadows that repo's project site path on katsuma.ca (that is why the tides detail page is `tides.html`, not `maritides.html`).

## No build step

No static site generator, no npm, no `package.json`. Every file is hand-authored source and served exactly as committed. Do not introduce a build step, a framework, or a package manager.

To preview, open the `.html` file directly or run any throwaway static server (there is a `static-site` entry in `.claude/launch.json` for the preview tools).

## Deploy and domains

GitHub Pages user site from the root of `main`. Pushing to `main` is the deploy. No workflows, no `.github/` directory.

Custom domain is `katsuma.ca` via the `CNAME` file. Because of that, every project repo with Pages also serves under it automatically: katsuma.ca/maritides, /on-camp, /on-fishing, /on-wildlife, /spotify-unwrapped. The other katsuma.* domains forward at GoDaddy: .org and .site to katsuma.ca, .shop and .store to katsuma.ca/shop, .life to katsuma.ca/life.

## Layout

```
*.html                    pages, see above
CNAME
style.css                 the only stylesheet, CSS variables, mobile first, 820px breakpoint
images/sewing/<slug>/1.jpeg, 2.jpeg, ...        originals, shown by the lightbox
images/sewing/<slug>/1-thumb.jpeg, ...          700px grid thumbnails, made with sips
```

## Conventions

- The design matches meishi.shop on purpose: cream background (#f2eee4), navy ink (#22304a), system sans, one narrow 36rem column, generous spacing. CSS variables in `:root`. Keep it that way.
- Everything displays lowercase, enforced by `text-transform: lowercase` on `body` and lowercase `<title>`/meta description text. Not a single uppercase letter anywhere. That is the owner's quirk, do not "fix" it.
- No nav. Every page except `index.html` starts with a `← back to katsuma.ca` backlink (detail pages also get `← projects`). The homepage is the hub; its sections link everything. Hub and spoke, never more than one hop from home.
- Every page ends with the universal footer: name, email, phone, then the manually maintained last-updated line. The footer is pinned to the viewport bottom on short pages (body is a flex column, footer has margin-top auto).
- Page titles are `Page Name · Katsuma Onishi` with a middle dot. `index.html` is just `Katsuma Onishi`.
- Every page has a `meta name="description"` (lowercase).
- Sewing entries: `div.project` with `h3` title, `p.meta` date, `div.photos` grid, then description. Newest first, directly after the lead paragraph.
- Apps entries in `apps.html`: `div.item` with linked `h3`, `p.meta` (`App · Month Year · Claude Code` or `Project · Month Year · Tool`), summary, `More →` button. Newest first.
- Photo grids reference `-thumb.jpeg` files; the lightbox swaps `-thumb.jpeg` back to `.jpeg` for the original. A new photo needs both files. Thumbnail: `sips -Z 700 -s format jpeg -s formatOptions 55 N.jpeg --out N-thumb.jpeg`. The first project's photos load eagerly, everything below gets `loading="lazy"`.
- The only JavaScript is about forty lines of lightbox code inlined at the bottom of `sewing-projects.html`. It makes grid images keyboard-focusable, opens on click or Enter/Space, closes on Escape, overlay click, or the Close button, and restores focus. It stays after the markup it operates on. Do not move it to a shared file.
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
