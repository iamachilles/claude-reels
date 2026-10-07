---
name: reel
description: Chef d'orchestre des vidéos verticales face caméra (Reels Instagram, TikTok, YouTube Shorts) : du sujet au montage audité, avec couverture et légendes, en enchaînant video-face-cam, reel-montage, reel-detourage et reel-publication. À utiliser quand on dit "on bosse sur la vidéo X", "/reel X", "on fait un Reel sur X", "reprends la vidéo X", ou qu'on dépose des rushes pour une vidéo déjà cadrée.
---

# Reel : du sujet à la publication

Tu demandes une vidéo ; ce skill déroule tout, et ne s'arrête que là où ta main est nécessaire.
Le savoir-faire est dans les quatre skills appelés et dans [METHODE.md](../../METHODE.md) ; ce skill
ne fait que les enchaîner. Outil unique : `~/claude-reels/outils/reel.py` (voir le README).

## Retrouver ou créer la vidéo

1. Chercher l'état existant : `~/video-reel-*/reel.json` (champs `slug`, `etape`), puis le cadrage
   de la vidéo. Une vidéo en cours se reprend à son étape, jamais depuis le début.
2. Nouvelle vidéo : slug court, et créer le projet **dès le cadrage** :
   `reel.py init SLUG` puis `reel.py etat cadrage=CHEMIN mise_en_page=...`.
   Les rushes s'ajoutent au tournage par `reel.py rushes FICHIER...`.

## Les étapes et les quatre arrêts

| Étape (`reel.json`) | Ce qui se fait | Skill | Arrêt |
|---|---|---|---|
| cadrage | promesse, accroches, texte et appuis, mise en page, plans, enregistrements à faire | video-face-cam | **1. Tu valides le texte et les plans** |
| tournage | tu tournes et tu enregistres tes écrans | (toi) | **2. Tu déposes les rushes** |
| derush, assemble | prises, liste de coupe, A-roll serré, relecture | reel-montage | non |
| detour | si la mise en page est `detoure` | reel-detourage | non |
| rendu, audit | fonds, scènes, rendu, audit par un agent indépendant | reel-montage | **3. Tu donnes tes retours** (boucle jusqu'au feu vert) |
| publication | couverture, légendes par plateforme | reel-publication | **4. Tu valides avant de publier** |

**Questions.** Au cadrage, ne pas interroger avant d'écrire : rédiger sur les réglages par défaut,
puis **poser toutes les questions ouvertes à l'arrêt 1**. L'accroche et la fin restent celles de la
personne filmée : proposer, sa version prime. Entre deux arrêts, ne rien demander.

**Une demande explicite prime sur un réglage par défaut.** La faire, en rappelant en une ligne le
réglage d'avant. Seule exception : une contrainte technique dure, qu'on explique au lieu d'obéir
(pas de musique sur un son de rush en 16 kHz, la voix se ferait couvrir).

## À chaque arrêt, rendre

- ce qui a été fait, en deux ou trois lignes ;
- le livrable (aperçu téléphone, couverture, légende) ;
- ce qu'il faut faire ou trancher, et rien d'autre.

## Règles

- L'outillage est local et gratuit. Une démo payante à filmer (un appel d'API facturé) s'annonce
  avec son coût et attend un oui explicite.
- Format plus long qu'une minute : `reel.py etat duree_max=90` au cadrage.
- Les longues tâches (dérushage, détourage, rendu) tournent en arrière-plan ; le dire en une ligne.
- Un rendu de test ne se copie jamais sur le Bureau.
- Chaque retour qui vaut pour toutes les vidéos s'écrit dans le skill concerné et dans METHODE.md.
