# World in Pixels

The directory of cities drawn in pixel art. One pixel world map, centred on Paris: every city that has its own map
is a dot, and a click opens that city's map in a new tab.

Live site: https://world-in-pixels.netlify.app/

The site only contains links. The maps, their names and their images belong to their authors, who are credited on
each entry.

## Add a city

1. Add an entry to [`data/cities.json`](data/cities.json):
   - in `cities` if the city has a pixel map (or voxels, or an isometric illustration) that anyone can **explore in
     a web browser**;
   - in `others` if it is only a video, an app or a work in progress for now.
2. Fields: `id`, `name`, `country`, `lat`, `lon`, `url`, `site`, `author`, `author_url`, `style` (`kind` in
   `others`), `note` (one sentence, verifiable facts), and optionally `post`, `making_of`, `source`, `label`
   (`right`, `left`, `top`, `bottom`: which side of the dot the label sits on).
3. Rebuild and check:

   ```
   pip install pillow playwright && playwright install chromium
   python3 tools/make_map.py   # refits the map and recomputes the dot positions
   python3 build.py            # writes dist/index.html
   python3 tools/shot.py       # screenshots + checks (390 px, no JavaScript, overlaps)
   python3 tools/og.py         # share image, only when a dot is added (then build again)
   ```
4. Open a pull request. No time? Open an issue with the link to the map.

A city is removed at its author's request, or when its map stops responding.

## How it works

- `data/cities.json`: the single source of truth.
- `tools/make_map.py`: Natural Earth land (public domain) in an azimuthal equidistant projection centred on Paris,
  with a lens effect (`r → r^0.5`) so that London and Warsaw do not sit on top of each other, then rasterised into
  SVG paths. Two framings: wide (192×120 cells) and tall for phones (96×120).
- `build.py`: assembles `src/template.html`, `src/style.css` and the data into one static page. The page works
  without JavaScript: the dots are plain links positioned with CSS.
- `tools/shot.py`: screenshots and automatic checks.

## License

- Code: MIT (see [`LICENSE`](LICENSE)).
- Directory data (`data/cities.json`): CC BY 4.0 (see [`data/LICENSE`](data/LICENSE)). Reuse it with a credit to
  "World in Pixels" and a link to this repository.
- Base map: Natural Earth, public domain.
- The listed maps remain the property of their authors.

A project by [Louis-Marie Soulard](https://x.com/LouisMarie_S), author of [parisenpixels.fr](https://parisenpixels.fr/).
