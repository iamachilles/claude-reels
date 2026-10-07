"""Exemple réel : le Reel « les pubs de ton concurrent » (mise en page détourée). À lire comme modèle,
les fichiers de données (public/assets, public/bg) ne sont pas fournis."""
import sys, os, json, re
sys.path.insert(0, os.path.expanduser("~/claude-reels/outils"))
from reelkit.mots import Mots
from reelkit.compo import Compo, ACCENT
from reelkit import scenes as S

m = Mots("words.json", corrections=[(["AP5"], ["Apify"]), (["Epify"], ["Apify"]), (["Décathlon"], ["Decathlon"])],
         majuscules=[])
at = m.at
for w in m.toks:
    if w["t"].lower() in ("apify",) and w["s"] > at("commente") - 0.1: w["t"] = "APIFY"
c = Compo(".", m, mise_en_page="detoure", fond="blanc")
q = c.q
H = 940  # moitié haute

T = dict(PUBS=at("publicites"), MIEUX=at("le mieux"), REFAIRE=at("refaire"), MONTRE=at("je te montre"), PRENONS=at("prenons"),
         DECA=at("decathlon"), N150=at("150"), TABLEAU=at("je les ai toutes"), TEXTE=at("le texte"), VISUEL=at("le visuel"),
         DATE=at("la date"), COMMENT=at("comment j'ai fait"), APIFY=at("s'appelle"), PLATEF=at("c'est une plateforme"),
         LOUER=at("louer"), INTERNET=at("sur internet"), INCR=at("ce qui est incroyable"), ENLIGNE=at("en ligne", 27),
         AVIS=at("par exemple"), ETOILE=at("une etoile"), COMM=at("tu peux avoir"), ZONE=at("d'une zone"), NUM=at("numero"),
         GENS=at("tu peux recuperer les gens"), COMMENTENT=at("qui commentent"), TIKTOK=at("les meilleurs"), REDDIT=at("ce que reddit"),
         AMAZON=at("le prix"), SURV=at("surveiller"), BREF=at("bref"), MILLIONS=at("millions"), EVID=at("evidemment"),
         PUISS=at("puissant"), IA=at("ton ia", 52), SI=at("si on revient"), CLAUDE=at("claude m'a classe"), NOMBRE=at("par nombre"),
         VU=at("ont vu"), RECETTE=at("et il est alle"), GAGN=at("gagnante"), GUIDE=at("si ca t'interesse"), ETAPE=at("etape par etape"),
         BRANCHER=at("brancher"), N24=at("24"), CTA=at("donc abonne-toi"), COMMENTE=at("commente"))
E = lambda k: T[k] - 0.05

