# Naked Without Shame — publishing to tlhg.org/nws

Everything is built and sitting on your Mac in this folder:
`Dropbox/Public/NakedWithoutShame/NWS-site-build/`

NOTE: 10/21/26: Trey renamed feed.xml > feed-OFF and index.html > index-OFF to prevent these two pages from loading/serving content, per a polite takedown request from TOBI in response to my request to host the podcast. Dropping -OFF from each filename and pushing to GH will restore access.

```
NWS-site-build/
  robots.txt            -> goes in your site repo ROOT (next to the site's index.html)
  README-nws.md         this file
  nws/                  -> move this whole folder into your repo root, so it serves at /nws
    audio/              the 9 re-encoded talks (64 kbps mono, 382 MB total)
    feed.xml            what podcast apps subscribe to
    index.html          the page friends open in a browser
    podcast.toml        the source you edit to change titles, order, or add talks
    build_feed.py       regenerates feed.xml + index.html from podcast.toml
```

## Put it in place

1. Move the `nws/` folder into the root of your site repo.
2. Move `robots.txt` to the repo root. If you already have one there, merge in the
   `Disallow: /nws/` lines instead of overwriting.
3. Commit and push:
   ```bash
   git add nws robots.txt
   git commit -m "Add Naked Without Shame audio feed at /nws"
   git push
   ```
4. Clean up: delete `NWS-site-build/` from Dropbox once it is in your repo, since the
   re-encoded copies synced there on the way through.

## Share it

- **Page for friends:** `https://tlhg.org/nws/`
- **Feed for podcast apps:** `https://tlhg.org/nws/feed.xml` — in Apple Podcasts,
  Overcast, Pocket Casts, and most others, it is "add a show by URL." It is set up as a
  series, so apps play it in order, 1 through 9.

## Changing it later

Edit `podcast.toml` (titles, the author name, dates, order), then from inside `nws/`:

```bash
python3 build_feed.py
```

That rewrites `feed.xml` and `index.html`. It needs Python 3.11 or newer; on an older
Python, run `pip install tomli` first. Adding a talk means dropping the file in
`nws/audio/` and adding one `[[episode]]` block.

## On keeping it off search and AI

The `robots.txt` tells search engines and the major AI crawlers to stay out of `/nws/`,
and the page carries a `noindex` tag as a second layer. That keeps it out of Google,
Bing, and the AI crawlers that honor the convention. Two honest limits hold: a few
crawlers obey inconsistently, and GitHub Pages has no password option, so anyone you
hand the link to can open it. This is an unlisted feed, not a locked one. Listing
`/nws/` in `robots.txt` also tells anyone who reads that file that the path exists; if
hiding it well ever matters more than the clean URL, an unguessable folder name with no
robots entry conceals it better.

## What I changed from the originals

The source files were 128 kbps stereo and totaled about 800 MB, with three over
GitHub's 100 MB per-file limit. I re-encoded all nine to 64 kbps mono, which for
spoken-word talks sounds essentially the same and brings the set to 382 MB, every file
well under the limit. Your originals in `NakedWithoutShame/` are untouched.
