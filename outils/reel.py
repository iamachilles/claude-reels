#!/usr/bin/env python3
"""Commande unique des Reels face cam (skills Claude Code du dépôt claude-reels). Tout est local et gratuit.

Un projet = un dossier ~/video-reel-{slug}/ avec reel.json (état), et selon l'étape :
coupes.json (liste de coupe), fonds.json (enregistrements d'écran), compo.py (scènes), cover.json.

  reel.py init SLUG [RUSH...] [--test] crée le projet (dès le cadrage ; --test : rien sur le Bureau)
  reel.py rushes RUSH [RUSH...]       ajoute les rushes
  reel.py etat [cle=valeur ...]       lit ou règle l'état (mise_en_page, cadrage, sync, duree_max, variante)
  reel.py derush                      contrôle des rushes, prises transcrites, liste de coupe proposée
  reel.py assemble [--variante B]     A-roll serré depuis coupes.json, relecture, mots, voix traitée
  reel.py musique FICHIER [LUFS]      lit musical (seulement sur demande)
  reel.py regards                     instants où la personne quitte la caméra des yeux (diagnostic)
  reel.py detour                      détourage de l'A-roll et suivi de la tête (skill reel-detourage)
  reel.py fonds                       prépare les fonds depuis fonds.json
  reel.py rendu [--at t1,t2]          compose, captures, rendu, export Instagram, aperçu téléphone
  reel.py captures t1,t2,...          captures seules (planche de contrôle)
  reel.py audit                       contrôles automatiques du rendu (audit.md)
  reel.py cover-sourire               les meilleurs sourires face caméra du rush
  reel.py cover-photo T [--rush N]    photo 4K détourée à l'instant T
  reel.py cover-effacer x0,y0,x1,y1,mode   efface un objet du décor collé à la silhouette
  reel.py icone NOM [RECHERCHE]       icône d'appli (App Store) pour la couverture
  reel.py cover                       couverture depuis cover.json, vues plein écran et grille
À lancer depuis le dossier du projet. La méthode : METHODE.md à la racine du dépôt.
"""
import sys, os, json, subprocess, re, glob, shutil, difflib, unicodedata
import numpy as np

OUTILS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUTILS)
from reelkit.compo import ACCENT
PY_MP = os.environ.get("REEL_PY_MEDIAPIPE", sys.executable)   # Python avec MediaPipe 0.10.14 (voir README)
WHISPER = "mlx-community/whisper-large-v3-turbo"
FPS, SR = 24, 48000
# Chaîne de voix : passe-haut, creux 250 Hz, présence, compression, -16 LUFS
VOIX = ("highpass=f=85,equalizer=f=250:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=3.5,equalizer=f=6500:t=q:w=1:g=2,"
        "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=9")


def sh(*a, **k):
    return subprocess.run(list(a), check=k.pop("check", True), capture_output=k.pop("cap", False), text=k.pop("text", False), **k)


def ff(*a):
    sh("ffmpeg", "-v", "error", "-y", *a)


def probe(f, entries):
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "json", f], capture_output=True, text=True).stdout


def etat():
    return json.load(open("reel.json"))


def sauve(e):
    json.dump(e, open("reel.json", "w"), ensure_ascii=False, indent=1)


def norm(s):
    return re.sub(r"[^a-z0-9' ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def transcrit(wav, mots=True):
    import mlx_whisper
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=WHISPER, language="fr", word_timestamps=mots, condition_on_previous_text=False)
    return r


