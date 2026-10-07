"""Mots de l'A-roll : chargement, recollage, corrections, et at() pour caler une animation sur un mot dit."""
import json, re, unicodedata


def norm(s):
    return re.sub(r"[^a-z0-9']", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


class Mots:
    """toks : liste de dict(t, s, e, p) ; p vaut vrai si le mot finit une phrase ou une proposition.

    corrections : liste de (suite de mots entendue par Whisper, suite à afficher), par exemple
    (["ce", "chat", "gpt"], ["ChatGPT"]) ou (["etre", "sur"], ["elle te", "sort"]). La comparaison
    se fait sur la forme normalisée, sans accents ni ponctuation.
    """

    def __init__(self, chemin, corrections=(), majuscules=()):
        raw = json.load(open(chemin))
        toks = []
        for w in raw:  # recolle « c » + « 'est », « abonne » + « -toi »
            if toks and (w["t"].startswith("'") or w["t"].startswith("-")):
                toks[-1]["t"] += w["t"]; toks[-1]["e"] = w["e"]
            else:
                toks.append(dict(t=w["t"], s=w["s"], e=w["e"]))
        for w in toks:
            w["p"] = bool(w["t"]) and w["t"][-1] in ".,?!"
            w["t"] = w["t"].rstrip(".,?!")
        toks = [w for w in toks if w["t"]]
        for entendu, affiche in corrections:
            toks = self._corrige(toks, [norm(x) for x in entendu], affiche)
        for k, w in enumerate(toks):
            if k and toks[k - 1]["p"] and w["t"][:1].islower():
                w["t"] = w["t"][0].upper() + w["t"][1:]
        for mot in majuscules:  # le mot-clé du CTA en capitales, partout où il est dit
            for w in toks:
                if norm(w["t"]) == norm(mot): w["t"] = mot.upper()
        self.toks = toks

    @staticmethod
    def _corrige(toks, entendu, affiche):
        out, i, n = [], 0, len(entendu)
        while i < len(toks):
            if [norm(t["t"]) for t in toks[i:i + n]] == entendu:
                bloc = toks[i:i + n]
                s, e, p = bloc[0]["s"], bloc[-1]["e"], bloc[-1]["p"]
                pas = (e - s) / len(affiche)
                for k, a in enumerate(affiche):
                    out.append(dict(t=a, s=round(s + k * pas, 3), e=round(s + (k + 1) * pas, 3), p=p and k == len(affiche) - 1))
                i += n
            else:
                out.append(toks[i]); i += 1
        return out

    def at(self, phrase, after=0.0, end=False):
        """Début (ou fin si end) de la première occurrence de la phrase après `after` secondes."""
        words = [norm(x) for x in phrase.split()]
        toks = self.toks
        for i, w in enumerate(toks):
            if w["s"] < after: continue
            if all(i + k < len(toks) and norm(toks[i + k]["t"]) == words[k] for k in range(len(words))):
                return toks[i + len(words) - 1]["e"] if end else w["s"]
        raise ValueError(f"introuvable dans l'A-roll : {phrase!r} après {after} s")

    def groupes(self, max_mots=3, max_car=24, pause=0.22):
        """Groupes de sous-titres : 3 mots au plus, coupés au-delà de 24 caractères, à chaque ponctuation ou pause."""
        groups, cur = [], []
        toks = self.toks
        for i, w in enumerate(toks):
            cur.append(w)
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            gap = (nxt["s"] - w["e"]) if nxt else 9
            nchar = sum(len(x["t"]) + 1 for x in cur) + (len(nxt["t"]) if nxt else 0)
            if len(cur) == max_mots or w["p"] or gap > pause or nxt is None or nchar > max_car:
                groups.append(cur); cur = []
        return groups
