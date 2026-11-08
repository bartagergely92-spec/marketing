#!/usr/bin/env python3
"""A „Mit vegyetek fel a karácsonyi fotózásra?” Reels kompozíciója.

Bemenet: work/edit.json (scripts/plan.py állítja elő). Kimenet: index.html + compositions/*.html.
A kimenet statikus HTML, a HyperFrames desktop appban szerkeszthető.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(ROOT, "work", "edit.json"), encoding="utf-8"))
CUT_LEN = E["cut_len"]
END_CARD = 3.0
TOTAL = round(CUT_LEN + END_CARD, 3)
HOOK_END = E["hook_end"]
HOOK_TITLE_END = 3.0   # a nagy cím addig áll; utána jönnek a feliratok (nem fedik egymást)
SEGS = E["segments"]

PHOTO_SIZE = {}
try:
    from PIL import Image
    for p in E["photos"]:
        if not p["name"].startswith("@"):
            with Image.open(os.path.join(ROOT, "assets", "photos", p["name"] + ".jpg")) as im:
                PHOTO_SIZE[p["name"]] = im.size
except Exception as ex:  # a méretek nélkül is működik (fekvő képaránnyal számol)
    print("figyelem: képméretek nem olvashatók:", ex)

# Közelítés szakaszonként (1.0 / 1.1 váltakozva), a horog alatt Kitti feljebb, hogy a cím ne takarja az arcát
PUNCH = [1.0 if i % 2 == 0 else 1.1 for i in range(len(SEGS))]

# Színpaletta – a blogcikk színei (mosolymuvesz.hu/tippek/mit-vegyunk-fel-a-karacsonyi-fotozasra/)
PALETTE = [
    ("Klasszikus ünnepi", [("bordó", "#7A1F2B"), ("fenyőzöld", "#1F4D3A"), ("meleg piros", "#B3262E"),
                            ("krém", "#F1E4CC"), ("törtfehér", "#F8F4EA")]),
    ("Meleg, természetes", [("bézs", "#D8C2A3"), ("konyak", "#8B4A2B"), ("tejeskávé", "#B48A68"),
                             ("mogyoró", "#9C6B45")]),
    ("Finom pasztell", [("lágy szürke", "#C8C6C2"), ("púder rózsa", "#E7C3C3"), ("pasztell kék", "#B8CDE2")]),
]

_grade = ""
_idx = os.path.join(ROOT, "index.html")
if os.path.exists(_idx):
    _m = re.search(r'data-color-grading="[^"]*"', open(_idx, encoding="utf-8").read())
    if _m:
        _grade = " " + _m.group(0)


def rich(p):
    return re.sub(r"\*(.+?)\*", r'<span class="hl">\1</span>', html.escape(p))


def write(path, s):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(s)


# =========================== index.html ===========================
sets = ['      tl.set("#kitti-wrap", { scale: 1.12, y: -150 }, 0);  // horog: arc feljebb, alatta a cím']
sets.append(f'      tl.set("#kitti-wrap", {{ scale: 1.0, y: 0 }}, {HOOK_TITLE_END:.3f});  // a cím után normál nézet')
for z, s in list(zip(PUNCH, SEGS))[1:]:
    sets.append(f'      tl.set("#kitti-wrap", {{ scale: {z}, y: 0 }}, {s["start"]:.3f});')
for p in E["photos"]:   # a teljesen látszó fotó/kártya alatt Kitti képe rejtve
    sets.append(f'      tl.set("#kitti-wrap", {{ opacity: 0 }}, {p["start"] + 0.22:.3f});')
    sets.append(f'      tl.set("#kitti-wrap", {{ opacity: 1 }}, {p["end"] - 0.16:.3f});')

music_lane = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.12}, {"t": round(CUT_LEN - 0.3, 2), "v": 0.12},
    {"t": round(CUT_LEN + 0.3, 2), "v": 0.42}, {"t": TOTAL, "v": 0.42}]}]}).replace('"', "&quot;")

write("index.html", f"""<!doctype html>
<html lang="hu" data-composition-variables='[
  {{"id":"accent","type":"color","label":"Kiemelőszín","default":"#FFC83F"}},
  {{"id":"ink","type":"color","label":"Sötét szövegszín","default":"#2A211B"}}
]'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      :root {{ --accent: #FFC83F; --ink: #2A211B; --cream: #F6E4C6; }}
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

      <audio id="music" class="clip" src="assets/music/cheerful-joyful-playful-maksymmalko.mp3" data-start="0"
        data-duration="{TOTAL}" data-track-index="5" data-volume="1" data-fade-in="0.4" data-fade-out="0.9"
        data-automation="{music_lane}"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(sets)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""")

# =========================== captions ===========================
caps = [c for c in E["captions"] if c[0] >= HOOK_TITLE_END - 0.2]
if caps and caps[0][0] < HOOK_TITLE_END:
    caps[0][0] = HOOK_TITLE_END
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
{chr(10).join(f'    <div id="cap-{i}" class="cap clip" data-start="{s}" data-duration="{round(e - s, 3)}"><span class="cap-in">{rich(p)}</span></div>' for i, (s, e, p) in enumerate(caps))}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(f'    tl.fromTo("#cap-{i} .cap-in", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.14, ease: "power3.out" }}, {s});' for i, (s, e, p) in enumerate(caps))}
    window.__timelines["captions"] = tl;
  </script>
</template>
""")

