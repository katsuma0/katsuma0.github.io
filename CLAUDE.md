# katsuma0.github.io

## What this is

My personal site, served at katsuma.ca. Hand-written HTML pages, no blog engine.

Every page is a folder with an `index.html`, so URLs are clean: `/` (home), `/projects/`, `/art-projects/`, `/contact/`. All internal links and asset paths are root-absolute (`/assets/site.css`, `/images/...`, `/projects/`), never relative, so a page works at any folder depth.

`privacy.html`, `support.html`, and `terms.html` are deliberately unlinked from the site but must stay live: the On-Site and On-Wildlife apps link to them from inside the apps, and their App Store submissions use them as the privacy and support URLs. They point to `/contact/` instead of listing an email.

Project detail pages live under `/projects/<name>/`: same-spot (repo camera-overlay), nfc-editor, road-trip-2026, satellite-ai, silly-spaces, used-car-take-two, maritides, on-wildlife, on-site, on-fishing, unwrapped, used-car, carbon-cycle, dsa-cryptosystem. The full car report is at `/projects/linearregressioncarpriceanalysis/`. Satellite AI's repo is private, so its page has no link out. They use a `backlink` to Projects, an `Open the app ↗` button for apps, and `h4` section headings. The old flat filenames (`apps.html`, `sewing-projects.html`, `contact.html`, `wildlife.html`, `camp.html`, `tides.html`, and the rest) are now redirect stubs to the new folders. Keep them: app repos, App Store listings, and old bookmarks link to them.

Short-URL redirect stubs: `unwrapped.html` (to `/spotify-unwrapped/`) and `nb-tides.html` (to `/maritides/`).

`business/` is gitignored and must never be committed to this public repo. Never create a top-level page or folder named like one of my app repos (on-site, on-fishing, on-wildlife, maritides, spotify-unwrapped, roadtrip-2026, shop), because it would shadow that repo's project site at katsuma.ca/<repo>/. Nesting under `/projects/` is safe.

## No build step

No static site generator, no npm, no `package.json`. Every file is hand-authored source and served exactly as committed. Do not introduce a build step, a framework, or a package manager.

To preview, open the `.html` file directly or run any throwaway static server (there is a `static-site` entry in `.claude/launch.json` for the preview tools).

## Deploy and domains

GitHub Pages user site from the root of `main`. Pushing to `main` is the deploy. The owner merges every PR by hand; that merge is the approval and the deploy, so nothing lands on the public site without the owner being the last one to push. Never merge to `main` yourself.

Custom domain is `katsuma.ca` via the `CNAME` file. Because of that, every project repo with Pages also serves under it automatically: katsuma.ca/maritides, /on-site, /on-fishing, /on-wildlife, /spotify-unwrapped, /shop. Old /on-camp/... addresses fall through to `404.html`, which forwards them to /on-site/... keeping path, search and hash. The other katsuma.* domains forward at GoDaddy. The old shop and life pages were removed in October 2026. The shop came back in November 2026 as its own repo, `shop` (formerly sticker-shop), served at katsuma.ca/shop/, so the .shop and .store forwards should point there and .life at katsuma.ca itself.

## Layout

```
index.html, 404.html         home and not-found
projects/<name>/index.html    projects page and project detail pages
art-projects/index.html       art projects
contact/index.html            contact
privacy.html, support.html, terms.html   app policy pages, unlinked, fixed URLs
*.html (other)                redirect stubs for old addresses
CNAME
assets/site.css           the only stylesheet: tokens at the top, the document components below
styleguide.html           the design contract page for the resume look, both colour schemes
images/sewing/<slug>/1.jpeg, 2.jpeg, ...        originals, shown by the lightbox
images/sewing/<slug>/1-thumb.jpeg, ...          700px grid thumbnails, made with sips
```

## Conventions

- The design is a plain document in the voice of a resume: one column at a 42rem measure, the system sans stack, quiet blue links, section names as small ruled `h2` labels, light and dark via `prefers-color-scheme`. Everything lives in `assets/site.css` (tokens at the top, components below); no hex outside the token block. `styleguide.html` is the contract; keep components matching it. No bars, no tiles, no glass, no app chrome of any kind.
- Normal sentence case and proper punctuation everywhere: names, nav, titles, descriptions, and body copy are written properly capitalized in the source. The old all-lowercase look was retired in October 2026; do not bring back `text-transform: lowercase`.
- Navigation is text: `header.top` carries the name (the way home) on the left and three links (Projects, Art Projects, Contact) on the right, on every page; the page it names gets `aria-current="page"`. No tab bar, nothing sticky. Redirect stubs carry no nav, just a single continue row. The homepage is the bio, then a `.rows.plain` list of the three links plus Shop (no section descriptions, no rules between them), then the footer. Contact uses the same `.rows.plain` list, with each label in plain text and only the address as the link.
- Every page ends with the universal footer: name, then the manually maintained last-updated line. The footer is pinned to the viewport bottom on short pages (body is a flex column, footer has margin-top auto).
- Page titles are `Page Name · Katsuma Onishi` with a middle dot. `index.html` is just `Katsuma Onishi`.
- Every page has a `meta name="description"`.
- Sewing entries: `div.project` with `h3` title, `p.meta` date, `div.photos` grid, then description. Newest first, directly after the lead paragraph.
- Apps entries in `projects/index.html`: `div.item` with a linked title row carrying the meta (`App · Month Year · Claude Code` or `Project · Month Year · Tool`), then the summary. No More button; the title is the link, and items are spaced 2rem apart instead. Roughly newest first, with On-Site ahead of the other On- apps by the owner's choice.
- Photo grids reference `-thumb.jpeg` files; the lightbox swaps `-thumb.jpeg` back to `.jpeg` for the original. A new photo needs both files. Thumbnail: `sips -Z 700 -s format jpeg -s formatOptions 55 N.jpeg --out N-thumb.jpeg`. The first project's photos load eagerly, everything below gets `loading="lazy"`.
- The only JavaScript is about forty lines of lightbox code inlined at the bottom of `art-projects/index.html`. It makes grid images keyboard-focusable, opens on click or Enter/Space, closes on Escape, overlay click, or the Close button, and restores focus. It stays after the markup it operates on. Do not move it to a shared file.
- The only place an email appears is the top row of `contact/index.html`. No email or phone number anywhere else, footers included (October 2026 decision).

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
