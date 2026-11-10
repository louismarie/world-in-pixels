#!/usr/bin/env python3
"""Screenshots and checks of dist/index.html (or a URL): desktop, phone 390 px, JavaScript off.

    python3 tools/shot.py [url] [--out shots]
Checks: no horizontal overflow, every pin inside the map, every city link opens in a new tab,
pins not overlapping each other.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
VIEWS = {"desktop": (1440, 900, True), "phone": (390, 844, True), "desktop-nojs": (1440, 900, False), "phone-nojs": (390, 844, False)}
JS = """() => {
  const map = document.querySelector('.map').getBoundingClientRect();
  const pins = [...document.querySelectorAll('.pins a.pin')].map(a => {
    const d = a.querySelector('.pin__dot').getBoundingClientRect(), l = a.querySelector('.pin__label').getBoundingClientRect();
    return {id: a.dataset.city, href: a.href, target: a.target, rel: a.rel,
            dot: [d.left, d.top, d.right, d.bottom], label: [l.left, l.top, l.right, l.bottom], labelVisible: l.width > 0};
  });
  const cards = [...document.querySelectorAll('.city__name a, .other__name a')].map(a => ({href: a.href, target: a.target, rel: a.rel}));
  return {overflow: document.documentElement.scrollWidth - window.innerWidth, map: [map.left, map.top, map.right, map.bottom], pins, cards};
}"""


def hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default=(ROOT / "dist" / "index.html").as_uri())
    ap.add_argument("--out", default=str(ROOT / "shots"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(exist_ok=True)
    ok = True
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, (w, h, js) in VIEWS.items():
            ctx = b.new_context(viewport={"width": w, "height": h}, java_script_enabled=js, device_scale_factor=2 if w < 500 else 1)
            pg = ctx.new_page()
            pg.goto(a.url)
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(out / f"{name}.png"))
            pg.screenshot(path=str(out / f"{name}-full.png"), full_page=True)
            if js:
                r = pg.evaluate(JS)
                problems = []
                if r["overflow"] > 0:
                    problems.append(f"horizontal overflow {r['overflow']} px")
                m = r["map"]
                for pin in r["pins"]:
                    for box, what in ((pin["dot"], "dot"), (pin["label"], "label")):
                        if what == "label" and not pin["labelVisible"]:
                            continue
                        if box[0] < m[0] - 1 or box[2] > m[2] + 1 or box[1] < m[1] - 1 or box[3] > m[3] + 1:
                            problems.append(f"{pin['id']} {what} outside the map")
                    if pin["target"] != "_blank" or "noopener" not in pin["rel"]:
                        problems.append(f"{pin['id']} does not open in a new tab")
                boxes = [(p_["id"], k, p_[k]) for p_ in r["pins"] for k in ("dot", "label") if k == "dot" or p_["labelVisible"]]
                for i, (ia, ka, ba) in enumerate(boxes):
                    for ib, kb, bb in boxes[i + 1:]:
                        if ia != ib and hit(ba, bb):
                            problems.append(f"overlap {ia} {ka} / {ib} {kb}")
                bad = [c["href"] for c in r["cards"] if c["target"] != "_blank" or "noopener" not in c["rel"]]
                if bad:
                    problems.append(f"card links without new tab: {bad}")
                print(name, f"{len(r['pins'])} pins, {len(r['cards'])} headings", "OK" if not problems else json.dumps(problems, ensure_ascii=False))
                ok = ok and not problems
            else:
                n = pg.locator(".pins a.pin").count()
                print(name, f"{n} pins without JS", "OK" if n else "AUCUN PIN")
                ok = ok and n > 0
            ctx.close()
        b.close()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
