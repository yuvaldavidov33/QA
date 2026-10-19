"""Generate reel4/index.html ("למה אנשים לא מתמידים"): same approved style as reel3 (face-centered zooms,
2-4 word captions, royal-blue key words, smooth glide-in cards, full-screen motion-graphics pages,
text behind the trainer, Instagram DM CTA). Content written for the reel4 script.

usage: build4.py <face.json> <words.json> <out index.html> <video src> <first cutout frame> <last cutout frame>
"""
import json
import random
import os
import sys

face = json.load(open(sys.argv[1]))
words = json.load(open(sys.argv[2]))
OUT, VIDEO = sys.argv[3], sys.argv[4]
CUT_A, CUT_B = int(sys.argv[5]), int(sys.argv[6])
SPEECH_END = 19.87
DURATION = 21.0  # last frame holds ~1.1 s so the DM notification stays readable
KEYWORDS = {"אחרת", "הפעם"}


def smooth(vals, sigma=14):
    """Heavier temporal smoothing of the face track for the zoom origin (about half a second)."""
    import math
    r = int(sigma * 3)
    k = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-r, r + 1)]
    n = len(vals)
    out = []
    for i in range(n):
        acc = wsum = 0.0
        for j, w in zip(range(i - r, i + r + 1), k):
            acc += vals[min(n - 1, max(0, j))] * w
            wsum += w
        out.append(round(acc / wsum, 2))
    return out


def t(word, nth=1):
    hits = [w["t"] for w in words if w["w"] == word]
    return hits[nth - 1]


def after(word, nth=1):
    i = [k for k, w in enumerate(words) if w["w"] == word][nth - 1]
    nxt = words[i + 1]["t"] if i + 1 < len(words) else SPEECH_END
    return min(nxt, words[i].get("segEnd", nxt))


# Captions only where no page, hook or big text is on screen.
CHUNKS = [
    ["בדיוק", "בגלל", "זה"], ["בנינו", "את", "הסטודיו"], ["בצורה", "קצת", "אחרת"],
    ["אם", "אתם", "רוצים"], ["שהפעם", "זה", "באמת"], ["יהיה", "חלק"], ["מהשגרה", "שלכם"],
]
captions = []
for ch in CHUNKS:
    i = next(k for k, w in enumerate(words) if w["w"] == ch[0] and [x["w"] for x in words[k:k + len(ch)]] == ch)
    start = words[i]["t"]
    j = i + len(ch)
    end = words[j]["t"] if j < len(words) else SPEECH_END
    seg_end = next((w["segEnd"] for w in words[i:j] if "segEnd" in w), None)
    if seg_end is not None:
        end = min(end, seg_end + 0.25)
    captions.append({"words": ch, "start": round(start - 0.04, 2), "end": round(end, 2)})
# "אחרת" leads straight into the solution page.
TIMES = {}
TIMES["sol_in"] = after("אחרת") + 0.05
captions[2]["end"] = round(min(captions[2]["end"], TIMES["sol_in"] - 0.05), 2)


def esc_words(ws):
    return " ".join(
        f'<span class="w{" key key-royal" if w.strip("?") in KEYWORDS or w == "שהפעם" else ""}">{w}</span>' for w in ws)


cap_html = "\n".join(
    f'      <div class="cap clip{" hi" if c["start"] >= t("יהיה") - 0.1 else ""}" id="cap{i}" data-start="{c["start"]}"'
    f' data-duration="{round(c["end"] - c["start"], 2)}" data-track-index="2"><div class="cap-in">{esc_words(c["words"])}</div></div>'
    for i, c in enumerate(captions))

TIMES.update({
    # Hook: two phrases, each enters whole.
    "hk_a": 0.06, "hk_a2": t("למה") - 0.06, "hk_out": t("באימונים") + 0.06,
    "hk_b": t("לא") - 0.06,
    # Reasons page (full screen): zoom-blur in, rows glide in as spoken, light-leak flash, hard cut at its peak back to the video on "ואז".
    "rs_in": t("מתחילים") - 0.04, "rs_1": t("מתחילים") + 0.08, "rs_2": t("מתאמנים") - 0.08, "rs_3": t("יודעים") - 0.12,
    "rs_out": t("ואז") - 0.02,
    # "אחרי חודש / מפסיקים" behind the trainer, calendar ticking to 30, drops on "מפסיקים".
    "tb_in": t("אחרי") - 0.1, "tb_big": t("מפסיקים") - 0.1, "tb_out": t("בדיוק", 2) - 0.3,
    # Solution page: rows with blue checks and live visuals; hard cut back (over-exposed settle) on "אם".
    "so_1": t("קבוצה") - 0.08, "so_2": t("בניית") - 0.1, "so_3": t("מעקב") - 0.1, "so_4": t("והתקדמות") - 0.1,
    "sol_out": t("אם") - 0.03,
    # CTA: Instagram DM notification.
    "dm_in": t("יהיה") - 0.05,
})
T_ = TIMES

ZOOM = [
    ("set", 0.0, 1.00, 0),
    ("push", 0.0, 1.08, T_["rs_in"]),
    # back on the video after the reasons page
    # (fix: one smooth push from the reasons page to the solution page; the old keys used the wrong "בדיוק"
    # and stacked a punch and a snap, which read as shaking)
    ("set", T_["rs_out"], 1.03, 0),
    ("push", T_["rs_out"], 1.14, T_["sol_in"] - T_["rs_out"]),
    ("set", T_["sol_out"], 1.00, 0),
    ("push", T_["sol_out"], 1.10, T_["dm_in"] - T_["sol_out"]),
    ("punch", t("שהפעם"), 1.16, 0.5),
    ("push", t("שהפעם") + 0.5, 1.20, DURATION - t("שהפעם") - 0.5),
]

