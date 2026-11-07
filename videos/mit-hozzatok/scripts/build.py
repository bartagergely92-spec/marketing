#!/usr/bin/env python3
"""A „Mit hozzatok magatokkal a fotózásra?” Reels kompozíciójának előállítása.

Minden időpontot a NYERS felvétel (VID_20261107_154444.mp4) idejében adunk meg,
a szkript ezt átszámolja a vágott (assets/kitti_cut.mp4) idővonalra.
A kimenet statikus HTML: index.html + compositions/*.html (Studióban szerkeszthető).
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30

# Megtartott szakaszok (nyers idő) – ugyanaz, mint a scripts/prepare.sh-ban.
SEGS = [(1.25, 3.54), (8.23, 9.24), (9.81, 13.98), (14.25, 25.42), (29.27, 33.15),
        (33.95, 35.07), (35.77, 36.62), (36.90, 42.33), (45.45, 53.18), (54.18, 55.30),
        (56.26, 59.37), (59.66, 69.29), (70.14, 71.27), (71.70, 74.66), (75.06, 82.57),
        (83.77, 86.60), (86.92, 93.90)]
FRAMES = [round((b - a) * FPS) for a, b in SEGS]
STARTS = []
acc = 0
for n in FRAMES:
    STARTS.append(acc / FPS)
    acc += n
CUT_LEN = acc / FPS                      # 72.9 s
END_CARD = 2.7
TOTAL = round(CUT_LEN + END_CARD, 3)


def cut(t):
    """Nyers idő → vágott idő (kivágott részbe eső időt a legközelebbi szélre húz)."""
    best = None
    for (a, b), s, n in zip(SEGS, STARTS, FRAMES):
        if a <= t <= a + n / FPS:
            return round(s + (t - a), 3)
        d = min(abs(t - a), abs(t - b))
        cand = s if abs(t - a) < abs(t - b) else s + n / FPS
        if best is None or d < best[0]:
            best = (d, cand)
    return round(best[1], 3)


# ---- Feliratok: (nyers kezdet, nyers vég, szöveg). „|” = csoporthatár, *szó* = sárga kiemelés.
# A szöveg a korábbi vágás feliratából származik (azt a hangból írták); a csoporthatárokat
# karakterarány szerint osztjuk szét, a beszéd szüneteihez igazítva.
PHRASES = [
    (8.33, 9.14, "Először is"),
    (9.91, 12.10, "a gyermeknek | a *kedvenc játékát*,"),
    (12.39, 13.88, "vagy egy *átmeneti tárgyat*."),
    (14.35, 15.96, "Új helyszínre megyünk,"),
    (16.34, 18.38, "illetve lehet, hogy | én is új vagyok számotokra,"),
    (18.38, 20.04, "hiszen még nem találkoztunk."),
    (20.20, 22.38, "Ilyenkor ezek a tárgyak | segítenek abban,"),
    (22.38, 25.36, "hogy a gyermek egy kicsit | *feloldódjon* az új helyzetben."),
    (29.37, 31.74, "Ilyen lehet például | a kedvenc *plüssé*,"),
    (32.18, 33.05, "vagy a *plédje*,"),
    (34.05, 34.97, "kis nyunyókája."),
    (35.87, 36.52, "Második:"),
    (37.00, 38.75, "már megbeszéltük a *ruhákat*,"),
    (38.75, 41.95, "amiket majd felvesztek | a fotózásra."),
    (45.55, 48.59, "*Kiegészítő kellékek*, | mint például egy *hajpánt*,"),
    (48.93, 53.08, "anya-lánya közös hajpánt | vagy közös *ékszerek*."),
    (54.28, 55.20, "A harmadik"),
    (56.36, 57.32, "lehet egy olyan tárgy,"),
    (57.50, 59.27, "amelyet szeretnétek, | hogy *megörökítsek*,"),
    (59.76, 61.45, "mondjuk, mert | számotokra *fontos*."),
    (61.72, 62.93, "Ilyen lehet például,"),
    (63.15, 66.30, "hogy sokat szoktatok | akár *labdázni*,"),
    (66.38, 69.19, "vagy *lufizni*, | azt is elhozhatjátok."),
    (70.24, 71.17, "A negyedik"),
    (71.80, 74.56, "lehet például egy *könyv*,"),
    (75.16, 77.95, "a kedvenc könyvetek, | vagy a gyermeknek | a kedvenc *könyve*."),
    (78.33, 80.80, "Egy-két kép erejéig | el tudjátok olvasni"),
    (80.80, 82.47, "ezeket a könyveket | a gyerekeknek."),
    (83.87, 86.50, "És az ötödik | és egyben *legfontosabb* kellék:"),
    (87.02, 88.42, "*ti magatok*, | a *jókedvetek*,"),
    (88.42, 90.93, "illetve a *nyitottságotok* | a fotózásra."),
    (91.23, 93.01, "Várlak szeretettel | benneteket,"),
    (93.34, 93.72, "sziasztok!"),
]

# ---- Fotók: (fájl, nyers kezdet, nyers vég, fókusz object-position)
PHOTOS = [
    ("Boti_1_eves-11", 10.95, 13.98, "50% 50%"),
    ("KEP01888", 20.15, 25.42, "45% 50%"),
    ("Zitaek-7", 32.10, 35.07, "60% 45%"),
    ("Zsuzsiek-9", 38.75, 48.85, "55% 50%"),
    ("Zitaek-2", 48.85, 53.18, "55% 45%"),
    ("Viki-12", 61.65, 69.29, "50% 60%"),
    ("KEP07843", 75.06, 82.57, "50% 45%"),
    ("KEP02968-Edit", 86.92, 91.05, "50% 50%"),
]
PHOTO_SIZE = {  # eredeti képarány (szélesség, magasság)
    "Boti_1_eves-11": (6000, 4000), "KEP01888": (6000, 4000), "Zitaek-7": (5239, 3183),
    "Zsuzsiek-9": (2084, 1318), "Zitaek-2": (6000, 3772), "Viki-12": (1389, 2084),
    "KEP07843": (3948, 5880), "KEP02968-Edit": (6140, 4214),
}

# ---- Fejezetcímkék: (szám, szöveg, nyers kezdet, nyers vég)
CHAPTERS = [
    (1, "Kedvenc játék, átmeneti tárgy", 8.23, 35.07),
    (2, "Kiegészítők", 35.77, 53.18),
    (3, "Egy fontos közös tárgy", 54.18, 69.29),
    (4, "Kedvenc könyv", 70.14, 82.57),
    (5, "Ti magatok és a jókedvetek", 83.77, 91.05),
]

# ---- Közelítés (punch-in) szakaszonként: 1.0 vagy 1.1, hogy a vágások ne ugorjanak
PUNCH = [1.0, 1.1, 1.0, 1.1, 1.0, 1.0, 1.1, 1.0, 1.0, 1.1, 1.0, 1.1, 1.0, 1.1, 1.0, 1.1, 1.0]

HOOK_END = cut(3.54)        # a horog-cím addig áll, amíg Kitti kimondja a kérdést


def caption_groups():
    groups = []
    for a, b, text in PHRASES:
        parts = [p.strip() for p in text.split("|")]
        lens = [len(p.replace("*", "")) for p in parts]
        tot = sum(lens)
        t = a
        for p, n in zip(parts, lens):
            e = t + (b - a) * n / tot
            groups.append([cut(t), cut(e), p])
            t = e
    # nyitás/zárás: kis előfutás, rövid utófutás; 0,35 mp-nél kisebb rést áthidalunk
    out = []
    for i, (s, e, p) in enumerate(groups):
        s2 = max(s - 0.06, out[-1][1] if out else 0)
        nxt = groups[i + 1][0] - 0.06 if i + 1 < len(groups) else e + 0.3
        e2 = nxt if nxt - e < 0.35 else e + 0.2
        out.append([round(s2, 3), round(min(e2, nxt), 3), p])
    return out


def rich(p):
    p = html.escape(p)
    return re.sub(r"\*(.+?)\*", r'<span class="hl">\1</span>', p)


def write(path, s):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(s)


# =========================== index.html ===========================
# A színkorrekciót a `hyperframes media-treatment` írja az index.html-be; újraépítéskor megtartjuk.
_grade = ""
_idx = os.path.join(ROOT, "index.html")
if os.path.exists(_idx):
    _m = re.search(r'data-color-grading="[^"]*"', open(_idx, encoding="utf-8").read())
    if _m:
        _grade = " " + _m.group(0)

punch_sets = "\n".join(
    f'      tl.set("#kitti-wrap", {{ scale: {z}, y: 0 }}, {s:.3f});' for z, s in zip(PUNCH[1:], STARTS[1:]))
punch_sets = '      tl.set("#kitti-wrap", { scale: 1.12, y: -150 }, 0);  // horog: arc feljebb, alatta a cím\n' + punch_sets

# Amíg egy fotó teljesen látszik, Kitti képét elrejtjük alatta (különben a render halványan átengedi)
punch_sets += "\n" + "\n".join(
    f'      tl.set("#kitti-wrap", {{ opacity: 0 }}, {cut(pa) + 0.22:.3f});\n'
    f'      tl.set("#kitti-wrap", {{ opacity: 1 }}, {cut(pb) - 0.16:.3f});' for _, pa, pb, _ in PHOTOS)

music_lane = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.13}, {"t": round(CUT_LEN - 0.3, 2), "v": 0.13},
    {"t": round(CUT_LEN + 0.3, 2), "v": 0.42}, {"t": TOTAL, "v": 0.42}]}]}).replace('"', "&quot;")

index = f"""<!doctype html>
<html lang="hu" data-composition-variables='[
  {{"id":"accent","type":"color","label":"Kiemelőszín","default":"#FFC83F"}},
  {{"id":"ink","type":"color","label":"Sötét szövegszín","default":"#2A211B"}}
]'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      :root {{
        --accent: #FFC83F;
        --ink: #2A211B;
        --cream: #F6E4C6;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #111; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "Poppins", sans-serif; }}
      #kitti-wrap {{ position: absolute; inset: 0; transform-origin: 50% 32%; }}
      #kitti {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="kitti-wrap">
        <video id="kitti" class="clip" src="assets/kitti_cut.mp4" data-start="0" data-duration="{CUT_LEN}"
          data-track-index="0" data-has-audio="true" data-volume="1" playsinline{_grade}></video>
      </div>

      <div id="photos" data-composition-id="photos" data-composition-src="compositions/photos.html"
        data-start="0" data-duration="{CUT_LEN}" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:2"></div>

      <div id="chapters" data-composition-id="chapters" data-composition-src="compositions/chapters.html"
        data-start="0" data-duration="{CUT_LEN}" data-track-index="2" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:3"></div>

      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{CUT_LEN}" data-track-index="3" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index:4"></div>

      <div id="endcard" data-composition-id="endcard" data-composition-src="compositions/endcard.html"
        data-start="{round(CUT_LEN - 0.25, 3)}" data-duration="{round(END_CARD + 0.25, 3)}" data-track-index="4"
        data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:5"></div>

      <audio id="music" class="clip" src="assets/music/cheerful-joyful-playful.mp3" data-start="0"
        data-duration="{TOTAL}" data-track-index="5" data-volume="1" data-fade-in="0.4" data-fade-out="0.9"
        data-automation="{music_lane}"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // Közelítés váltása minden vágásnál (szakaszkezdetek a vágott idővonalon)
{punch_sets}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
write("index.html", index)