# =========================== photos + palette card ===========================
BOX_W, BOX_H, BOX_TOP = 960, 830, 300
ph_html, ph_js = [], []
for i, p in enumerate(E["photos"]):
    s, e, name = p["start"], p["end"], p["name"]
    d = round(e - s, 3)
    if name == "@palette":
        rows = []
        for r, (label, cols) in enumerate(PALETTE):
            sw = "".join(f'<div class="sw"><div class="dot" style="background:{c}"></div><div class="sw-n">{html.escape(n)}</div></div>'
                         for n, c in cols)
            rows.append(f'<div class="pal-row" id="pal-row-{r}"><div class="pal-l">{html.escape(label)}</div><div class="pal-sw">{sw}</div></div>')
        ph_html.append(f'''    <div id="ph-{i}" class="ph clip" data-start="{s}" data-duration="{d}">
      <div class="ph-layer pal-bg">
        <div class="pal-card">
          <div class="pal-title">Válasszatok <span class="hl">2–3</span> harmonizáló színt</div>
          {"".join(rows)}
        </div>
      </div>
    </div>''')
        ph_js.append(f'''    tl.fromTo("#ph-{i} .ph-layer", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, {s});
    tl.fromTo("#ph-{i} .pal-card", {{ y: 40, scale: 0.96 }}, {{ y: 0, scale: 1, duration: 0.5, ease: "expo.out" }}, {s});''')
        for r in range(len(PALETTE)):
            ph_js.append(f'''    tl.fromTo("#pal-row-{r}", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "expo.out" }}, {round(s + 0.35 + r * 0.9, 3)});''')
        ph_js.append(f'''    tl.to("#ph-{i} .ph-layer", {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, {round(e - 0.14, 3)});''')
        continue
    w, h = PHOTO_SIZE.get(name, (3, 2))
    sc = min(BOX_W / w, BOX_H / h)
    cw, ch = round(w * sc), round(h * sc)
    left, top = (1080 - cw) // 2, BOX_TOP + (BOX_H - ch) // 2
    ph_html.append(f'''    <div id="ph-{i}" class="ph clip" data-start="{s}" data-duration="{d}">
      <div class="ph-layer">
        <img class="ph-bg" src="assets/photos/{name}-bg.jpg" alt="" />
        <div class="ph-card" data-layout-allow-overflow style="left:{left}px; top:{top}px; width:{cw}px; height:{ch}px">
          <img class="ph-img" src="assets/photos/{name}.jpg" alt="" style="object-position:{p['pos']}" />
        </div>
      </div>
    </div>''')
    ph_js.append(f'''    tl.fromTo("#ph-{i} .ph-layer", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, {s});
    tl.fromTo("#ph-{i} .ph-card", {{ scale: 0.94, filter: "blur(8px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {s});
    tl.fromTo("#ph-{i} .ph-img", {{ scale: 1.0 }}, {{ scale: 1.06, duration: {d}, ease: "none" }}, {s});
    tl.to("#ph-{i} .ph-layer", {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, {round(e - 0.14, 3)});''')