# ---------- éléments propres à la vidéo ----------
CSS = """
.voile{position:absolute;left:0;top:0;width:1080px;height:1920px;background:rgba(255,255,255,.55)}
.haut{position:absolute;left:0;top:0;width:1080px;height:940px;overflow:hidden}
.hv{position:absolute;left:0;top:0;width:1080px;height:940px;object-fit:cover;z-index:1}
.lbl{position:absolute;left:0;right:0;margin:0 auto;width:max-content;background:#1A1A1A;color:#fff;border-radius:999px;padding:14px 40px;
  font-size:56px;font-weight:900;letter-spacing:-1.5px;opacity:0;box-shadow:0 18px 40px rgba(0,0,0,.2);display:flex;align-items:center;gap:20px}
.lbl.ac{background:var(--p)}
.lbl img{width:64px;height:64px;border-radius:16px}
.logo{position:absolute;border-radius:44px;box-shadow:0 24px 60px rgba(0,0,0,.18);opacity:0}
.tab{position:absolute;left:40px;top:150px;width:1000px;border-radius:28px;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.14);overflow:hidden;border:2px solid #eee}
.tab .hd,.tab .rw{display:grid;grid-template-columns:120px 1fr 190px 170px;align-items:center;gap:16px;padding:0 22px}
.tab .hd{height:78px;background:#1A1A1A;color:#fff;font-size:28px;font-weight:800}
.tab .hd span{opacity:.35}
.tab .rw{height:106px;border-top:1px solid #eee;color:#1A1A1A;font-size:24px;font-weight:600;opacity:0}
.tab .rw img{width:88px;height:88px;object-fit:cover;border-radius:12px}
.tab .rw .tx{overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.tab .rw .po{font-weight:900;font-size:28px;text-align:right}
.bars{position:absolute;left:60px;top:200px;width:960px;height:600px;display:flex;align-items:flex-end;gap:4px}
.bars div{flex:1;background:#d8d8d8;border-radius:3px 3px 0 0;transform-origin:50% 100%;transform:scaleY(0)}
.bars div.w{background:var(--p)}
.mapw{position:absolute;left:140px;top:150px;width:800px;height:640px}
.pt{position:absolute;width:14px;height:14px;border-radius:50%;background:var(--p);opacity:0}
.post{position:absolute;left:120px;top:170px;width:840px;border-radius:28px;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.14);padding:30px}
.post .l{height:22px;border-radius:11px;background:#e6e6e6;margin:12px 0}
.cm{display:flex;align-items:center;gap:18px;margin-top:22px;opacity:0}
.cm .av{width:70px;height:70px;border-radius:50%;background:#cfcfcf;filter:blur(3px)}
.cm .b{height:44px;border-radius:22px;background:#f0f0f0;flex:1}
.cm .tg{background:var(--p);color:#fff;border-radius:999px;padding:6px 18px;font-size:26px;font-weight:800}
.prix{position:absolute;left:90px;top:200px;width:900px;height:520px;background:#fff;border-radius:28px;box-shadow:0 30px 80px rgba(0,0,0,.14)}
.tiles{position:absolute;left:90px;top:170px;width:900px;display:grid;grid-template-columns:repeat(6,1fr);gap:16px}
.tiles div{height:120px;border-radius:18px;background:#ececec;opacity:0}
.tiles div.on{background:var(--p)}
.link{position:absolute;left:0;top:0}
.avis{position:absolute;left:0;top:0;width:1080px}
.plein{position:absolute;inset:0;background:#fff}
"""


def video_haut(src, start, end, seek=0.0, cls="brut"):
    c.bg(src + "P", start, end, cls, seek=seek)


def label(sid, start, end, txt, t, top=60, accent=False, logo=None, sortie=None):
    img = f'<img src="assets/logos/{logo}.png">' if logo else ""
    c.scene(sid, start, end, f'<div class="lbl{" ac" if accent else ""}" id="{sid}l" style="top:{top}px">{img}{txt}</div>',
            front=True, zone_bas=top + 100)
    c.pop(f"#{sid}l", t - 0.05, 0.3)
    if sortie: c.hide(f"#{sid}l", sortie)


def logo(sid, start, end, nom, t, x=390, y=250, taille=300, html_suite=""):
    c.scene(sid, start, end, f'<img class="logo" id="{sid}g" src="assets/logos/{nom}.png" style="left:{x}px;top:{y}px;width:{taille}px;height:{taille}px">'
                             + html_suite, zone_bas=y + taille)
    c.pop(f"#{sid}g", t - 0.05, 0.35, "back.out(2)", "opacity:0,scale:0.3,rotation:-8", "opacity:1,scale:1,rotation:0")


def sans_emoji(s):
    return re.sub(r"[^\w\s'’,.!?:;()\-àâäéèêëîïôöùûüçœÀÂÉÈÊÎÔÙÛÇ]", "", s).strip()


c.sous_titres()

