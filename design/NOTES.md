# Notes de design

## Direction

Un atlas numérique sombre, inspiré des écrans 8 bits et des cartographies techniques. La carte est le seul héros du premier écran : cadre anguleux, repères de coordonnées, grille et tramé de mer. Les sections suivantes utilisent des fiches carrées, sans ombres douces ni décor superflu.

## Palette

- Fond principal : `#07171b`
- Fond des fiches : `#0b2026`
- Mer : `#123844`
- Terre : `#8faf62`
- Rivage : `#c2d778`
- Falaise : `#587846`
- Texte : `#f4f1d6`
- Texte secondaire : `#aec2bd`
- Points et accents : `#ff7657`
- Paris et appels à contribution : `#f4df62`

Le mode sombre est unique. Les contrastes de texte visent AA et le focus clavier jaune reste visible sur tous les fonds.

## Polices

- **Silkscreen** pour les titres, étiquettes, numéros et boutons.
- **Atkinson Hyperlegible** pour les paragraphes et la navigation.

Les deux familles sont chargées depuis Google Fonts avec `display=swap`. Les polices système assurent le repli.

## Choix d'interface

- Mer tramée en CSS, grille discrète et SVG avec `crispEdges`.
- Paris possède un point plus grand, jaune, avec une pulsation en `steps()`.
- Étiquettes orientées dans `data/cities.json` pour éviter les collisions sur les deux projections.
- Zones tactiles des points de 40 × 40 px, y compris autour du petit point visible.
- Fiches en grille de trois colonnes sur ordinateur, puis une colonne sur téléphone.
- Aucun JavaScript, aucune image tierce. Le favicon est un dessin SVG original.
- Les animations sont désactivées avec `prefers-reduced-motion`.
