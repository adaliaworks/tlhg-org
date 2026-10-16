#!/usr/bin/env python3
"""Build podcast feed.xml + landing index.html for /nws. Standard library only.

Needs Python 3.11+ (for tomllib). On 3.10 or earlier: pip install tomli.
Run from inside the nws/ folder:   python3 build_feed.py
"""
import os, html
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # pip install tomli
from email.utils import format_datetime
from datetime import datetime, date as _date, time as _time, timezone
from xml.dom import minidom

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "podcast.toml")
AUDIO = os.path.join(HERE, "audio")
MIME = {".mp3": "audio/mpeg", ".m4a": "audio/x-m4a", ".mp4": "audio/mp4",
        ".aac": "audio/aac", ".ogg": "audio/ogg", ".wav": "audio/wav", ".flac": "audio/flac"}

def rfc822(d):
    if isinstance(d, datetime):
        dt = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    elif isinstance(d, _date):
        dt = datetime.combine(d, _time(12, 0), tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(str(d)).replace(tzinfo=timezone.utc)
    return format_datetime(dt)

def esc(s):
    return html.escape(str(s or ""), quote=True)

def hms(secs):
    try:
        s = int(round(float(secs)))
    except (TypeError, ValueError):
        return str(secs or "")
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def main():
    cfg = tomllib.load(open(CFG, "rb"))
    ch = cfg["channel"]
    base = ch["base_url"].rstrip("/")
    path = "/" + ch.get("path", "nws").strip("/")
    feed_url, page_url = f"{base}{path}/feed.xml", f"{base}{path}/"
    show_type = ch.get("type", "episodic")  # "serial" plays oldest/ep1 first

    eps = cfg.get("episode", [])
    if show_type == "serial":
        eps = sorted(eps, key=lambda e: e.get("number", 0))
    else:
        eps = sorted(eps, key=lambda e: str(e["date"]), reverse=True)

    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" '
         'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
         'xmlns:atom="http://www.w3.org/2005/Atom">', "<channel>",
         f"<title>{esc(ch['title'])}</title>",
         f"<link>{esc(page_url)}</link>",
         f'<atom:link href="{esc(feed_url)}" rel="self" type="application/rss+xml"/>',
         f"<language>{esc(ch.get('language','en-us'))}</language>",
         f"<description>{esc(ch.get('description',''))}</description>",
         f"<itunes:author>{esc(ch.get('author',''))}</itunes:author>",
         f"<itunes:summary>{esc(ch.get('description',''))}</itunes:summary>",
         f"<itunes:explicit>{'true' if ch.get('explicit') else 'false'}</itunes:explicit>",
         f"<itunes:type>{esc(show_type)}</itunes:type>"]
    if ch.get("category"):
        x.append(f'<itunes:category text="{esc(ch["category"])}"/>')
    if ch.get("owner_name") or ch.get("owner_email"):
        x.append("<itunes:owner>")
        if ch.get("owner_name"):
            x.append(f"<itunes:name>{esc(ch['owner_name'])}</itunes:name>")
        if ch.get("owner_email"):
            x.append(f"<itunes:email>{esc(ch['owner_email'])}</itunes:email>")
        x.append("</itunes:owner>")
    if ch.get("image"):
        x.append(f'<itunes:image href="{esc(base + path + "/" + ch["image"].lstrip("/"))}"/>')

    for e in eps:
        fn = e["file"]
        ext = os.path.splitext(fn)[1].lower()
        url = f"{base}{path}/audio/{fn}"
        fp = os.path.join(AUDIO, fn)
        size = os.path.getsize(fp) if os.path.exists(fp) else int(e.get("bytes", 0))
        x.append("<item>")
        x.append(f"<title>{esc(e['title'])}</title>")
        if e.get("number"):
            x.append(f"<itunes:episode>{int(e['number'])}</itunes:episode>")
        x.append(f"<pubDate>{rfc822(e['date'])}</pubDate>")
        x.append(f'<guid isPermaLink="false">{esc(url)}</guid>')
        if e.get("description"):
            x.append(f"<description><![CDATA[{e['description']}]]></description>")
        x.append(f'<enclosure url="{esc(url)}" length="{size}" type="{MIME.get(ext,"audio/mpeg")}"/>')
        if e.get("duration"):
            x.append(f"<itunes:duration>{esc(hms(e['duration']))}</itunes:duration>")
        x.append(f"<itunes:author>{esc(ch.get('author',''))}</itunes:author>")
        x.append(f"<itunes:explicit>{'true' if e.get('explicit', ch.get('explicit')) else 'false'}</itunes:explicit>")
        x.append("</item>")
    x += ["</channel>", "</rss>"]
    xml = "\n".join(x)
    minidom.parseString(xml)  # fail loudly if malformed
    open(os.path.join(HERE, "feed.xml"), "w", encoding="utf-8").write(xml + "\n")

    cover = f'<img class="cover" src="{esc(ch["image"])}" alt="">' if ch.get("image") else ""
    rows = []
    for e in eps:
        num = f'{int(e["number"])}. ' if e.get("number") else ""
        dur = f' &middot; {esc(hms(e["duration"]))}' if e.get("duration") else ""
        desc = f'<p class="d">{e["description"]}</p>' if e.get("description") else ""
        rows.append(f'<li><h2>{num}{esc(e["title"])}</h2>'
                    f'<p class="meta">{esc(rfc822(e["date"]).rsplit(" ",2)[0])}{dur}</p>{desc}'
                    f'<audio controls preload="none" src="audio/{esc(e["file"])}"></audio></li>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="googlebot" content="noindex, nofollow">
<title>{esc(ch['title'])}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ max-width: 640px; margin: 40px auto; padding: 0 20px;
         font: 17px/1.55 -apple-system, Helvetica, Arial, sans-serif; }}
  h1 {{ font-size: 1.9em; margin: 0 0 .2em; }}
  .cover {{ width: 200px; height: 200px; object-fit: cover; border-radius: 10px; }}
  .sub {{ background: rgba(127,127,127,.12); padding: 14px 16px; border-radius: 10px; margin: 24px 0; }}
  .sub code {{ user-select: all; word-break: break-all; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ padding: 18px 0; border-top: 1px solid rgba(127,127,127,.25); }}
  li h2 {{ font-size: 1.1em; margin: 0 0 .15em; }}
  .meta {{ color: #888; font-size: .85em; margin: 0 0 .4em; }}
  .d {{ margin: .2em 0 .5em; }}
  audio {{ width: 100%; margin-top: 8px; }}
</style>
</head>
<body>
{cover}
<h1>{esc(ch['title'])}</h1>
<p>{esc(ch.get('description',''))}</p>
<div class="sub"><strong>Listen in a podcast app:</strong> add a show by URL and paste<br>
<code>{esc(feed_url)}</code></div>
<ul>
{chr(10).join(rows)}
</ul>
</body>
</html>
"""
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
    print(f"Built feed.xml + index.html with {len(eps)} episode(s), type={show_type}.")

if __name__ == "__main__":
    main()
