---
name: reel-montage
description: Monte un Reel face cam, des rushes à la vidéo auditée : dérushage, liste de coupe, A-roll aux coupes serrées, relecture, fonds depuis les enregistrements d'écran, scènes calées sur les mots, rendu, audit par un agent indépendant. À utiliser quand on dit "j'ai mis les rushes", "tu peux monter", "refais le montage", "corrige la v2", ou quand le skill reel arrive à l'étape montage. Le cadrage doit exister (video-face-cam).
---

# Reel : le montage

Tout passe par la commande `~/claude-reels/outils/reel.py` (lire son en-tête) et la bibliothèque
`~/claude-reels/outils/reelkit/` (scènes réutilisables dans `scenes.py`). Local et gratuit. La
méthode fait foi : [METHODE.md](../../METHODE.md). Modèle de composition : `exemples/compo.py`.

## Réglages par défaut (ne pas les reproposer)

Ni musique ni bruitages. La personne toujours à l'écran (aucun plan de coupe qui la masque). Fond
blanc en mise en page `detoure`. Titres en concepts, sans émoji. Sous-titres karaoké trois mots au
plus, mot en cours dans la couleur d'accent. Une minute visée. Voix à -16 LUFS (chaîne intégrée à `reel.py`).
Synchro : image avancée de 0,16 s (micro sans fil), à réécouter si le micro change.

## Les étapes

1. **Projet** : `reel.py init SLUG` existe en général depuis le cadrage. Ajouter les rushes :
   `reel.py rushes FICHIER...`. **Identifier rushes et enregistrements par leur date** (créés après
   le cadrage) et en regardant une image de chacun, jamais en prenant « les plus récents » à
   l'aveugle. Projet de test : `init SLUG --test` (rien sur le Bureau).
2. **Dérushage** : `reel.py derush`. Lire `prises.md`. Une ALERTE de son sous 44,1 kHz se signale
   tout de suite (aigus perdus, rien ne les rend), sans bloquer le montage.
3. **Liste de coupe** : partir de `coupes_proposees.json`, écrire `coupes.json` :
   - suivre le texte du cadrage, et **la version dite quand la personne improvise** ;
   - la **dernière prise propre** de chaque phrase, sauf si une prise antérieure est plus juste ;
   - couper les redites et les phrases qui doublent la suivante ;
   - `lo` après la fin de la prise précédente, `hi` avant le premier mot de la suivante ;
   - un bégaiement ou un long silence dans une prise se retire en coupant le bloc en deux.
   Le champ `texte` de chaque bloc est la phrase attendue (la relecture s'en sert). Une accroche
   alternative porte `"variante": "B"` ; sans ce champ, un bloc entre dans toutes les variantes.
4. **A-roll** : `reel.py assemble`. Lire `relecture.md` : chaque bloc doit être « OK ». Un MANQUE
   dû à l'orthographe de Whisper (un nom propre mal entendu) se règle dans le `texte` ; un vrai
   MANQUE ou une REDITE se corrige dans `coupes.json`. Ne jamais continuer avec une alerte.
5. **Détourage** (mise en page `detoure` seulement) : skill **reel-detourage**.
6. **Fonds** : `fonds.json` depuis les enregistrements, puis `reel.py fonds`. Un fond est **inversé
   par défaut** (enregistrement sombre affiché en clair) ; un enregistrement déjà clair (page web)
   prend la classe `brut`. **Confidentialité** : regarder une image de chaque enregistrement ; tout
   nom de client ou de tiers lisible se recadre ou se floute (`scenes.flou`) avant le rendu.
7. **Composition** : écrire `compo.py`. Les instants viennent tous de `Mots.at("mots dits")`, jamais
   en dur. Chaque scène vient de `reelkit.scenes` ; une scène nouvelle s'ajoute à `scenes.py` si elle
   peut resservir. Compteurs calés pour atteindre leur valeur **au moment où le chiffre est dit**.
   - `detoure` : `c.personne_detouree(hauteurs, punch)` (voir reel-detourage) ;
   - `plein_cadre` : `c.personne_plein_cadre(punch)` ;
   - `ecran_coupe` : scènes dans la moitié haute ; régler dans le CSS du projet la fenêtre de la
     personne (`#me{top:-150px !important}` si la tête est coupée) et les sous-titres sur la
     jonction (`.cap{top:880px !important}`).
8. **Rendu** : `reel.py rendu --at t1,t2,...` (un instant par scène). Regarder les planches de
   captures soi-même avant toute autre chose.
9. **Audit indépendant** : lancer un sous-agent qui ne connaît pas le montage : se placer dans le
   projet, lancer `reel.py audit`, regarder chaque planche de `public/snapshots/`, lire le cadrage et
   la checklist de METHODE.md, rendre un verdict par ligne (OK, À VOIR, ROUGE) avec la preuve. Il ne
   corrige rien. Toute ligne ROUGE se corrige avant de montrer la vidéo ; un compteur capturé en
   pleine montée n'est pas une erreur.
10. **Livrer** : l'aperçu téléphone, le fichier Instagram, les lignes « à vérifier » de `audit.md`
    (synchro à l'oreille, réserves d'interface sur téléphone).

## Quand on demande l'inverse d'un réglage par défaut

La demande explicite prime : la faire en rappelant le réglage d'avant. Musique : `reel.py musique
FICHIER` (environ 9 dB sous la voix, nappe sans percussions) ; **jamais sur un son de rush en
16 kHz** (expliquer pourquoi). Synchro à changer : `reel.py etat sync=0.10`.

## Erreurs déjà commises (et ce qui les empêche maintenant)

| Erreur | La parade |
|---|---|
| Blancs entre phrases, tête qui part vers le script | bornes serrées dans `assemble`, audit des blancs |
| Phrase dite deux fois | relecture : détecteur de redites |
| Musique « gênante », bruitages bizarres | aucun lit ni bruitage par défaut |
| Bande vide sous les pieds, tête qui mord le titre | hauteurs ≥ 500, zones déclarées par les scènes, audit |
| Zoom alterné aux coupes qui passe la tête sous les titres | `alterne=1.0` quand le haut est chargé |
| Compteur à 0 pendant que le chiffre est dit | `compteur(t_mot=...)` |
| Deux classes CSS de même nom (une colonne de tableau vide) | noms de classes propres à chaque scène |
| Copies de test sur le Bureau | ne rendre que dans le projet de la vraie vidéo |
