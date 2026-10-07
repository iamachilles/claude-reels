---
name: video-face-cam
description: Cadre une vidéo verticale face caméra (Reel Instagram, TikTok, YouTube Shorts) : promesse, accroches, texte complet et appuis, mise en page, plan de tournage, enregistrements d'écran à faire, ce qui s'affiche à l'image. À utiliser quand on dit "je veux faire une vidéo sur X", "cadre-moi un Reel", "prépare le tournage", "aide-moi sur l'accroche", ou quand le skill reel arrive à l'étape cadrage.
---

# Vidéo face cam : le cadrage

La méthode fait foi et ce skill ne la recopie pas : [METHODE.md](../../METHODE.md). **La lire en
entier avant d'agir.** Lire aussi le cadrage précédent s'il en existe un (dossier `cadrages/` choisi
par l'utilisateur, par défaut `~/video-reels-cadrages/`).

## La règle qui passe avant tout

Sur Instagram et tous les réseaux verticaux, **la vidéo divertit et livre toute sa valeur elle-même
en une minute** (1:30 au plus). Tension, sensationnel, une histoire. **Une ressource à offrir n'est
qu'un bonus** de quelques secondes à la fin. Un cadrage qui part de la ressource est à refaire :
partir de ce que la vidéo apprend ou montre de spectaculaire.

## Ce que le cadrage produit

Un fichier `cadrages/YYYY-MM-DD-{slug}.md` qui contient dans cet ordre :

1. **La promesse** : ce que le spectateur sait ou voit à la fin. Une seule.
2. **L'accroche, au mot** : une retenue et deux à tourner aussi, chacune avec ce qu'elle ouvre et ce
   qu'elle retient. Écarter toute accroche qui contient sa réponse. Une surimpression d'intro, qui
   est un **concept**, pas une phrase (« Une IA sans mémoire »).
3. **La boucle** : ouverte, nourrie, fermée.
4. **Le texte complet** puis **les appuis** : accroche et bascules au mot, le reste en appuis. La
   personne lit le texte deux fois puis pose la feuille ; sa version dite prime au montage. Environ
   150 mots par minute ; viser 140 à 160 mots.
5. **La mise en page**, une seule par vidéo :
   - `detoure` : la personne détourée devant ses enregistrements d'écran. Appelle reel-detourage.
   - `plein_cadre` : la personne filmée telle quelle, illustrations par-dessus.
   - `ecran_coupe` : scène animée en haut (y de 0 à 940), la personne en bas.
6. **Le plan de tournage** : les plans, les prises (trois accroches à la suite, le reste d'une traite
   deux fois ; au montage, chaque accroche donne une variante A, B, C), les plans muets (sourire
   face caméra pour la couverture, geste vers le haut).
7. **Les enregistrements d'écran à faire**, un par un : quoi, combien de temps, quels gestes (lents),
   et les réglages pour qu'**aucun nom de client ni de tiers** ne soit lisible.
8. **Ce qui s'affiche** : un tableau moment, image, source. Toute entreprise, tout chiffre, tout
   outil nommé y a sa ligne. Les titres sont des **concepts sans émojis**.
9. **Les sources** : chaque chiffre avec son origine vérifiable.

**La preuve** s'adapte au sujet : un fait vérifiable propre à la vidéo vaut mieux qu'un palmarès
général. Le chiffre dit et le chiffre affiché sont identiques. **Une démo payante à filmer** (un
appel d'API facturé) s'annonce avec son coût dans les points à trancher.

## Règles d'écriture

- Aucun tiret cadratin ni demi-cadratin ; français accentué ; jamais « ce n'est pas X, c'est Y ».
- Jamais un chiffre, un nom ou une date non vérifiés : tout ce qui est nommé s'affiche en grand.
- Chaque phrase passe le test du pote (la dirais-tu exactement comme ça à un ami ?).
- La version de la personne filmée prime : si elle réécrit, le cadrage prend sa version.

## Erreurs déjà commises (ne pas refaire)

| Erreur | La parade |
|---|---|
| Vidéo construite autour de la ressource | partir de la valeur et du divertissement, la ressource en bonus |
| Vocabulaire de la ressource repris tel quel | des mots de tous les jours |
| Titres en phrases, émojis | « Lecture avant chaque tâche », sans émoji |
| Chiffre qui affirme plus que ce qu'on sait | ne garder que ce qui est prouvé |
| Enregistrement d'écran montrant des clients | lister les dossiers et pages propres dans le cadrage |

## À la fin du cadrage

Écrire le cadrage, créer le projet (`reel.py init SLUG`, puis `reel.py etat cadrage=CHEMIN
mise_en_page=...`), lister les points à trancher, et rappeler : micro branché en filaire (USB-C)
plutôt qu'en Bluetooth (sinon le son sort en 16 kHz), rushes et enregistrements dans `~/Downloads`.
