# katsuma0.github.io

## What this is

My personal site, served at katsuma.ca. Hand-written HTML pages, no blog engine.

Main pages: `index.html`, `apps.html` (projects), `sewing-projects.html` (art projects), `contact.html`.

`privacy.html`, `support.html`, and `terms.html` are deliberately unlinked from the site but must stay live: the On-Site and On-Wildlife apps link to them from inside the apps, and their App Store submissions use them as the privacy and support URLs. They point to `contact.html` instead of listing an email.

App and project detail pages, all linked from `apps.html`: `nfc.html`, `road-trip.html`, `satellite.html`, `silly.html`, `used-car-take-two.html`, `tides.html`, `wildlife.html`, `fishing.html`, `camp.html`, `spotify.html`, `used-car.html`, `carbon-cycle.html`, `dsa.html`. Satellite AI's repo is private, so its page has no link out. They use a `backlink` to Projects, an `Open the app ↗` button for apps, and `h4` section headings. Display names are the brand names (On-Site is `camp.html`, On-Fishing is `fishing.html`, On-Wildlife is `wildlife.html`, Maritides is `tides.html`, Unwrapped is `spotify.html`); the filenames are older than the names and stay.

Redirect stubs for short URLs: `unwrapped.html` (to `/spotify-unwrapped/`), `nb-tides.html` (to `/maritides/`), and `on-site.html` (to `/camp.html`, kept so old links to the removed On-Site hub page still land somewhere).

`business/` is gitignored and must never be committed to this public repo. Detail pages must never share a name with one of my app repos, because a page named like a repo shadows that repo's project site path on katsuma.ca (that is why the tides detail page is `tides.html`, not `maritides.html`).

## No build step

No static site generator, no npm, no `package.json`. Every file is hand-authored source and served exactly as committed. Do not introduce a build step, a framework, or a package manager.

To preview, open the `.html` file directly or run any throwaway static server (there is a `static-site` entry in `.claude/launch.json` for the preview tools).

## Deploy and domains

GitHub Pages user site from the root of `main`. Pushing to `main` is the deploy. The owner merges every PR by hand; that merge is the approval and the deploy, so nothing lands on the public site without the owner being the last one to push. Never merge to `main` yourself.

Custom domain is `katsuma.ca` via the `CNAME` file. Because of that, every project repo with Pages also serves under it automatically: katsuma.ca/maritides, /on-site, /on-fishing, /on-wildlife, /spotify-unwrapped. Old /on-camp/... addresses fall through to `404.html`, which forwards them to /on-site/... keeping path, search and hash. The other katsuma.* domains forward at GoDaddy. The shop and life pages were removed in October 2026, so the .shop, .store, and .life forwards should point at katsuma.ca itself.

## Layout

```
*.html                    pages, see above
CNAME
assets/site.css           the only stylesheet: tokens at the top, the document components below
styleguide.html           the design contract page for the resume look, both colour schemes
images/sewing/<slug>/1.jpeg, 2.jpeg, ...        originals, shown by the lightbox
images/sewing/<slug>/1-thumb.jpeg, ...          700px grid thumbnails, made with sips
```

## Conventions

- The design is a plain document in the voice of a resume: one column at a 42rem measure, the system sans stack, quiet blue links, section names as small ruled `h2` labels, light and dark via `prefers-color-scheme`. Everything lives in `assets/site.css` (tokens at the top, components below); no hex outside the token block. `styleguide.html` is the contract; keep components matching it. No bars, no tiles, no glass, no app chrome of any kind.
- Normal sentence case and proper punctuation everywhere: names, nav, titles, descriptions, and body copy are written properly capitalized in the source. The old all-lowercase look was retired in October 2026; do not bring back `text-transform: lowercase`.
- Navigation is text: `header.top` carries the name (the way home) on the left and three links (Projects, Art Projects, Contact) on the right, on every page; the page it names gets `aria-current="page"`. No tab bar, nothing sticky. The redirect stubs (`nb-tides.html`, `on-site.html`, `unwrapped.html`) keep their single `opening … →` row. The homepage is the bio, then a `.rows` list of the three links (no section descriptions), then the footer.
- Every page ends with the universal footer: name, then the manually maintained last-updated line. The footer is pinned to the viewport bottom on short pages (body is a flex column, footer has margin-top auto).
- Page titles are `Page Name · Katsuma Onishi` with a middle dot. `index.html` is just `Katsuma Onishi`.
- Every page has a `meta name="description"`.
- Sewing entries: `div.project` with `h3` title, `p.meta` date, `div.photos` grid, then description. Newest first, directly after the lead paragraph.
- Apps entries in `apps.html`: `div.item` with linked `h3`, `p.meta` (`App · Month Year · Claude Code` or `Project · Month Year · Tool`), summary, `More →` button. Newest first.
- Photo grids reference `-thumb.jpeg` files; the lightbox swaps `-thumb.jpeg` back to `.jpeg` for the original. A new photo needs both files. Thumbnail: `sips -Z 700 -s format jpeg -s formatOptions 55 N.jpeg --out N-thumb.jpeg`. The first project's photos load eagerly, everything below gets `loading="lazy"`.
- The only JavaScript is about forty lines of lightbox code inlined at the bottom of `sewing-projects.html`. It makes grid images keyboard-focusable, opens on click or Enter/Space, closes on Escape, overlay click, or the Close button, and restores focus. It stays after the markup it operates on. Do not move it to a shared file.
- The only place an email appears is the top row of `contact.html`. No email or phone number anywhere else, footers included (October 2026 decision).

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
