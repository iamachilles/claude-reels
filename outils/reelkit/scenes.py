"""Bibliothèque de scènes des Reels. Chaque scène se cale sur des instants donnés par Mots.at() et
déclare sa zone basse (pour l'audit de chevauchement avec la tête).

Règles appliquées partout : titres en concepts, jamais en phrases ; aucun émoji ;
police grasse, pas d'italique ; texte noir ou pastille noire ou d'accent sur fond clair.
Une scène nouvelle, inventée pour une vidéo, s'ajoute ici si elle peut resservir.
"""
from .compo import ACCENT, eclaircir

PERSON = ('<svg viewBox="0 0 24 24" width="64" height="64"><circle cx="12" cy="8" r="4.2" fill="#1A1A1A"/>'
          '<path d="M3.5 21c0-4.7 3.8-7.5 8.5-7.5s8.5 2.8 8.5 7.5" fill="#1A1A1A"/></svg>')


def titre(c, sid, start, end, ligne1, ligne2, t_choc=None, sortie=None):
    """Titre d'accroche présent dès la première image (noir puis couleur d'accent). t_choc : glitch et secousse
    sur le mot fort ; sortie : instant où il s'efface."""
    c.scene(sid, start, end, f'<div class="hooktxt" id="{sid}t">{ligne1}<br><span class="o">{ligne2}</span></div>'
                             f'<div class="glitch" id="{sid}g"></div>', front=True, zone_bas=400)
    c.A(f"tl.set('#{sid}t',{{opacity:1,scale:1}},{c.q(start)});")
    if t_choc is not None:
        c.A(f"tl.fromTo('#{sid}g',{{opacity:0}},{{opacity:1,duration:0.05,yoyo:true,repeat:5}},{c.q(t_choc)});")
        c.shake(f"#{sid}t", t_choc, 16)
    if sortie is not None:
        c.hide(f"#{sid}t", sortie - 0.25)


def pastilles(c, sid, start, end, items, couleur="noir", top=120, pas=130, remplace=False):
    """Une ou plusieurs pastilles qui surgissent chacune sur son mot. items : [(texte, t)].
    remplace : chaque pastille efface la précédente (même place) au lieu de s'empiler."""
    cls = "pill ac" if couleur == "accent" else "pill"
    html, bas = "", top
    for k, (txt, _) in enumerate(items):
        y = top if remplace else top + k * pas
        html += f'<div class="{cls}" id="{sid}{k}" style="top:{y}px">{txt}</div>'
        bas = max(bas, y + 100)
    c.scene(sid, start, end, html, front=True, zone_bas=bas)
    for k, (_, t) in enumerate(items):
        c.pop(f"#{sid}{k}", t - 0.05, 0.35)
        if remplace and k + 1 < len(items):
            c.hide(f"#{sid}{k}", items[k + 1][1] - 0.2)


def compteur(c, sid, start, end, valeur, t_mot, unite="", prefixe="", t_apparition=None, top=110):
    """Grand chiffre dans une carte blanche, qui atteint `valeur` au moment où le chiffre est dit
    (t_mot = Mots.at du chiffre). Un compteur calé après le mot affiche 0 pendant
    que la personne dit 3 500."""
    c.scene(sid, start, end, f'<div class="big" id="{sid}b" style="top:{top}px"><span id="{sid}n">0</span><small>{unite}</small></div>',
            front=True, zone_bas=top + 260)
    t0 = t_apparition if t_apparition is not None else max(start, t_mot - 0.9)
    c.pop(f"#{sid}b", t0, 0.3)
    c.A(f"const c_{sid}={{v:0}};")
    c.A(f"tl.fromTo(c_{sid},{{v:0}},{{v:{valeur},duration:{max(0.4, t_mot - t0):.2f},ease:'power2.out',onUpdate:()=>"
        f"{{document.getElementById('{sid}n').textContent='{prefixe}'+Math.round(c_{sid}.v).toLocaleString('fr-FR').replace(/\\u202f|\\u00a0/g,' ')}}}},{c.q(t0)});")


def grille(c, sid, start, end, n, t_debut, valeur_label, t_valeur, t_alerte=None, alerte=""):
    """La preuve chiffrée : un compteur « +n » et n cases qui s'allument, puis passent au rouge sur
    le mot du problème (t_alerte) avec une étiquette."""
    cells = "".join(f'<div class="bx" id="{sid}x{k}"></div>' for k in range(n))
    c.scene(sid, start, end,
            f'<div class="count"><div class="n" id="{sid}n">+0</div><div class="s">{valeur_label}</div></div>'
            f'<div class="grid40">{cells}</div>' + (f'<div class="same" id="{sid}a">{alerte}</div>' if alerte else ""),
            zone_bas=780)
    c.A(f"const c_{sid}={{v:0}};")
    c.A(f"tl.fromTo(c_{sid},{{v:0}},{{v:{n},duration:1.0,ease:'power2.out',onUpdate:()=>{{document.getElementById('{sid}n').textContent='+'+Math.round(c_{sid}.v)}}}},{c.q(t_valeur-0.8)});")
    for k in range(n):
        c.pop(f"#{sid}x{k}", t_debut + 0.2 + k * 0.035, 0.22, "back.out(2)", "opacity:0,scale:0", "opacity:1,scale:1")
    c.A(f"tl.to('#sc-{sid} .bx',{{background:'{ACCENT}',borderColor:'{eclaircir(ACCENT)}',duration:0.2,stagger:0.03}},{c.q(t_valeur-0.3)});")
    if t_alerte is not None:
        c.A(f"tl.to('#sc-{sid} .bx',{{background:'#ff3b3b',borderColor:'#ff8a8a',duration:0.25,stagger:0.01}},{c.q(t_alerte-0.2)});")
        if alerte:
            c.pop(f"#{sid}a", t_alerte, 0.35, "back.out(3)", "opacity:0,scale:2,rotation:-4", "opacity:1,scale:1,rotation:-4")


