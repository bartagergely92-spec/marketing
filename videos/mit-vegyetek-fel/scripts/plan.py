#!/usr/bin/env python3
"""Vágási terv: „Mit vegyetek fel a karácsonyi fotózásra?” Reels.

Bemenet: work/<felvétel>.json (whisper medium, szó szintű időbélyegek) és work/<felvétel>.wav.
Kimenet: work/edit.json – a megtartott szakaszok (szünethez igazított vágópontokkal),
a feliratcsoportok és a fotók/kártyák a vágott idővonalon.
"""
import json, os, re, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ROOT, "work")
FPS = 30

# (felvétel, kezdet, vég, fejezet) – a felvételen belüli idő, a whisper szóhatárai alapján
SEGMENTS = [
    ("v1_102154", 0.10, 6.75, 0),    # Mindjárt itt a fotózás … Gyertek és segítek!
    ("v2_102402", 0.05, 10.15, 1),   # Az egyik legfontosabb szempont … oda az egész fotózás hangulata.
    ("v3_102634", 0.00, 15.00, 2),   # Második szempont … cserélgetitek egymás között a családtagokkal.
    ("v4_102948", 0.00, 12.62, 3),   # Tudjátok, itt a mintákra gondolok … elviszik rólatok a figyelmet.
    ("v4_102948", 17.86, 24.40, 3),  # helyette részesítsétek előnyben … kötött anyagú ruhákat.
    ("v5_103324", 0.10, 4.15, 4),    # Negyedik szempont a réteges öltözködés.
    ("v5_103324", 6.66, 12.60, 4),   # Jó kiegészítője lehet … vagy akár egy kardigán.
    ("v6_103743", 0.00, 6.97, 5),    # Ötödik szempont … igazi mentőmellények egy fotózáson.
    ("v7_104235", 0.00, 7.00, 6),    # Hatodik és egyben legfontosabb szempont … nem pótolja a nyugalmat.
    ("v7_104235", 12.00, 15.05, 6),  # Nálam nem kell pózolni, nem kell egy helyben ülni.
    ("v8_104413", 0.05, 9.05, 6),    # Játékos feladatokkal … maguktól születnek.
    ("v9_104611", 0.00, 9.45, 7),    # A videó alatt küldöm … Sziasztok!
]

# A whisper elírásainak javítása (szövegszinten, a hangfelvétel alapján). "" = a szó az előzőhöz olvad.
FIX = {
    "öltözzetek!": "öltözzetek?", "Gyertek": "Gyertek,",
    "összevállogattok,": "összeválogattok,", "cserégetitek": "cserélgetitek",
    "gondolok–": "gondolok:", "disznis,": "Disney-s,", "mancsőrjáratos": "Mancs őrjáratos",
    "ovodás": "óvodás", "Tudjátok": "Tudjátok,", "ruhákat,": "ruhákat.",
    "4.": "Negyedik", "kardigan,": "kardigán.", "mentő": "mentőmellények", "mellények": "",
    "6.": "Hatodik,", "szempont,": "szempont,", "videmsággal,": "vidámsággal,", "mosajok": "mosolyok", "fotózáson,": "fotózáson.",
    "küld": "küldöm", "mai": "", "tájékoztadót": "tájékoztatót",
}
# szakaszonként: az első szó nagybetűsítése, ha mondat közepén kezdünk
CAPITALIZE_FIRST = True
HIGHLIGHT = {"kényelmes", "harmonizáljanak.", "kettő", "három", "Disney-s,", "Mancs őrjáratos",
             "bársony", "kötött", "réteges", "kalap,", "mellény,", "kardigán.", "átmeneti",
             "mentőmellények", "nyugalom.", "nyugalmat.", "pózolni,", "mosolyok"}

# Fotók és kártyák: (fájl vagy kártya, felvétel, kezdet, vég, fókusz) – a felvétel idejében
PHOTOS = [
    ("KEP01027", "v2_102402", 4.30, 10.15, "50% 40%"),
    ("KEP07399-Edit", "v3_102634", 3.55, 7.10, "50% 50%"),
    ("@palette", "v3_102634", 7.10, 15.00, ""),
    ("KEP07575-Edit", "v4_102948", 17.78, 21.10, "50% 45%"),
    ("KEP02177_1", "v4_102948", 21.10, 24.40, "50% 45%"),
    ("KEP01860_1", "v5_103324", 6.66, 12.60, "50% 45%"),
    ("7", "v6_103743", 3.95, 6.97, "40% 50%"),
    ("KEP09578", "v7_104235", 12.00, 15.05, "50% 50%"),
    ("KEP09606", "v8_104413", 0.05, 4.60, "50% 45%"),
    ("KEP06552-Recovered", "v8_104413", 4.60, 9.05, "50% 45%"),
]

# Ezeknél a végpontoknál a következő szó szorosan rátapad: nem keresünk későbbre, és hosszabb hangáttűnés kell.
TIGHT_END = {("v2_102402", 10.15), ("v6_103743", 6.97)}

