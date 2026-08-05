# katsuma0.github.io

## What this is

My personal site. Seven hand-written HTML pages: `index.html`, `data-projects.html`, `sewing-projects.html`, `on-site.html` (Ontario fishing and wildlife), `shop.html`, `contact.html`, and `life.html` (events and a small public log, the landing page for katsuma.life, deliberately outside the main nav). Nav labels are Apps and Projects (`data-projects.html`) and Arts and Crafts (`sewing-projects.html`); the filenames are older than the labels and stay as they are.

## No build step

There is no static site generator here. No Jekyll, no Astro, no npm, no `package.json`, no `node_modules`. Every file in the repo is hand-authored source and is served exactly as committed.

There is no dev server and no port. To preview, open the `.html` file directly, or run any throwaway static server if you need one.

Do not introduce a build step, a framework, or a package manager. If something feels like it needs a build, it does not.

## Deploy

GitHub Pages user site, served from the root of `main` at `https://github.com/katsuma0/katsuma0.github.io`. Pushing to `main` is the deploy. There are no workflows and no `.github/` directory. Custom domain is `katsuma.ca` via the `CNAME` file; other katsuma.* domains forward to it at the registrar.

## Layout

```
index.html
data-projects.html
sewing-projects.html
on-site.html
shop.html
contact.html
life.html
CNAME
style.css                 shared by all pages
katsuma_onishi_resume.pdf
images/sewing/<slug>/1.jpeg, 2.jpeg, ...        originals, shown by the lightbox
images/sewing/<slug>/1-thumb.jpeg, ...          700px grid thumbnails, made with sips
```

`style.css` is the only stylesheet. Times New Roman, 700px max width, black and white. Keep it that way.

The only JavaScript in the project is about forty lines of lightbox code inlined at the bottom of `sewing-projects.html`. It makes the grid images keyboard-focusable, opens on click or Enter/Space, closes on Escape, overlay click, or the Close button, and restores focus afterwards. It has to stay after the markup it operates on. Do not move it to a shared file.

## Conventions

- The six-link `<nav>` block is duplicated verbatim in every page except `life.html`, which only links back home on purpose. Adding or renaming a page means editing each one by hand. There is no include mechanism and that is fine.
- Photo grids reference the `-thumb.jpeg` files; the lightbox swaps `-thumb.jpeg` back to `.jpeg` to show the original. A new photo needs both files. Regenerate a thumbnail with: `sips -Z 700 -s format jpeg -s formatOptions 55 N.jpeg --out N-thumb.jpeg`.
- Every page has a footer with a manually maintained `Last updated: <Month Year>` string.
- Page titles are `Page Name — Katsuma Onishi`. `index.html` is just `Katsuma Onishi`.
- Sewing entries use `<div class="project">` containing `<h3>` title, `<p class="meta">Month Year</p>`, a `<div class="photos">` grid, then a description paragraph.
- `data-projects.html` reuses the same `.project` and `.meta` classes, but `.meta` there is `Month Year &nbsp;·&nbsp; Tools`.
- Sewing projects are newest first. A new entry goes at the top, directly after the intro paragraph.
- Sewing image folders are slugs like `sashiko3`, `hemsashiko`, `jorts`. Files inside are always numbered `1.jpeg`, `2.jpeg`, and so on.
- The email on `contact.html` is deliberately written as `[My first name]123@gmail.com` instead of literally, to avoid scrapers. Preserve that. Do not "fix" it.

## Note on the em dash rule

My global CLAUDE.md says no em dashes. That applies to prose you write. It does not apply to the existing `<title>` tags here, which already use one as a separator. Leave those alone unless I ask to change them, and match the existing pattern if you add a page.

## Known issues, not urgent

Listed so you do not "discover" them at me every session. Do not fix these unless I ask.

- `.DS_Store` files are tracked. There is no `.gitignore`.
- The `hemsashiko` originals are only 240x320, smaller than every other project's photos, so their thumbs are just copies. Replace them with higher-resolution exports when available and regenerate the thumbs.
- Project entries use `h3` titles directly under the page `h1` (no `h2` level). Screen reader outline purists would prefer `h2`, but `h3` is the documented convention here.

The alt text, footer date drift, and sewing entry typos that used to be listed here were fixed in August 2026.

## Do not

- Do not add a framework, bundler, or package manager.
- Do not extract the nav or footer into a templating system.
- Do not reformat or prettify the HTML wholesale. Diffs should be small and readable.
- Do not rewrite the copy on the site into marketing voice. It is deliberately plain.
