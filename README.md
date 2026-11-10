# Villes en pixels

L'annuaire des villes dessinées en pixel art. Une carte du monde en pixels, centrée sur Paris : chaque ville qui a
sa carte est un point, un clic ouvre la carte de la ville dans un nouvel onglet.

*A directory of cities drawn as pixel-art maps. One pixel world map centred on Paris; each dot opens that city's map
in a new tab. Pull requests adding a city are welcome, in French or English.*

Le site ne contient que des liens. Les cartes, leurs noms et leurs images appartiennent à leurs auteurs, crédités
sur chaque fiche.

## Ajouter une ville

1. Ajoutez une entrée dans [`data/cities.json`](data/cities.json) :
   - dans `cities` si la ville a une carte en pixels (ou voxels, ou illustration isométrique) **navigable dans un
     navigateur**, ouverte à tous ;
   - dans `others` si ce n'est encore qu'une vidéo, une application ou une carte en cours.
2. Champs d'une ville : `id`, `name`, `country`, `lat`, `lon`, `url`, `site`, `author`, `author_url`, `style`,
   `note` (une phrase, des faits vérifiables), et au choix `post`, `making_of`, `source`, `label`
   (`right`, `left`, `top`, `bottom` : côté de l'étiquette sur la carte).
3. Régénérez et vérifiez :

   ```
   pip install pillow playwright && playwright install chromium
   python3 tools/make_map.py   # recalcule le cadrage et la position des points
   python3 build.py            # écrit dist/index.html
   python3 tools/shot.py       # captures + contrôles (390 px, sans JavaScript, chevauchements)
   ```
4. Ouvrez une pull request. Pas le temps ? Ouvrez une issue avec le lien de la carte.

Une ville est retirée à la demande de son auteur, ou si sa carte ne répond plus.

## Comment c'est fait

- `data/cities.json` : la seule source de vérité.
- `tools/make_map.py` : fond Natural Earth (domaine public) projeté en azimutale équidistante centrée sur Paris,
  avec un effet loupe (`r → r^0,5`) pour que Londres et Varsovie ne se marchent pas dessus, puis pixelisé en
  chemins SVG. Deux cadrages : large (192×120 cellules) et haut pour les téléphones (96×120).
- `build.py` : assemble `src/template.html`, `src/style.css` et les données en une page statique. La page marche
  sans JavaScript : les points sont de simples liens placés en CSS.
- `tools/shot.py` : captures et contrôles automatiques.

## Licence

- Code : licence MIT (voir [`LICENSE`](LICENSE)).
- Données de l'annuaire (`data/cities.json`) : CC BY 4.0 (voir [`data/LICENSE`](data/LICENSE)), réutilisables en
  créditant « Villes en pixels » avec un lien vers ce dépôt.
- Fond de carte : Natural Earth, domaine public.
- Les cartes listées restent la propriété de leurs auteurs.
