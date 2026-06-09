# TREY + LORI + HUCK + GUS

A static site that mirrors the old Tumblr blog at **tlhg.org**, plus per-person pages
driven by short "what I'm working on" posts. Built for GitHub Pages.

- The whole 2006–2016 Tumblr archive (111 posts, 123 photos, 32 YouTube videos) is
  baked in as committed content — the site never depends on Tumblr staying up.
- Each name in the header links to that person's page: **TREY → /trey**, **LORI → /lori**,
  **HUCK → /huck**, **GUS → /gus**.
- You publish updates by editing one file, [`posts.toml`](posts.toml). A post tagged
  `trey` shows up in the home feed, the RSS feed, and on `/trey`.

---

## Publishing an update (the only thing you do day to day)

Open [`posts.toml`](posts.toml) and add a block:

```toml
[[post]]
title = "Finished the deck refinishing"
date  = 2026-07-04
tags  = ["lori"]
body  = """
Two weekends of sanding later, the back deck is **done**. Photos and the stain we
used are over on [the project log](https://example.com).
"""
```

Commit and push. The GitHub Action rebuilds and redeploys automatically — usually live
within a minute or two. That's it.

- `tags` decides which person page it lands on (`trey` / `lori` / `huck` / `gus`).
  Leave it off for a general family post (still shows in the feed, just not on a person page).
- `body` is Markdown: `**bold**`, `_italics_`, `[text](https://link)`, blank line = new paragraph.
- `date` can be a plain day (`2026-07-04`) or a precise time (`2026-07-04T18:30:00Z`).

---

## Building locally (optional, for previewing before you push)

```bash
pip install -r requirements.txt
python build.py
python -m http.server -d dist 8000   # then open http://localhost:8000
```

`build.py` reads `data/all_posts.json`, `assets/`, and `posts.toml`, and writes the
finished site into `dist/` (which is git-ignored — the Action builds it fresh).

---

## First-time setup on GitHub Pages

1. **Create the repo and push this folder.**
   ```bash
   git init && git add . && git commit -m "Initial site"
   git branch -M main
   git remote add origin https://github.com/<you>/tlhg.git
   git push -u origin main
   ```
2. **Turn on Pages via Actions.** In the repo: **Settings → Pages → Build and deployment →
   Source = GitHub Actions.** The included workflow (`.github/workflows/deploy.yml`) handles
   build + deploy on every push to `main`.
3. **Set the custom domain.** Still under **Settings → Pages**, enter `tlhg.org` in
   **Custom domain** and save. Then add these records at your DNS provider for the apex
   domain `tlhg.org`:

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

   (A `CNAME` file with `tlhg.org` is also included in the build as a fallback.)
4. Once DNS propagates, tick **Enforce HTTPS** in the Pages settings.

---

## gb.tlhg.org (the Grandiloquent Bloviator) — separate repo

`gb.tlhg.org` is a **subdomain**, so it's a second GitHub Pages site in its own repo:

1. Put the GB static site in its own repo and enable Pages the same way.
2. Set that repo's custom domain to `gb.tlhg.org`, and include a `CNAME` file containing
   `gb.tlhg.org`.
3. Add **one** DNS record for the subdomain (no A records needed for subdomains):

   | Type  | Name | Value |
   |-------|------|-------|
   | CNAME | gb   | `<you>.github.io` |

The link from Trey's page already points at `https://gb.tlhg.org`, so it lights up the
moment that subdomain is live.

---

## Layout

```
build.py                     generator (no network; reads the sources below)
posts.toml                   <- you edit this to publish updates
requirements.txt             markdown (only build dependency)
CNAME                        tlhg.org  (custom-domain fallback)
data/all_posts.json          archived Tumblr posts (source of truth)
assets/img/                  123 archived photos
assets/theme.css             original "Not Quite" theme CSS
.github/workflows/deploy.yml build + deploy to Pages
dist/                        build output (git-ignored)
```

Styling lives entirely in `assets/theme.css` plus a small additions block in `build.py`.
