"""Composition HyperFrames d'un Reel : fonds, scènes, sous-titres, personne filmée, audio, et les métadonnées
que l'audit relit (textes à l'écran, zones occupées en haut, position de la tête).

Une vidéo = un petit fichier compo.py dans son projet, qui importe ce module et scenes.py, et
n'écrit que ses scènes calées sur les mots (Mots.at). Tout le reste vient d'ici.
Mises en page : "detoure" (la personne détourée devant les fonds), "plein_cadre" (le rush tel quel,
éléments par-dessus), "ecran_coupe" (scène en haut, la personne en bas).
"""
import json, os, re, shutil

ICI = os.path.dirname(os.path.abspath(__file__))
# Charte graphique : à adapter à la tienne (ou par variables d'environnement).
ACCENT = os.environ.get("REEL_ACCENT", "#2563EB")   # mot en cours, pastilles et bandeaux d'accent
CLAIR = os.environ.get("REEL_CLAIR", "#F3F4F6")     # fond clair des pages et de l'appel à l'action
NOIR = "#1A1A1A"


def eclaircir(hexa, f=0.45):
    """La couleur mélangée à du blanc (f = part de blanc)."""
    r, g, b = (int(hexa.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(round(x + (255 - x) * f) for x in (r, g, b))


class Compo:
    def __init__(self, projet, mots, mise_en_page="detoure", fond="blanc", fps=24, nom=None):
        self.p = projet
        self.mots = mots
        self.fps = fps
        self.mep = mise_en_page
        self.fond = fond
        self.dur = float(open(os.path.join(projet, "dur.txt")).read())
        self.nom = nom or "reel-" + os.path.basename(os.path.abspath(projet)).replace("video-reel-", "")
        self.els, self.tl = [], []
        self.textes, self.zones, self.tete = [], [], []
        self.musique = None
        self._bg = 0

    # ---------- primitives ----------
    def q(self, x):
        return round(round(x * self.fps) / self.fps, 4)

    def A(self, js):
        self.tl.append(js)

    def bg(self, src, start, end, cls="", seek=0.0):
        """Un enregistrement d'écran plein cadre (public/bg/{src}.mp4). Par défaut ses couleurs sont
        inversées (enregistrement sombre affiché en clair, teintes gardées). cls : "brut" pour un
        enregistrement déjà clair (aucune inversion), "blur" (flouté), "dim" (adouci), combinables."""
        self._bg += 1
        k = self._bg
        self.els.append(f'<video class="bg clip {cls}" id="bg{k}" src="bg/{src}.mp4" muted playsinline data-start="{self.q(start)}" '
                        f'data-duration="{self.q(end-start)}" data-media-start="{seek}" data-track-index="{30+k}"></video>')
        return f"#bg{k}"

    def scene(self, sid, start, end, html, enter="cut", front=False, zone_bas=None, titre=True):
        """zone_bas : le pixel le plus bas occupé en haut de l'écran par la scène. L'audit vérifie que
        la tête de la personne reste en dessous (mise en page detoure)."""
        self.els.append(f'<div class="scene clip{" front" if front else ""}" id="sc-{sid}" data-start="{self.q(start)}" '
                        f'data-duration="{self.q(end-start)}" data-track-index="{4 if front else 3}"><div class="in">{html}</div></div>')
        sel = f"#sc-{sid} > .in"
        if enter == "pop":
            self.A(f"tl.fromTo('{sel}',{{opacity:0,scale:0.94}},{{opacity:1,scale:1,duration:0.22,ease:'back.out(1.6)'}},{self.q(start)});")
        else:
            self.A(f"tl.set('{sel}',{{opacity:1}},{self.q(start)});")
        texte = re.sub(r"<[^>]+>", " ", html)
        texte = re.sub(r"\s+", " ", texte).strip()
        # titre=False : maquette d'interface (fenêtre de chat, page), exclue du contrôle « titres en concepts »
        if texte: self.textes.append(dict(scene=sid, start=round(start, 2), texte=texte, titre=titre))
        if zone_bas is not None: self.zones.append(dict(scene=sid, start=start, end=end, bas=zone_bas))

    def pop(self, sel, t, dur=0.32, ease="back.out(2.2)", fr="opacity:0,scale:0.4", to="opacity:1,scale:1"):
        self.A(f"tl.fromTo('{sel}',{{{fr}}},{{{to},duration:{dur},ease:'{ease}'}},{self.q(t)});")

    def hide(self, sel, t, dur=0.2):
        self.A(f"tl.to('{sel}',{{opacity:0,duration:{dur}}},{self.q(t)});")

    def shake(self, sel, t, amp=18):
        for k, x in enumerate([-amp, amp * 0.8, -amp * 0.55, amp * 0.3, 0]):
            self.A(f"tl.to('{sel}',{{x:{x:.1f},duration:0.045,ease:'none'}},{self.q(t + k*0.045)});")

    def flash(self, t, o=0.5):
        self.A(f"tl.fromTo('#fl',{{opacity:0}},{{opacity:{o},duration:0.05}},{self.q(t)}); tl.to('#fl',{{opacity:0,duration:0.3}},{self.q(t+0.06)});")

    # ---------- sous-titres karaoké ----------
    def sous_titres(self):
        groups = self.mots.groupes()
        for gi, g in enumerate(groups):
            s = g[0]["s"]
            e = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else self.dur
            e = min(e, g[-1]["e"] + 0.45)
            spans = " ".join(f'<span id="w{gi}_{k}">{w["t"]}</span>' for k, w in enumerate(g))
            self.els.append(f'<div class="cap clip" id="capw{gi}" data-start="{self.q(s)}" data-duration="{self.q(e-s)}" data-track-index="8">'
                            f'<span class="in" id="cap{gi}">{spans}</span></div>')
            self.A(f"tl.fromTo('#cap{gi}',{{scale:0.85,opacity:0}},{{scale:1,opacity:1,duration:0.1,ease:'power2.out'}},{self.q(s)});")
            for k, w in enumerate(g):
                off = g[k + 1]["s"] if k + 1 < len(g) else e
                self.A(f"tl.set('#w{gi}_{k}',{{color:'{ACCENT}'}},{self.q(w['s'])});")
                if off < e - 0.01:
                    self.A(f"tl.set('#w{gi}_{k}',{{color:'#ffffff'}},{self.q(off)});")
        self.n_sous_titres = len(groups)

    # ---------- la personne filmée ----------
    @staticmethod
    def _val(lst, x):
        v = lst[0][1]
        for t0, y0 in lst:
            if t0 <= x + 1e-6: v = y0
        return v

    def masquer(self, intervalles):
        """Masque la personne sur des intervalles [(debut, fin)] (le fond prend tout l'écran, la voix
        continue). Désactivé par défaut (l'effet est déroutant) : seulement sur demande explicite."""
        for s, e in intervalles:
            self.A(f"tl.set('#me',{{opacity:0}},{self.q(s)}); tl.set('#me',{{opacity:1}},{self.q(e)});")

    def personne_detouree(self, hauteurs, punch, alterne=1.07):
        """hauteurs : [(t, H)] où H est la hauteur du haut de la tête **sans zoom** (px). Avec un zoom p,
        la tête réelle monte de 1420 x (p - 1) : à p = 1,2 et H = 832, elle est à 548. Pour garder la tête
        sous un titre pendant un zoom, relever H d'autant. Jamais moins de 500 : en dessous, le corps
        remonte et laisse une bande vide sous les pieds. La taille est bornée entre 0,6 et 1,35.
        punch : [(t, facteur)] ; alterne : zoom appliqué un morceau sur deux (rythme des coupes).
        La taille suit headtrack.json (la personne avance vers la caméra pendant ses prises)."""
        HT = json.load(open(os.path.join(self.p, "headtrack.json")))
        self.A("tl.set('#me',{transformOrigin:'50% 100%'},0);")
        prev = None
        for i, top in enumerate(HT["top"]):
            x = i / HT["fps"]
            if x > self.dur: break
            p = self._val(punch, x) * (1.0 if HT["seg"][i] % 2 == 0 else alterne)
            S = max(0.6, min(1.35, 1420 / (1920 - top) * p))
            if HT["seg"][i] != prev or i == 0:
                self.A(f"tl.set('#me',{{scale:{S:.4f}}},{self.q(x)});")
            else:
                self.A(f"tl.to('#me',{{scale:{S:.4f},duration:{1/HT['fps']:.4f},ease:'none'}},{self.q(x - 1/HT['fps'])});")
            prev = HT["seg"][i]
            H = self._val(hauteurs, x)
            y = H - 500
            # position réelle du haut de la tête après zoom (origine en bas du cadre)
            self.tete.append(dict(t=round(x, 3), haut=round(1920 - 1420 * p + y, 1), y=y))
        for k, (t0, H) in enumerate(hauteurs):
            y = H - 500
            if k == 0: self.A(f"tl.set('#me',{{y:{y}}},0);")
            else: self.A(f"tl.to('#me',{{y:{y},duration:0.3,ease:'power3.inOut'}},{self.q(t0 - 0.1)});")
        self.hauteurs = hauteurs

    def personne_plein_cadre(self, punch):
        """Le rush plein cadre ; punch-ins centrés sur le visage."""
        self.A("tl.set('#me',{transformOrigin:'50% 30%'},0);")
        for t0, s in punch:
            self.A(f"tl.set('#me',{{scale:{s}}},{self.q(t0)});")

    # ---------- sortie ----------
    def ecrire(self, css_projet=""):
        pub = os.path.join(self.p, "public")
        os.makedirs(os.path.join(pub, "vendor"), exist_ok=True); os.makedirs(os.path.join(pub, "fonts"), exist_ok=True)
        shutil.copy(os.path.join(ICI, "static", "gsap.min.js"), os.path.join(pub, "vendor", "gsap.min.js"))
        shutil.copy(os.path.join(ICI, "static", "police.woff2"), os.path.join(pub, "fonts", "police.woff2"))
        css = open(os.path.join(ICI, "static", "base.css")).read().replace("$ACCENT_CLAIR", eclaircir(ACCENT)).replace("$ACCENT", ACCENT).replace("$CLAIR", CLAIR) + "\n" + css_projet
        if self.fond == "noir":
            css += "\nhtml,body,#stage{background:#0B0B0D}\n.bg{filter:none}\n"
        D = self.dur
        if self.mep == "detoure":
            moi = (f'<div class="me-wrap"><video id="me" src="me.webm" muted playsinline data-start="0" data-duration="{D}" '
                   f'data-track-index="2"></video></div>')
        elif self.mep == "plein_cadre":
            moi = (f'<div class="me-wrap"><video id="me" src="input-video.mp4" muted playsinline data-start="0" data-duration="{D}" '
                   f'data-track-index="2" style="object-fit:cover"></video></div>')
        else:  # ecran_coupe
            moi = (f'<div class="me-wrap" style="top:960px;height:960px"><video id="me" src="input-video.mp4" muted playsinline '
                   f'data-start="0" data-duration="{D}" data-track-index="2" style="top:-480px"></video></div>')
        musique = ""
        if self.musique:
            musique = f'<audio id="bed" src="{self.musique}" data-start="0" data-duration="{D}" data-track-index="11" data-volume="1"></audio>'
        html = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><style>{css}</style></head><body>
<div id="stage" data-composition-id="{self.nom}" data-start="0" data-duration="{D}" data-fps="{self.fps}" data-width="1080" data-height="1920">
<div class="shade"></div>
{moi}
<div class="flash" id="fl"></div>
<audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{D}" data-track-index="10" data-volume="1"></audio>
{musique}
{chr(10).join(self.els)}
<script src="vendor/gsap.min.js"></script>
<script>
(function(){{
const tl=window.gsap.timeline({{paused:true}});
{chr(10).join(self.tl)}
window.__timelines=window.__timelines||{{}};
window.__timelines["{self.nom}"]=tl;
}})();
</script>
</div></body></html>'''
        open(os.path.join(pub, "index.html"), "w").write(html)
        meta = dict(mise_en_page=self.mep, fond=self.fond, duree=D, textes=self.textes, zones=self.zones,
                    tete=self.tete, musique=self.musique, n_elements=len(self.els))
        json.dump(meta, open(os.path.join(self.p, "compo_meta.json"), "w"), ensure_ascii=False, indent=1)
        print(f"{getattr(self, 'n_sous_titres', 0)} sous-titres ; {len(self.els)} éléments ; durée {D}")
