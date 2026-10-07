# La méthode

Ce que les skills appliquent. Tiré de plusieurs Reels tournés, montés et corrigés à la main, puis
écrits ici pour que Claude les applique d'office. À enrichir à chaque vidéo : un retour qui vaut pour
toutes les vidéos s'écrit ici et dans le skill concerné.

## La règle qui passe avant toutes les autres

Sur Instagram, TikTok et YouTube Shorts, **la vidéo divertit et livre toute sa valeur elle-même**, en
une minute (1:30 au plus). Tension, sensationnel, une histoire. **La ressource offerte en fin de
vidéo n'est qu'un bonus** : le « commente X » est la dernière brique, il ne structure pas la vidéo.

Structure fixe : **accroche, preuve, contenu, appel à l'action**, dans cet ordre.

## Tournage

1. **Les yeux au tiers supérieur du cadre**, jamais au centre : le bas sert aux sous-titres, le haut
   aux éléments graphiques.
2. **Un micro, branché en filaire.** Un micro sans fil passé par le Bluetooth sort en 16 kHz (voix
   étouffée, aigus perdus, aucun traitement ne les rend). Vérifier la fréquence du son de chaque
   rush (`ffprobe ... sample_rate`).
3. **Plusieurs accroches à la suite**, puis le reste d'une traite, deux fois. Chaque accroche donne
   une variante du montage ; on poste les variantes et on garde celle qui gagne.
4. **Plans muets** à la fin : sourire face caméra (couverture), geste vers le haut de l'écran.
5. **Enregistrements d'écran** : gestes lents (au montage on accélère), mode Concentration, aucun nom
   de client ni de tiers lisible.
6. **Vidéo de l'app Caméra de l'iPhone = HDR** (HLG, BT.2020, 10 bits). Passée telle quelle dans
   ffmpeg, elle sort délavée et pâle. La convertir avant tout :
   `zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`
   puis `eq=brightness=0.04:saturation=1.1:gamma=1.05`.

## Écriture

- **L'accroche coûte plus de temps que tout le reste.** Une seule question : qu'est-ce que je promets
  sans donner la réponse ? Ce qui marche : une expérience partagée (« j'ai trouvé un truc qui… »),
  une affirmation forte et contrebalancée, un défi, connecter le spectateur au sujet.
- **Le stop-scroll** est ce qui arrête le pouce avant qu'on ait parlé : un mouvement, un visuel, un
  texte, une couleur. Il s'empile avec l'accroche.
- **Une boucle de curiosité** : ouverte au début, nourrie par miettes, fermée à la fin.
- **Le test du pote** : chaque phrase se dirait exactement comme ça à un ami. Pas de ton de
  présentateur. Les idées se retiennent, jamais les phrases par cœur.
- **Tout ce qui est nommé s'affiche** : une entreprise, son logo ; un chiffre, le chiffre en grand.
- **La preuve** : un fait vérifiable propre au sujet ; le chiffre dit et le chiffre affiché sont
  identiques. Jamais un chiffre qui affirme plus que ce qu'on sait.
- **Le contenu** : la clarté que la ressource apporte, en mots de tous les jours, pas le vocabulaire
  de la ressource.
- **L'appel à l'action** : « Abonne-toi, commente MOT, et je te l'envoie en message. » L'abonnement
  se dit à l'oral (un message d'un compte qu'on ne suit pas tombe dans les demandes).

## Montage

- **La dernière prise propre de chaque phrase**, sauf si une prise antérieure est plus juste. Une
  prise qui affirme plus que ce qu'on sait se laisse de côté, même si c'est la dernière.
- **Coupes sèches** : aucune pause de plus de 0,25 s entre deux phrases, jamais un mot de fin rogné.
  Borner sur l'énergie de la voix, pas sur les horodatages de Whisper, qui étirent le premier mot
  sur le silence d'avant.
- **Relire l'A-roll morceau par morceau** contre le texte attendu : les reprises cachées
  (« la vi… la publicité ») n'apparaissent qu'ainsi.
- **Synchro** : se juge à l'oreille. Avec un micro sans fil, la voix arrive environ 0,16 s après les
  lèvres ; on avance l'image, jamais le son.
- **Son** : voix à -16 LUFS. **Pas de musique par défaut** sous un Reel parlé ; si on en met une,
  une nappe sans percussions, 9 dB sous la voix, et jamais sur un son en 16 kHz.
- **Habillage** : style réseaux sociaux (texte blanc gras sur fond sombre ou l'inverse), le moins de
  texte possible, sous-titres karaoké de trois mots au plus, éléments qui surgissent sur le mot qui
  les nomme, un changement d'image toutes les deux à quatre secondes, zooms légers sur les mots
  forts. Titres en concepts, sans émoji.
- **Trois mises en page** : détourée devant les enregistrements (fond blanc), plein cadre avec
  illustrations, écran coupé (scène en haut, personne en bas, sous-titres sur la jonction).

## Couverture

- Photo plein cadre, visage zoomé et centré, souriant, tirée du rush 4K.
- Le titre seul, court, en capitales, en deux bandeaux au-dessus du visage. Pas de surtitre, pas de
  badge, pas d'encart.
- De grosses icônes d'applis aux coins arrondis autour du visage (API publique de l'App Store).
- Format 1080 × 1920, l'essentiel dans la zone 3:4 centrale (y de 240 à 1680), seule visible dans la
  grille du profil.
- Elle se pose dans Instagram à la publication (« Modifier la couverture », puis « Ajouter depuis
  la pellicule »).

## Légendes

- **Instagram** : l'appel à l'action en première ligne, puis le problème, la valeur en étapes
  numérotées, ce que contient la ressource, quelques hashtags.
- **TikTok** : une phrase avec les mots qu'on taperait dans la recherche, une question.
- **YouTube Shorts** : le titre compte, mots-clés dedans.
- Le même fichier vidéo partout, sans filigrane d'une autre plateforme.

## La checklist avant publication

À passer sur le rendu final, sur un téléphone. Une case rouge est bloquante.

**Image**
- [ ] Les yeux sont sur le tiers supérieur
- [ ] Aucun texte utile dans les réserves d'interface (haut, bas, côtés), vérifié dans le fil réel
- [ ] Aucune apparition de sous-titre ne dépasse 4 mots
- [ ] Image nette, couleurs naturelles (HDR converti)

**Son**
- [ ] Enregistré au micro, en 44,1 kHz ou plus
- [ ] Pas de musique par défaut ; si elle existe, elle ne couvre jamais la voix

**Structure**
- [ ] L'accroche promet sans donner la réponse
- [ ] Un stop-scroll dans la première seconde
- [ ] La boucle ouverte au début est fermée à la fin
- [ ] La surimpression d'intro a disparu après l'intro
- [ ] Chaque entreprise, chiffre ou outil nommé apparaît à l'image

**Voix**
- [ ] La voix varie entre les phrases importantes et les transitions
- [ ] Aucune phrase ne sonne comme une phrase écrite
- [ ] Pas de micro-silence entre deux phrases