PERSON = ('<svg viewBox="0 0 24 24" class="{cls}"><circle cx="12" cy="7" r="4.2"/>'
          '<path d="M3.5 23c0-4.7 3.8-8.5 8.5-8.5s8.5 3.8 8.5 8.5z"/></svg>')


def letters(word_list, cls):
    return "&nbsp;".join("".join(f'<span class="{cls}">{ch}</span>' for ch in w) for w in word_list)


TB_A, TB_B = letters(["אחרי", "חודש"], "la"), letters(["מפסיקים"], "lb")

# Live visuals for each row (left side of the row, RTL page).
VIS_ENERGY = ('<div class="vis energy"><div class="batt"><i id="battFill"></i><b id="battPct">0%</b></div>'
              '<div class="cap-tip"></div></div>')
VIS_ALONE = ('<div class="vis alone">' + "".join(
    PERSON.format(cls=f"ghost g{k}") for k in range(4)) + PERSON.format(cls="solo") + '</div>')
VIS_Q = '<div class="vis qs"><span class="q q0">?</span><span class="q q1">?</span><span class="q q2">?</span><span class="q big" id="qBig">?</span></div>'
VIS_SIX = '<div class="vis six">' + "".join(PERSON.format(cls=f"p6 p6-{k}") for k in range(6)) + '<b id="sixN">0</b></div>'
VIS_PLAN = ('<div class="vis plan"><div class="sheet"><div class="hd"><i></i><b>התכנית שלך</b></div>' + "".join(
    f'<div class="ln"><span class="ck">✓</span><i style="width:{w}px"></i></div>' for w in (150, 118, 170, 132)) + '</div></div>')
VIS_KG = ('<div class="vis kg"><svg viewBox="-110 -50 220 100" class="db"><g fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">'
          '<line x1="-46" y1="0" x2="46" y2="0"/><rect x="-78" y="-34" width="22" height="68" rx="6"/><rect x="56" y="-34" width="22" height="68" rx="6"/>'
          '<line x1="-94" y1="-16" x2="-94" y2="16"/><line x1="94" y1="-16" x2="94" y2="16"/></g></svg>'
          '<div class="num"><b id="kgN">40</b><span>ק״ג</span></div><div class="up" id="kgUp">▲</div></div>')
GRAPH_PTS = [(10, 150), (60, 132), (105, 138), (150, 104), (195, 110), (240, 72), (285, 52), (320, 22)]
GRAPH_D = "M " + " L ".join(f"{x} {y}" for x, y in GRAPH_PTS)
VIS_GRAPH = ('<div class="vis graph"><svg viewBox="0 0 330 170"><g stroke="rgba(255,255,255,.1)" stroke-width="2">'
             + "".join(f'<line x1="0" y1="{y}" x2="330" y2="{y}"/>' for y in (40, 85, 130)) +
             f'</g><path id="gArea" d="{GRAPH_D} L 320 170 L 10 170 Z" fill="url(#gFill)" opacity="0"/>'
             f'<path id="gLine" d="{GRAPH_D}" fill="none" stroke="#5b86ff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"'
             ' style="filter: drop-shadow(0 0 10px rgba(80,130,255,.9))"/><circle id="gDot" r="11" fill="#fff"/>'
             '<defs><linearGradient id="gFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a64f0" stop-opacity=".55"/>'
             '<stop offset="1" stop-color="#3a64f0" stop-opacity="0"/></linearGradient></defs></svg></div>')


def row(rid, badge, main, sub, vis):
    return (f'<div class="row" id="{rid}"><div class="txt"><span class="badge {badge}">{"✕" if badge == "x" else "✓"}</span>'
            f'<div><div class="m">{main}</div>{f"<div class=s>{sub}</div>" if sub else ""}</div></div>{vis}</div>')


REASONS = "\n".join([
    row("r1", "x", "מתחילים חזק מדי", "", VIS_ENERGY),
    row("r2", "x", "מתאמנים לבד", "בלי אף אחד שידחוף", VIS_ALONE),
    row("r3", "x", "לא יודעים", "מה בדיוק לעשות", VIS_Q),
])
SOLUTION = "\n".join(f'<div class="rw">{r}</div>' for r in [
    row("s1", "v", "עד 6 מתאמנים", "בקבוצה קטנה", VIS_SIX),
    row("s2", "v", "תכנית אישית", "לכל מתאמן", VIS_PLAN),
    row("s3", "v", "מעקב משקלים", "בכל אימון", VIS_KG),
    row("s4", "v", "והתקדמות", "שרואים בעיניים", VIS_GRAPH),
])
# Dust specks lying on the solution page's plane.
_r2 = random.Random(5)
DUST = "".join(
    f'<i class="dust" style="left:{_r2.uniform(-10, 110):.1f}%;top:{_r2.uniform(-1400, 3300):.0f}px;opacity:{_r2.uniform(.2, .8):.2f};'
    f'width:{_r2.choice([3, 4, 4, 6, 9])}px;height:{_r2.choice([3, 4, 4])}px"></i>' for _ in range(120))

