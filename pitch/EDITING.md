# Editing the pitch deck

How to view, change and share the SoyMate pitch deck. No installs are needed to view it or to change text: a
browser, a text editor and Python 3 are enough.

## Where the deck lives

| What | Where | Who can change it |
|---|---|---|
| **Slides (the source)** | `pitch/slides/`: one HTML file per slide, `deck.json` gives the order | anyone, through git |
| **HTML deck** | `pitch/deck/index.html` + `pitch/deck/assets/` (images, demo video). Built from `pitch/slides/` | rebuilt with `python3 pitch/build_deck.py` |
| **Online deck** | https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2 (same slide files, presenter mode, PDF/PPTX export) | Fede (owner) |

`pitch/slides/` is the copy to edit. The HTML deck is generated from it, and the online deck holds the same
files, so a change made in `pitch/slides/` can be pasted into the online deck and the other way round
(see [Keeping the online deck in sync](#keeping-the-online-deck-in-sync)).

## View it

Open `pitch/deck/index.html` in a browser (double-click it, or `open pitch/deck/index.html` on a Mac).

| Key | Action |
|---|---|
| → ↓ Space Enter, or click the right two thirds | next slide |
| ← ↑ Backspace, or click the left third | previous slide |
| Home / End | first / last slide |
| `N` | show or hide the speaker notes |
| `F` | full screen |
| click the video | pause / play |

`index.html#8` opens slide 8. The demo video starts from the beginning each time its slide is shown.

**PDF for the submission:** in Chrome, Print (Ctrl/Cmd + P), destination "Save as PDF", margins "None",
"Background graphics" ticked. You get one 1920×1080 page per slide; the demo slide shows the video's still frame.

## The edit loop

1. Edit the slide file in `pitch/slides/` (the file name is the slide id; `deck.json` lists them in order).
2. Rebuild: `python3 pitch/build_deck.py` (from the repo root; prints `wrote pitch/deck/index.html (11 slides)`).
3. Reload `pitch/deck/index.html` in the browser and look at the slide.
4. Commit both the slide and `pitch/deck/index.html`, and push.

Quick text fixes can also be made straight in `pitch/deck/index.html` (each slide is a `<section>` with a
`<!-- 8. demo -->` comment above it), but the next rebuild overwrites them: copy the change into
`pitch/slides/` too.

## Slide format

Each file in `pitch/slides/` is exactly one `<section id="<file name>">` on a fixed 1920×1080 canvas. Rules,
so it renders the same here and in the online deck:

- **Every style inline** (`style="..."`): no classes, no `<style>`, no `margin`. Lengths in `px`.
- **Layout with flexbox or grid** on the `<section>` and on `<div>`s. A `<div>` with no `display` stacks its
  children in a column. Margins are the section's `padding:128px` (with a footer line: `128px 128px 160px`).
- **Elements:** `h1` `h2` `h3` `p`, `ul`/`ol` of plain `li`, `b` `i` `u` `a` `span style="color:…"`, `div`,
  `img`, `table`/`tr`/`th`/`td`, `svg`, `x-icon`, `x-shape kind="arrow-right"`. Anything else may be dropped
  by the online deck.
- **Text never under 24px.** Text wraps only at spaces, so leave room (about 0.6 × font size per character).
- **Speaker notes:** plain text in one `<aside>`, the last element of the section, with the timing in brackets,
  e.g. `(~15 s)`.
- **Footer line** (sources): one `<p>` pinned with `position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px`.

### Look

Font: **DM Sans** (Arial fallback). Colours used across the deck:

| Use | Colour |
|---|---|
| Dark slide background, main text on light slides | `#18301F` |
| Card on a dark slide | `#22402B` |
| Light slide background / alternate light background | `#F7F5EE` / `#EEF2EA` |
| Accent (labels, big numbers) on light / on dark | `#2E7D32` / `#9BD3A0` |
| Body text on light: normal / muted (footers) | `#44564A` / `#5E6E63` |
| Text on dark: title / body / muted | `#F2EFE4` / `#D7E4D3` / `#BFD0C3` |
| Card border on light | `#DCE3D8` |

Type scale: eyebrow label 24px bold uppercase (`letter-spacing:2px`), slide title `h2` 64px bold, card titles
`h3` 30-40px bold, body 24-30px, big numbers 64-80px bold, footer 24px.

### A content slide to copy

```html
<section id="newslide" data-transition="fade" style="background:#F7F5EE;color:#18301F;font-family:'DM Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#2E7D32">Section label</p>
<h2 style="font-size:64px;font-weight:700;line-height:1.1;color:#18301F">One idea, said as a sentence</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px">
<div style="display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:1px solid #DCE3D8;border-radius:20px;padding:36px">
<h3 style="font-size:34px;font-weight:700;line-height:1.2;color:#18301F">Card title</h3>
<p style="font-size:26px;line-height:1.4;color:#44564A">Card text.</p>
</div>
<div style="display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:1px solid #DCE3D8;border-radius:20px;padding:36px">
<h3 style="font-size:34px;font-weight:700;line-height:1.2;color:#18301F">Card title</h3>
<p style="font-size:26px;line-height:1.4;color:#44564A">Card text.</p>
</div>
</div>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5E6E63">Source: ...</p>
<aside>What to say on this slide. (~15 s)</aside>
</section>
```

## Common tasks

**Change text:** edit the slide file, rebuild.

**Add a slide:** create `pitch/slides/<id>.html` (id: letters, digits, `-`, `_`) whose `<section id>` is the
same id, add the id to `"order"` in `pitch/slides/deck.json` where it should appear, rebuild.

**Remove a slide:** delete its file and its id from `"order"`. If a `"sections"` entry in `deck.json` starts at it,
point `"start"` at the next slide (or delete that section). Rebuild.

**Reorder:** change `"order"` in `deck.json`, rebuild.

**Add or replace an image:** put the file (png, jpg, webp, gif or svg) in `pitch/deck/assets/` and use
`<img src="assets/<file>" alt="what it shows" style="width:…px;height:…px;object-fit:contain">` (`cover` for
photos). Screenshots look best with `object-fit:contain` on a white or dark box. For the online deck the image
must be uploaded there instead; it then gets a `/_blob/<id>` address. Images already in the online deck use
those addresses in `pitch/slides/`; `ASSETS` at the top of `pitch/build_deck.py` maps each one to its file in
`pitch/deck/assets/`.

**Icons:** `<x-icon name="Search" style="color:#2E7D32;width:56px;height:56px"></x-icon>`. The HTML deck has
`Search`, `Users`, `Lock`, `Verified`, `Globe`, `Chart`, `Lightning` (add others to `ICONS` in
`build_deck.py`; the online deck has about 30, listed in its format guide).

**Change the team line or contact:** cover (`cover.html`) and last slide (`close.html`).

## Re-record the demo video

The video on the demo slide is a screen recording of the live app (http://18.206.176.19): the Ghana
farmer-saved example (164 seeds), then the single seed labelled insect hole. To record it again, for example
after the app changes:

```bash
npm install playwright && npx playwright install chromium     # once
node pitch/record_demo.js                                      # or: node pitch/record_demo.js http://<other-host>
cd pitch/deck/assets
ffmpeg -y -i demo_raw.webm -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -movflags +faststart -an demo.mp4
ffmpeg -y -i demo.mp4 -c:v libvpx-vp9 -b:v 0 -crf 38 -row-mt 1 -an demo.webm
ffmpeg -y -ss 16 -i demo.mp4 -frames:v 1 -q:v 2 demo_poster.jpg   # still frame: pick a second where a result shows
rm demo_raw.webm
cd ../../.. && python3 pitch/build_deck.py
```

`demo.mp4` (H.264) plays in Chrome, Safari and Edge; `demo.webm` is the same clip for browsers without
H.264. The still frame is what thumbnails and the PDF show. To show other examples, change the two `click`
lines in `record_demo.js`; then update the two steps and the speaker notes in `pitch/slides/demo.html`.
Keep the clip under 20 MB (the online deck's limit).

## Keeping the online deck in sync

The online deck (https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2) is owned by Fede and can only be changed
from his account: in its editor, or by asking Claude in his session to publish the changed files from
`pitch/slides/` (and to upload any new image or video). Its slide files are the same as `pitch/slides/`, with
images as `/_blob/<id>` addresses.

- **Changed something in the repo?** Tell Fede which slides, so he publishes them online.
- **Changed something online?** Copy the slide's HTML back into `pitch/slides/` (Claude can read it from the
  artifact), rebuild and commit, so the repo stays the full copy.

## If something goes wrong

| Problem | Fix |
|---|---|
| `build_deck.py` says `unknown asset /_blob/…` | the slide uses an online image that is not in `pitch/deck/assets/`: download it, save it there, add it to `ASSETS` |
| `no icon for <x-icon name=…>` | add the icon's SVG paths to `ICONS` in `build_deck.py`, or pick one that exists |
| `the <section> id must be …` | the file name and the `<section id>` differ; make them the same |
| Video doesn't play | check `demo.mp4` and `demo.webm` are in `pitch/deck/assets/`; some browsers block autoplay on `file://`: click the video, or serve the folder with `python3 -m http.server -d pitch/deck` and open http://localhost:8000 |
| Text looks different from the online deck | DM Sans loads from Google Fonts: without internet the deck falls back to Arial |
| Text overflows its box | shorten it or split the slide; don't go under 24px |
