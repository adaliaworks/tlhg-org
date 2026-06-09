#!/usr/bin/env python3
"""Build the TREY + LORI + HUCK + GUS static site into ./dist.

Sources (all committed to the repo, so builds never touch the network):
  data/all_posts.json   the archived Tumblr blog (111 posts, 2006-2016)
  assets/img/           the 123 archived photos
  assets/theme.css      the original "Not Quite" theme CSS
  posts.toml            <-- the file you edit to publish new updates

Run:  python build.py      (output goes to ./dist)
"""
import json, os, re, html, shutil
from datetime import datetime, timezone, date as _date, time as _time

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(BASE, "dist")
IMG_SRC = os.path.join(BASE, "assets", "img")
THEME_CSS = os.path.join(BASE, "assets", "theme.css")
DATA = os.path.join(BASE, "data", "all_posts.json")
POSTS_TOML = os.path.join(BASE, "posts.toml")

PER_PAGE = 10
PEOPLE = [("TREY", "trey"), ("LORI", "lori"), ("HUCK", "huck"), ("GUS", "gus")]
PERSON_SLUGS = {slug for _, slug in PEOPLE}
PERSON_INTRO = {"trey": "Trey", "lori": "Lori", "huck": "Huck", "gus": "Gus"}
SITE_TITLE = "TREY + LORI + HUCK + GUS"

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
tslug = slugify

# ---------------------------------------------------------------- markdown
try:
    import markdown as _md
    def md_to_html(text):
        return _md.markdown(text.strip(), extensions=["extra"])
except Exception:
    # Minimal fallback so a local build works even without the markdown package.
    def md_to_html(text):
        out = []
        for para in re.split(r"\n\s*\n", text.strip()):
            p = html.escape(para.strip())
            p = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', p)
            p = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", p)
            p = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", p)
            out.append("<p>" + p.replace("\n", "<br>") + "</p>")
        return "\n".join(out)

# ---------------------------------------------------------------- load posts
def load_archived():
    return json.load(open(DATA))

def load_custom():
    if not os.path.exists(POSTS_TOML):
        return []
    import tomllib
    data = tomllib.load(open(POSTS_TOML, "rb"))
    out = []
    for e in data.get("post", []):
        d = e["date"]
        if isinstance(d, datetime):
            dt = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        elif isinstance(d, _date):
            dt = datetime.combine(d, _time(12, 0), tzinfo=timezone.utc)
        else:  # string
            s = str(d).replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(s)
            except ValueError:
                dt = datetime.fromisoformat(s + "T12:00:00")
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
        slug = e.get("slug") or slugify(e["title"])
        out.append({
            "id": e.get("id") or slug,
            "custom": True,
            "type": "regular",
            "slug": slug,
            "regular-title": e["title"],
            "regular-body": md_to_html(e["body"]),
            "tags": e.get("tags", []),
            "unix-timestamp": int(dt.timestamp()),
        })
    return out

POSTS = load_custom() + load_archived()
POSTS.sort(key=lambda p: int(p["unix-timestamp"]), reverse=True)

# ---------------------------------------------------------------- helpers
def localname(url):
    if not url:
        return None
    import urllib.parse
    base = os.path.basename(urllib.parse.urlparse(url).path)
    return re.sub(r"[^A-Za-z0-9_.-]", "_", base)

def biggest_photo(d):
    for k in ("photo-url-1280", "photo-url-500", "photo-url-400", "photo-url-250", "photo-url-100"):
        if d.get(k):
            return d[k]
    return None

def prefix(depth):
    return "../" * depth

def post_path(p):
    slug = p.get("slug") or ""
    if p.get("custom"):
        return f"post/{slug}/"
    pid = p["id"]
    return f"post/{pid}/{slug}/" if slug else f"post/{pid}/"

def fmt_date(p):
    dt = datetime.fromtimestamp(int(p["unix-timestamp"]), tz=timezone.utc)
    return f"{dt.strftime('%b')}. {dt.day}, {dt.year} at {dt.strftime('%-I:%M%p').lower()}"