def fenetre_chat(c, sid, start, end, app, message, tags, t_message, t_reponse=None, tampon=None, t_tampon=None,
                 t_oubli=None, t_recommence=None, jours=("Jour 2", "Jour 3", "Jour 4")):
    """Fenêtre de chat claire : le message de l'utilisateur, des étiquettes qui surgissent sur leurs
    mots [(texte, t)], une réponse grise, un tampon rouge, puis l'oubli (la fenêtre se vide, les jours
    défilent) et le recommencement."""
    tg = "".join(f'<span class="tag" id="{sid}g{k}">{t}</span>' for k, (t, _) in enumerate(tags))
    c.scene(sid, start, end,
            f'<div class="win" id="{sid}w"><div class="winbar"><span class="dotc"><svg viewBox="0 0 24 24" width="26" height="26"><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg></span>{app}<span class="day" id="{sid}d">Jour 1</span></div>'
            f'<div class="msgs" id="{sid}m"><div class="um" id="{sid}u">{message}<div class="tags">{tg}</div></div>'
            '<div class="am" id="' + sid + 'a"><div class="ln" style="width:620px"></div><div class="ln" style="width:540px"></div>'
            '<div class="ln" style="width:580px"></div></div></div>'
            f'<div class="newc" id="{sid}c">Nouvelle conversation</div>'
            + (f'<div class="stampg" id="{sid}s">{tampon}</div>' if tampon else "") + '</div>', zone_bas=880, titre=False)
    c.pop(f"#{sid}u", t_message + 0.3, 0.3, "back.out(1.8)", "opacity:0,y:40", "opacity:1,y:0")
    c.pop(f"#{sid}d", t_message + 0.1, 0.25)
    for k, (_, t) in enumerate(tags):
        c.pop(f"#{sid}g{k}", t, 0.25)
    if t_reponse is not None:
        c.pop(f"#{sid}a", t_reponse + 0.2, 0.3, "power2.out", "opacity:0,y:30", "opacity:1,y:0")
    if tampon and t_tampon is not None:
        c.pop(f"#{sid}s", t_tampon, 0.3, "back.out(3)", "opacity:0,scale:2.4,rotation:-10", "opacity:1,scale:1,rotation:-10")
    if t_oubli is not None:
        c.A(f"tl.to('#{sid}m" + (f",#{sid}s" if tampon else "") + f"',{{opacity:0,duration:0.15}},{c.q(t_oubli+0.3)});")
        c.pop(f"#{sid}c", t_oubli + 0.45, 0.25, "power2.out", "opacity:0", "opacity:1")
        for k, d in enumerate(jours):
            c.A(f"tl.call(()=>{{document.getElementById('{sid}d').textContent='{d}'}},null,{c.q(t_oubli+0.4+k*0.38)});")
            c.A(f"tl.fromTo('#{sid}d',{{scale:1.4}},{{scale:1,duration:0.2}},{c.q(t_oubli+0.4+k*0.38)});")
        c.A(f"tl.call(()=>{{document.getElementById('{sid}d').textContent='Jour 1'}},null,{c.q(start+0.01)});")
    if t_recommence is not None:
        c.A(f"tl.set('#{sid}m',{{opacity:1}},{c.q(t_recommence)}); tl.set('#{sid}u',{{opacity:0}},{c.q(t_recommence)}); "
            f"tl.set('#{sid}a',{{opacity:0}},{c.q(t_recommence)});")
        c.pop(f"#{sid}u", t_recommence + 0.05, 0.25, "back.out(1.8)", "opacity:0,y:40", "opacity:1,y:0")
        c.shake(f"#{sid}w", t_recommence + 0.3, 12)


