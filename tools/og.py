#!/usr/bin/env python3
"""Share image (og:image, X card): the site's own map, 1200x630 -> src/static/og.png.

    python3 build.py && python3 tools/og.py && python3 build.py

Run it again when a city gets a dot on the map.
"""
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
W, H, BG = 1200, 630, "#07171b"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=2)
    page.goto((ROOT / "dist" / "index.html").as_uri())
    page.wait_for_load_state("networkidle")
    page.add_style_tag(content="*{animation:none!important} .map__legend{display:none!important}")
    shot = page.locator(".map").screenshot()
    browser.close()

m = Image.open(io.BytesIO(shot)).convert("RGB")
m = m.resize((round(m.width * H / m.height), H), Image.LANCZOS)
card = Image.new("RGB", (W, H), BG)
card.paste(m, ((W - m.width) // 2, 0))
out = ROOT / "src" / "static" / "og.png"
card.save(out, optimize=True)
print(out.relative_to(ROOT), card.size, out.stat().st_size // 1024, "KB")