# 1. accroche : le mur des pubs de Decathlon qui défile, titre en concept
video_haut("mur", 0, E("PRENONS"), seek=2.0)
c.scene("voile", 0, E("MONTRE"), '<div class="voile"></div>')
c.A(f"tl.to('#sc-voile > .in',{{opacity:0,duration:0.3}},{q(E('MONTRE')-0.3)});")
S.titre(c, "hook", 0, E("MONTRE"), "Les pubs", "de ton concurrent", t_choc=T["PUBS"], sortie=E("MONTRE"))
label("mieux", T["MIEUX"] - 0.1, E("MONTRE"), "Celles qui marchent", T["MIEUX"], top=520, accent=True)
c.flash(T["MONTRE"], 0.35)

# 2. Decathlon, environ 150 pubs
video_haut("mur", E("PRENONS"), E("TABLEAU"), seek=0.0)
S.compteur(c, "n150", E("PRENONS"), E("TABLEAU"), 149, T["N150"], unite="pubs actives", top=360, t_apparition=T["DECA"] + 0.3)

# 3. le tableau : une ligne par pub
rows = json.load(open("public/assets/table.json"))[:6]
rw = "".join(f'<div class="rw" id="tr{k}"><img src="{r["img"]}"><div class="tx">{sans_emoji(r["texte"])}</div>'
             f'<div>{r["date"][8:10]}/{r["date"][5:7]}/{r["date"][:4]}</div><div class="po">{r["portee"]/1e6:.1f} M</div></div>'
             for k, r in enumerate(rows))
c.scene("tab", E("TABLEAU"), E("COMMENT"), f'<div class="tab"><div class="hd"><span id="h0">Visuel</span><span id="h1">Texte</span>'
        f'<span id="h2">Lancement</span><span id="h3">Portée</span></div>{rw}</div>', zone_bas=870, titre=False)
for k in range(6):
    c.pop(f"#tr{k}", T["TABLEAU"] + 0.25 + k * 0.12, 0.25, "power2.out", "opacity:0,x:-60", "opacity:1,x:0")
for k, key in enumerate(["VISUEL", "TEXTE", "DATE"]):
    c.A(f"tl.to('#h{k}',{{opacity:1,color:'{ACCENT}',duration:0.15}},{q(T[key])});")
c.A(f"tl.to('#h3',{{opacity:1,duration:0.15}},{q(T['DATE'] + 0.6)});")

# 4. l'outil : Apify, des robots à louer
logo("apify", E("COMMENT"), E("INCR"), "apify", T["APIFY"], x=390, y=180, taille=300)
label("louer", E("COMMENT"), E("INCR"), "Des robots à louer", T["LOUER"], top=560, accent=True)

# 5. tout ce qui est public
icones = "".join(f'<img class="logo" id="ic{k}" src="assets/logos/{n}.png" style="left:{90+k*160}px;top:330px;width:130px;height:130px;border-radius:30px">'
                 for k, n in enumerate(["googlemaps", "instagram", "tiktok", "reddit", "amazon", "facebook"]))
c.scene("pub", E("INCR"), E("AVIS"), icones, zone_bas=460)
for k in range(6):
    c.pop(f"#ic{k}", T["INCR"] + 0.5 + k * 0.18, 0.28)
label("enligne", E("INCR"), E("AVIS"), "Tout ce qui est public", T["ENLIGNE"] - 0.4, top=600, accent=True)

# 6. la rafale d'usages
c.scene("avis", E("AVIS"), E("COMM"), '<img class="avis" id="avi" src="assets/avis.jpg">', titre=False)
c.A(f"tl.set('#avi',{{y:0}},{q(E('AVIS'))}); tl.to('#avi',{{y:-21,duration:{q(T['COMM']-T['AVIS'])},ease:'none'}},{q(E('AVIS'))});")
label("l_avis", E("AVIS"), E("COMM"), "Avis une étoile", T["ETOILE"], top=120, accent=True, logo="googlemaps")

