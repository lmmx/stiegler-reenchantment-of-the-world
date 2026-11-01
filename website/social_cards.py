#!/usr/bin/env python3
"""The site's social cards: the 1200 × 630 images that link previews show (Open Graph, Twitter).

One card per page of the nav, written into the built site at
site/assets/social/<page URL>card.jpg (the home page's at site/assets/social/card.jpg), which
website/overrides/main.html names in each page's <head>. Each card sets the page's title, its
front-matter description (the home page's: site_description) and its section of the nav beside
the home page's painting (website/overrides/partials/rew-hero-art.html), rendered to JPEG by
headless Chromium (the painting's grain makes PNGs ten times larger) through Playwright.

Run from the repository root after `zensical build`:

    uv run --no-project -p 3.13 --with playwright==1.48.0 --with pyyaml python website/social_cards.py

Chromium comes from `playwright install chromium`, or from the binary that --chrome or the
CHROME environment variable names.

Adapted from lmmx/mibz2's docs/scripts/social_cards.py, which commits its cards; these are made
at build time instead, so no images live in the repository.
"""

import argparse
import html
import os
import re
import sys
import tomllib
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "website/overrides/partials/rew-hero-art.html"
W, H = 1200, 630

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500&family=Barlow+Condensed:wght@600;700&display=block">
<style>
  html, body {{ margin: 0; width: {w}px; height: {h}px; overflow: hidden; }}
  body {{
    position: relative; color: #ffffff; font-family: "Barlow", sans-serif;
    background:
      radial-gradient(60% 90% at 82% 40%, rgba(168, 216, 15, 0.22), transparent 70%),
      radial-gradient(40% 60% at 6% 100%, rgba(35, 194, 107, 0.16), transparent 70%),
      #131512;
  }}
  .art {{ position: absolute; top: 0; right: 0; width: 640px; height: 630px;
    -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 26%); }}
  .art svg {{ width: 100%; height: 100%; }}
  .text {{ position: absolute; left: 72px; top: 64px; bottom: 76px; width: {text_w}px;
    display: flex; flex-direction: column; }}
  .kicker {{ align-self: flex-start; padding: 5px 12px; font-family: "Barlow Condensed";
    font-weight: 700; font-size: 25px; letter-spacing: 0.12em; text-transform: uppercase;
    color: #131512; background: #a8d80f; }}
  h1 span {{ white-space: nowrap; }}
  h1 {{ margin: 30px 0 0; font-family: "Barlow Condensed"; font-weight: 600;
    font-size: {title_px}px; line-height: 0.98; letter-spacing: 0.005em; text-transform: uppercase;
    display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }}
  p {{ margin: 24px 0 0; font-size: 28px; line-height: 1.35; color: {desc_color};
    font-weight: {desc_weight};
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
  .foot {{ margin-top: auto; font-size: 22px; color: rgba(255, 255, 255, 0.62); }}
  .foot b {{ font-weight: 500; color: #bdf02a; }}
  .bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 12px; background: #a8d80f; }}
</style></head>
<body>
  <div class="art">{art}</div>
  <div class="text">
    <div class="kicker">{kicker}</div>
    <h1>{title}</h1>
    <p>{description}</p>
    <div class="foot">{foot}</div>
  </div>
  <div class="bar"></div>
</body></html>
"""


def nav_entries(nav, section=None):
    """Yield (page, nav title or None, top-level section or None) for every page in the nav."""
    for entry in nav:
        if isinstance(entry, str):
            yield entry, None, section
        else:
            for title, value in entry.items():
                if isinstance(value, str):
                    yield value, title, section
                else:
                    yield from nav_entries(value, section or title)


def page_url(page):
    """The page's URL under the site root, as Zensical serves it ("" for the home page)."""
    stem = page.removesuffix(".md")
    if stem == "README" or stem == "index":
        return ""
    if stem.endswith("/README") or stem.endswith("/index"):
        return stem.rsplit("/", 1)[0] + "/"
    return stem + "/"


def read_page(path):
    """A page's front matter and its first H1, as plain text."""
    text = path.read_text()
    meta = {}
    if text.startswith("---\n"):
        meta = yaml.safe_load(text[4 : text.index("\n---\n", 4)]) or {}
    m = re.search(r"^# (.+)$", text, re.M)
    h1 = re.sub(r"[*_`]", "", m.group(1)).strip() if m else ""
    return meta, h1


def art_svg():
    """The home page's painting, without its template comment."""
    return re.sub(r"\{#.*?#\}", "", ART.read_text(), flags=re.S).strip()


def cards(config):
    """Yield (output path relative to the site, HTML) for every card."""
    project = config["project"]
    art = art_svg()
    for page, nav_title, section in nav_entries(project["nav"]):
        meta, h1 = read_page(ROOT / project["docs_dir"] / page)
        url = page_url(page)
        home = url == ""
        if home:
            title, kicker = "The Re-Enchantment of the World", "A study companion"
            description = "The Value of Spirit against Industrial Populism"
        else:
            title = h1 or nav_title or page
            kicker = section or nav_title or "Overview"
            description = meta.get("description", project["site_description"])
        size = 88 if home else (74 if len(title) < 34 else 58 if len(title) < 64 else 48)
        heading = (
            "The <span>Re-Enchantment</span><br>of the World" if home else html.escape(title)
        )
        foot = (
            "<b>" + html.escape(project["site_url"].split("://", 1)[1].rstrip("/")) + "</b>"
            if home
            else "<b>The Re-Enchantment of the World</b> · a study companion"
        )
        doc = PAGE.format(
            w=W,
            h=H,
            text_w=660 if home else 640,
            title_px=size,
            desc_color="#bdf02a" if home else "rgba(255, 255, 255, 0.82)",
            desc_weight=500 if home else 400,
            art=art,
            kicker=html.escape(kicker),
            title=heading,
            foot=foot,
            description=html.escape(description),
        )
        yield f"assets/social/{url}card.jpg", doc


def main():
    """Render every card into the built site."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=str(ROOT / "site"))
    parser.add_argument("--chrome", default=os.environ.get("CHROME"))
    args = parser.parse_args()
    site = Path(args.site)
    if not (site / "index.html").exists():
        sys.exit(f"no built site at {site} (zensical build first)")
    config = tomllib.loads((ROOT / "zensical.toml").read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chrome) if args.chrome else p.chromium.launch()
        tab = browser.new_page(viewport={"width": W, "height": H})
        count = 0
        for rel, doc in cards(config):
            out = site / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            tab.set_content(doc, wait_until="networkidle")
            tab.evaluate("document.fonts.ready")
            tab.screenshot(path=str(out), type="jpeg", quality=84)
            count += 1
        browser.close()
    print(f"{count} social cards written to {site / 'assets/social'}", file=sys.stderr)


if __name__ == "__main__":
    main()