write("compositions/photos.html", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; font-family: "Poppins", sans-serif; }}
    .ph, .ph-layer {{ position: absolute; inset: 0; }}
    .ph-layer {{ opacity: 0; }}
    .ph-bg {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    .ph-card {{ position: absolute; overflow: hidden; border-radius: 26px; border: 10px solid #FFFDF8; box-shadow: 0 30px 70px rgba(0,0,0,.35); }}
    .ph-img {{ width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }}
    .pal-bg {{ background: #EADBC4; }}
    .pal-card {{
      position: absolute; left: 60px; right: 60px; top: 280px; padding: 34px 40px 26px; border-radius: 34px;
      background: #FFFDF8; box-shadow: 0 30px 70px rgba(60,40,20,.18); color: var(--ink, #2A211B);
    }}
    .pal-title {{ font-weight: 800; font-size: 48px; line-height: 1.1; letter-spacing: -0.015em; margin-bottom: 14px; text-align: center; }}
    .pal-title .hl {{ background: var(--accent, #FFC83F); padding: 0 12px; border-radius: 12px; }}
    .pal-row {{ margin-top: 18px; }}
    .pal-l {{ font-weight: 700; font-size: 34px; margin-bottom: 8px; }}
    .pal-sw {{ display: flex; gap: 10px; }}
    .sw {{ width: 164px; text-align: center; }}
    .dot {{ width: 88px; height: 88px; margin: 0 auto 6px; border-radius: 50%; border: 3px solid rgba(42,33,27,.12); }}
    .sw-n {{ font-weight: 600; font-size: 30px; line-height: 1.1; }}
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

# =========================== hook + chapters ===========================
ch_html = [f'''    <div id="hook-chip" class="clip" data-start="0" data-duration="{HOOK_END}">
      <div class="chap-in"><span class="chap-num">6</span><span class="chap-txt">ruhatipp óvónénitől</span></div>
    </div>
    <div id="hook" class="clip" data-start="0" data-duration="{HOOK_TITLE_END}">
      <div class="hook-in"><div class="hook-title">Mit vegyetek fel<br />a <span class="hl">karácsonyi</span><br /><span class="hl">fotózásra?</span></div></div>
    </div>''']
ch_js = [f'''    tl.to("#hook-chip .chap-in", {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, {round(HOOK_END - 0.16, 3)});
    tl.to("#hook .hook-in", {{ opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power2.in" }}, {round(HOOK_TITLE_END - 0.18, 3)});''']
for c in E["chapters"]:
    s, e, n = c["start"], c["end"], c["n"]
    ch_html.append(f'''    <div id="chap-{n}" class="chap clip" data-start="{s}" data-duration="{round(e - s, 3)}">
      <div class="chap-in"><span class="chap-num">{n}</span><span class="chap-txt">{html.escape(c["label"])}</span></div>
    </div>''')
    ch_js.append(f'''    tl.fromTo("#chap-{n} .chap-in", {{ opacity: 0, y: -16, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }}, {s});
    tl.to("#chap-{n} .chap-in", {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, {round(e - 0.16, 3)});''')
write("compositions/chapters.html", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; font-family: "Poppins", sans-serif; }}
    #hook {{ position: absolute; left: 0; right: 0; top: 1000px; text-align: center; }}
    .hook-title {{
      font-weight: 800; font-size: 86px; line-height: 1.04; color: #fff; letter-spacing: -0.02em;
      text-shadow: 0 4px 0 rgba(0,0,0,.45), 0 0 30px rgba(0,0,0,.45);
    }}
    .hook-title .hl {{ color: var(--accent, #FFC83F); }}
    #hook-chip, .chap {{ position: absolute; left: 0; right: 0; top: 196px; text-align: center; }}
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
    #end-logo {{ position: absolute; left: 315px; top: 220px; width: 450px; height: auto; }}
    #end-text {{ position: absolute; left: 0; right: 0; top: 920px; text-align: center; color: var(--ink, #2A211B); }}
    .end-l1 {{ font-weight: 800; font-size: 62px; line-height: 1.1; letter-spacing: -0.015em; }}
    .end-l2 {{ font-weight: 600; font-size: 44px; margin-top: 18px; opacity: .85; }}
    .end-url {{ display: inline-block; margin-top: 30px; padding: 12px 34px; border-radius: 999px; background: var(--accent, #FFC83F); font-weight: 700; font-size: 46px; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="end-bg" class="clip" data-start="0" data-duration="{round(END_CARD + 0.25, 3)}"></div>
    <img id="end-logo" class="clip" src="assets/logo.png" alt="Mosolyművész" data-start="0.15" data-duration="{round(END_CARD + 0.1, 3)}" />
    <div id="end-text" class="clip" data-start="0.35" data-duration="{round(END_CARD - 0.1, 3)}">
      <div class="end-l1">Részletes ruhatippek<br />és színpaletta</div>
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
print(f"cut={CUT_LEN} total={TOTAL} captions={len(caps)} photos={len(E['photos'])}")
