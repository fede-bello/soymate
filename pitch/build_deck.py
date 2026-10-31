"""Build pitch/deck/index.html, a self-contained HTML version of the pitch deck.

Source of truth: pitch/slides/ (one <section> per slide, deck.json gives the order), the same files as the
online deck at https://claude.ai/artifact/AiZ254A4Y2tTDnwKEr5GH2. Images and the demo video live in
pitch/deck/assets/. Run from the repo root after editing a slide:

    python3 pitch/build_deck.py

Only the standard library is used.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLIDES = HERE / "slides"
OUT = HERE / "deck" / "index.html"

# Online deck asset id -> file in pitch/deck/assets/ (same bytes, checked by sha256).
ASSETS = {
    "3d190495cb9280f55d9c7e6ae65ecb76": "assets/logo.png",
    "04204e5c3849beba5f242437c22399a5": "assets/lentil_bruchid.png",
    "7f85915837432e1f5fb60d5c0e42a2eb": "assets/app_bulk_harvest.jpg",
    "9f9b0631e104e4d065690d0c7c07de0a": "assets/demo_poster.jpg",
    "83ffb969a3037e789da101aaabba235f": "assets/demo.mp4",
}

# Line icons for <x-icon name="...">, 24x24 stroke paths.
ICONS = {
    "Search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "Users": '<circle cx="9" cy="8" r="4"/><path d="M2 21v-1a6 6 0 0 1 6-6h2a6 6 0 0 1 6 6v1"/>'
    '<path d="M16 3.5a4 4 0 0 1 0 9"/><path d="M22 21v-1a6 6 0 0 0-4-5.6"/>',
    "Lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "Verified": '<path d="M12 2l2.4 1.8 3-.2.9 2.9 2.5 1.7-1 2.8 1 2.8-2.5 1.7-.9 2.9-3-.2L12 22l-2.4-1.8-3 .2'
    '-.9-2.9L3.2 15.8l1-2.8-1-2.8 2.5-1.7.9-2.9 3 .2z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "Globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18"/>',
    "Chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-6"/>',
    "Lightning": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
}


def asset(m: re.Match) -> str:
    key = m.group(1)
    if key not in ASSETS:
        raise SystemExit(f"unknown asset /_blob/{key}: add it to ASSETS and pitch/deck/assets/")
    return ASSETS[key]


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def x_icon(m: re.Match) -> str:
    tag = m.group(0)
    name = attr(tag, "name")
    if name not in ICONS:
        raise SystemExit(f"no icon for <x-icon name={name!r}>: add it to ICONS")
    style = attr(tag, "style") or ""
    color = re.search(r"color:\s*([^;]+)", style)
    return (
        f'<svg viewBox="0 0 24 24" fill="none" stroke="{color.group(1).strip() if color else "currentColor"}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="{style};flex:none" '
        f'aria-hidden="true">{ICONS[name]}</svg>'
    )


def x_shape(m: re.Match) -> str:
    tag = m.group(0)
    kind = attr(tag, "kind")
    if kind != "arrow-right":
        raise SystemExit(f"<x-shape kind={kind!r}> is not handled: add it to build_deck.py")
    style = attr(tag, "style") or ""
    fill = re.search(r"background:\s*([^;]+)", style)
    return (
        f'<svg viewBox="0 0 100 50" preserveAspectRatio="none" style="{style};background:none;flex:none" '
        f'aria-hidden="true"><path d="M0 15H60V0L100 25L60 50V35H0z" fill="{fill.group(1).strip()}"/></svg>'
    )


def video(m: re.Match) -> str:
    tag = m.group(0)
    mp4 = attr(tag, "data-video")
    webm = mp4.rsplit(".", 1)[0] + ".webm"  # same clip in VP9, for browsers without H.264
    if not (OUT.parent / webm).exists():
        raise SystemExit(f"missing {webm}: ffmpeg -i {mp4} -c:v libvpx-vp9 -b:v 0 -crf 38 -an {webm}")
    return (
        f'<video poster="{attr(tag, "src")}" muted loop playsinline preload="metadata" '
        f'aria-label="{attr(tag, "alt")}" style="{attr(tag, "style")}">'
        f'<source src="{mp4}" type="video/mp4"><source src="{webm}" type="video/webm"></video>'
    )


def convert(section: str) -> str:
    s = re.sub(r"/?_blob/([0-9a-f]+)", asset, section)
    s = re.sub(r"<x-icon\b[^>]*>\s*</x-icon>", x_icon, s)
    s = re.sub(r"<x-shape\b[^>]*>\s*</x-shape>", x_shape, s)
    s = re.sub(r"<img\b[^>]*\bdata-video=\"[^\"]*\"[^>]*>", video, s)
    return s


def main() -> None:
    deck = json.loads((SLIDES / "deck.json").read_text())
    fonts = "\n".join(
        f'<link rel="stylesheet" href="{html.escape(f["href"])}">' for f in deck["faces"].values() if "href" in f
    )
    sections = []
    for i, sid in enumerate(deck["order"], 1):
        text = (SLIDES / f"{sid}.html").read_text().strip()
        if f'id="{sid}"' not in text.split(">", 1)[0]:
            raise SystemExit(f"{sid}.html: the <section> id must be {sid!r}")
        sections.append(f"<!-- {i}. {sid} -->\n{convert(text)}")
    OUT.write_text(
        TEMPLATE.replace("{{title}}", html.escape(deck["title"]))
        .replace("{{fonts}}", fonts)
        .replace("{{slides}}", "\n\n".join(sections))
    )
    print(f"wrote {OUT.relative_to(HERE.parent)} ({len(sections)} slides)")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<!-- Generated by pitch/build_deck.py from pitch/slides/. Edit the slides there and rebuild,
     or edit this file directly (each slide is one <section>, all styles inline). -->
<link rel="preconnect" href="https://fonts.googleapis.com">
{{fonts}}
<style>
  html, body { margin: 0; height: 100%; background: #0E1A12; overflow: hidden; }
  #stage { position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px; transform-origin: 0 0; }
  #stage > section { position: absolute; inset: 0; box-sizing: border-box; width: 1920px; height: 1080px;
    overflow: hidden; visibility: hidden; opacity: 0; transition: opacity .35s ease; }
  #stage > section.active { visibility: visible; opacity: 1; }
  section * { box-sizing: border-box; margin: 0; }
  section h1, section h2, section h3, section p { font-weight: inherit; }
  section h1 { font-size: 96px; font-weight: 600; line-height: 1.1; }
  section h2 { font-size: 64px; font-weight: 600; line-height: 1.15; }
  section h3 { font-size: 44px; font-weight: 600; line-height: 1.2; }
  section p { font-size: 32px; line-height: 1.4; }
  section div { display: flex; flex-direction: column; }
  section div[style*="display:grid"] { display: grid; }
  section div[style*="flex-direction:row"] { flex-direction: row; }
  section table { border-collapse: collapse; width: 100%; overflow: hidden; }
  section th, section td { padding: .35em .6em; text-align: left; border-bottom: 1px solid rgba(0,0,0,.08); }
  section th { font-weight: 700; }
  section aside { display: none; }
  #notes { position: fixed; left: 0; right: 0; bottom: 0; max-height: 35%; overflow: auto; padding: 16px 24px;
    background: rgba(14,26,18,.95); color: #F2EFE4; font: 18px/1.5 'DM Sans', Arial, sans-serif; display: none; }
  body.show-notes #notes { display: block; }
  #bar { position: fixed; right: 16px; bottom: 12px; color: rgba(242,239,228,.55); font: 14px 'DM Sans', Arial, sans-serif;
    user-select: none; }
  body.show-notes #bar { display: none; }
  @media print {
    @page { size: 1920px 1080px; margin: 0; }
    html, body { height: auto; overflow: visible; background: none; }
    #stage { position: static; transform: none !important; width: 1920px; height: auto; }
    #stage > section { position: relative; visibility: visible; opacity: 1; break-after: page; }
    #notes, #bar { display: none !important; }
  }
</style>
</head>
<body>
<div id="stage">

{{slides}}

</div>
<div id="notes"></div>
<div id="bar"></div>
<script>
(() => {
  const stage = document.getElementById('stage');
  const slides = [...stage.querySelectorAll(':scope > section')];
  const notes = document.getElementById('notes');
  const bar = document.getElementById('bar');
  let cur = 0;

  function fit() {
    const k = Math.min(innerWidth / 1920, innerHeight / 1080);
    stage.style.transform = `scale(${k}) translate(-50%, -50%)`;
  }
  function show(i) {
    cur = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((s, j) => {
      s.classList.toggle('active', j === cur);
      s.querySelectorAll('video').forEach(v => { if (j === cur) { v.currentTime = 0; v.play().catch(() => {}); } else v.pause(); });
    });
    const aside = slides[cur].querySelector('aside');
    notes.textContent = aside ? aside.textContent : '(no notes)';
    bar.textContent = `${cur + 1} / ${slides.length}  ·  ← → to move, N notes, F full screen`;
    history.replaceState(null, '', '#' + (cur + 1));
  }
  addEventListener('resize', fit);
  addEventListener('keydown', e => {
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(e.key)) show(cur + 1);
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) show(cur - 1);
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
    else if (e.key === 'n' || e.key === 'N') document.body.classList.toggle('show-notes');
    else if (e.key === 'f' || e.key === 'F') document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    else return;
    e.preventDefault();
  });
  addEventListener('click', e => {
    if (e.target.closest('video, a, #notes')) {
      const v = e.target.closest('video');
      if (v) v.paused ? v.play() : v.pause();
      return;
    }
    show(e.clientX > innerWidth / 3 ? cur + 1 : cur - 1);
  });
  fit();
  show((parseInt(location.hash.slice(1), 10) || 1) - 1);
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