def yt_id(src):
    src = src or ""
    m = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/))([A-Za-z0-9_-]{6,})", src)
    return m.group(1) if m else None

def fix_caption_links(t, px):
    if not t:
        return ""
    def repl(m):
        pid, slug = m.group(1), m.group(2) or ""
        rel = f"post/{pid}/{slug}/" if slug else f"post/{pid}/"
        return f'href="{px}{rel}"'
    return re.sub(r'href="https?://tlhg\.org/post/(\d+)(?:/([^"/]+))?/?"', repl, t)

# ---------------------------------------------------------------- render post
def render_post(p, px):
    pp = post_path(p)
    permalink = px + pp
    tag_links = []
    for tg in (p.get("tags") or []):
        s = tslug(tg)
        if s in PERSON_SLUGS:
            tag_links.append(f'<a href="{px}{s}/" class="tag">{html.escape(tg)}</a>')
        else:
            tag_links.append(f'<span class="tag">{html.escape(tg)}</span>')
    tags_html = f'\n\t<div class="tags">{"".join(tag_links)}</div>' if tag_links else ""
    left = (f'<div class="left">\n'
            f'\t<a href="{permalink}" class="timestamp">{fmt_date(p)}</a>'
            f'{tags_html}\n</div>')

    parts = []
    t = p["type"]
    if t == "photo":
        photos = p.get("photos") or []
        srcs = [biggest_photo(ph) for ph in photos] if photos else [biggest_photo(p)]
        for src in srcs:
            ln = localname(src)
            if ln:
                parts.append(f'<a href="{permalink}"><img src="{px}img/{ln}" alt=""></a>')
                parts.append('<div class="space small"></div>')
        cap = fix_caption_links(p.get("photo-caption") or "", px)
        if cap:
            parts.append(cap)
    elif t == "video":
        vid = yt_id(p.get("video-source"))
        if vid:
            parts.append('<div class="video-embed"><iframe width="500" height="281" '
                         f'src="https://www.youtube.com/embed/{vid}" frameborder="0" '
                         'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                         'gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
        else:
            parts.append(f'<p><a href="{html.escape(p.get("video-source") or "")}">Watch video</a></p>')
        parts.append('<div class="space small"></div>')
        cap = fix_caption_links(p.get("video-caption") or "", px)
        if cap:
            parts.append(cap)
    elif t == "regular":
        if p.get("regular-title"):
            parts.append(f'<a href="{permalink}" class="title">{html.escape(p["regular-title"])}</a>')
        body = fix_caption_links(p.get("regular-body") or "", px)
        if body:
            parts.append(body)
    else:
        body = fix_caption_links(p.get("photo-caption") or p.get("video-caption") or "", px)
        if body:
            parts.append(body)

    right = '<div class="right">\n\t' + "\n\t".join(parts) + "\n</div>"
    return f'<div id="post">\n{left}\n{right}\n</div>'

# ---------------------------------------------------------------- page shell
def header(px):
    names = " + ".join(f'<a href="{px}{slug}/">{disp}</a>' for disp, slug in PEOPLE)
    return ('<div id="header">\n'
            f'\t<h1 class="title">{names}</h1>\n'
            '\t<div class="bar">\n'
            f'\t\t<a href="{px}about/">about</a> | <a href="{px}subscribe/">subscribe</a> | '
            f'<span style="text-transform:lowercase;"><a href="{px}rss.xml">RSS</a> | '
            f'<a href="{px}archive/">Archive</a></span>\n\t</div>\n</div>')

def footer(px, pagination=""):
    return ('<div id="footer">\n'
            f'\t{pagination}\n'
            '\t<div class="credit">Mirrored from the &ldquo;Not Quite&rdquo; theme by '
            '<a href="http://www.petervidani.com" target="_blank" rel="noopener">Peter Vidani</a>.'
            '</div>\n</div>')

def page_shell(title, body, px):
    foot = footer(px) if '<div id="footer"' not in body else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{px}style.css">
<link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="{px}rss.xml">
</head>
<body>
{header(px)}
<div id="content">
{body}
</div>
{foot}
</body>
</html>
"""

def write(relpath, text):
    full = os.path.join(DIST, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)

# ---------------------------------------------------------------- pages
def build_index_pages():
    pages = [POSTS[i:i + PER_PAGE] for i in range(0, len(POSTS), PER_PAGE)]
    total = len(pages)
    for idx, chunk in enumerate(pages, start=1):
        relpath, px = ("index.html", "") if idx == 1 else (f"page/{idx}/index.html", "../../")
        body_posts = '\n<div class="space big"></div>\n'.join(render_post(p, px) for p in chunk)
        prev_link = next_link = ""
        if idx > 1:
            target = px + ("" if idx - 1 == 1 else f"page/{idx-1}/")
            prev_link = f'<a href="{target}" class="previous">Previous page</a>'
        if idx < total:
            next_link = f'<a href="{px}page/{idx+1}/" class="next">Next page</a>'
        pag = ('<div id="pagination" style="text-transform:lowercase;">'
               f'<span class="count">page {idx} of {total}</span>{prev_link} {next_link}</div>')
        body = body_posts + '\n<div class="space big"></div>\n' + footer(px, pag)
        write(relpath, page_shell(SITE_TITLE, body, px))
    return total

def build_post_pages():
    for i, p in enumerate(POSTS):
        pp = post_path(p)
        depth = pp.strip("/").count("/") + 1
        px = prefix(depth)
        newer = POSTS[i - 1] if i > 0 else None
        older = POSTS[i + 1] if i < len(POSTS) - 1 else None
        nav = ['<a href="%s">&larr; Newer</a>' % (px + post_path(newer)) if newer
               else '<span class="muted">&larr; Newer</span>',
               f'<a href="{px}">Home</a>',
               '<a href="%s">Older &rarr;</a>' % (px + post_path(older)) if older
               else '<span class="muted">Older &rarr;</span>']
        body = (render_post(p, px) + '\n<div class="space big"></div>\n'
                + '<div class="postnav">' + " &middot; ".join(nav) + "</div>")
        title = SITE_TITLE
        if p.get("slug"):
            title = p["slug"].replace("-", " ").title() + " — " + SITE_TITLE
        write(pp + "index.html", page_shell(title, body, px))

def build_archive():
    px = "../"
    rows = []
    for p in POSTS:
        dt = datetime.fromtimestamp(int(p["unix-timestamp"]), tz=timezone.utc)
        label = dt.strftime("%b %-d, %Y")
        slug = (p.get("slug") or p["type"]).replace("-", " ")
        rows.append(f'<a class="arc" href="{px + post_path(p)}">'
                    f'<span class="arc-date">{label}</span>'
                    f'<span class="arc-title">{html.escape(slug)}</span></a>')
    body = ('<div id="post"><div class="right" style="padding-left:0;width:auto;">'
            '<a class="title">Archive</a><div class="space small"></div>'
            '<div class="archive-list">' + "\n".join(rows) + '</div></div></div>')
    write("archive/index.html", page_shell("Archive — " + SITE_TITLE, body, px))

def build_person_pages():
    px = "../"
    for disp, slug in PEOPLE:
        name = PERSON_INTRO[slug]
        tagged = [p for p in POSTS if slug in {tslug(t) for t in (p.get("tags") or [])}]
        if tagged:
            body = '\n<div class="space big"></div>\n'.join(render_post(p, px) for p in tagged)
        else:
            body = ('<div id="post"><div class="right" style="padding-left:0;">'
                    f'<a class="title">{name}</a><div class="space small"></div>'
                    f'<p>Nothing here yet. Add a post tagged <strong>{slug}</strong> in '
                    '<code>posts.toml</code> and it will appear here, in the home feed, and in RSS.</p>'
                    '</div></div>')
        write(f"{slug}/index.html", page_shell(f"{name} — " + SITE_TITLE, body, px))

def build_stub(slug, heading, text):
    px = "../"
    body = ('<div id="post"><div class="right" style="padding-left:0;">'
            f'<a class="title">{heading}</a><div class="space small"></div>{text}</div></div>')
    write(f"{slug}/index.html", page_shell(f"{heading} — " + SITE_TITLE, body, px))

def build_rss():
    items = []
    for p in POSTS[:50]:
        link = f"https://tlhg.org/{post_path(p)}"
        dt = datetime.fromtimestamp(int(p["unix-timestamp"]), tz=timezone.utc)
        pub = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        if p["type"] == "regular":
            title = p.get("regular-title") or "Post"
            desc = p.get("regular-body") or ""
        else:
            title = (p.get("slug") or p["type"]).replace("-", " ").title()
            desc = p.get("photo-caption") or p.get("video-caption") or ""
        items.append(f"<item><title>{html.escape(title)}</title><link>{link}</link>"
                     f"<guid>{link}</guid><pubDate>{pub}</pubDate>"
                     f"<description>{html.escape(desc)}</description></item>")
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n'
           f'<title>{SITE_TITLE}</title>\n<link>https://tlhg.org/</link>\n'
           '<description>Family blog</description>\n' + "\n".join(items) + "\n</channel>\n</rss>\n")
    write("rss.xml", rss)

EXTRA_CSS = """
/* ---- static-mirror additions (header name links + nav, identical look) ---- */
#header h1.title { color:#1D1801; text-align:center; font-size:3.75em; letter-spacing:-1px;
    font-weight:normal; margin:0; line-height:1.05em; font-family:Helvetica,Arial,sans-serif; }