CHAPTERS = {1: "Kényelem", 2: "Színharmónia", 3: "Minták: a kevesebb több", 4: "Rétegek",
            5: "Átmeneti tárgy", 6: "Nyugalom"}


def load_words(take):
    d = json.load(open(os.path.join(W, take + ".json")))
    return d if isinstance(d, list) else d["words"]


_wav = {}
def energy(take):
    if take not in _wav:
        w = wave.open(os.path.join(W, take + ".wav")); sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        hop = sr // 100
        e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) + 1e-9 for i in range(len(x) // hop)])
        _wav[take] = 20 * np.log10(np.convolve(e, np.ones(3) / 3, mode="same"))
    return _wav[take]


def snap(take, t, before=0.12, after=0.12):
    """A vágópontot a [t-before, t+after] sáv leghalkabb 10 ms-ára húzzuk.
    Kezdőpontnál inkább korábbra, végpontnál inkább későbbre keresünk, hogy szót ne vágjunk el."""
    e = energy(take)
    i0, i1 = max(0, int((t - before) * 100)), min(len(e) - 1, int((t + after) * 100))
    if i1 <= i0:
        return t
    return (i0 + int(np.argmin(e[i0:i1 + 1]))) / 100


def main():
    segs, acc = [], 0
    for take, a, b, ch in SEGMENTS:
        a2 = max(0.0, snap(take, a, 0.15, 0.03)); b2 = snap(take, b, 0.03, 0.03 if (take, b) in TIGHT_END else 0.15)
        n = round((b2 - a2) * FPS)
        segs.append({"take": take, "in": a2, "out": round(a2 + n / FPS, 4), "frames": n,
                     "fade_out": 0.08 if (take, b) in TIGHT_END else 0.015,
                     "start": round(acc / FPS, 4), "chapter": ch})
        acc += n
    total = acc / FPS

    def to_cut(take, t):
        for s in segs:
            if s["take"] == take and s["in"] - 0.25 <= t <= s["out"] + 0.25:
                return round(s["start"] + min(max(t - s["in"], 0), s["out"] - s["in"]), 3)
        raise ValueError((take, t))

    # feliratcsoportok
    groups = []
    for s in segs:
        words = [w for w in load_words(s["take"]) if s["in"] <= (w["start"] + w["end"]) / 2 < s["out"]]
        toks = []
        for w in words:
            txt = FIX.get(w["text"], w["text"])
            if txt == "" and toks:
                toks[-1][2] = max(toks[-1][2], w["end"]); continue
            toks.append([txt, w["start"], w["end"]])
        if CAPITALIZE_FIRST and toks:
            toks[0][0] = toks[0][0][0].upper() + toks[0][0][1:]
        cur = []
        for i, (txt, st, en) in enumerate(toks):
            cur.append((txt, st, en))
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            # 4 szó után törünk, kivéve ha a mondatból már csak egy szó maradna
            last_of_sentence = nxt is not None and re.search(r"[.!?:,]$", nxt[0])
            brk = (nxt is None or (len(cur) >= 4 and not (last_of_sentence and len(cur) < 5)) or re.search(r"[.!?:]$", txt)
                   or (re.search(r",$", txt) and len(cur) >= 2) or (nxt and nxt[1] - en > 0.3))
            if brk:
                text = " ".join(f"*{t}*" if t in HIGHLIGHT else t for t, _, _ in cur)
                groups.append([to_cut(s["take"], max(cur[0][1], s["in"])),
                               to_cut(s["take"], min(cur[-1][2], s["out"])), text])
                cur = []
    # nyitás/zárás finomítás
    caps = []
    for i, (st, en, text) in enumerate(groups):
        st2 = max(st - 0.06, caps[-1][1] if caps else 0.1)
        nxt = groups[i + 1][0] - 0.04 if i + 1 < len(groups) else en + 0.3
        en2 = nxt if nxt - en < 0.4 else en + 0.2
        caps.append([round(st2, 3), round(max(min(en2, nxt), st2 + 0.3), 3), text])

    photos = [{"name": n, "start": to_cut(tk, a), "end": to_cut(tk, b), "pos": pos} for n, tk, a, b, pos in PHOTOS]
    chapters = []
    for ch, label in CHAPTERS.items():
        ss = [s for s in segs if s["chapter"] == ch]
        chapters.append({"n": ch, "label": label, "start": ss[0]["start"],
                         "end": round(ss[-1]["start"] + ss[-1]["frames"] / FPS, 4)})
    out = {"fps": FPS, "cut_len": round(total, 4), "segments": segs, "captions": caps,
           "photos": photos, "chapters": chapters, "hook_end": round(segs[0]["frames"] / FPS, 4)}
    json.dump(out, open(os.path.join(W, "edit.json"), "w"), ensure_ascii=False, indent=1)
    print(f"vágott hossz: {total:.2f} s, {len(caps)} feliratcsoport")
    for c in caps:
        print(f"  {c[0]:6.2f}-{c[1]:6.2f} {c[2]}")


if __name__ == "__main__":
    main()