def carte_video(c, sid, start, end, src, top=190, hauteur=663, clair=True, legende=None, t_legende=None):
    """Un enregistrement d'écran posé en carte (note ouverte, page lisible), sur un fond flouté.
    clair=True : inverse les couleurs d'un enregistrement en thème sombre ; clair=False pour un
    enregistrement déjà clair."""
    if legende:
        c.scene(sid, start, end, f'<div class="pill ac" id="{sid}l" style="top:70px">{legende}</div>', zone_bas=top + hauteur)
        if t_legende is not None: c.pop(f"#{sid}l", t_legende, 0.35)
    filt = "filter:invert(1) hue-rotate(180deg);" if clair else ""
    c.els.append(f'<video class="clip" id="{sid}v" src="bg/{src}.mp4" muted playsinline data-start="{c.q(start)}" data-duration="{c.q(end-start)}" '
                 f'data-track-index="29" style="position:absolute;left:40px;top:{top}px;width:1000px;height:{hauteur}px;object-fit:cover;'
                 f'border-radius:28px;z-index:3;box-shadow:0 30px 80px rgba(0,0,0,.18);{filt}"></video>')
    c.pop(f"#{sid}v", start, 0.3, "back.out(1.6)", "opacity:0,scale:0.9,y:40", "opacity:1,scale:1,y:0")
    if not legende: c.zones.append(dict(scene=sid, start=start, end=end, bas=top + hauteur))


def page_defilante(c, sid, start, end, image, t_apparition, items=(), course=-2900):
    """Capture de la page d'une ressource qui défile dans une carte, avec des pastilles noires qui
    surgissent sur leurs mots [(texte, t)] en bas de la carte. Ne jamais capturer un nom interdit
    (une signature, un nom de client) : recadrer la capture avant."""
    it = "".join(f'<div class="res" id="{sid}q{k}" style="top:760px">{t}</div>' for k, (t, _) in enumerate(items))
    c.scene(sid, start, end, f'<div class="page" id="{sid}p"><img id="{sid}i" src="{image}"></div>{it}', zone_bas=860, titre=True)
    c.pop(f"#{sid}p", t_apparition - 0.2, 0.35, "back.out(1.6)", "opacity:0,y:200", "opacity:1,y:0")
    c.A(f"tl.fromTo('#{sid}i',{{y:0}},{{y:{course},duration:{c.q(end-t_apparition)},ease:'power1.inOut'}},{c.q(t_apparition+0.3)});")
    for k, (_, t) in enumerate(items):
        c.pop(f"#{sid}q{k}", t, 0.3)
        if k + 1 < len(items): c.hide(f"#{sid}q{k}", items[k + 1][1] - 0.15, 0.15)


def equipe(c, sid, start, end, t_apparition, t_liens, centre="IA", top=280):
    """Six personnes reliées à un noyau central (l'équipe qui travaille avec la même IA)."""
    pos = [(110, 40), (110, 280), (330, 0), (630, 0), (850, 40), (850, 280)]
    lines = "".join(f'<line class="tl" x1="540" y1="220" x2="{x+60}" y2="{y+60}" stroke="{ACCENT}" stroke-width="7" '
                    f'stroke-dasharray="520" stroke-dashoffset="520"/>' for x, y in pos)
    avh = "".join(f'<div class="av" id="{sid}a{k}" style="left:{x}px;top:{y}px">{PERSON}</div>' for k, (x, y) in enumerate(pos))
    c.scene(sid, start, end, f'<div class="team" id="{sid}t" style="top:{top}px"><svg width="1080" height="420" viewBox="0 0 1080 420">'
                             f'{lines}</svg>{avh}<div class="hub">{centre}</div></div>', front=True, zone_bas=top + 420)
    c.A(f"tl.set('#{sid}t',{{opacity:1}},{c.q(t_apparition)});")
    for k in range(6):
        c.pop(f"#{sid}a{k}", t_apparition + k * 0.07, 0.25)
    c.A(f"tl.to('#sc-{sid} .tl',{{strokeDashoffset:0,duration:0.35,stagger:0.06}},{c.q(t_liens-0.4)});")
    c.A(f"tl.to('#sc-{sid} .av',{{borderColor:'{ACCENT}',duration:0.2,stagger:0.06}},{c.q(t_liens-0.1)});")


def cta(c, start, end, mot, t_commente, t_mot):
    """« Commente MOT » : le mot en pastille d'accent. L'abonnement se dit, il ne s'écrit pas."""
    c.scene("cta", start, end, f'<div class="ctaw"><div class="ctat" id="ct1">Commente</div><div class="ctapill" id="cp">{mot.upper()}</div></div>',
            front=True, zone_bas=600)
    c.pop("#ct1", t_commente, 0.3)
    c.pop("#cp", t_mot - 0.05, 0.4, "back.out(2.6)", "opacity:0,scale:0.3", "opacity:1,scale:1")
    c.A(f"tl.to('#cp',{{scale:1.08,duration:0.18,yoyo:true,repeat:3,ease:'power1.inOut'}},{c.q(t_mot+0.5)});")


def flou(c, sid, start, end, zones):
    """Floute des zones de l'écran (noms de prospects, photos, messages) par-dessus le fond.
    zones : [(x, y, largeur, hauteur)] en pixels du cadre 1080 x 1920. À poser sur toute carte Slack,
    tout CRM ou toute boîte mail filmés. Vérifier ensuite sur les captures que rien n'est lisible."""
    html = "".join(f'<div class="flou" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>' for x, y, w, h in zones)
    c.els.append(f'<div class="clip" id="{sid}" data-start="{c.q(start)}" data-duration="{c.q(end-start)}" data-track-index="28" '
                 f'style="position:absolute;inset:0;z-index:2">{html}</div>')