#header h1.title a { color:#1D1801; text-decoration:none; }
#header h1.title a:hover { text-decoration:underline; }
.video-embed { position:relative; }
.video-embed iframe { max-width:100%; }
.postnav { width:488px; font-family:Verdana,Arial,sans-serif; font-size:0.75em; color:#9C9C9C;
    border-top:1px dotted #ccc; margin:0 0 0 300px; padding:8px 6px; }
.postnav a { color:#1D1801; text-decoration:none; }
.postnav a:hover { text-decoration:underline; }
.postnav .muted { color:#ccc; }
#footer .credit { width:488px; margin:8px 0 0 300px; color:#9C9C9C;
    font-family:Verdana,Arial,sans-serif; font-size:0.69em; }
#footer .credit a { color:#9C9C9C; }
.archive-list { line-height:1.9em; }
.archive-list a.arc { display:block; text-decoration:none; color:#1D1801; }
.archive-list a.arc:hover .arc-title { text-decoration:underline; }
.archive-list .arc-date { color:#9C9C9C; font-family:Verdana,Arial,sans-serif;
    font-size:0.8em; display:inline-block; width:130px; }
#content #post .left .tags span.tag { color:#9C9C9C; text-decoration:none; padding:1px 3px;
    margin:0 0 3px 3px; float:right; }
@media (max-width:840px) {
    #header,#content,#content #post,#footer { width:auto; max-width:800px; }
    #content #post .left { width:auto; float:none; text-align:left; }
    #content #post .left a.timestamp { width:auto; display:inline-block; }
    #content #post .right { width:auto; float:none; padding:10px 0 0 0; }
    #footer #pagination,.postnav,#footer .credit { width:auto; margin-left:0; }
}
"""

def build_css():
    css = open(THEME_CSS).read()
    css = re.sub(r"a\.install\s*\{[^}]*\}", "", css)
    write("style.css", css + "\n" + EXTRA_CSS)

# ---------------------------------------------------------------- run
def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)
    # copy archived images
    shutil.copytree(IMG_SRC, os.path.join(DIST, "img"))
    build_post_pages()
    n = build_index_pages()
    build_archive()
    build_person_pages()
    build_stub("about", "About",
               "<p>TREY + LORI + HUCK + GUS &mdash; a family blog.</p>")
    build_stub("subscribe", "Subscribe",
               '<p>Follow along via the <a href="../rss.xml">RSS feed</a>.</p>')
    build_rss()
    build_css()
    # custom-domain + no-jekyll for GitHub Pages
    cname = os.path.join(BASE, "CNAME")
    if os.path.exists(cname):
        shutil.copy(cname, os.path.join(DIST, "CNAME"))
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    print(f"Built {len(POSTS)} posts across {n} pages -> {DIST}")

if __name__ == "__main__":
    main()