html = f"""<!doctype html>
<html lang="he" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="stylesheet" href="fonts.css" />
    <script src="gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      :root {{ --red: #ff3340; --green: #39e46b; --royal: #3a64f0; --blue: #5b86ff; }}
      #cam {{ position: absolute; inset: 0; overflow: hidden; }}
      #frame {{ position: absolute; inset: 0; will-change: transform; }}
      #cutout {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .ov {{ position: absolute; inset: 0; direction: rtl; font-family: "Heebo", sans-serif; color: #fff; pointer-events: none; }}

      /* Opening: plain centered text, each phrase enters whole. */
      #hook {{ top: 1060px; bottom: auto; }}
      #hook .hl {{ opacity: 0; }}
      #hook .beat {{ position: absolute; left: 0; right: 0; top: 0; display: flex; flex-direction: column; align-items: center; gap: 6px; }}
      #hook .hl {{ font-family: "Heebo", sans-serif; font-weight: 900; font-size: 84px; line-height: 1.08; color: #fff; white-space: nowrap;
                   text-shadow: 0 6px 26px rgba(0,0,0,.65), 0 0 2px rgba(0,0,0,.9); }}
      #hook .royal {{ color: var(--royal); display: inline-block; text-shadow: 0 0 2px rgba(255,255,255,.45), 0 6px 26px rgba(0,0,0,.6); }}

      /* Captions */
      .cap {{ position: absolute; left: 0; right: 0; top: 1240px; display: flex; justify-content: center; direction: rtl; }}
      .cap.hi {{ top: 1110px; }}
      .cap-in {{ font-family: "Heebo", sans-serif; font-weight: 900; font-size: 74px; color: #fff; letter-spacing: -0.5px;
                 text-shadow: 0 4px 18px rgba(0,0,0,.75), 0 0 2px rgba(0,0,0,.95); white-space: nowrap; }}
      .cap .w {{ display: inline-block; }}
      .key.key-royal {{ color: var(--royal); text-shadow: 0 0 2px rgba(255,255,255,.4), 0 4px 18px rgba(0,0,0,.7); }}

      /* Text behind the trainer: left of the head, person cutout on top. */
      #behind {{ position: absolute; left: 0; right: 0; top: 215px; direction: rtl; text-align: center; font-family: "Heebo", sans-serif;
                 color: rgba(255,255,255,.95); text-shadow: 0 6px 28px rgba(0,0,0,.35); white-space: nowrap; transform-origin: 50% 50%; }}
      #behind .top {{ font-weight: 800; font-size: 80px; line-height: 1; text-shadow: 0 3px 16px rgba(0,0,0,.55), 0 0 2px rgba(0,0,0,.6); display: flex; align-items: center; justify-content: center; gap: 22px; }}
      #behind .big {{ font-weight: 900; font-size: 196px; line-height: .95; margin-top: 4px; letter-spacing: -2px; color: var(--royal);
                      text-shadow: 0 0 2px rgba(255,255,255,.4), 0 8px 30px rgba(0,0,0,.35); }}
      #behind span {{ display: inline-block; }}
      #cal {{ width: 104px; height: 112px; border-radius: 18px; background: #fff; overflow: hidden; flex: none; box-shadow: 0 10px 30px rgba(0,0,0,.35);
              display: flex; flex-direction: column; }}
      #cal .bar {{ height: 30px; background: var(--red); }}
      #cal b {{ flex: 1; display: grid; place-items: center; color: #16171a; font-weight: 900; font-size: 58px; line-height: 1; }}

      /* Full-screen pages */
      .page {{ position: absolute; inset: 0; overflow: hidden; direction: rtl; font-family: "Heebo", sans-serif; color: #fff;
               background: radial-gradient(120% 80% at 45% 40%, #34353a 0%, #232428 55%, #151619 100%); }}
      .page .inner {{ position: absolute; inset: 0; }}
      .page .glow {{ position: absolute; width: 1000px; height: 820px; border-radius: 50%; filter: blur(40px); }}
      #reasons .glow {{ right: -320px; bottom: -260px; background: radial-gradient(closest-side, rgba(255,40,50,.38), rgba(255,40,50,0)); }}
      #solution .glow {{ left: -320px; top: -240px; background: radial-gradient(closest-side, rgba(58,100,240,.5), rgba(58,100,240,0)); }}
      .page .grid {{ position: absolute; inset: -60px; opacity: .6;
        background-image: linear-gradient(rgba(255,255,255,.045) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.045) 2px, transparent 2px);
        background-size: 108px 108px; }}
      .page .title {{ position: absolute; left: 0; right: 0; top: 400px; text-align: center; font-weight: 900; font-size: 96px; line-height: 1; white-space: nowrap; }}
      .page .title .acc {{ display: inline-block; }}
      #reasons .title .acc {{ color: #ff4b55; text-shadow: 0 0 26px rgba(255,40,50,.5); }}
      #solution .title .acc {{ color: var(--blue); text-shadow: 0 0 26px rgba(58,100,240,.6); }}
      .rows {{ position: absolute; left: 60px; right: 60px; top: 555px; display: flex; flex-direction: column; gap: 30px; }}
      #solution .rows {{ top: 500px; }}
      #solution .title {{ top: 340px; }}
      /* Block cascade page (client reference d3e71928-….mov, measured frame by frame): flat, no tilt or roll.
         Blocks sit on a fixed pitch; the whole board moves up as each new block opens below centre and slides in. */
      #soScroll {{ position: absolute; inset: 0; will-change: transform; }}
      #soScroll .plane {{ position: absolute; left: -60px; right: -60px; top: -1500px; bottom: -1900px;
        background-image: linear-gradient(rgba(255,255,255,.06) 3px, transparent 3px), linear-gradient(90deg, rgba(255,255,255,.06) 3px, transparent 3px);
        background-size: 250px 250px; background-position: 40px 60px; }}
      #soScroll .glow {{ top: -500px; }}
      #soScroll .dust {{ position: absolute; border-radius: 50%; background: rgba(255,255,255,.55); }}
      #soTtlW {{ position: absolute; left: 0; right: 0; top: 0; height: 0; }}
      #solution .rows {{ gap: 157px; }}
      #solution .rw {{ position: relative; }}
      .row {{ position: relative; height: 250px; border-radius: 36px; background: rgba(255,255,255,.07); border: 2px solid rgba(255,255,255,.13);
              box-shadow: 0 24px 60px rgba(0,0,0,.35); display: flex; align-items: center; justify-content: space-between; padding: 0 40px; }}
      #solution .row {{ height: 228px; }}
      .row .txt {{ display: flex; align-items: center; gap: 28px; }}
      .row .m {{ font-weight: 900; font-size: 62px; line-height: 1.05; white-space: nowrap; }}
      .row .s {{ font-weight: 600; font-size: 40px; line-height: 1.2; color: rgba(255,255,255,.66); white-space: nowrap; margin-top: 6px; }}
      .badge {{ width: 84px; height: 84px; border-radius: 50%; display: grid; place-items: center; font-size: 50px; font-weight: 900; flex: none; }}
      .badge.x {{ background: var(--red); box-shadow: 0 0 30px rgba(255,40,50,.45); }}
      .badge.v {{ background: var(--royal); box-shadow: 0 0 30px rgba(58,100,240,.6); }}
      .vis {{ position: relative; width: 330px; height: 190px; flex: none; direction: ltr; }}
      /* energy battery */
      .energy .batt {{ position: absolute; left: 10px; top: 45px; width: 280px; height: 100px; border: 7px solid #fff; border-radius: 22px; padding: 8px; }}
      .energy .cap-tip {{ position: absolute; left: 296px; top: 75px; width: 18px; height: 40px; border-radius: 0 8px 8px 0; background: #fff; }}
      #battFill {{ display: block; height: 100%; width: 0%; border-radius: 12px; background: var(--green); }}
      #battPct {{ position: absolute; inset: 0; display: grid; place-items: center; font-size: 46px; font-weight: 900; color: #fff;
                  text-shadow: 0 2px 10px rgba(0,0,0,.6); }}
      /* alone */
      .alone svg {{ position: absolute; width: 110px; height: 110px; top: 40px; }}
      .alone .solo {{ left: 110px; fill: #fff; }}
      .alone .ghost {{ fill: none; stroke: rgba(255,255,255,.5); stroke-width: 1.2; stroke-dasharray: 2 2; }}
      .alone .g0 {{ left: 0; top: 10px; }} .alone .g1 {{ left: 220px; top: 10px; }} .alone .g2 {{ left: 30px; top: 92px; }} .alone .g3 {{ left: 190px; top: 92px; }}
      /* question marks */
      .qs .q {{ position: absolute; font-weight: 900; color: rgba(255,255,255,.55); }}
      .qs .big {{ left: 120px; top: -10px; font-size: 190px; line-height: 1; color: #fff; text-shadow: 0 0 30px rgba(255,255,255,.35); }}
      .qs .q0 {{ left: 20px; top: 40px; font-size: 80px; }} .qs .q1 {{ left: 255px; top: 20px; font-size: 70px; }} .qs .q2 {{ left: 245px; top: 110px; font-size: 56px; }}
      /* six people */
      .six svg {{ position: absolute; width: 66px; height: 66px; fill: rgba(255,255,255,.18); }}
      .six .p6-0 {{ left: 110px; top: 26px; }} .six .p6-1 {{ left: 182px; top: 26px; }} .six .p6-2 {{ left: 254px; top: 26px; }}
      .six .p6-3 {{ left: 110px; top: 100px; }} .six .p6-4 {{ left: 182px; top: 100px; }} .six .p6-5 {{ left: 254px; top: 100px; }}
      #sixN {{ position: absolute; left: 4px; top: 22px; font-size: 140px; font-weight: 900; line-height: 1; color: var(--blue);
               text-shadow: 0 0 26px rgba(58,100,240,.7); }}
      /* plan sheet */
      .plan .sheet {{ position: absolute; left: 50px; top: 0; width: 240px; height: 190px; border-radius: 20px; background: #f4f5f8; padding: 16px 18px;
                      box-shadow: 0 16px 40px rgba(0,0,0,.4); direction: rtl; }}
      .plan .hd {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
      .plan .hd i {{ width: 26px; height: 26px; border-radius: 50%; background: var(--royal); }}
      .plan .hd b {{ font-size: 26px; font-weight: 900; color: #16171a; }}
      .plan .ln {{ display: flex; align-items: center; gap: 10px; height: 31px; }}
      .plan .ck {{ width: 24px; height: 24px; border-radius: 50%; background: var(--royal); color: #fff; font-size: 15px; font-weight: 900; display: grid; place-items: center; }}
      .plan .ln i {{ display: block; height: 11px; border-radius: 6px; background: #c9ccd4; transform-origin: 100% 50%; }}
      /* kg */
      .kg .db {{ position: absolute; left: 196px; top: 64px; width: 130px; height: 62px; }}
      .kg .num {{ position: absolute; left: 0; top: 36px; display: flex; align-items: baseline; gap: 8px; direction: rtl; }}
      .kg .num b {{ font-size: 108px; font-weight: 900; line-height: 1; }}
      .kg .num span {{ font-size: 40px; font-weight: 800; color: rgba(255,255,255,.7); }}
      .kg .up {{ position: absolute; left: 240px; top: 2px; font-size: 52px; color: var(--green); }}
      /* graph */
      .graph svg {{ width: 330px; height: 170px; margin-top: 10px; overflow: visible; }}
      #leak {{ position: absolute; inset: -10%; pointer-events: none; mix-blend-mode: screen;
               background: radial-gradient(60% 50% at 50% 55%, rgba(255,255,255,.95), rgba(255,200,205,.7) 45%, rgba(255,120,130,.25) 75%, rgba(255,90,100,0)); }}

      /* CTA: Instagram DM notification, low-opacity glass, round profile picture. */
      #g6 {{ top: auto; bottom: 440px; display: flex; flex-direction: column; align-items: center; direction: rtl; }}
      #dm {{ display: flex; align-items: center; gap: 26px; width: 900px; padding: 26px 32px; border-radius: 46px;
             background: rgba(255,255,255,.14); border: 1.5px solid rgba(255,255,255,.28); backdrop-filter: blur(22px) saturate(1.3);
             box-shadow: 0 20px 60px rgba(0,0,0,.28); }}
      #dm .av {{ width: 128px; height: 128px; border-radius: 50%; flex: none; padding: 5px;
                 background: conic-gradient(from 200deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5, #feda75); }}
      #dm .av img {{ width: 100%; height: 100%; border-radius: 50%; display: block; border: 4px solid rgba(20,20,22,.9); }}
      #dm .body {{ flex: 1; min-width: 0; text-align: right; }}
      #dm .top {{ display: flex; align-items: baseline; gap: 14px; font-size: 40px; font-weight: 800; color: #fff; direction: ltr; justify-content: flex-end; }}
      #dm .top .when {{ font-weight: 500; font-size: 34px; color: rgba(255,255,255,.7); }}
      #dm .msg {{ font-size: 62px; font-weight: 900; color: #fff; margin-top: 6px; line-height: 1.1; text-shadow: 0 2px 10px rgba(0,0,0,.25); }}
      #dm .dot {{ width: 26px; height: 26px; border-radius: 50%; background: #3797f0; flex: none; box-shadow: 0 0 14px rgba(55,151,240,.7); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}" data-width="1080" data-height="1920">
      <div id="cam">
        <div id="side">
        <div id="frame">
          <video id="a-roll" class="clip" src="{VIDEO}" playsinline data-start="0" data-duration="{DURATION}" data-track-index="0"
                 data-has-audio="true" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>
          <div id="behind" class="clip" data-start="{T_["tb_in"]}" data-duration="{round(T_["tb_out"] + 0.35 - T_["tb_in"], 2)}" data-track-index="1">
            <div class="top"><span class="tw">{TB_A}</span><div id="cal"><i class="bar"></i><b id="calN">1</b></div></div>
            <div class="big">{TB_B}</div>
          </div>
          <img id="cutout" class="clip" alt="" data-cut-ranges="{CUT_A}-{CUT_B}" data-start="0" data-duration="{DURATION}" data-track-index="1" />
        </div>
        </div>
      </div>

      <audio id="music" src="music.wav" data-start="0" data-duration="{DURATION}" data-track-index="6" data-volume="1"></audio>
      <audio id="sfx" src="sfx.wav" data-start="0" data-duration="{DURATION}" data-track-index="5" data-volume="0.35"></audio>

      <div class="ov clip" id="hook" data-start="0" data-duration="{round(T_["hk_out"] + 0.25, 2)}" data-track-index="2">
        <div class="beat" id="hookA"><div class="hl" id="hookL">בואו אני אגיד לכם</div><div class="hl" id="hookL2">למה רוב האנשים</div></div>
        <div class="beat" id="hookB"><div class="hl" id="hookR">לא מצליחים</div><div class="hl" id="hookR2"><span class="royal">להתמיד</span> באימונים</div></div>
      </div>

      <div class="clip page" id="reasons" data-start="{round(T_["rs_in"], 2)}" data-duration="{round(T_["rs_out"] - T_["rs_in"], 2)}" data-track-index="3">
        <div class="inner" id="rsIn">
          <div class="grid"></div><div class="glow"></div>
          <div class="rows">
{REASONS}
          </div>
        </div>
      </div>

      <div class="clip page" id="solution" data-start="{round(T_["sol_in"], 2)}" data-duration="{round(T_["sol_out"] - T_["sol_in"], 2)}" data-track-index="3">
        <div class="inner" id="soIn">
          <div id="soScroll"><div class="plane"></div><div class="glow"></div>{DUST}
          <div class="rows">
{SOLUTION}
          </div></div>
        </div>
      </div>

      <div class="clip" id="leakClip" data-start="{round(T_["rs_out"] - 0.2, 2)}" data-duration="0.2" data-track-index="4"><div id="leak"></div></div>

      <div class="ov clip" id="g6" data-start="{round(T_["dm_in"] - 0.05, 2)}" data-duration="{round(DURATION - T_["dm_in"] + 0.05, 2)}" data-track-index="3">
        <div id="dm">
          <div class="av"><img src="avatar.png" alt="" /></div>
          <div class="body">
            <div class="top"><span class="when">עכשיו</span><span>idoamarr</span></div>
            <div class="msg">שלחו לנו הודעה</div>
          </div>
          <i class="dot"></i>
        </div>
      </div>

{cap_html}
    </div>

    <script>
      const spring = (p) => (1 - (1 + 7 * p) * Math.exp(-7 * p)) / (1 - 8 * Math.exp(-7));
      const FACE_FPS = {face["fps"]};
      const FACE_X = {json.dumps(smooth([p["x"] for p in face["track"]]))};
      const FACE_Y = {json.dumps(smooth([p["y"] for p in face["track"]]))};
      const ZOOM = {json.dumps(ZOOM)};
      const CAPS = {json.dumps([c["start"] for c in captions])};
      const T = {json.dumps({k: round(v, 2) for k, v in TIMES.items()})};
      const tl = gsap.timeline({{ paused: true }});

      // Zoom center follows the face.
      for (let i = 0; i < FACE_X.length; i++) tl.set("#frame", {{ transformOrigin: `${{FACE_X[i]}}% ${{FACE_Y[i]}}%` }}, i / FACE_FPS);
      let cur = 1;
      for (const [kind, at, scale, dur] of ZOOM) {{
        if (kind === "set") tl.set("#frame", {{ scale }}, at);
        else {{
          const ease = kind === "punch" || kind === "snap" ? spring : kind === "back" ? "power3.inOut" : "sine.inOut";
          if (kind === "snap") tl.fromTo("#frame", {{ filter: "blur(5px)" }}, {{ filter: "blur(0px)", duration: 0.16, ease: "power2.out", immediateRender: false }}, at);
          tl.fromTo("#frame", {{ scale: cur }}, {{ scale, duration: dur, ease, immediateRender: false }}, at);
        }}
        cur = scale;
      }}

      // Hidden until their own entrance.
      tl.set(["#hookL", "#hookL2", "#hookR", "#hookR2", ".row", "#dm", "#behind .la", "#behind .lb", "#cal"], {{ opacity: 0 }}, 0);

      // Opening: each phrase enters whole from a soft blur.
      const phraseIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, y: 34, scale: 0.94, filter: "blur(12px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out", immediateRender: false }}, at);
      phraseIn("#hookL", T.hk_a);
      phraseIn("#hookL2", T.hk_a2);
      // Beat A leaves, beat B "לא מצליחים / להתמיד באימונים" comes in whole.
      tl.to("#hookA", {{ opacity: 0, y: -24, filter: "blur(12px)", duration: 0.18, ease: "power2.in" }}, T.hk_b - 0.18);
      phraseIn(["#hookR", "#hookR2"], T.hk_b);
      tl.fromTo("#hookR2 .royal", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.45, ease: spring, immediateRender: false }}, T.hk_b + 0.45);
      tl.to("#hookB", {{ opacity: 0, y: -24, filter: "blur(12px)", duration: 0.22, ease: "power2.in" }}, T.hk_out);


      // Captions pop in.
      CAPS.forEach((at, i) => tl.fromTo(`#cap${{i}} .cap-in`, {{ opacity: 0, scale: 0.82, y: 24 }},
        {{ opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2.2)", immediateRender: false }}, at));

      // Page entrance: zoom-blur push through the shot into the dark page (approved on reel3).
      const pageIn = (sel, inner, at, dur) => {{
        tl.fromTo("#cam", {{ scale: 1, filter: "blur(0px)" }}, {{ scale: 2.4, filter: "blur(24px)", duration: 0.28, ease: "power2.in", immediateRender: false }}, at - 0.2);
        tl.fromTo(sel, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.14, ease: "power1.in", immediateRender: false }}, at);
        tl.fromTo(inner, {{ scale: 1.0 }}, {{ scale: 1.05, duration: dur, ease: "none", immediateRender: false }}, at);
      }};
      // Rows glide and fade in smoothly (client: no 3D flips).
      const smoothIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, y: 80, scale: 0.97, filter: "blur(6px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "sine.out", immediateRender: false }}, at);
      const badgeIn = (sel, at) => tl.fromTo(sel, {{ scale: 0.4, rotation: -30 }}, {{ scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2)", immediateRender: false }}, at);
      const titleIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, y: -30, filter: "blur(12px)", letterSpacing: "18px" }},
        {{ opacity: 1, y: 0, filter: "blur(0px)", letterSpacing: "0px", duration: 0.45, ease: "power3.out", immediateRender: false }}, at);

      // ===== Reasons page =====
      pageIn("#reasons", "#rsIn", T.rs_in, T.rs_out - T.rs_in);
      tl.set("#cam", {{ scale: 1, filter: "blur(0px)" }}, T.rs_out);
      smoothIn("#r1", T.rs_1); badgeIn("#r1 .badge", T.rs_1 + 0.25);
      smoothIn("#r2", T.rs_2); badgeIn("#r2 .badge", T.rs_2 + 0.25);
      smoothIn("#r3", T.rs_3); badgeIn("#r3 .badge", T.rs_3 + 0.25);
      // Energy: shoots up to 100% green, then drains to 8% red and flickers.
      const batt = {{ v: 0 }};
      const battDraw = () => {{
        const v = batt.v, el = document.querySelector("#battFill");
        el.style.width = v + "%";
        el.style.background = v > 55 ? "#39e46b" : v > 25 ? "#ffb020" : "#ff3340";
        document.querySelector("#battPct").textContent = Math.round(v) + "%";
      }};
      tl.fromTo(batt, {{ v: 0 }}, {{ v: 100, duration: 0.45, ease: "power3.out", immediateRender: false, onUpdate: battDraw }}, T.rs_1 + 0.25);
      tl.fromTo(batt, {{ v: 100 }}, {{ v: 8, duration: Math.max(0.6, T.rs_2 - T.rs_1 - 0.6), ease: "power2.in", immediateRender: false, onUpdate: battDraw }}, T.rs_1 + 0.75);
      [0, 1, 2, 3, 4, 5].forEach((k) => tl.set("#battFill", {{ opacity: k % 2 ? 1 : 0.35 }}, T.rs_2 - 0.05 + k * 0.09));
      // Alone: the friends around him fade away, he stays alone.
      tl.fromTo("#r2 .ghost", {{ opacity: 1, scale: 1 }}, {{ opacity: 0, scale: 0.6, duration: 0.5, stagger: 0.12, ease: "power2.in", immediateRender: false }}, T.rs_2 + 0.45);
      tl.fromTo("#r2 .solo", {{ scale: 1 }}, {{ scale: 0.9, duration: 0.6, ease: "sine.inOut", immediateRender: false }}, T.rs_2 + 0.9);
      // Question marks: pop around, the big one wobbles.
      tl.fromTo("#r3 .q:not(.big)", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, stagger: 0.12, ease: "back.out(3)", immediateRender: false }}, T.rs_3 + 0.35);
      tl.fromTo("#qBig", {{ rotation: -14 }}, {{ rotation: 14, duration: 0.32, ease: "sine.inOut", yoyo: true, repeat: 5, immediateRender: false }}, T.rs_3 + 0.3);
      // Light-leak flash over the reasons page, then a hard cut at its peak straight to the clean shot
      // (client: liked the flash, not the washed-out frame of the trainer that followed it).
      tl.fromTo("#leak", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1.2, duration: 0.17, ease: "power1.in", immediateRender: false }}, T.rs_out - 0.2);

      // ===== "אחרי חודש / מפסיקים" behind the trainer =====
      tl.fromTo("#behind .top", {{ letterSpacing: "24px" }}, {{ letterSpacing: "0px", duration: 0.55, ease: "power3.out", immediateRender: false }}, T.tb_in);
      tl.fromTo([...document.querySelectorAll("#behind .la")].reverse(), {{ opacity: 0, x: -40, filter: "blur(10px)" }},
        {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.3, stagger: 0.03, ease: "power3.out", immediateRender: false }}, T.tb_in);
      tl.fromTo("#cal", {{ opacity: 0, y: -40, rotation: -10 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.4, ease: "back.out(2)", immediateRender: false }}, T.tb_in + 0.15);
      const cal = {{ n: 1 }};
      tl.fromTo(cal, {{ n: 1 }}, {{ n: 30, duration: Math.max(0.4, T.tb_big - T.tb_in - 0.3), ease: "power1.in", immediateRender: false,
        onUpdate: () => {{ document.querySelector("#calN").textContent = Math.round(cal.n); }} }}, T.tb_in + 0.25);
      tl.fromTo([...document.querySelectorAll("#behind .lb")].reverse(), {{ opacity: 0, x: -70, scale: 1.25, filter: "blur(14px)" }},
        {{ opacity: 1, x: 0, scale: 1, filter: "blur(0px)", duration: 0.38, stagger: 0.045, ease: "power3.out", immediateRender: false }}, T.tb_big);
      tl.to("#cal", {{ y: 260, rotation: 35, opacity: 0, duration: 0.55, ease: "power2.in" }}, T.tb_big + 0.25);
      tl.fromTo("#behind", {{ x: 6, rotationY: 7, transformPerspective: 1200 }},
        {{ x: 24, rotationY: 3, transformPerspective: 1200, duration: T.tb_out - T.tb_in, ease: "none", immediateRender: false }}, T.tb_in);
      tl.to("#behind", {{ x: 420, scaleX: 1.35, opacity: 0, filter: "blur(22px)", duration: 0.3, ease: "power2.in" }}, T.tb_out);

      // ===== Solution page =====
      pageIn("#solution", "#soIn", T.sol_in, T.sol_out - T.sol_in);
      // Block cascade, keyframed from the reference (1248 px frame scaled to 1920):
      //  - a new block opens below centre (its centre at y≈1190), width growing from a narrow strip with a slight
      //    overshoot, and rises ~70 px on its own;
      //  - the whole board (title, earlier blocks, grid) moves up with it: the new block's centre goes
      //    1190 → 1040 in 0.25 s (ease in-out) → 930 by 0.6 s (ease out) → drifts and speeds up to 805 when the
      //    next block arrives (= 1190 minus one pitch), so the motion never stops;
      //  - fixed pitch 385 px between block centres (row 228 + gap 157), title one step above the first block.
      const PITCH = 385, C1 = 614, CT = 390;
      const BT = [T.so_1, T.so_2, T.so_3, T.so_4];
      tl.set("#soScroll", {{ y: 1240 - C1 }}, 0);
      tl.fromTo("#soScroll", {{ y: 1240 - C1 }}, {{ y: 1190 - C1, duration: Math.max(0.2, BT[0] - T.sol_in), ease: "power1.in", immediateRender: false }}, T.sol_in);
      BT.forEach((at, k) => {{
        const c = C1 + PITCH * k, next = k < 3 ? BT[k + 1] : T.sol_out;
        tl.to("#soScroll", {{ y: 1040 - c, duration: 0.25, ease: "power2.inOut" }}, at);
        tl.to("#soScroll", {{ y: 930 - c, duration: 0.35, ease: "power2.out" }}, at + 0.25);
        tl.to("#soScroll", {{ y: (k < 3 ? 805 : 880) - c, duration: Math.max(0.2, next - at - 0.6), ease: k < 3 ? "power1.in" : "none" }}, at + 0.6);
        // the block itself: opens sideways from a strip and rises into its slot; its content moves with it
        const sel = `#s${{k + 1}}`;
        tl.fromTo(sel, {{ opacity: 0, scaleX: 0.16, y: 70 }}, {{ opacity: 1, duration: 0.08, ease: "none", immediateRender: false }}, at - 0.02);
        tl.fromTo(sel, {{ scaleX: 0.16 }}, {{ scaleX: 1.04, duration: 0.22, ease: "power2.out", immediateRender: false }}, at - 0.02);
        tl.to(sel, {{ scaleX: 1, duration: 0.2, ease: "sine.inOut" }}, at + 0.2);
        tl.fromTo(sel, {{ y: 70 }}, {{ y: 0, duration: 0.4, ease: "power2.out", immediateRender: false }}, at - 0.02);
      }});
      tl.fromTo("#solution .dust", {{ x: 0, y: 0 }}, {{ x: (i) => (i % 2 ? 22 : -18), y: (i) => -20 - (i % 5) * 10, duration: T.sol_out - T.sol_in, ease: "none", immediateRender: false }}, T.sol_in);
      // Blocks that have moved well above the focus go soft, as in the reference.
      const dofEls = [...document.querySelectorAll("#solution .rw")];
      const dof = {{ k: 0 }};
      tl.fromTo(dof, {{ k: 0 }}, {{ k: 1, duration: T.sol_out - T.sol_in, ease: "none", immediateRender: false, onUpdate: () => {{
        for (const el of dofEls) {{
          const r = el.firstElementChild.getBoundingClientRect(), d = 960 - (r.top + r.height / 2);
          const b = Math.max(0, Math.min(4, (d - 300) / 110));
          el.style.filter = b > 0.05 ? `blur(${{b.toFixed(2)}}px)` : "none";
        }}
      }} }}, T.sol_in);
      badgeIn("#s1 .badge", T.so_1 + 0.25);
      badgeIn("#s2 .badge", T.so_2 + 0.25);
      badgeIn("#s3 .badge", T.so_3 + 0.25);
      badgeIn("#s4 .badge", T.so_4 + 0.25);
      // Six people light up blue one by one, counter to 6.
      document.querySelectorAll("#s1 .p6").forEach((el, k) => {{
        tl.fromTo(el, {{ fill: "rgba(255,255,255,.18)", scale: 1 }}, {{ fill: "#5b86ff", scale: 1.12, duration: 0.14, ease: "power2.out", immediateRender: false }}, T.so_1 + 0.35 + k * 0.13);
        tl.to(el, {{ scale: 1, duration: 0.2, ease: "power2.out" }}, T.so_1 + 0.49 + k * 0.13);
        tl.set("#sixN", {{ textContent: String(k + 1) }}, T.so_1 + 0.35 + k * 0.13);
      }});
      tl.set("#sixN", {{ textContent: "0" }}, 0);
      tl.fromTo("#sixN", {{ scale: 1 }}, {{ scale: 1.2, duration: 0.4, ease: spring, immediateRender: false }}, T.so_1 + 1.0);
      // Plan sheet: lines write in with their checks.
      tl.fromTo("#s2 .ln i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.28, stagger: 0.16, ease: "power2.out", immediateRender: false }}, T.so_2 + 0.35);
      tl.fromTo("#s2 .ck", {{ scale: 0 }}, {{ scale: 1, duration: 0.25, stagger: 0.16, ease: "back.out(3)", immediateRender: false }}, T.so_2 + 0.5);
      tl.fromTo("#s2 .sheet", {{ rotation: -6 }}, {{ rotation: 3, duration: 1.6, ease: "sine.inOut", immediateRender: false }}, T.so_2);
      // Weights count up 40 -> 60 kg, arrow pulses.
      const kg = {{ n: 40 }};
      tl.fromTo(kg, {{ n: 40 }}, {{ n: 60, duration: 0.9, ease: "power2.out", immediateRender: false,
        onUpdate: () => {{ document.querySelector("#kgN").textContent = Math.round(kg.n / 5) * 5; }} }}, T.so_3 + 0.3);
      tl.fromTo("#kgUp", {{ y: 10, opacity: 0.3 }}, {{ y: -10, opacity: 1, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }}, T.so_3 + 0.3);
      tl.fromTo("#s3 .db", {{ rotation: 0 }}, {{ rotation: -10, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }}, T.so_3 + 0.3);
      // Progress graph draws itself with a glowing dot riding the line.
      const gLine = document.querySelector("#gLine"), gLen = gLine.getTotalLength(), gDot = document.querySelector("#gDot");
      gLine.style.strokeDasharray = gLen;
      const g = {{ p: 0 }};
      const gDraw = () => {{ gLine.style.strokeDashoffset = gLen * (1 - g.p); const pt = gLine.getPointAtLength(gLen * g.p); gDot.setAttribute("cx", pt.x); gDot.setAttribute("cy", pt.y); }};
      tl.fromTo(g, {{ p: 0 }}, {{ p: 1, duration: 0.9, ease: "power1.inOut", immediateRender: false, onUpdate: gDraw }}, T.so_4 + 0.3);
      tl.set(g, {{ p: 0, onComplete: gDraw }}, 0.001);
      tl.fromTo("#gArea", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "power1.out", immediateRender: false }}, T.so_4 + 0.9);
      // Back to the video: hard cut, opens over-exposed and soft, settles in ~0.2 s (approved transition).
      tl.set("#cam", {{ scale: 1, filter: "brightness(1.35) blur(1.2px)" }}, T.sol_out);
      tl.to("#cam", {{ filter: "brightness(1) blur(0px)", duration: 0.22, ease: "power2.out" }}, T.sol_out + 0.035);

      // ===== CTA: DM notification drops in like a real banner =====
      tl.fromTo("#dm", {{ opacity: 0, y: -90, scale: 0.92, filter: "blur(8px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: spring, immediateRender: false }}, T.dm_in);
      tl.fromTo("#dm .dot", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false }}, T.dm_in + 0.4);
      tl.fromTo("#dm", {{ scale: 1 }}, {{ scale: 1.03, duration: 0.18, yoyo: true, repeat: 1, ease: "sine.inOut", immediateRender: false }}, {round(t("תשלחו"), 2)});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(OUT, "w").write(html)

# Sound cues, rendered to sfx.wav by tools/sfx.py.
G = TIMES
ev = [("whoosh_soft", G["hk_a"]), ("whoosh_soft", G["hk_b"]), ("pop", G["hk_b"] + 0.45)]
ev += [("thump", at) for kind, at, *_ in ZOOM if kind in ("snap", "punch")]
ev += [("whoosh", G["rs_in"] - 0.2), ("thump", G["rs_in"]), ("pop", G["rs_in"] + 0.1)]
for k in ("rs_1", "rs_2", "rs_3"):
    ev += [("whoosh_soft", G[k]), ("scratch", G[k] + 0.25)]
ev += [("tick", G["rs_3"] + 0.35 + i * 0.12) for i in range(3)]
ev += [("whoosh_out", G["rs_out"] - 0.2), ("whoosh_soft", G["tb_in"]), ("pop", G["tb_in"] + 0.15)]
ev += [("tick", G["tb_in"] + 0.25 + i * 0.09) for i in range(max(1, int((G["tb_big"] - G["tb_in"] - 0.3) / 0.09)))]
ev += [("whoosh", G["tb_big"]), ("thump", G["tb_big"] + 0.25), ("whoosh_out", G["tb_out"])]
ev += [("whoosh", G["sol_in"] - 0.2), ("thump", G["sol_in"]), ("pop", G["sol_in"] + 0.1)]
for k in ("so_1", "so_2", "so_3", "so_4"):
    ev += [("whoosh_soft", G[k]), ("ding", G[k] + 0.25)]
ev += [("tick", G["so_1"] + 0.35 + i * 0.13) for i in range(6)]
ev += [("tick", G["so_3"] + 0.3 + i * 0.1) for i in range(8)]
ev += [("thump", G["sol_out"]), ("whoosh_soft", G["dm_in"]), ("ding", G["dm_in"] + 0.4), ("pop", t("תשלחו"))]
json.dump({"duration": DURATION, "events": [[n, round(a, 3)] for n, a in sorted(ev, key=lambda e: e[1]) if a < DURATION - 0.3]},
          open(os.path.join(os.path.dirname(OUT), "sfx.json"), "w"))
print("wrote", OUT, len(captions), "captions;", {k: round(v, 2) for k, v in TIMES.items()})
