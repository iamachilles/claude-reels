---
name: reel-publication
description: Prépare la publication d'un Reel : couverture (sourire tiré du rush, détourage, titre en deux bandeaux, icônes d'applis), légendes Instagram, TikTok et YouTube Shorts. À utiliser quand on dit "fais la couverture", "fais la légende", "prépare la publication", ou quand le skill reel arrive à l'étape publication.
---

# Reel : couverture et légendes

La méthode fait foi : [METHODE.md](../../METHODE.md), sections « Couverture » et « Légendes ».
Outils : `~/claude-reels/outils/reel.py`.

## La couverture

1. **La photo** : `reel.py cover-sourire` classe les instants du rush par sourire et regard caméra
   (planche `cover/sourires.jpg`) ; un plan muet de couverture tourné exprès passe avant. Choisir un
   grand sourire, regard caméra.
2. **Le détourage** : skill **reel-detourage**, partie photo.
3. **Les icônes** : `reel.py icone NOM "Nom App Store"` (API publique de l'App Store, gratuite),
   des outils dont la vidéo parle.
4. **`cover.json`** puis `reel.py cover` :
   - photo plein cadre, visage zoomé et centré, aucun voile, aucune bande vide ;
   - **le titre seul**, en capitales, deux bandeaux au-dessus du visage (noir, puis couleur d'accent) ; il
     reprend la tension de l'accroche ; pas de surtitre, pas de badge, pas d'encart ;
   - fond : le visuel principal de la vidéo. Le fond est inversé par défaut (fait pour un écran
     sombre) : un fond déjà clair se pré-inverse avant `reel.py cover`.
5. **Vérifier les deux vues** : `cover/vue_pleine.jpg` et `cover/vue_grille.jpg` (la zone 3:4 de la
   grille du profil). Visage et titre doivent tenir dans la grille.

## Les légendes (une par plateforme)

Règles communes : aucun tiret cadratin ni demi-cadratin, français accentué, aucun chiffre non
vérifié, rien qui affirme plus que la vidéo. **La légende prolonge la valeur de la vidéo** ; le
mot-clé n'est qu'une offre en plus. Pas de mot-clé si aucune ressource n'est à envoyer : une
question pour les commentaires.

- **Instagram** : la première ligne accroche (seule visible avant « plus »). Si une ressource
  existe : « Commente MOT et je t'envoie … en message » puis « (Abonne-toi, sinon mon message finit
  dans tes demandes.) ». Ensuite le problème, la valeur en étapes numérotées, la ressource, trois à
  cinq hashtags.
- **TikTok** : une ou deux phrases avec les mots qu'on taperait dans la recherche, une question,
  hashtags.
- **YouTube Shorts** : **un titre** avec les mots-clés (c'est lui qu'on voit et qu'on cherche), une
  description courte qui reprend les étapes, trois hashtags.

## Pour finir

- Écrire couverture et légendes dans le cadrage, copier la légende Instagram dans un `.txt`.
- Rappeler : couverture envoyée sur le téléphone, « Modifier la couverture » puis « Ajouter depuis
  la pellicule » dans Instagram ; le lien de la ressource à envoyer à ceux qui commentent.
- Mettre `reel.json` à `etape: publication`.