P = json.load(open("public/assets/points.json"))
la0, la1, lo0, lo1 = 43.40, 44.13, 1.63, 2.80
pts = "".join(f'<div class="pt" style="left:{(lo-lo0)/(lo1-lo0)*786:.0f}px;top:{(la1-la)/(la1-la0)*626:.0f}px"></div>' for la, lo, _ in P)
c.scene("carte", E("COMM"), E("GENS"), f'<div class="mapw" style="top:360px">{pts}</div>', zone_bas=320)
c.A(f"tl.to('#sc-carte .pt',{{opacity:0.85,duration:0.08,stagger:{min(0.004, 1.6/len(P)):.4f}}},{q(T['COMM']+0.2)});")
S.compteur(c, "n652", E("COMM"), E("GENS"), 652, T["NUM"], unite="commerces", top=40, t_apparition=T["ZONE"] - 0.6)

post = ('<div class="post"><div class="l" style="width:70%"></div><div class="l" style="width:90%"></div><div class="l" style="width:55%"></div>'
        + "".join(f'<div class="cm" id="cm{k}"><div class="av"></div><div class="b"></div><span class="tg">Prospect</span></div>' for k in range(4))
        + '</div>')
c.scene("comm", E("GENS"), E("TIKTOK"), post, zone_bas=660, titre=False)
for k in range(4):
    c.pop(f"#cm{k}", T["COMMENTENT"] + k * 0.25, 0.25, "power2.out", "opacity:0,y:30", "opacity:1,y:0")
label("l_comm", E("GENS"), E("TIKTOK"), "Commentateurs du concurrent", T["COMMENTENT"], top=40, accent=True, logo="instagram")

logo("tt", E("TIKTOK"), E("REDDIT"), "tiktok", T["TIKTOK"], x=390, y=200, taille=300)
label("l_tt", E("TIKTOK"), E("REDDIT"), "Les TikTok qui cartonnent", T["TIKTOK"] + 0.3, top=580, accent=True)
logo("rd", E("REDDIT"), E("AMAZON"), "reddit", T["REDDIT"], x=390, y=200, taille=300)
label("l_rd", E("REDDIT"), E("AMAZON"), "Les problèmes de ta cible", T["REDDIT"] + 0.3, top=580, accent=True)

courbe = ('<div class="prix"><svg width="900" height="520" viewBox="0 0 900 520"><polyline id="pl" fill="none" stroke="' + ACCENT + '" stroke-width="10" '
          'stroke-linejoin="round" stroke-dasharray="1800" stroke-dashoffset="1800" points="40,300 160,280 260,320 360,240 460,260 560,180 660,330 760,200 860,230"/></svg></div>')
c.scene("prix", E("AMAZON"), E("BREF"), courbe, zone_bas=720, titre=False)
c.A(f"tl.to('#pl',{{strokeDashoffset:0,duration:2.6,ease:'none'}},{q(T['AMAZON']+0.2)});")
label("l_px", E("AMAZON"), E("BREF"), "Prix surveillé chaque jour", T["SURV"] - 0.3, top=60, accent=True, logo="amazon")

tiles = "".join(f'<div id="ti{k}"></div>' for k in range(24))
c.scene("tiles", E("BREF"), E("EVID"), f'<div class="tiles">{tiles}</div>', zone_bas=870)
for k in range(24):
    c.pop(f"#ti{k}", T["BREF"] + 0.1 + k * 0.05, 0.2, "back.out(2)", "opacity:0,scale:0", "opacity:1,scale:1")
c.A(f"tl.to('#sc-tiles .tiles div',{{background:'{ACCENT}',duration:0.1,stagger:0.02}},{q(T['MILLIONS'])});")

# 7. branché sur ton IA
logo("ap2", E("EVID"), E("SI"), "apify", T["EVID"] + 0.2, x=130, y=220, taille=260,
     html_suite=f'<svg class="link" width="1080" height="940"><line id="ln" x1="400" y1="350" x2="680" y2="350" stroke="{ACCENT}" stroke-width="12" '
                f'stroke-linecap="round" stroke-dasharray="280" stroke-dashoffset="280"/></svg>'
                f'<img class="logo" id="clg" src="assets/logos/claude.png" style="left:690px;top:220px;width:260px;height:260px">')
