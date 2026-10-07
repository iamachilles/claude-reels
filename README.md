# claude-reels

Les skills Claude Code avec lesquels je cadre, monte, sous-titre et habille mes Reels (Instagram,
TikTok, YouTube Shorts). Je tourne, Claude fait le reste : cadrage, dérushage, coupes, sous-titres
karaoké, animations, détourage, couverture et légendes. Tout tourne en local, sans abonnement.

Exemple : 9 minutes de rush deviennent un Reel d'une minute, monté et sous-titré, après une demi-heure
de travail de Claude. Mon temps effectif : une trentaine de minutes (cadrage, tournage, retouches).

## Ce qu'il y a dedans

| Dossier | Contenu |
|---|---|
| `skills/reel` | Le chef d'orchestre : enchaîne les quatre skills ci-dessous et ne s'arrête qu'aux quatre moments où ta main est nécessaire (valider le texte, déposer les rushes, donner tes retours, valider avant publication) |
| `skills/video-face-cam` | Le cadrage : promesse, accroches, texte, plans, enregistrements d'écran à faire |
| `skills/reel-montage` | Le montage : prises, coupes serrées, A-roll, scènes calées sur les mots, rendu, audit par un agent indépendant |
| `skills/reel-detourage` | Le détourage de la personne filmée, en vidéo et pour la couverture |
| `skills/reel-publication` | La couverture et les légendes par plateforme |
| `outils/reel.py` | La commande unique que les skills pilotent (`init`, `derush`, `assemble`, `detour`, `rendu`, `audit`, `cover`…) |
| `outils/reelkit/` | La bibliothèque de composition : mises en page, sous-titres karaoké, scènes réutilisables |
| `METHODE.md` | Les règles que les skills appliquent : tournage, écriture, montage, couverture, checklist |
| `exemples/compo.py` | Une composition réelle, pour voir à quoi ressemble une vidéo une fois montée |

Le montage repose sur [HyperFrames](https://github.com/heygen-com/hyperframes), le framework vidéo
open source de HeyGen : chaque Reel est une page HTML animée, rendue en MP4.

## Prérequis

- Un Mac avec puce Apple (la transcription utilise `mlx-whisper`).
- [Claude Code](https://claude.com/claude-code).
- `ffmpeg` (`brew install ffmpeg`), Node.js 18 ou plus (pour `npx hyperframes`).
- Python 3.10 ou plus.

## Installation

```bash
git clone https://github.com/iamachilles/claude-reels.git ~/claude-reels
```

```bash
python3 -m venv ~/.reels-venv && ~/.reels-venv/bin/pip install numpy mlx-whisper pillow
```

```bash
~/claude-reels/outils/installer.sh
```

```bash
mkdir -p ~/.claude/skills && ln -s ~/claude-reels/skills/* ~/.claude/skills/
```

Lance Claude Code depuis un terminal où le Python du venv est actif (`source ~/.reels-venv/bin/activate`),
pour que `reel.py` trouve ses dépendances.

**Optionnel** : la recherche du meilleur sourire pour la couverture et le repérage des regards hors
caméra utilisent MediaPipe 0.10.14, dans un Python à part. Indique-le par
`export REEL_PY_MEDIAPIPE=/chemin/vers/python`.

## Utilisation

Dans Claude Code :

```
/reel une vidéo sur ton sujet
```

Le skill écrit le cadrage et s'arrête pour que tu le valides. Tu tournes, tu déposes tes rushes et
tes enregistrements d'écran dans `~/Downloads`, et il monte. Chaque vidéo vit dans son dossier
`~/video-reel-{slug}/`.

## À savoir

- La charte se règle en tête de `outils/reelkit/compo.py` : couleur d'accent (`REEL_ACCENT`, bleu par
  défaut), fond clair (`REEL_CLAIR`), police (Inter, téléchargée par `installer.sh`). Le reste des
  réglages (pas de musique, sous-titres de trois mots) se change dans `METHODE.md` et les skills.
- Filme avec un micro branché en filaire : en Bluetooth, le son sort en 16 kHz et la voix s'étouffe.
- Une vidéo filmée avec l'app Caméra de l'iPhone est en HDR : la méthode donne la conversion à
  appliquer, sinon l'image sort pâle.
- Rien de magique : c'est toi qui tranches l'accroche, les prises et ce qui part en ligne.