# =========================== captions ===========================
caps = caption_groups()
cap_html = "\n".join(
    f'    <div id="cap-{i}" class="cap clip" data-start="{s}" data-duration="{round(e - s, 3)}">'
    f'<span class="cap-in">{rich(p)}</span></div>' for i, (s, e, p) in enumerate(caps))
cap_js = "\n".join(
    f'    tl.fromTo("#cap-{i} .cap-in", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.14, ease: "power3.out" }}, {s});'
    for i, (s, e, p) in enumerate(caps))
write("compositions/captions.html", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{ position: absolute; left: 60px; right: 60px; bottom: 640px; text-align: center; overflow: visible; }}
    .cap-in {{
      display: inline-block; max-width: 960px; padding: 10px 26px 14px; border-radius: 22px;
      background: rgba(24, 18, 14, 0.42);
      font-family: "Poppins", sans-serif; font-weight: 700; font-size: 62px; line-height: 1.18;
      color: #fff; letter-spacing: -0.01em;
      text-shadow: 0 2px 0 rgba(0,0,0,.55), 0 0 14px rgba(0,0,0,.35);
    }}
    .hl {{ color: var(--accent, #FFC83F); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{cap_html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{cap_js}
    window.__timelines["captions"] = tl;
  </script>
</template>
""")

# =========================== photos ===========================
BOX_W, BOX_H, BOX_TOP = 960, 830, 300
ph_html, ph_js = [], []
for i, (name, a, b, pos) in enumerate(PHOTOS):
    s, e = cut(a), cut(b)
    w, h = PHOTO_SIZE[name]
    sc = min(BOX_W / w, BOX_H / h)
    cw, ch = round(w * sc), round(h * sc)
    left = (1080 - cw) // 2
    top = BOX_TOP + (BOX_H - ch) // 2
    d = round(e - s, 3)
    ph_html.append(f'''    <div id="ph-{i}" class="ph clip" data-start="{s}" data-duration="{d}">
      <div class="ph-layer">
        <img class="ph-bg" src="assets/photos/{name}-bg.jpg" alt="" />
        <div class="ph-card" data-layout-allow-overflow style="left:{left}px; top:{top}px; width:{cw}px; height:{ch}px">
          <img class="ph-img" src="assets/photos/{name}.jpg" alt="" style="object-position:{pos}" />
        </div>
      </div>
    </div>''')
    ph_js.append(f'''    tl.fromTo("#ph-{i} .ph-layer", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, {s});
    tl.fromTo("#ph-{i} .ph-card", {{ scale: 0.94, filter: "blur(8px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {s});
    tl.fromTo("#ph-{i} .ph-img", {{ scale: 1.0 }}, {{ scale: 1.06, duration: {d}, ease: "none" }}, {s});
    tl.to("#ph-{i} .ph-layer", {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, {round(e - 0.14, 3)});''')
write("compositions/photos.html", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .ph, .ph-layer {{ position: absolute; inset: 0; }}
    .ph-bg {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    .ph-card {{
      position: absolute; overflow: hidden; border-radius: 26px; border: 10px solid #FFFDF8;
      box-shadow: 0 30px 70px rgba(0,0,0,.35);
    }}
    .ph-img {{ width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }}
  </style>
  <div id="root" data-composition-id="photos" data-width="1080" data-height="1920">
{chr(10).join(ph_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(ph_js)}
    window.__timelines["photos"] = tl;
  </script>
</template>
""")

# =========================== chapters + hook ===========================
ch_html = [f'''    <div id="hook" class="clip" data-start="0" data-duration="{HOOK_END}">
      <div class="hook-in">
        <div class="hook-title">Mit hozzatok magatokkal<br />a <span class="hl">fotózásra?</span></div>
      </div>
    </div>
    <div id="hook-chip" class="clip" data-start="0" data-duration="{HOOK_END}">
      <div class="chap-in"><span class="chap-num">5</span><span class="chap-txt">tipp a fotózásra</span></div>
    </div>''']
ch_js = [f'''    tl.to("#hook-chip .chap-in", {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, {round(HOOK_END - 0.16, 3)});
    tl.to("#hook .hook-in", {{ opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power2.in" }}, {round(HOOK_END - 0.18, 3)});''']
for n, text, a, b in CHAPTERS:
    s, e = cut(a), cut(b)
    ch_html.append(f'''    <div id="chap-{n}" class="chap clip" data-start="{s}" data-duration="{round(e - s, 3)}">
      <div class="chap-in"><span class="chap-num">{n}</span><span class="chap-txt">{html.escape(text)}</span></div>
    </div>''')
    ch_js.append(f'''    tl.fromTo("#chap-{n} .chap-in", {{ opacity: 0, y: -16, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, {s});
    tl.to("#chap-{n} .chap-in", {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, {round(e - 0.16, 3)});''')
write("compositions/chapters.html", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; font-family: "Poppins", sans-serif; }}
    #hook {{ position: absolute; left: 0; right: 0; top: 1030px; text-align: center; }}
    #hook-chip {{ position: absolute; left: 0; right: 0; top: 196px; text-align: center; }}
    .hook-chip {{
      display: inline-block; padding: 8px 26px; border-radius: 999px; margin-bottom: 18px;
      background: var(--accent, #FFC83F); color: var(--ink, #2A211B); font-weight: 700; font-size: 44px;
    }}
    .hook-title {{
      font-weight: 800; font-size: 88px; line-height: 1.06; color: #fff; letter-spacing: -0.02em;
      text-shadow: 0 4px 0 rgba(0,0,0,.45), 0 0 30px rgba(0,0,0,.45);
    }}
    .hook-title .hl {{ color: var(--accent, #FFC83F); }}
    .chap {{ position: absolute; left: 0; right: 0; top: 196px; text-align: center; }}
    .chap-in {{
      display: inline-flex; align-items: center; gap: 16px; padding: 10px 30px 10px 12px; border-radius: 999px;
      background: var(--accent, #FFC83F); color: var(--ink, #2A211B); font-weight: 700; font-size: 42px;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }}
    .chap-num {{
      display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px;
      border-radius: 50%; background: var(--ink, #2A211B); color: var(--accent, #FFC83F); font-size: 40px;
    }}
  </style>
  <div id="root" data-composition-id="chapters" data-width="1080" data-height="1920">
{chr(10).join(ch_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(ch_js)}
    window.__timelines["chapters"] = tl;
  </script>
</template>
""")

# =========================== end card ===========================
write("compositions/endcard.html", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; font-family: "Poppins", sans-serif; }}
    #end-bg {{ position: absolute; inset: 0; background: var(--cream, #F6E4C6); transform-origin: 50% 100%; }}
    #end-logo {{ position: absolute; left: 290px; top: 230px; width: 500px; height: auto; }}
    #end-text {{ position: absolute; left: 0; right: 0; top: 1000px; text-align: center; color: var(--ink, #2A211B); }}
    .end-l1 {{ font-weight: 800; font-size: 66px; line-height: 1.1; letter-spacing: -0.015em; }}
    .end-l2 {{ font-weight: 600; font-size: 46px; margin-top: 18px; opacity: .85; }}
    .end-url {{
      display: inline-block; margin-top: 34px; padding: 12px 34px; border-radius: 999px;
      background: var(--accent, #FFC83F); font-weight: 700; font-size: 48px;
    }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="end-bg" class="clip" data-start="0" data-duration="{round(END_CARD + 0.25, 3)}"></div>
    <img id="end-logo" class="clip" src="assets/logo.png" alt="Mosolyművész" data-start="0.15" data-duration="{round(END_CARD + 0.1, 3)}" />
    <div id="end-text" class="clip" data-start="0.35" data-duration="{round(END_CARD - 0.1, 3)}">
      <div class="end-l1">Szabad karácsonyi<br />időpontok</div>
      <div class="end-l2">Link az első kommentben</div>
      <div class="end-url">mosolymuvesz.hu</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#end-bg", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.4, ease: "power2.inOut" }}, 0);
    tl.fromTo("#end-logo", {{ opacity: 0, scale: 0.8, y: 40 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.6, ease: "back.out(1.4)" }}, 0.15);
    tl.fromTo("#end-text", {{ opacity: 0, y: 24, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, 0.35);
    window.__timelines["endcard"] = tl;
  </script>
</template>
""")

print(f"cut={CUT_LEN} total={TOTAL} captions={len(caps)} hook_end={HOOK_END}")
for s, e, p in caps[:6]:
    print(f"  {s:6.2f}-{e:6.2f} {p}")
