#!/usr/bin/env python3
"""Build the static site: data/cities.json + data/map.json + src/ -> dist/.

    python3 tools/make_map.py   # only when cities are added or moved
    python3 build.py

The page works without JavaScript: every city is a plain link placed on the map
with CSS custom properties (--x/--y for the wide map, --xt/--yt for the tall one).
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = json.loads((ROOT / "site.json").read_text())
DATA = json.loads((ROOT / "data" / "cities.json").read_text())
MAP = json.loads((ROOT / "data" / "map.json").read_text())
EXT = 'target="_blank" rel="noopener"'


def e(s):
    return html.escape(str(s), quote=True)


def svg(name):
    L = MAP["layouts"][name]
    return (f'<svg class="map__land map__land--{name}" viewBox="0 0 {L["w"]} {L["h"]}" '
            f'preserveAspectRatio="none" shape-rendering="crispEdges" aria-hidden="true" focusable="false">'
            f'<path class="land" d="{L["land"]}"/><path class="coast" d="{L["coast"]}"/>'
            f'<path class="cliff" d="{L["cliff"]}"/></svg>')


def pins():
    wide, tall = MAP["layouts"]["wide"]["pos"], MAP["layouts"]["tall"]["pos"]
    out = []
    for n, c in enumerate(DATA["cities"], 1):
        w, t = wide[c["id"]], tall[c["id"]]
        cls = "pin" + (" pin--center" if c["id"] == DATA["center"] else "") + f' pin--{c.get("label", "right")}'
        out.append(
            f'<li><a class="{cls}" href="{e(c["url"])}" {EXT} data-city="{e(c["id"])}" '
            f'style="--x:{w["x"]};--y:{w["y"]};--xt:{t["x"]};--yt:{t["y"]}" '
            f'title="{e(c["name"])} : ouvrir {e(c["site"])} dans un nouvel onglet">'
            f'<span class="pin__dot" aria-hidden="true"></span>'
            f'<span class="pin__label">{e(c["name"])}</span>'
            f'<span class="visually-hidden"> (carte de {e(c["author"])}, nouvel onglet)</span></a></li>')
    return "\n".join(out)


def extra_links(c):
    links = []
    for key, label in (("making_of", "Coulisses"), ("post", "Post de l'auteur"), ("source", "Code source")):
        if c.get(key):
            links.append(f'<a href="{e(c[key])}" {EXT}>{label}</a>')
    return "".join(f"<li>{l}</li>" for l in links)


def cards():
    out = []
    for n, c in enumerate(DATA["cities"], 1):
        cls = "city" + (" city--center" if c["id"] == DATA["center"] else "")
        out.append(f'''<li class="{cls}" id="{e(c["id"])}">
  <span class="city__num" aria-hidden="true">{n:02d}</span>
  <h3 class="city__name"><a href="{e(c["url"])}" {EXT}>{e(c["name"])}<span class="visually-hidden"> (nouvel onglet)</span></a></h3>
  <p class="city__meta"><span class="city__country">{e(c["country"])}</span> <span class="city__style">{e(c["style"])}</span></p>
  <p class="city__note">{e(c["note"])}</p>
  <p class="city__author">Carte de <a href="{e(c["author_url"])}" {EXT}>{e(c["author"])}</a></p>
  <p class="city__site"><a href="{e(c["url"])}" {EXT}>{e(c["site"])}</a></p>
  <ul class="city__links">{extra_links(c)}</ul>
</li>''')
    return "\n".join(out)


def others():
    out = []
    for c in DATA["others"]:
        post = f' <a class="other__post" href="{e(c["post"])}" {EXT}>Post de l\'auteur</a>' if c.get("post") else ""
        out.append(f'''<li class="other" id="{e(c["id"])}">
  <h3 class="other__name"><a href="{e(c["url"])}" {EXT}>{e(c["name"])}<span class="visually-hidden"> (nouvel onglet)</span></a></h3>
  <p class="other__meta"><span class="other__kind">{e(c["kind"])}</span> <span class="other__country">{e(c["country"])}</span></p>
  <p class="other__note">{e(c["note"])}</p>
  <p class="other__author">Par <a href="{e(c["author_url"])}" {EXT}>{e(c["author"])}</a>{post}</p>
</li>''')
    return "\n".join(out)


def main():
    page = (ROOT / "src" / "template.html").read_text()
    values = {
        "MAP_WIDE": svg("wide"), "MAP_TALL": svg("tall"), "PINS": pins(), "CARDS": cards(), "OTHERS": others(),
        "COUNT": len(DATA["cities"]), "COUNT_OTHERS": len(DATA["others"]),
        "CSS": (ROOT / "src" / "style.css").read_text(),
        **{k.upper(): e(v) for k, v in SITE.items()},
    }
    for k, v in values.items():
        page = page.replace("{{" + k + "}}", str(v))
    missing = [w for w in page.split("{{")[1:]]
    assert not missing, f"placeholders left: {[m[:20] for m in missing]}"
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(page)
    for f in (ROOT / "src" / "static").glob("*"):
        shutil.copy(f, dist / f.name)
    print(f"dist/index.html {len(page) // 1024} KB, {len(DATA['cities'])} villes, {len(DATA['others'])} à part")


if __name__ == "__main__":
    main()
