# Brief design : Villes en pixels

Tu es le designer de ce site. Dossier : la racine du dépôt. Écris en français.

## Le site
Un annuaire des villes dessinées en pixel art. La page principale est une carte du monde en pixels, centrée sur
Paris (projection azimutale avec effet loupe), où chaque ville qui a sa carte en pixels est un point cliquable qui
ouvre le site de la ville dans un nouvel onglet. Sous la carte : la liste des villes (fiches avec auteur crédité),
une liste « À part » (vidéos, applis, 3D, sans point sur la carte), un appel à contribution (projet open source,
lien GitHub). Public : curieux et développeurs venus de X, qui connaissent parisenpixels.fr, tiny.london,
isometric.nyc.

## Ce que tu modifies
- `src/style.css` : tout le style (il est injecté dans la page par `build.py`). Le fichier actuel n'est qu'un
  squelette de positionnement, remplace-le entièrement.
- `src/template.html` : tu peux réorganiser, ajouter des enveloppes, des classes, un favicon (`src/static/favicon.svg`,
  pixel art, sera copié à la racine). Garde tous les textes, tous les liens et tous les `{{PLACEHOLDERS}}`.
- `data/cities.json` : uniquement le champ optionnel `"label"` d'une ville (`"right"`, `"left"`, `"top"`,
  `"bottom"`) qui donne la classe `pin--right|left|top|bottom` pour placer l'étiquette sans chevauchement.
- Ne touche pas à `build.py`, `tools/`, `data/map.json`, `site.json`, ni au reste de `data/cities.json`.

## Contrat technique (à respecter)
- Zéro JavaScript obligatoire : la page doit être complète et cliquable sans JS. Pas de framework, pas de build.
  Un petit script d'agrément inline est toléré, pas nécessaire.
- Fragments générés par `build.py` (lis-le) : `.map` contient deux SVG `.map__land--wide` (192×120 cellules, écrans
  larges) et `.map__land--tall` (96×120, téléphones) avec trois `<path>` : `.land`, `.coast` (cellules de rivage),
  `.cliff` (cellule de terre avec la mer juste au sud). Tu les colories en CSS (`fill`). `shape-rendering: crispEdges`.
- Points : `ol.pins > li > a.pin[.pin--center]` avec `--x/--y` (pourcentages dans la carte large) et `--xt/--yt`
  (carte haute), `.pin__dot`, `.pin__label`. Paris (`.pin--center`) doit être clairement le centre et le plus visible.
  Londres est à 13 px de Paris sur téléphone : étiquettes à placer avec soin (champ `label`).
- La carte large garde le ratio 192/120, la haute 96/120 (sinon les points se décalent). Bascule sous ~700 px.
- Fiches : `.city` (`.city--center` pour Paris) et `.other` : voir `build.py` pour les classes internes.
- Polices : système ou Google Fonts (2 familles au plus, `display=swap`). Aucune image tierce : on ne recopie pas
  les captures des autres sites. Tout le décor est en CSS/SVG fait maison.
- Accessibilité : contrastes AA, focus visible sur les points et les liens, cibles tactiles ≥ 40 px sur téléphone
  (la zone cliquable peut dépasser le point visible), `prefers-reduced-motion` respecté.

## Direction
Pixel art assumé, pas un tableau de bord SaaS : grille visible, couleurs franches, typographie à caractère (une
police pixel ou mono pour les titres et étiquettes, une police très lisible pour le texte). La carte est le héros :
elle occupe presque tout le premier écran sur ordinateur (titre court au-dessus ou incrusté), et la largeur
complète sur téléphone. Mer avec un léger motif tramé (dithering) en CSS, terre avec le rivage et la falaise en
deux tons. Animations sobres et faites de pas francs (`steps()`), par exemple le point de Paris qui pulse,
l'étiquette qui se révèle au survol. Mode clair ou sombre : choisis-en un et tiens-le. À éviter : dégradés violets,
cartes à coins arrondis et ombres douces génériques, emojis, tirets cadratins dans les textes.

## Vérifie ton rendu toi-même, puis itère
```
python3 build.py && python3 tools/shot.py
```
Le script écrit `shots/desktop.png`, `shots/phone.png`, `shots/*-full.png`, `shots/*-nojs.png` et vérifie : pas de
débordement horizontal à 390 px, points et étiquettes dans la carte, aucun chevauchement entre points et
étiquettes, liens en nouvel onglet. Regarde les captures, corrige, relance jusqu'à ce que les quatre lignes
finissent par `OK` et que le rendu te plaise à 1440 px et à 390 px.

## Livrable
Les fichiers modifiés en place, les captures finales dans `shots/`, et un court `design/NOTES.md` (palette,
polices, choix).
