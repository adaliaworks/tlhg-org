# How to add a new page

Every entry is a plain HTML file. No build step, no tools — you edit HTML and (if you
host on GitHub Pages) commit & push.

Each page has a `<base href>` line in its `<head>` that points back to the site root, so
all the in-page links are written plain (`t/`, `img/…`, `entry/…`). The payoff: **the
entry block is identical on every page** — you paste the very same block onto the home
page, the person page, and its own page, with no path fiddling. Just don't edit the
`<base href>` line.

Start from **`entry-template.html`** in the site root.

> Person pages are single initials: Trey = `t/`, Lori = `l/`, Huck = `h/`, Gus = `g/`.

---

## 1. Create the entry's own page

1. Pick a short **slug**, e.g. `deck-refinish`.
2. Make the folder `entry/deck-refinish/` and copy `entry-template.html` into it as
   `index.html`.
3. Edit, in that file: the **`<title>`**, both **`entry/SLUG/`** links (→ `entry/deck-refinish/`),
   the **date**, the **tag** (set the link to `t/`/`l/`/`h/`/`g/` and the label to the
   name, or delete the `<div class="tags">…</div>` line), the **title**, and the **body**.
   Leave the `<base href="../../">` line alone.

That page now works on its own at `/entry/deck-refinish/`.

## 2. Show it on the home page

1. In your new file, copy everything between `<!-- THE ENTRY BLOCK -->` and
   `<!-- END ENTRY BLOCK -->` (the `<div id="post"> … </div>`).
2. Open `index.html`, paste it right after `<div id="content">` (above the newest entry).
3. Delete the **oldest** `<div id="post">…</div>` at the bottom so the home page keeps 10.

## 3. (If you tagged it) add it to the person page

Open `t/index.html` (or `l/`, `h/`, `g/`) and paste the **same block** at the top. No
edits needed — the base tag makes it resolve correctly here too. If the page still says
"Nothing here yet," replace that placeholder block instead.

## 4. Add it to the Archive

Open `archive/index.html` and add one line at the top of the `archive-list`:

```html
<a class="arc" href="entry/deck-refinish/"><span class="arc-date">Jul 4, 2026</span><span class="arc-title">deck refinish</span></a>
```

---

## Preview & publish

- **Preview:** just open the `.html` file in your browser — it's styled correctly now,
  because the `<base>` tag resolves the stylesheet and images relative to the file.
  (Clicking *between* pages locally is smoother through a quick server —
  `python3 -m http.server 8000` from the site folder — but viewing any single page works
  with a plain double-click.)
- **Publish (GitHub Pages):** `git add . && git commit -m "New entry" && git push`. Live
  in a minute or so.

## Notes

- The 111 archived Tumblr posts live under `post/…` and don't need touching.
- `rss.xml` is a static snapshot; updating it is optional.