c.pop("#clg", T["PUISS"] - 0.3, 0.35, "back.out(2)", "opacity:0,scale:0.3", "opacity:1,scale:1")
c.A(f"tl.to('#ln',{{strokeDashoffset:0,duration:0.4}},{q(T['IA']-0.3)});")
label("l_ia", E("EVID"), E("SI"), "Apify branché à ton IA", T["IA"] - 0.2, top=600, accent=True)

# 8. Decathlon classé par portée
video_haut("reach", E("SI"), T["NOMBRE"] - 0.4, seek=1.0)
c.scene("rz", E("SI"), T["NOMBRE"] - 0.4, f'<div class="lbl ac" id="rzl" style="top:180px">4 638 216 personnes</div>', front=True, zone_bas=280)
c.pop("#rzl", T["CLAUDE"], 0.3)
V = json.load(open("public/assets/portees.json"))[:60]
bars = "".join(f'<div class="{"w" if k < 6 else ""}" style="height:{max(2, v / V[0] * 100):.2f}%"></div>' for k, v in enumerate(V))
c.scene("bars", T["NOMBRE"] - 0.4, E("RECETTE"), f'<div class="bars">{bars}</div>', zone_bas=780)
c.A(f"tl.to('#sc-bars .bars div',{{scaleY:1,duration:0.5,stagger:0.006,ease:'power2.out'}},{q(T['NOMBRE']-0.3)});")
label("l_bars", T["NOMBRE"] - 0.4, E("RECETTE"), "6 gagnantes sur 149 pubs", T["VU"], top=50, accent=True)

# 9. la recette des gagnantes (analyse du tableau du 06/10)
S.pastilles(c, "rec", E("RECETTE"), E("GUIDE"), [("Pub catalogue", T["GAGN"] - 0.3), ("Une phrase, un émoji", T["GAGN"] + 0.3),
                                                 ("En ligne depuis mai", T["GAGN"] + 0.9)], couleur="noir", top=170, pas=150)
c.scene("rect", E("RECETTE"), E("GUIDE"), '<div class="lbl ac" id="rectl" style="top:40px">La recette gagnante</div>', zone_bas=140)
c.pop("#rectl", T["RECETTE"], 0.3)

# 10. le kit
video_haut("kit", E("GUIDE"), E("CTA"), seek=0.0)
label("l_guide", E("GUIDE"), E("N24") - 0.1, "Guide pas à pas", T["ETAPE"], top=140, accent=True, sortie=E("N24") - 0.3)
S.compteur(c, "n24", E("N24") - 0.3, E("CTA"), 24, T["N24"], unite="cas d'usage", top=300, t_apparition=T["N24"] - 0.5)

# 11. CTA
c.scene("ctab", E("CTA"), c.dur, '<div style="position:absolute;inset:0;background:var(--cream)"></div>')
S.cta(c, E("CTA"), c.dur, "apify", T["COMMENTE"] - 0.1, T["COMMENTE"] + 0.3)

c.personne_detouree(
    hauteurs=[(0, 730), (E("PRENONS"), 720), (E("TABLEAU"), 960), (E("COMMENT"), 760), (E("INCR"), 800), (E("AVIS"), 600),
              (E("COMM"), 620), (E("GENS"), 760), (E("TIKTOK"), 780), (E("AMAZON"), 820), (E("BREF"), 960), (E("EVID"), 800),
              (E("SI"), 900), (T["NOMBRE"] - 0.4, 880), (E("RECETTE"), 640), (E("GUIDE"), 620), (E("CTA"), 740)],
    punch=[(0, 1.0), (T["PUBS"], 1.06), (E("MONTRE"), 1.0), (T["N150"], 1.06), (E("TABLEAU"), 1.0), (T["INCR"], 1.06),
           (E("AVIS"), 1.0), (T["PUISS"], 1.06), (E("SI"), 1.0), (T["VU"], 1.06), (E("RECETTE"), 1.0), (E("CTA"), 1.05)], alterne=1.0)
c.ecrire(CSS)
