# TREY + LORI + HUCK + GUS

A plain static HTML site. No build step, no tools, no dependencies — just HTML, CSS,
and images you can edit directly.

- The home page (`index.html`) shows the **10 most recent entries**, expanded.
- **Every entry is its own page** under `entry/<slug>/` (going forward) or `post/…`
  (the archived 2006–2016 Tumblr posts).
- Each name in the header links to that person's page at their **initial**:
  **TREY → /t**, **LORI → /l**, **HUCK → /h**, **GUS → /g**. A page tagged `trey`
  shows up on `/t` as well as the home page.
- The full chronological list of everything is on the **Archive** page.

## Adding a page

See **[HOW-TO-ADD-A-PAGE.md](HOW-TO-ADD-A-PAGE.md)**. Short version: copy
`entry-template.html`, fill it in, drop it at `entry/<slug>/index.html`, paste its
entry block at the top of `index.html` (and trim the oldest), then commit & push.

## Previewing locally

The site uses absolute paths (`/style.css`, `/entry/…`), so serve it rather than
opening files directly:

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Hosting on GitHub Pages

1. Push this folder to a repo, then **Settings → Pages → Source = Deploy from a branch**,
   branch `main`, folder `/ (root)`. (No Action needed — it's already static HTML.)
2. Under **Settings → Pages**, set **Custom domain** to `tlhg.org`. A `CNAME` file is
   already included.
3. At your DNS provider, point the apex domain `tlhg.org` at GitHub Pages:

   | Type | Name | Value |
   |------|------|-------|
   | A    | @    | 185.199.108.153 |
   | A    | @    | 185.199.109.153 |
   | A    | @    | 185.199.110.153 |
   | A    | @    | 185.199.111.153 |
   | AAAA | @    | 2606:50c0:8000::153 |
   | AAAA | @    | 2606:50c0:8001::153 |
   | AAAA | @    | 2606:50c0:8002::153 |
   | AAAA | @    | 2606:50c0:8003::153 |

4. After DNS propagates, tick **Enforce HTTPS**.

`gb.tlhg.org` (the Grandiloquent Bloviator) is a **subdomain** = its own repo. There,
set the custom domain to `gb.tlhg.org` and add one DNS record: `CNAME gb → <you>.github.io`.

## Layout

```
index.html              home — 10 newest entries, expanded
entry/<slug>/           your hand-written entries (one folder each)
post/<id>/<slug>/        the 111 archived Tumblr posts
t/ l/ h/ g/              person pages (Trey / Lori / Huck / Gus)
archive/                 full chronological index
about/  subscribe/       simple pages
img/                     all photos
style.css                the whole look (one file)
entry-template.html      copy this to make a new entry
rss.xml                  static feed snapshot (optional to update)
CNAME                    tlhg.org
```