def energie(wav):
    x = np.frombuffer(sh("ffmpeg", "-loglevel", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-", cap=True).stdout,
                      dtype=np.int16).astype(float)
    m = len(x) // 160
    return 20 * np.log10(np.sqrt((x[:m * 160].reshape(m, 160) ** 2).mean(1)) + 1)   # tranches de 10 ms


# ---------------------------------------------------------------- init
def cmd_init(slug, *args):
    """Crée le projet dès le cadrage (les rushes s'ajoutent ensuite par `rushes`). --test : projet
    de test, rien n'est copié sur le Bureau."""
    test = "--test" in args
    rushes = [x for x in args if x != "--test"]
    d = os.path.expanduser(f"~/video-reel-{slug}")
    os.makedirs(d, exist_ok=True); os.chdir(d)
    for s in ("public/bg", "public/assets", "renders", "src", "cover"): os.makedirs(s, exist_ok=True)
    e = dict(slug=slug, rushes=[os.path.abspath(os.path.expanduser(x)) for x in rushes], sync=0.16,
             etape="tournage" if rushes else "cadrage", version=0, mise_en_page=None, cadrage=None, variante="A",
             duree_max=62, bureau=not test)
    sauve(e)
    print("projet", d)


def cmd_rushes(*rushes):
    """Ajoute les rushes au projet (l'ordre fixe leur numéro dans coupes.json)."""
    e = etat(); e["rushes"] += [os.path.abspath(os.path.expanduser(x)) for x in rushes]; e["etape"] = "tournage"; sauve(e)
    for i, x in enumerate(e["rushes"]): print(f"rush{i}", x)


def cmd_etat(*paires):
    """Lit ou règle l'état : reel.py etat mise_en_page=detoure cadrage=chemin sync=0.12 duree_max=90."""
    e = etat()
    for p in paires:
        k, v = p.split("=", 1)
        try: v = json.loads(v)
        except Exception: pass
        e[k] = v
    sauve(e); print(json.dumps(e, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- derush
def cmd_derush():
    e = etat(); rapport, prises = [], []
    for ri, r in enumerate(e["rushes"]):
        info = json.loads(probe(r, "stream=codec_type,sample_rate,width,height:format=duration:format_tags"))
        sr = [int(s["sample_rate"]) for s in info["streams"] if s["codec_type"] == "audio"]
        tags = info["format"].get("tags", {})
        dur = float(info["format"]["duration"])
        alerte = []
        if sr and sr[0] < 44100:
            alerte.append(f"son en {sr[0]} Hz : qualité téléphone, aigus coupés au-dessus de {sr[0]//2} Hz (micro passé par le Bluetooth ?). "
                          "Aucun traitement ne les rend.")
        rapport.append(dict(rush=ri, fichier=r, duree=round(dur, 1), son_hz=sr[0] if sr else None,
                            camera=tags.get("com.apple.quicktime.model"), logiciel=tags.get("com.apple.quicktime.software"), alertes=alerte))
        wav = f"src/rush{ri}.wav"
        ff("-i", r, "-vn", "-ac", "1", "-ar", str(SR), wav)
        log = sh("ffmpeg", "-i", wav, "-af", "silencedetect=noise=-38dB:d=0.45", "-f", "null", "-", cap=True, text=True, check=False).stderr
        ss = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
        se = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
        isl = []
        for a in [0.0] + se:
            b = min([s for s in ss + [dur] if s > a], default=dur)
            if b - a > 0.4: isl.append((round(a, 2), round(b, 2)))
        for a, b in sorted(set(isl)):
            ff("-ss", str(max(0, a - 0.1)), "-t", str(b - a + 0.2), "-i", wav, "-ar", "16000", "src/isl.wav")
            res = transcrit("src/isl.wav")
            mots = [dict(t=w["word"].strip(), s=round(max(0, a - 0.1) + w["start"], 2), e=round(max(0, a - 0.1) + w["end"], 2))
                    for sg in res["segments"] for w in sg["words"]]
            txt = res["text"].strip()
            # hallucinations connues de Whisper sur un silence ou un bruit
            if not mots or len(norm(txt)) < 3 or norm(txt).strip() in ("merci", "sous-titrage st 501", "...") or "sous-titrage" in norm(txt): continue
            prises.append(dict(rush=ri, a=a, b=b, texte=txt, mots=mots))
            print(f"rush{ri} {a:7.2f}-{b:7.2f} {txt}", flush=True)
    # regroupe les prises d'une même phrase (textes proches), propose la dernière prise de chaque groupe
    groupes = []
    for p in prises:
        n = norm(p["texte"])
        # rattache aux deux dernières phrases (un faux départ peut s'intercaler entre deux prises)
        sc = [(max(difflib.SequenceMatcher(None, n, norm(q["texte"])).ratio() for q in g[-3:]), gi)
              for gi, g in enumerate(groupes[-2:], start=max(0, len(groupes) - 2))]
        best = max(sc, default=(0, None))
        if best[0] > 0.55:
            groupes[best[1]].append(p)
            if best[1] < len(groupes) - 1:  # le faux départ intercalé rejoint la même phrase
                g = groupes.pop(); groupes[best[1]][-1:-1] = g
        else:
            groupes.append([p])
    coupes = []
    for gi, g in enumerate(groupes):
        p = g[-1]
        idx = prises.index(p)
        prec = prises[idx - 1]["b"] if idx and prises[idx - 1]["rush"] == p["rush"] else 0
        suiv = prises[idx + 1]["a"] if idx + 1 < len(prises) and prises[idx + 1]["rush"] == p["rush"] else p["b"] + 1
        coupes.append(dict(bloc=f"p{gi:02d}", rush=p["rush"], s=p["mots"][0]["s"], t=p["mots"][-1]["e"],
                           lo=round(max(prec + 0.02, p["mots"][0]["s"] - 0.4), 2), hi=round(min(suiv - 0.02, p["mots"][-1]["e"] + 0.5), 2),
                           texte=p["texte"], prises=len(g)))
    json.dump(dict(rapport=rapport, prises=prises), open("prises.json", "w"), ensure_ascii=False, indent=1)
    json.dump(coupes, open("coupes_proposees.json", "w"), ensure_ascii=False, indent=1)
    with open("prises.md", "w") as f:
        f.write("# Rushes\n\n")
        for r in rapport:
            f.write(f"- rush{r['rush']} : {r['fichier']} ({r['duree']} s, son {r['son_hz']} Hz, caméra {r['camera']})\n")
            for a in r["alertes"]: f.write(f"  - ALERTE : {a}\n")
        f.write("\n# Prises, regroupées par phrase (la dernière est proposée)\n\n")
        for gi, g in enumerate(groupes):
            f.write(f"## p{gi:02d} ({len(g)} prise{'s' if len(g) > 1 else ''})\n")
            for p in g: f.write(f"- rush{p['rush']} {p['a']:.2f}-{p['b']:.2f} : {p['texte']}\n")
            f.write("\n")
    e["etape"] = "derush"; sauve(e)
    for r in rapport:
        for a in r["alertes"]: print("ALERTE rush", r["rush"], ":", a)
    print(len(prises), "prises,", len(groupes), "phrases proposées : prises.md, coupes_proposees.json")


# ---------------------------------------------------------------- assemble
def cmd_assemble():
    """Coupes serrées : bornes extérieures sur la voix franche (bruit de fond
    + 22 dB à l'attaque, + 19 dB en fin), aucune marge après le dernier son, silences internes coupés
    dès 0,13 s. Image avancée de `sync` s (micro sans fil). Audio collé en WAV, encodé une fois."""
    e = etat(); SYNC = e.get("sync", 0.16)
    # variantes d'accroche (règle 19) : un bloc avec "variante": "B" n'entre que dans l'A-roll B
    var = sys.argv[sys.argv.index("--variante") + 1] if "--variante" in sys.argv else e.get("variante", "A")
    P = [c for c in json.load(open("coupes.json")) if c.get("variante", var) == var]
    e["variante"] = var
    EN = {}
    pieces = []
    for c in P:
        r = c["rush"]
        if r not in EN: EN[r] = energie(f"src/rush{r}.wav")
        en = EN[r]; thr = np.percentile(en, 10) + 14
        s, t, lo, hi = c["s"], c["t"], c["lo"], c["hi"]
        a = int(max(lo, s - 0.25) * 100); b = int(min(hi, t + 0.45) * 100)
        von = np.where(en[a:b] > thr + 8)[0]; voff = np.where(en[a:b] > thr + 5)[0]
        if not len(von): von = np.where(en[a:b] > thr)[0]
        if not len(voff): voff = von
        st = max(lo, (a + von[0]) / 100 - 0.03); fin = min(hi, (a + voff[-1]) / 100 + 0.06)
        i0, i1 = int(st * 100), int(fin * 100); act = en[i0:i1] > thr; runs = []; cur = None
        for k, v in enumerate(act):
            if v:
                if cur is None: cur = [k, k]
                elif k - cur[1] > 13: runs.append(cur); cur = [k, k]
                else: cur[1] = k
        if cur: runs.append(cur)
        for r0, r1 in runs:
            ra = max(lo, (i0 + r0) / 100 - (0.0 if r0 == runs[0][0] else 0.06))
            rb = min(hi, (i0 + r1) / 100 + (0.0 if r1 == runs[-1][1] else 0.05))
            if rb - ra > 0.12: pieces.append(dict(bloc=c["bloc"], rush=r, a_in=round(ra, 3), a_out=round(rb, 3)))
    d = "src/pieces"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    vl = open(f"{d}/v.txt", "w"); al = open(f"{d}/a.txt", "w"); T = 0; tl = []
    for k, p in enumerate(pieces):
        src = e["rushes"][p["rush"]]
        n = max(1, round((p["a_out"] - p["a_in"]) * FPS)); dur = n / FPS
        ff("-ss", f"{p['a_in']-SYNC:.3f}", "-i", src, "-frames:v", str(n), "-an", "-vf", "scale=1080:1920:flags=lanczos,fps=24,format=yuv420p",
           "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-g", "24", f"{d}/v{k:02d}.mp4")
        ff("-ss", f"{p['a_in']:.4f}", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), "-af",
           f"aresample={SR},atrim=end_sample={round(dur*SR)},apad=whole_len={round(dur*SR)},afade=t=in:d=0.015,afade=t=out:st={dur-0.025:.4f}:d=0.025",
           "-c:a", "pcm_s16le", f"{d}/a{k:02d}.wav")
        vl.write(f"file 'v{k:02d}.mp4'\n"); al.write(f"file 'a{k:02d}.wav'\n")
        tl.append(dict(bloc=p["bloc"], start=round(T, 4), end=round(T + dur, 4), a_in=p["a_in"], rush=p["rush"])); T += dur
    vl.close(); al.close()
    ff("-f", "concat", "-safe", "0", "-i", f"{d}/v.txt", "-c", "copy", f"{d}/v.mp4")
    ff("-f", "concat", "-safe", "0", "-i", f"{d}/a.txt", "-c", "copy", f"{d}/a.wav")
    ff("-i", f"{d}/v.mp4", "-i", f"{d}/a.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "aroll.mp4")
    json.dump(tl, open("timeline.json", "w"), indent=1)
    dur = float(json.loads(probe("aroll.mp4", "format=duration"))["format"]["duration"])
    open("dur.txt", "w").write(f"{dur:.3f}")
    # voix traitée pour le rendu
    ff("-i", "aroll.mp4", "-vn", "-af", VOIX, "-ar", str(SR), "src/voix.wav")
    ff("-i", "aroll.mp4", "-i", "src/voix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "public/input-video.mp4")
    print(len(pieces), "morceaux, A-roll", round(dur, 2), "s, variante", var)
    alertes = relire(P, tl)
    e["etape"] = "assemble"; sauve(e)
    if alertes: sys.exit("relecture en alerte : corriger coupes.json avant de continuer")


def relire(P, tl):
    """Retranscrit l'A-roll bloc par bloc (au-delà d'une minute, la transcription d'un bloc entier perd
    ses horodatages), compare au texte attendu, repère les mots manquants et les redites, et écrit
    words.json (mots de l'A-roll, horodatés)."""
    blocs = []
    for p in tl:
        if blocs and blocs[-1]["bloc"] == p["bloc"]: blocs[-1]["end"] = p["end"]
        else: blocs.append(dict(bloc=p["bloc"], start=p["start"], end=p["end"]))
    attendu = {c["bloc"]: c.get("texte", "") for c in P}
    out, lignes, alertes = [], [], []
    for b in blocs:
        ff("-ss", str(b["start"]), "-to", str(b["end"]), "-i", "aroll.mp4", "-vn", "-ac", "1", "-ar", "16000", "src/r.wav")
        r = transcrit("src/r.wav")
        txt = r["text"].strip()
        for sg in r["segments"]:
            for w in sg["words"]:
                out.append(dict(t=w["word"].strip(), s=round(b["start"] + w["start"], 3), e=round(min(b["end"], b["start"] + w["end"]), 3)))
        mots_de = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
        a_mots, l_mots = mots_de(attendu.get(b["bloc"], "")), mots_de(txt)
        manque = [m for m in a_mots if m not in l_mots and len(m) > 3]
        # redite : une suite de 3 mots ou plus dite deux fois de suite (« si ça t'intéresse, si ça t'intéresse »)
        redite = None
        for n in range(6, 2, -1):
            for i in range(len(l_mots) - 2 * n + 1):
                if l_mots[i:i + n] == l_mots[i + n:i + 2 * n]: redite = " ".join(l_mots[i:i + n]); break
            if redite: break
        etat_l = "OK"
        if manque: etat_l = "MANQUE " + ", ".join(manque); alertes.append((b["bloc"], etat_l))
        if redite: etat_l += f" ; REDITE « {redite} »"; alertes.append((b["bloc"], f"redite « {redite} »"))
        lignes.append(f"{b['start']:6.2f}-{b['end']:6.2f} {b['bloc']:6s} {etat_l:10s} {txt}")
        print(lignes[-1], flush=True)
    json.dump(out, open("words.json", "w"), ensure_ascii=False, indent=0)
    open("relecture.md", "w").write("# Relecture de l'A-roll\n\n```\n" + "\n".join(lignes) + "\n```\n")
    if alertes: print("ALERTES relecture :", alertes)
    return alertes


# ---------------------------------------------------------------- detour
def cmd_detour(src="aroll.mp4", sortie="public/me.webm"):
    sh("npx", "hyperframes", "remove-background", src, "-o", sortie, cap=True)
    headtrack(sortie)
    e = etat(); e["etape"] = "detour"; sauve(e)
    print("détourage :", sortie, "; suivi de la tête : headtrack.json")


def headtrack(webm, fps=8, W=135, H=240):
    """Haut de la tête image par image (8 i/s), lissé, mains levées ignorées (percentile 80)."""
    raw = sh("ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", webm, "-vf", f"fps={fps},alphaextract,scale={W}:{H}",
             "-f", "rawvideo", "-pix_fmt", "gray", "-", cap=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
    tops = []
    for f in a:
        rows = np.where((f[:, W // 3:2 * W // 3] > 128).sum(1) > 4)[0]
        tops.append(rows[0] * 1920 / H if len(rows) else 1920)
    tops = np.array(tops); n = len(tops); t = np.arange(n) / fps
    tl = json.load(open("timeline.json")); seg = np.zeros(n, int)
    for k, p in enumerate(tl): seg[(t >= p["start"]) & (t < p["end"])] = k
    sm = np.array([np.percentile(tops[[j for j in range(max(0, i - 4), min(n, i + 5)) if seg[j] == seg[i]]], 80) for i in range(n)])
    sm2 = np.array([sm[[j for j in range(max(0, i - 3), min(n, i + 4)) if seg[j] == seg[i]]].mean() for i in range(n)])
    json.dump(dict(fps=fps, top=[round(float(x), 1) for x in sm2], seg=seg.tolist()), open("headtrack.json", "w"))


# ---------------------------------------------------------------- fonds
def cmd_fonds():
    """fonds.json : [{nom, src, debut, duree, vitesse, cadrage}] ; cadrage : "centre" (9:16 au centre),
    "x:N" (9:16 depuis x=N), "colonne:x0:x1" (colonne de texte mise à la largeur, fond complété),
    "vertical" (déjà vertical, mis à la largeur), "largeur" (mis à la largeur, pour une carte)."""
    for f in json.load(open("fonds.json")):
        w, h = [json.loads(probe(f["src"], "stream=width,height"))["streams"][0][k] for k in ("width", "height")]
        cw = int(h * 9 / 16) // 2 * 2
        cad = f.get("cadrage", "centre")
        if cad == "centre": vf = f"crop={cw}:{h}:{(w-cw)//2}:0,scale=1080:1920"
        elif cad.startswith("x:"): vf = f"crop={cw}:{h}:{int(cad[2:])}:0,scale=1080:1920"
        elif cad.startswith("colonne:"):
            x0, x1 = map(int, cad.split(":")[1:]); vf = f"crop={x1-x0}:{h}:{x0}:0,scale=1080:-2,pad=1080:1920:0:60:0x1e1e1e"
        elif cad == "vertical": vf = "scale=1080:-2,crop=1080:1920:0:0"
        else: vf = "scale=1080:-2"
        v = f.get("vitesse", 1)
        pre = [] if not f.get("inverse") else []
        args = ["-ss", str(f.get("debut", 0))] + (["-t", str(f["duree"])] if f.get("duree") else []) + ["-i", f["src"]]
        filt = (f"setpts=PTS/{v}," if v != 1 else "") + f"fps=24,{vf}" + (",reverse" if f.get("inverse") else "")
        ff(*args, "-vf", filt, "-an", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", f"public/bg/{f['nom']}.mp4")
        d = json.loads(probe(f"public/bg/{f['nom']}.mp4", "format=duration"))["format"]["duration"]
        print(f["nom"], round(float(d), 2), "s")
    e = etat(); e["etape"] = "fonds"; sauve(e)


# ---------------------------------------------------------------- musique (seulement sur demande)
def cmd_musique(fichier, lufs="-25"):
    """Prépare un lit musical à la longueur de l'A-roll, à `lufs` (défaut -25, soit environ 9 dB sous
    la voix comme Rob Prod), creux de 4 dB à 2,5 kHz, fondus. Par défaut un Reel n'a pas de musique :
    ne s'emploie que sur demande, et jamais sur un son de rush en 16 kHz. Dans compo.py :
    c.musique = "audio/bed.mp3"."""
    D = float(open("dur.txt").read())
    o = sh("ffmpeg", "-nostats", "-i", fichier, "-af", "ebur128", "-f", "null", "-", cap=True, text=True, check=False).stderr
    I = float([x for x in o.splitlines() if " I:" in x][-1].split()[1])
    os.makedirs("public/audio", exist_ok=True)
    ff("-stream_loop", "-1", "-i", fichier, "-t", f"{D:.3f}", "-af",
       f"volume={float(lufs)-I:.1f}dB,equalizer=f=2500:t=q:w=1.5:g=-4,afade=t=in:d=0.4,afade=t=out:st={D-1.6:.3f}:d=1.6",
       "-c:a", "libmp3lame", "-b:a", "192k", "public/audio/bed.mp3")
    print("public/audio/bed.mp3 à", lufs, "LUFS ; dans compo.py : c.musique = \"audio/bed.mp3\"")


# ---------------------------------------------------------------- rendu
def captures(temps, dossier="public"):
    shutil.rmtree(f"{dossier}/snapshots", ignore_errors=True)
    sh("npx", "hyperframes", "snapshot", "--at", ",".join(f"{t:g}" for t in temps), "--no-end", "--timeout", "15000",
       cwd=dossier, cap=True, check=False)
    return sorted(glob.glob(f"{dossier}/snapshots/contact-sheet*.jpg"))


def cmd_captures(liste):
    print("\n".join(captures([float(x) for x in liste.split(",")])))


def cmd_rendu(*args):
    e = etat()
    sh(sys.executable, "compo.py")
    lint = sh("npx", "hyperframes", "lint", cwd="public", cap=True, text=True, check=False).stdout
    err = re.search(r"(\d+) error", lint)
    if err and int(err.group(1)): print(lint); sys.exit("lint en erreur")
    D = float(open("dur.txt").read())
    temps = [float(x) for x in args[1].split(",")] if len(args) > 1 and args[0] == "--at" else list(np.arange(0.5, D, 4.0))
    feuilles = captures(temps)
    e["version"] += 1; v = e["version"]; nom = f"{e['slug']}-v{v}" + ("" if e.get("variante", "A") == "A" else e["variante"])
    sh("npx", "hyperframes", "render", "--fps", "24", "-o", f"../renders/{nom}.mp4", cwd="public", cap=True)
    ff("-i", f"renders/{nom}.mp4", "-c:v", "libx264", "-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "192k", f"renders/{nom}-insta.mp4")
    ff("-i", f"renders/{nom}-insta.mp4", "-vf", "scale=540:960", "-c:v", "libx264", "-crf", "28", "-preset", "fast", "-c:a", "aac",
       "-b:a", "128k", f"renders/{nom}-apercu-telephone.mp4")
    if e.get("bureau", True):  # un projet de test met "bureau": false dans reel.json
        for s in ("-insta", "-apercu-telephone"):
            shutil.copy(f"renders/{nom}{s}.mp4", os.path.expanduser(f"~/Desktop/reel-{nom}{s}.mp4"))
    e["etape"] = "rendu"; e["dernier_rendu"] = f"renders/{nom}-insta.mp4"; sauve(e)
    print("rendu", e["dernier_rendu"], "; captures :", " ".join(feuilles))


# ---------------------------------------------------------------- audit
def cmd_audit(fichier=None):
    """Contrôles mesurables. Ce qui ne se juge qu'à l'oreille ou sur téléphone reste « à vérifier à la
    main ». L'agent d'audit indépendant lance cette commande puis regarde lui-même les captures."""
    e = etat(); f = fichier or e["dernier_rendu"]
    M = json.load(open("compo_meta.json")); res = []
    def ligne(statut, quoi, detail=""): res.append((statut, quoi, detail))
    D = float(json.loads(probe(f, "format=duration"))["format"]["duration"])
    dm = e.get("duree_max", 62)
    ligne("OK" if D <= dm else ("A VOIR" if D <= max(90, dm) else "ROUGE"), f"Durée ({dm:g} s visées, 1:30 au plus)", f"{D:.1f} s")
    o = sh("ffmpeg", "-nostats", "-i", f, "-af", "ebur128", "-f", "null", "-", cap=True, text=True, check=False).stderr
    I = float([x for x in o.splitlines() if " I:" in x][-1].split()[1])
    ligne("OK" if abs(I + 16) <= 1.2 else "ROUGE", "Voix à -16 LUFS", f"{I} LUFS")
    log = sh("ffmpeg", "-i", f, "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-", cap=True, text=True, check=False).stderr
    sil = [(float(a), float(b)) for a, b in zip(re.findall(r"silence_start: ([0-9.]+)", log), re.findall(r"silence_end: ([0-9.]+)", log))]
    sil = [(a, b) for a, b in sil if a > 0.3 and b < D - 0.3]
    ligne("OK" if not sil else ("A VOIR" if all(b - a < 0.45 for a, b in sil) else "ROUGE"), "Aucun blanc de plus de 0,25 s entre deux phrases",
          ", ".join(f"{a:.1f}s ({b-a:.2f})" for a, b in sil) or "aucun")
    pr = json.load(open("prises.json"))["rapport"] if os.path.exists("prises.json") else []
    bas = [r for r in pr if r["son_hz"] and r["son_hz"] < 44100]
    ligne("A VOIR" if bas else "OK", "Son enregistré en 44,1 kHz ou plus", ", ".join(f"rush{r['rush']} {r['son_hz']} Hz" for r in bas) or "oui")
    html = open("public/index.html").read()
    caps = re.findall(r'<span class="in" id="cap\d+">(.*?)</span></div>', html)
    trop = [re.sub("<[^>]+>", "", c) for c in caps if len(re.findall(r"<span", c)) > 3]
    ligne("OK" if not trop else "ROUGE", "Sous-titres de 3 mots au plus", "; ".join(trop) or f"{len(caps)} groupes")
    textes = " | ".join(t["texte"] for t in M["textes"])
    titres = " | ".join(t["texte"] for t in M["textes"] if t.get("titre", True))
    emo = re.findall("[\U0001F300-\U0001FAFF☀-➿]", textes)
    ligne("OK" if not emo else "ROUGE", "Aucun émoji dans les titres", "".join(emo) or "")
    tir = [c for c in (chr(0x2013), chr(0x2014)) if c in textes or any(c in x for x in caps)]
    ligne("OK" if not tir else "ROUGE", "Aucun tiret cadratin ni demi-cadratin à l'écran")
    # noms à ne jamais afficher (clients, tiers) : REEL_NOMS_INTERDITS="nom1,nom2"
    interdits = [n.strip().lower() for n in os.environ.get("REEL_NOMS_INTERDITS", "").split(",") if n.strip()]
    ban = [m for m in ["ce n'est pas", "c'est pas"] + interdits if m in textes.lower()]
    ligne("OK" if not ban else "ROUGE", "Ni formule bannie ni nom interdit à l'écran", ", ".join(ban))
    phrases = [t["texte"] for t in M["textes"] if t.get("titre", True) and len(t["texte"].split()) >= 5 and re.search(r"\b(je|tu|il|elle|on|nous|vous)\b", t["texte"].lower())]
    ligne("OK" if not phrases else "A VOIR", "Titres en concepts, pas en phrases", "; ".join(phrases))
    aud = re.findall(r"<audio id=\"([\w-]+)", html)
    extra = [a for a in aud if a != "source-audio"]
    ligne("ROUGE" if (extra and bas) else ("OK" if not extra else "A VOIR"), "Ni musique ni bruitages (sauf demande explicite, et jamais sur un son en 16 kHz)",
          ", ".join(extra) or "voix seule")
    if M["mise_en_page"] == "detoure" and M["tete"]:
        trou = [t for t in M["tete"] if t["y"] < 0]
        ligne("OK" if not trou else "ROUGE", "Pas de bande vide sous les pieds (hauteurs saisies, à confirmer sur les captures)", f"{len(trou)} instants" if trou else "")
        conflits = []
        for z in M["zones"]:
            for t in M["tete"]:
                if z["start"] <= t["t"] < z["end"] and t["haut"] < z["bas"] - 30:
                    conflits.append(f"{z['scene']} à {t['t']:.1f} s (tête {t['haut']:.0f}, scène jusqu'à {z['bas']})"); break
        ligne("OK" if not conflits else "A VOIR", "La tête ne passe pas sous un titre ou une carte du haut", "; ".join(conflits))
    humain = ["Synchro des lèvres, à l'oreille", "Prosodie et ton de café (test du pote)", "Accroche : promet sans donner la réponse, divertit",
              "La valeur est livrée dans la vidéo, la ressource n'est qu'un bonus", "Réserves d'interface 9:16 vérifiées sur téléphone, dans le fil",
              "Aucun nom de client ni de prospect lisible dans les enregistrements d'écran"]
    with open("audit.md", "w") as fo:
        fo.write(f"# Audit automatique de {f}\n\n| Statut | Contrôle | Détail |\n|---|---|---|\n")
        for s, q, d in res: fo.write(f"| {s} | {q} | {d} |\n")
        fo.write("\n## À vérifier à la main\n\n" + "\n".join(f"- [ ] {h}" for h in humain) + "\n")
    for s, q, d in res: print(f"{s:7s} {q}  {d}")
    print("audit.md écrit")


# ---------------------------------------------------------------- couverture
def cmd_cover_sourire(rush="0"):
    e = etat(); r = e["rushes"][int(rush)]
    ff("-i", r, "-vf", "fps=4,scale=540:960", "-an", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "cover/rush4.mp4")
    sh(PY_MP, os.path.join(OUTILS, "smile.py"), cwd="cover", cap=True, check=False)
    best = json.load(open("cover/meilleurs.json"))
    for k, t in enumerate(best[:8]):
        ff("-ss", str(t), "-i", "cover/rush4.mp4", "-frames:v", "1", "-vf", "crop=300:340:120:40,scale=200:-1", f"cover/s{k}.jpg")
    ins = sum((["-i", f"cover/s{k}.jpg"] for k in range(min(8, len(best)))), [])
    ff(*ins, "-filter_complex", f"hstack=inputs={min(8, len(best))}", "cover/sourires.jpg")
    print("instants :", best[:8], "; planche cover/sourires.jpg (dans l'ordre)")


def cmd_cover_photo(t, *args):
    e = etat(); rush = e["rushes"][int(args[1]) if len(args) > 1 and args[0] == "--rush" else 0]
    ff("-ss", str(t), "-i", rush, "-frames:v", "1", "cover/photo.png")
    ff("-loop", "1", "-i", "cover/photo.png", "-t", "0.25", "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "cover/photo.mp4")
    sh("npx", "hyperframes", "remove-background", "cover/photo.mp4", "-o", "cover/photo.webm", cap=True)
    ff("-c:v", "libvpx-vp9", "-i", "cover/photo.webm", "-frames:v", "1", "cover/photo_detouree.png")
    ff("-i", "cover/photo_detouree.png", "-f", "lavfi", "-i", "color=c=0x00B140:s=2160x3840", "-filter_complex", "[1][0]overlay,scale=540:-1",
       "-frames:v", "1", "-update", "1", "cover/controle.jpg")
    print("cover/photo_detouree.png ; contrôle sur fond vert : cover/controle.jpg (vérifier les objets du décor restés collés)")


def cmd_cover_effacer(*zones):
    """Efface de la photo détourée un objet du décor resté collé à la silhouette. Chaque zone :
    x0,y0,x1,y1,mode (pixels de la photo 4K) ; mode : tout (zone entière), sombre (pixels noirs,
    une lampe), gris (ni peau ni vêtement : ni rouge ni bleu dominant). Vérifier ensuite cover/controle.jpg."""
    f = "cover/photo_detouree.png"
    w, h = [json.loads(probe(f, "stream=width,height"))["streams"][0][k] for k in ("width", "height")]
    a = np.frombuffer(sh("ffmpeg", "-v", "error", "-i", f, "-f", "rawvideo", "-pix_fmt", "rgba", "-", cap=True).stdout, np.uint8).reshape(h, w, 4).copy()
    R, G, B = (a[..., i].astype(int) for i in range(3)); V = np.maximum(np.maximum(R, G), B)
    for z in zones:
        x0, y0, x1, y1, mode = z.split(",")
        x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
        m = np.zeros((h, w), bool); m[y0:y1, x0:x1] = True
        if mode == "sombre": m &= V < 60
        elif mode == "gris": m &= ((B - R) < 25) & ((R - B) < 35)
        a[..., 3][m] = 0
    sh("ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-i", "-", f, input=a.tobytes())
    ff("-i", f, "-f", "lavfi", "-i", f"color=c=0x00B140:s={w}x{h}", "-filter_complex", "[1][0]overlay,scale=540:-1", "-frames:v", "1",
       "-update", "1", "cover/controle.jpg")
    print("zones effacées ; contrôle : cover/controle.jpg")


def cmd_cover():
    """cover.json : {titre: [ligne noire, ligne d'accent], photo: png détourée, fond: image ou null,
    gauche/droite: noms d'icônes (cover/icons/{nom}.png), x, y, largeur: placement de la photo}."""
    c = json.load(open("cover.json"))
    os.makedirs("cover/fonts", exist_ok=True); os.makedirs("cover/vendor", exist_ok=True)
    shutil.copy(os.path.join(OUTILS, "reelkit/static/police.woff2"), "cover/fonts/police.woff2")
    shutil.copy(os.path.join(OUTILS, "reelkit/static/gsap.min.js"), "cover/vendor/gsap.min.js")
    ic = ""
    for cote, x0 in (("gauche", 30), ("droite", 894)):
        for k, n in enumerate(c.get(cote, [])):
            rot = [-8, 6, -5][k % 3] * (1 if cote == "gauche" else -1)
            ic += (f'<div class="icon" style="left:{x0 + (26 if k == 1 else 0) * (1 if cote == "gauche" else -1)}px;top:{700 + k * 290 - (40 if cote == "droite" else 0)}px;'
                   f'transform:rotate({rot}deg)"><img src="icons/{n}.png"></div>')
    fond = f'<img class="graph" src="{c["fond"]}">' if c.get("fond") else ""
    html = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
@font-face{{font-family:"Reel";src:url("fonts/police.woff2") format("woff2");font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}} html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#fff;font-family:"Reel",sans-serif}}
#stage{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f6f6f4}}
.graph{{position:absolute;left:-200px;top:-260px;width:1480px;height:2632px;object-fit:cover;{c.get("fond_filtre", "filter:invert(1) hue-rotate(180deg) contrast(.9);opacity:.85")}}}
.face{{position:absolute;left:{c.get("x", -880)}px;top:{c.get("y", 380)}px;width:{c.get("largeur", 2160)}px;filter:drop-shadow(0 30px 60px rgba(0,0,0,.25))}}
.top{{position:absolute;left:0;top:250px;width:1080px;text-align:center;z-index:5}}
.t1,.t2{{display:inline-block;font-size:96px;font-weight:900;line-height:1;letter-spacing:-3px;padding:16px 30px 20px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.22);color:#fff}}
.t1{{background:#1A1A1A}} .t2{{margin-top:14px;background:{ACCENT}}}
.icon{{position:absolute;width:156px;height:156px;border-radius:36px;overflow:hidden;z-index:4;box-shadow:0 10px 0 rgba(0,0,0,.12),0 22px 44px rgba(0,0,0,.28)}}
.icon img{{width:100%;height:100%;display:block}}
</style></head><body>
<div id="stage" data-composition-id="cover" data-start="0" data-duration="1" data-fps="24" data-width="1080" data-height="1920">
{fond}<img class="face" src="{c["photo"]}">
<div class="top"><div class="t1">{c["titre"][0]}</div><br><div class="t2">{c["titre"][1]}</div></div>
{ic}
<script src="vendor/gsap.min.js"></script>
<script>(function(){{const tl=window.gsap.timeline({{paused:true}});tl.set({{}},{{}},1);window.__timelines=window.__timelines||{{}};window.__timelines["cover"]=tl;}})();</script>
</div></body></html>'''
    open("cover/index.html", "w").write(html)
    shutil.rmtree("cover/snapshots", ignore_errors=True)
    sh("npx", "hyperframes", "snapshot", "--at", "0.5", "--no-end", "--timeout", "15000", cwd="cover", cap=True, check=False)
    e = etat(); sortie = f"renders/couverture-{e['slug']}.png"
    shutil.copy("cover/snapshots/frame-00-at-0.5s.png", sortie)
    ff("-i", sortie, "-vf", "scale=540:-1", "cover/vue_pleine.jpg")
    ff("-i", sortie, "-vf", "crop=1080:1440:0:240,scale=405:-1", "cover/vue_grille.jpg")
    if e.get("bureau", True): shutil.copy(sortie, os.path.expanduser(f"~/Desktop/couverture-{e['slug']}.png"))
    print(sortie, "; vues : cover/vue_pleine.jpg, cover/vue_grille.jpg (zone 3:4 de la grille du profil)")


def cmd_regards():
    """Diagnostic : instants où la personne quitte la caméra des yeux (gaze.py, MediaPipe). Sert à choisir
    d'autres prises ou des bornes plus sèches ; masquer la personne sur ces instants est déconseillé."""
    ff("-i", "aroll.mp4", "-vf", "scale=540:960", "-an", "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "low.mp4")
    sh(PY_MP, os.path.join(OUTILS, "gaze.py"), cap=True, check=False)
    print(open("gaze.json").read()[:200] if os.path.exists("gaze.json") else "gaze.json absent")


def cmd_icone(nom, *recherche):
    import urllib.request, urllib.parse
    q = " ".join(recherche) or nom
    u = "https://itunes.apple.com/search?" + urllib.parse.urlencode({"term": q, "entity": "software", "limit": 3, "country": "fr"})
    r = json.load(urllib.request.urlopen(u, timeout=30))["results"]
    print("trouvé :", r[0]["trackName"], "/", r[0]["sellerName"])
    os.makedirs("cover/icons", exist_ok=True)
    urllib.request.urlretrieve(r[0]["artworkUrl512"].replace("512x512bb", "1024x1024bb"), f"cover/icons/{nom}.png")


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit()
    c, a = sys.argv[1].replace("-", "_"), sys.argv[2:]
    globals()["cmd_" + c](*a)
