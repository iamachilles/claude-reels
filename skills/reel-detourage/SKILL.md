---
name: reel-detourage
description: Détoure la personne filmée dans un Reel (vidéo ou photo de couverture) et la garde à taille constante : retrait du fond en local, suivi du haut de la tête, hauteur par scène, effacement des objets du décor collés à la silhouette. À utiliser quand la mise en page est `detoure`, ou quand on dit "détoure-moi", "mets-moi devant la vidéo", "enlève le fond derrière moi".
---

# Reel : le détourage

Outils : `~/claude-reels/outils/reel.py` (commandes `detour`, `cover-photo`, `cover-effacer`) ; le
détourage lui-même est `npx hyperframes remove-background` (modèle local, environ 0,1 s par image,
3 à 4 minutes pour une minute de Reel). Gratuit.

## Vidéo (mise en page detoure)

1. Après un `reel.py assemble` réussi : `reel.py detour` (en arrière-plan). Il écrit
   `public/me.webm` (fond transparent) et `headtrack.json` (haut de la tête, 8 fois par seconde).
2. Contrôler deux images sur fond de couleur avant de composer (cheveux, mains, micro) :
   `ffmpeg -v error -y -c:v libvpx-vp9 -ss T -i public/me.webm -f lavfi -i color=c=0x00B140:s=1080x1920 -filter_complex "[1][0]overlay=shortest=1,scale=405:-1" -frames:v 1 src/controle_T.jpg`.
3. Dans `compo.py`, `c.personne_detouree(hauteurs, punch, alterne)` :
   - **la taille suit la tête** : quand la personne avance vers la caméra pendant ses prises, la
     taille se corrige en continu pour garder le visage au même endroit ;
   - **hauteurs** : `[(t, H)]`, H étant la hauteur du haut de la tête **sans zoom**, choisie scène
     par scène selon la place prise en haut (zone basse de la scène + 100 environ). Avec un zoom p,
     la tête monte de 1420 x (p - 1). **Jamais sous 500** : le corps remonterait et laisserait une
     bande vide sous les pieds. L'audit signale les instants où la tête passe sous une scène ;
   - **punch** : zooms sur les mots forts (1,05 à 1,12) ; `alterne` (1,07 par défaut) zoome un
     morceau sur deux pour le rythme, à mettre à 1,0 quand les scènes du haut sont chargées.
4. Toute coupe modifiée après le détourage impose de le refaire (l'A-roll a changé).

**Fond derrière la personne : blanc par défaut.** Un mur de tournage clair laisse un liseré clair
dans les cheveux, visible sur un fond sombre.

## Photo (couverture)

1. `reel.py cover-photo T` : l'image 4K du rush à l'instant T, détourée (`cover/photo_detouree.png`)
   et posée sur fond vert (`cover/controle.jpg`).
2. Regarder le contrôle : un objet du décor collé à la silhouette (une suspension de plafond
   au-dessus de la tête) s'efface par zones : `reel.py cover-effacer x0,y0,x1,y1,mode` en pixels de
   la photo 4K, avec `tout`, `sombre` ou `gris`. Sur les cheveux, préférer un masque elliptique
   adouci (Pillow, flou gaussien) au rectangle, qui laisse une encoche. **Vérifier ensuite le menton,
   le col et le haut des cheveux en gros plan.**

## Erreurs déjà commises

| Erreur | La parade |
|---|---|
| Taille qui change d'une prise à l'autre, tête qui cache les titres | suivi de la tête, hauteurs par scène |
| Bande vide sous les pieds (H trop haut) | H jamais sous 500 ; l'audit le vérifie |
| Liseré dans les cheveux sur fond noir | fond blanc |
| Lampe restée sur la photo de couverture | contrôle sur fond vert, effacement par zones |
| Encoche dans les cheveux après effacement | masque elliptique adouci |
