#!/usr/bin/env python3
"""Pixel world map centred on the directory's centre city (Paris).

Projection: azimuthal equidistant centred on the centre city, then a radial
"lens" (r -> r**LENS) so that nearby cities do not overlap. Land comes from
Natural Earth (public domain). Output: data/map.json with, per layout, the land
and coast cells as SVG path data and each city's position in percent.

    python3 tools/make_map.py            # downloads Natural Earth once into .cache/
"""
import json
import math
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_{}.geojson"
EARTH_KM = 6371.0
LENS = 0.5          # 1 = true distances, lower = more room around the centre
SS = 4              # supersampling when rasterising
MARGIN = (6.0, 8.0)  # percent kept free on the sides / top and bottom when fitting the cities
LAYOUTS = {         # size in cells; the scale is fitted so that every city is inside the frame
    "wide": {"w": 192, "h": 120},
    "tall": {"w": 96, "h": 120},
}


def fit_reach(centre, cities, w, h):
    """Smallest reach (km mapped to half the width) that keeps every city inside the margins."""
    reach = 4000.0
    while reach < 40000:
        proj = Projection(centre["lat"], centre["lon"], reach)
        pts = [proj(c["lon"], c["lat"]) for c in cities]
        if all(abs(x) * 50 <= 50 - MARGIN[0] and abs(y) * 50 * w / h <= 50 - MARGIN[1] for x, y in pts):
            return reach
        reach += 250
    return reach


def natural_earth(name):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"ne_50m_{name}.geojson"
    if not f.exists():
        req = urllib.request.Request(NE_URL.format(name), headers={"User-Agent": "villes-en-pixels"})
        f.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return json.loads(f.read_text())


def rings(geojson):
    for feat in geojson["features"]:
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            yield poly[0], poly[1:]


class Projection:
    def __init__(self, lat0, lon0, reach):
        self.p0, self.l0, self.reach = math.radians(lat0), math.radians(lon0), reach

    def __call__(self, lon, lat):
        """-> (x, y) in units where 1.0 = `reach` km east; y grows southwards."""
        p, dl = math.radians(lat), math.radians(lon) - self.l0
        cosc = math.sin(self.p0) * math.sin(p) + math.cos(self.p0) * math.cos(p) * math.cos(dl)
        c = math.acos(max(-1.0, min(1.0, cosc)))
        if c < 1e-9:
            return 0.0, 0.0
        k = c / math.sin(c) if math.sin(c) > 1e-9 else 0.0
        x = k * math.cos(p) * math.sin(dl)
        y = k * (math.cos(self.p0) * math.sin(p) - math.sin(self.p0) * math.cos(p) * math.cos(dl))
        r = math.hypot(x, y)
        if r == 0:
            return 0.0, 0.0
        r2 = (c * EARTH_KM / self.reach) ** LENS
        return x / r * r2, -y / r * r2


def densify(ring, step=1.0):
    out = []
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        n = max(1, int(max(abs(x2 - x1), abs(y2 - y1)) / step))
        out.extend((x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n) for i in range(n))
    out.append(tuple(ring[-1][:2]))
    return out


def rasterise(proj, w, h, land, lakes):
    W, H = w * SS, h * SS
    img = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(img)
    scale = W / 2  # x = 1.0 -> right edge

    def to_px(ring):
        pts = []
        for lon, lat in densify([c[:2] for c in ring]):
            x, y = proj(lon, lat)
            pts.append((W / 2 + x * scale, H / 2 + y * scale))
        return pts

    far = (1.9 * EARTH_KM * math.pi / 2 / proj.reach) ** LENS  # skip rings wrapping the antipode
    for layer, value in ((land, 255), (lakes, 0)):
        for outer, holes in rings(layer):
            pts = to_px(outer)
            if max(math.hypot(px - W / 2, py - H / 2) for px, py in pts) / scale > far:
                continue
            if len(pts) >= 3:
                draw.polygon(pts, fill=value)
            for hole in holes:
                hp = to_px(hole)
                if len(hp) >= 3:
                    draw.polygon(hp, fill=255 - value)
    small = img.resize((w, h), Image.BOX)
    return [[small.getpixel((x, y)) >= 128 for x in range(w)] for y in range(h)]


def runs_to_path(grid, keep):
    d = []
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            if keep(x, y):
                x0 = x
                while x < len(row) and keep(x, y):
                    x += 1
                d.append(f"M{x0} {y}h{x - x0}v1h{x0 - x}z")
            else:
                x += 1
    return "".join(d)


def main():
    data = json.loads((ROOT / "data" / "cities.json").read_text())
    everyone = data["cities"] + data["others"]
    centre = next(c for c in data["cities"] if c["id"] == data["center"])
    land, lakes = natural_earth("land"), natural_earth("lakes")
    out = {"center": centre["id"], "lens": LENS, "layouts": {}}
    for name, cfg in LAYOUTS.items():
        w, h = cfg["w"], cfg["h"]
        cfg["reach"] = fit_reach(centre, data["cities"], w, h)
        proj = Projection(centre["lat"], centre["lon"], cfg["reach"])
        grid = rasterise(proj, w, h, land, lakes)

        def is_land(x, y):
            return 0 <= x < w and 0 <= y < h and grid[y][x]

        def is_coast(x, y):
            return is_land(x, y) and not all(is_land(x + dx, y + dy) or not (0 <= x + dx < w and 0 <= y + dy < h)
                                             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))

        def is_south_edge(x, y):  # land cell with sea just below: drawn darker, as a cliff
            return is_land(x, y) and y + 1 < h and not grid[y + 1][x]

        pos = {}
        for c in everyone:
            x, y = proj(c["lon"], c["lat"])
            px, py = 50 + x * 50, 50 + y * 50 * w / h
            pos[c["id"]] = {"x": round(px, 2), "y": round(py, 2), "inside": 1 < px < 99 and 1 < py < 99}
        out["layouts"][name] = {
            "w": w, "h": h, "reach_km": cfg["reach"],
            "land": runs_to_path(grid, is_land),
            "coast": runs_to_path(grid, is_coast),
            "cliff": runs_to_path(grid, is_south_edge),
            "pos": pos,
        }
        outside = [k for k, v in pos.items() if not v["inside"]]
        print(f"{name}: {w}x{h} cells, land path {len(out['layouts'][name]['land']) // 1024} KB, outside: {outside}")
    (ROOT / "data" / "map.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
