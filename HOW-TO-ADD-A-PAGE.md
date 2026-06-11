# How to add a new page

Every entry is a plain HTML file. There's no build step and no tools to install —
you edit HTML and (if you host on GitHub Pages) commit & push. Adding one is four
short steps; the only one that takes a minute is pasting the block onto the home page.

Use **`entry-template.html`** (in the site root) as your starting point — it already
has the entry block marked and the spots you edit called out in ALL CAPS.

> **Person pages are single initials:** Trey = `/t/`, Lori = `/l/`, Huck = `/h/`,
> Gus = `/g/`. Tag links and the header all point to those.

---

## 1. Create the entry's own page

1. Pick a short **slug** for the URL, e.g. `deck-refinish`.
2. Make the folder `entry/deck-refinish/` and copy `entry-template.html` into it as
   `index.html` (so the file is `entry/deck-refinish/index.html`).
3. Edit these spots in that file:
   - **`<title>`** — your headline (keep the ` — TREY + LORI + HUCK + GUS` part).
   - **both `/entry/SLUG/`** links — change `SLUG` to `deck-refinish`.
   - the **date** in the timestamp.
   - the **tag** — set the link to the right initial (`/t/`, `/l/`, `/h/`, `/g/`) and
     the label to the name, or delete that whole `<div class="tags">…</div>` line for a
     general family post.
   - the **title** and the **body** paragraphs.

That page now works on its own at `/entry/deck-refinish/`.

## 2. Show it on the home page

1. In your new file, copy everything between `<!-- THE ENTRY BLOCK -->` and
   `<!-- END ENTRY BLOCK -->` (the `<div id="post"> … </div>`).
2. Open `index.html` and paste it right after `<div id="content">`, above the
   current newest entry.
3. Scroll to the bottom of the entry list and delete the **oldest** `<div id="post">…</div>`
   block, so the home page keeps showing 10. (Older entries still live on the Archive page.)

## 3. (If you tagged it) add it to the person page

Open the tagged person's page — `t/index.html` for Trey (or `l/`, `h/`, `g/`) — and
paste the same block at the top, right after `<div id="content">`. If the page still
says "Nothing here yet," replace that placeholder block instead.

## 4. Add it to the Archive

Open `archive/index.html` and add one line at the top of the `archive-list`:

```html
<a class="arc" href="/entry/deck-refinish/"><span class="arc-date">Jul 4, 2026</span><span class="arc-title">deck refinish</span></a>
```

---

## Publish

If you're on GitHub Pages: `git add . && git commit -m "New entry" && git push`.
It's live in a minute or so. To preview locally first, run a tiny web server from the
site folder (the site uses absolute `/` paths, so opening files directly won't load the
CSS):

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Notes

- **Paths are absolute** (`/style.css`, `/entry/…`, `/img/…`, `/t/`), which is why the
  same entry block can be pasted onto any page unchanged. It assumes the site is served
  at the domain root (which GitHub Pages with your custom domain does).
- **`rss.xml`** is a static snapshot; updating it is optional.
- The 111 archived Tumblr posts live under `/post/…` and don't need touching.
