"""Generate reel3/index.html ("מבצע חגים"): same approved style as reel2 (face-centered zooms,
blur-in hook, 2-4 word captions, glass cards), content rewritten for the holiday-offer script.

usage: build3.py <face.json> <words.json> <out index.html> <video src> <first cutout frame> <last cutout frame>
"""
import json
import os
import sys

face = json.load(open(sys.argv[1]))
words = json.load(open(sys.argv[2]))
OUT, VIDEO = sys.argv[3], sys.argv[4]
DURATION = 22.3
KEYWORDS = {"לשגרה", "לאימונים", "עכשיו", "6", "אישית", "מלווה", "199"}
# Keyword color class; anything not listed is red.
KEY_COLOR = {"6": "key-green", "מלווה": "key-cyan", "לאימונים": "key-royal", "עכשיו": "key-royal"}


def t(word, nth=1):
    hits = [w["t"] for w in words if w["w"] == word]
    return hits[nth - 1]


def after(word, nth=1):
    """Time the word's segment ends (the next word's start, or the pause)."""
    i = [k for k, w in enumerate(words) if w["w"] == word][nth - 1]
    nxt = words[i + 1]["t"] if i + 1 < len(words) else DURATION
    return min(nxt, words[i].get("segEnd", nxt))


N_HOOK = 4  # "החגים נגמרו / חוזרים לשגרה"
CHUNKS = [
    ["וזה", "הזמן"], ["לחזור", "גם", "לאימונים"],
    ["אם", "כבר", "הרבה", "זמן"], ["אתם", "אומרים", "לעצמכם"], ["שהגיע", "הזמן"], ["להתחיל", "להתאמן"],
    ["עכשיו", "זה", "סיבה", "טובה"], ["להתחיל"],
    ["אימוני", "כוח"], ["בקבוצות", "קטנות"], ["עד", "6", "מתאמנים"], ["באימון"],
    ["אני", "בונה"], ["לכל", "מתאמן"], ["תכנית", "אישית"],
    ["מלווה", "אתכם"], ["לאורך", "כל", "הדרך"],
    ["לכבוד", "החזרה"], ["לשגרה"], ["יצאתי", "במבצע"], ["של", "199", "ש״ח"], ["לחודש", "הראשון"],
    ["רוצים", "גם", "אתם"], ["להצטרף", "למשפחה?"], ["שלחו", "לי", "הודעה"], ["ונשמור", "לכם", "מקום"],
]
assert sum(map(len, CHUNKS)) + N_HOOK == len(words), (sum(map(len, CHUNKS)) + N_HOOK, len(words))
idx, captions = N_HOOK, []
for ch in CHUNKS:
    start = words[idx]["t"]
    idx += len(ch)
    end = words[idx]["t"] if idx < len(words) else DURATION
    seg_end = next((w["segEnd"] for w in words[idx - len(ch):idx] if "segEnd" in w), None)
    if seg_end is not None:
        end = min(end, seg_end + 0.25)
    captions.append({"words": ch, "start": round(start, 2), "end": round(end, 2)})

HOOK = words[:N_HOOK]

# Zoom keyframes: (kind, time, scale, duration)
ZOOM = [
    ("set", 0.0, 1.00, 0),
    ("push", 0.0, 1.07, t("וזה")),
    # "לאימונים": sharp snap in, then glide back out before the next sentence.
    ("snap", t("לאימונים"), 1.30, 0.2),
    ("back", after("לאימונים"), 1.00, t("אם") - after("לאימונים") + 0.25),
    ("push", t("אם") + 0.25, 1.12, t("עכשיו") - t("אם") - 0.25),
    ("back", t("עכשיו") - 0.3, 1.00, t("אימוני") - t("עכשיו") + 0.3),
    ("push", t("אימוני"), 1.10, t("בקבוצות") - t("אימוני")),
    # (8.6-12.45 the motion-graphics page covers the video)
    ("set", t("אישית") + 0.42, 1.00, 0),
    ("push", t("אישית") + 0.42, 1.05, t("מלווה") - t("אישית") - 0.42),
    ("punch", t("מלווה"), 1.06, 0.45),
    ("back", t("לאורך"), 1.00, t("לכבוד") - t("לאורך")),
    ("push", t("לכבוד"), 1.10, t("במבצע") - t("לכבוד")),
    ("push", t("רוצים"), 1.16, DURATION - t("רוצים")),
]

TIMES = {
    "g1_in": t("אומרים") - 0.05, "g1_strike": t("לעצמכם") + 0.1, "g1_b": t("עכשיו") - 0.05, "g1_out": after("להתחיל", 2) + 0.1,
    # Small groups + personal plan (client's motion-graphics reference): big word pops on the video, zoom-blur
    # through to a dark page, a glowing marquee line, a red band with typed text, the band flips into a 3D card
    # with two filling rings, light-leak flash back to the video.
    "mg_word": t("אימוני") - 0.06, "mg_in": t("בקבוצות") - 0.08, "mg_band": t("עד") - 0.14, "mg_type0": t("עד"),
    "mg_type1": t("באימון") + 0.28, "mg_card": t("אני") - 0.06, "mg_lbl": t("לכל"), "mg_title": t("תכנית"),
    "mg_out": t("אישית") + 0.42,
    # "ומלווה אתכם לאורך כל הדרך" (client's third reference): hard cut to a grid page with a long glowing line,
    # a red dot travelling along it, text resolving above; hard cut back on "לכבוד".
    "ln_in": t("מלווה") - 0.03, "ln_w1": t("מלווה"), "ln_w2": t("אתכם"), "ln_b": t("לאורך"), "ln_red": t("כל"),
    "tb_in": t("לכבוד") - 0.12, "tb_big": t("לשגרה", 2) - 0.2, "tb_out": t("במבצע") + 0.5,
    # Offer (client reference): the frame slides off sideways onto a black star page, hard cut back at "רוצים".
    "mq_in": t("יצאתי") - 0.05, "sp_in": t("במבצע") - 0.05, "sp_num": t("199") - 0.1, "sp_sub": t("לחודש"),
    "sp_sub2": t("הראשון") + 0.25, "sp_out": t("רוצים"),
    "g6_in": t("שלחו"), "g6_here": t("ונשמור"),
}


def esc_words(ws):
    return " ".join(
        f'<span class="w{" key " + KEY_COLOR.get(w.strip("?"), "") if w.strip("?") in KEYWORDS else ""}">{w}</span>' for w in ws)


# The DM card and "ונשמור לכם מקום" cover the last two chunks, so their captions are dropped.
captions = [c for c in captions if c["words"] not in (["שלחו", "לי", "הודעה"], ["ונשמור", "לכם", "מקום"])]
# The price card shows "199₪", so that caption is dropped too.
captions = [c for c in captions if c["words"] not in (["של", "199", "ש״ח"], ["יצאתי", "במבצע"], ["לחודש", "הראשון"])]
# The big text behind the trainer already says "לכבוד החזרה / לשגרה" (client: no duplicate at the bottom).
captions = [c for c in captions if c["words"] not in (["לכבוד", "החזרה"], ["לשגרה"], ["מלווה", "אתכם"], ["לאורך", "כל", "הדרך"])]
# 8.6-12.45 is the motion-graphics sequence; its own text replaces the captions.
captions = [c for c in captions if not (TIMES["mg_word"] - 0.01 <= c["start"] < TIMES["mg_out"])]
cap_html = "\n".join(
    f'      <div class="cap clip" id="cap{i}" data-start="{c["start"]}" data-duration="{round(c["end"] - c["start"], 2)}"'
    f' data-track-index="2"><div class="cap-in">{esc_words(c["words"])}</div></div>'
    for i, c in enumerate(captions)
)
# Beat A: "החגים נגמרו"; beat B replaces it alone: "חוזרים לשגרה".
HOOK_BEATS = [("hookA", [(0, 2)]), ("hookB", [(2, 4)])]
def hook_line(a, b):
    return "<div>" + " ".join(
        f'<span class="hw{" key" if HOOK[i]["w"] in KEYWORDS else ""}{" royal" if HOOK[i]["w"] == "לשגרה" else ""}" id="hw{i}">{HOOK[i]["w"]}</span>' for i in range(a, b)) + "</div>"
hook_html = "\n".join(
    f'        <div class="beat" id="{bid}">' + "".join(hook_line(a, b) for a, b in lines) + "</div>" for bid, lines in HOOK_BEATS)

PERSON = ('<svg viewBox="0 0 24 24" class="person"><circle cx="12" cy="7" r="4"/>'
          '<path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8z"/></svg>')
ROW = '<div class="row"><span class="tick"><b>✓</b></span><i class="bar" style="width:{w}px"></i></div>'

import random
_rng = random.Random(11)
STARS = "".join(
    f'<i class="star" style="left:{_rng.uniform(0, 100):.2f}%;top:{_rng.uniform(0, 100):.2f}%;width:{sz}px;height:{sz}px;opacity:{_rng.uniform(.25, .9):.2f}"></i>'
    for sz in (_rng.choice([2, 3, 3, 3, 4, 5]) for _ in range(230)))
STREAKS = "".join(
    f'<i class="streak" style="top:{_rng.uniform(20, 80):.1f}%;width:{_rng.randint(260, 620)}px;left:-700px"></i>' for _ in range(7))


RING = ('<svg viewBox="0 0 330 330"><circle cx="165" cy="165" r="150" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="16"/>'
        '<circle id="{id}" cx="165" cy="165" r="150" fill="none" stroke="#fff" stroke-width="16" stroke-linecap="round"'
        ' transform="rotate(-90 165 165)" stroke-dasharray="942.5" stroke-dashoffset="942.5"/>'
        '<g transform="translate(165 165)" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">{icon}</g></svg>')
ICON_DUMBBELL = ('<line x1="-48" y1="0" x2="48" y2="0"/><rect x="-80" y="-38" width="22" height="76" rx="6"/>'
                 '<rect x="58" y="-38" width="22" height="76" rx="6"/><line x1="-96" y1="-18" x2="-96" y2="18"/><line x1="96" y1="-18" x2="96" y2="18"/>')
ICON_PEOPLE = ('<circle cx="0" cy="-30" r="24"/><path d="M -46 52 C -46 14, 46 14, 46 52"/>'
               '<circle cx="-62" cy="-14" r="17"/><path d="M -100 52 C -100 26, -78 18, -62 18"/>'
               '<circle cx="62" cy="-14" r="17"/><path d="M 100 52 C 100 26, 78 18, 62 18"/>')
POP = "&nbsp;".join("".join(f"<span>{ch}</span>" for ch in w) for w in ["אימוני", "כוח"])


def letters(word_list, cls):
    """One span per letter (Hebrew letters don't join), words kept apart."""
    return "&nbsp;".join("".join(f'<span class="{cls}">{ch}</span>' for ch in w) for w in word_list)


TB_A, TB_B = letters(["לכבוד", "החזרה"], "la"), letters(["לשגרה"], "lb")
# Person cutouts (RGBA PNGs from tools/cutout.py) cover the text while it is on screen.
CUT_A, CUT_B = int(sys.argv[5]), int(sys.argv[6])
CUT_RANGES = f"{CUT_A}-{CUT_B}"  # "לכבוד החזרה לשגרה"

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
      :root {{ --red: #ff3340; --green: #39e46b; --cyan: #29c4f6; --glass: rgba(18, 18, 22, 0.62); --line: rgba(255, 255, 255, 0.16); }}
      #cam {{ position: absolute; inset: 0; overflow: hidden; }}
      #frame {{ position: absolute; inset: 0; will-change: transform; }}
      /* Text behind the subject (reference reel): big two-line block left of the head, the person cutout on top. */
      #behind {{ position: absolute; right: 528px; top: 595px; direction: rtl; text-align: right; font-family: "Heebo", sans-serif;
                 color: rgba(255,255,255,.9); text-shadow: 0 6px 28px rgba(0,0,0,.35); white-space: nowrap; transform-origin: 100% 50%; }}
      #behind .top {{ font-weight: 800; font-size: 76px; line-height: 1; margin-inline-end: 6px; }}
      #behind .big {{ font-weight: 900; font-size: 174px; line-height: .9; letter-spacing: -2px; }}
      #behind span {{ display: inline-block; }}
      /* Opening (client, fix 14): plain text on top of the video, centered, each phrase enters whole. */
      #hook {{ top: 1010px; bottom: auto; display: flex; flex-direction: column; align-items: center; gap: 4px; }}
      #hook .hl {{ font-family: "Heebo", sans-serif; font-weight: 900; font-size: 112px; line-height: 1.05; color: #fff; white-space: nowrap;
                   text-shadow: 0 6px 26px rgba(0,0,0,.6), 0 0 2px rgba(0,0,0,.9); }}
      #hook .royal {{ color: #3a64f0; text-shadow: 0 0 2px rgba(255,255,255,.4), 0 6px 26px rgba(0,0,0,.6); }}
      #cutout {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .ov {{ position: absolute; inset: 0; direction: rtl; font-family: "Heebo", sans-serif; color: #fff; pointer-events: none; }}

      /* Hook: big condensed lines at chest height, words resolve from blur. */
      #hook {{ top: 1000px; bottom: auto; text-align: center; font-family: "Karantina", "Heebo", sans-serif; font-weight: 700;
               font-size: 150px; line-height: 0.95; white-space: nowrap; text-shadow: 0 6px 30px rgba(0,0,0,.55); }}
      .hw {{ display: inline-block; opacity: 0; }}
      #hook .beat {{ position: absolute; left: 0; right: 0; top: 0; }}
      #hookB {{ font-size: 165px; }}
      .key {{ color: var(--red); }}
      .key.key-green {{ color: var(--green); }}
      .key.key-cyan {{ color: var(--cyan); }}
      .key.key-royal {{ color: #3a64f0; text-shadow: 0 0 2px rgba(255,255,255,.35), 0 4px 18px rgba(0,0,0,.7); }}
      .hw.royal {{ color: #3a64f0; text-shadow: 0 0 2px rgba(255,255,255,.35), 0 6px 30px rgba(0,0,0,.55); }}

      /* Captions: 2-4 words, white heavy, centered on the chest. */
      .cap {{ position: absolute; left: 0; right: 0; top: 1240px; display: flex; justify-content: center; direction: rtl; }}
      .cap-in {{ font-family: "Heebo", sans-serif; font-weight: 900; font-size: 74px; color: #fff; letter-spacing: -0.5px;
                 text-shadow: 0 4px 18px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.9); white-space: nowrap; }}
      .cap .w {{ display: inline-block; }}

      .card {{ display: flex; align-items: center; gap: 22px; background: var(--glass); border: 2px solid var(--line);
               border-radius: 30px; padding: 22px 34px; font-weight: 800; font-size: 56px; backdrop-filter: blur(14px);
               box-shadow: 0 18px 50px rgba(0,0,0,.35); }}
      .badge {{ width: 70px; height: 70px; border-radius: 50%; display: grid; place-items: center; font-size: 44px; font-weight: 900; flex: none; }}
      .badge.x {{ background: var(--red); }}
      .badge.v {{ background: var(--green); color: #0b1a10; }}

      /* G1: "I'll start tomorrow" struck out, "now!" checked. */
      #g1 {{ display: flex; flex-direction: column; align-items: center; gap: 22px; top: 250px; bottom: auto; }}
      #g1 .card {{ position: relative; }}
      #g1 .strike {{ position: absolute; right: 120px; left: 30px; top: 50%; height: 7px; background: var(--red); border-radius: 4px; transform-origin: right center; }}
      #g1b {{ font-size: 64px; font-weight: 900; border-color: rgba(57,228,107,.7); }}

      /* Motion-graphics page (client reference). */
      #pop {{ position: absolute; left: 0; right: 0; top: 1010px; text-align: center; direction: rtl; font-family: "Heebo", sans-serif;
              font-weight: 900; font-size: 168px; line-height: 1; color: #fff; white-space: nowrap; text-shadow: 0 10px 40px rgba(0,0,0,.45); }}
      #pop span {{ display: inline-block; }}
      #mg {{ position: absolute; inset: 0; overflow: hidden; direction: rtl; font-family: "Heebo", sans-serif; color: #fff;
             background: radial-gradient(120% 80% at 45% 40%, #3a3a3d 0%, #2a2a2c 55%, #1b1b1d 100%); }}
      #mgIn {{ position: absolute; inset: 0; }}
      #mg .glow {{ position: absolute; right: -260px; bottom: -200px; width: 900px; height: 760px; border-radius: 50%;
                   background: radial-gradient(closest-side, rgba(255,40,50,.42), rgba(255,40,50,0)); filter: blur(30px); }}
      #mg .glow2 {{ position: absolute; left: -200px; right: -200px; top: 900px; height: 240px; border-radius: 50%;
                    background: radial-gradient(closest-side, rgba(255,30,40,.7), rgba(255,30,40,0)); filter: blur(26px); }}
      #mgMarq {{ position: absolute; top: 905px; left: 0; white-space: nowrap; font-weight: 900; font-size: 118px; line-height: 1; }}
      #mgBand {{ position: absolute; left: -60px; right: -60px; top: 870px; height: 190px;
                 background: linear-gradient(180deg, #a0141c 0%, #7c0d14 55%, #5e0a10 100%); box-shadow: 0 0 80px rgba(255,30,40,.35);
                 transform-origin: 50% 50%; }}
      #mgType {{ position: absolute; right: 120px; top: 52px; font-weight: 900; font-size: 86px; line-height: 1; white-space: nowrap; }}
      #mgCursor {{ display: inline-block; width: 6px; height: 88px; background: #fff; margin-right: 8px; vertical-align: -12px; }}
      #mgCard {{ position: absolute; left: 90px; right: 90px; top: 640px; height: 620px; border-radius: 44px;
                 background: linear-gradient(160deg, #b51720 0%, #8d1018 50%, #650b11 100%);
                 box-shadow: 0 40px 120px rgba(0,0,0,.55), inset 0 2px 0 rgba(255,255,255,.18); transform-origin: 50% 50%; }}
      #mgCard .ttl {{ position: absolute; left: 0; right: 0; top: 46px; text-align: center; font-weight: 900; font-size: 92px; }}
      #mgCard .ring {{ position: absolute; top: 200px; width: 260px; height: 260px; }}
      #mgCard .ring.r1 {{ right: 70px; }}
      #mgCard .ring.r2 {{ left: 70px; }}
      #mgCard .ring svg {{ width: 100%; height: 100%; overflow: visible; }}
      #mgCard .lbl {{ position: absolute; left: 0; right: 0; top: 300px; text-align: center; font-weight: 800; font-size: 46px; }}
      #leak {{ position: absolute; inset: -10%; pointer-events: none; mix-blend-mode: screen;
               background: radial-gradient(60% 50% at 50% 55%, rgba(255,255,255,.95), rgba(255,170,175,.75) 45%, rgba(255,90,100,.25) 75%, rgba(255,60,70,0)); }}

      /* Line page: dark grid, one long glowing white line, red dot running along it, text above. */
      #lines {{ position: absolute; left: 30px; right: 30px; top: 120px; height: 440px; border-radius: 40px; overflow: hidden;
                border: 2px solid rgba(255,255,255,.14); box-shadow: 0 30px 80px rgba(0,0,0,.5); direction: rtl; font-family: "Heebo", sans-serif; color: #fff;
                background: radial-gradient(110% 75% at 50% 50%, #2b2c2e 0%, #1c1d1f 70%, #121314 100%); }}
      #lines .grid {{ position: absolute; inset: -60px;
        background-image: linear-gradient(rgba(255,255,255,.055) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.055) 2px, transparent 2px);
        background-size: 112px 112px; }}
      #lines .beam {{ position: absolute; left: -40px; right: -40px; top: 284px; height: 18px; border-radius: 10px; background: #fff;
        box-shadow: 0 0 10px #fff, 0 0 34px rgba(255,255,255,.7), 0 0 90px rgba(255,255,255,.35); filter: url(#rough); transform-origin: 0 50%; }}
      #lines .shine {{ position: absolute; top: -10px; bottom: -10px; left: 0; width: 360px; margin-left: -180px; border-radius: 20px;
        background: radial-gradient(closest-side, rgba(255,255,255,1), rgba(255,255,255,0)); filter: blur(4px); }}
      #lines .dot {{ position: absolute; top: 293px; left: 0; width: 56px; height: 56px; margin: -28px 0 0 -28px; border-radius: 50%;
        background: radial-gradient(circle at 40% 40%, #ff6b6b, #ff2a2a 55%, #c40d0d); box-shadow: 0 0 24px #ff3030, 0 0 70px rgba(255,40,40,.75); }}
      #lines .txt {{ position: absolute; left: 0; right: 0; bottom: 186px; text-align: center; white-space: nowrap; text-shadow: 0 6px 30px rgba(0,0,0,.5); }}
      #lines .l1 {{ font-weight: 700; font-size: 70px; line-height: 1.05; }}
      #lines .l2 {{ font-weight: 900; font-size: 108px; line-height: .95; position: relative; }}
      #lines .w {{ display: inline-block; }}
      #lines .red {{ color: #ff2b2b; text-shadow: 0 0 22px rgba(255,40,40,.55); }}

      /* Offer page: black sky with stars behind the video; the video slides away sideways to reveal it. */
      #space {{ position: absolute; inset: 0; overflow: hidden; background: radial-gradient(120% 80% at 60% 45%, #1b1f28 0%, #0d1016 60%, #07090c 100%); }}
      #space .star {{ position: absolute; border-radius: 50%; background: #fff; }}
      #space .streak {{ position: absolute; height: 3px; border-radius: 2px; background: linear-gradient(90deg, transparent, rgba(255,255,255,.75), transparent); }}
      #stars {{ position: absolute; inset: -40px; }}
      #deal {{ position: absolute; right: 110px; top: 690px; direction: rtl; text-align: right; font-family: "Heebo", sans-serif; color: #fff;
               text-shadow: 0 8px 40px rgba(0,0,0,.6); white-space: nowrap; }}
      #deal .big {{ direction: ltr; font-weight: 900; font-size: 330px; line-height: .85; letter-spacing: -8px; }}
      #deal .big .cur {{ font-size: 210px; color: #fff; margin-left: 14px; letter-spacing: 0; }}
      #deal .big span {{ display: inline-block; }}
      #deal .s1 {{ font-weight: 900; font-size: 92px; line-height: 1.05; margin-top: 18px; margin-inline-end: 40px; }}
      #deal .s2 {{ font-weight: 700; font-size: 62px; line-height: 1.1; margin-inline-end: 40px; color: rgba(255,255,255,.82); }}
      #marq {{ position: absolute; left: 0; right: 0; top: 1170px; direction: rtl; text-align: center; white-space: nowrap; font-family: "Heebo", sans-serif;
               font-weight: 900; font-size: 128px; color: #fff; text-shadow: 0 6px 30px rgba(0,0,0,.6); pointer-events: none; }}

      /* G6: call to action. */
      /* CTA as an Instagram DM notification: low-opacity glass, round profile picture. */
      #g6 {{ top: auto; bottom: 440px; display: flex; flex-direction: column; align-items: center; gap: 14px; direction: rtl; }}
      #dm {{ display: flex; align-items: center; gap: 26px; width: 900px; padding: 26px 32px; border-radius: 46px;
             background: rgba(255,255,255,.14); border: 1.5px solid rgba(255,255,255,.28); backdrop-filter: blur(22px) saturate(1.3);
             box-shadow: 0 20px 60px rgba(0,0,0,.28); }}
      #dm .av {{ width: 128px; height: 128px; border-radius: 50%; flex: none; padding: 5px;
                 background: conic-gradient(from 200deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5, #feda75); }}
      #dm .av img {{ width: 100%; height: 100%; border-radius: 50%; display: block; border: 4px solid rgba(20,20,22,.9); }}
      #dm .body {{ flex: 1; min-width: 0; text-align: right; }}
      #dm .top {{ display: flex; align-items: baseline; gap: 14px; font-size: 40px; font-weight: 800; color: #fff; direction: ltr; justify-content: flex-end; }}
      #dm .top .when {{ font-weight: 500; font-size: 34px; color: rgba(255,255,255,.7); }}
      #dm .top .ig {{ font-weight: 500; font-size: 34px; color: rgba(255,255,255,.7); }}
      #dm .msg {{ font-size: 62px; font-weight: 900; color: #fff; margin-top: 6px; line-height: 1.1; text-shadow: 0 2px 10px rgba(0,0,0,.25); }}
      #dm .dot {{ width: 26px; height: 26px; border-radius: 50%; background: #3797f0; flex: none; box-shadow: 0 0 14px rgba(55,151,240,.7); }}
      #g6 .here {{ font-weight: 900; font-size: 62px; text-shadow: 0 4px 18px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.9); margin-top: 6px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}" data-width="1080" data-height="1920">
      <div id="space" class="clip" data-start="{round(TIMES["sp_in"] - 0.05, 2)}" data-duration="{round(TIMES["sp_out"] - TIMES["sp_in"] + 0.05, 2)}" data-track-index="0">
        <div id="stars">{STARS}</div>
        {STREAKS}
        <div id="deal">
          <div class="big"><span>1</span><span>9</span><span>9</span><span class="cur">₪</span></div>
          <div class="s1">לחודש הראשון</div>
        </div>
      </div>
      <div id="cam">
        <div id="frame">
          <video id="a-roll" class="clip" src="{VIDEO}" playsinline data-start="0" data-duration="{DURATION}" data-track-index="0"
                 data-has-audio="true" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>
          <div id="behind" class="clip" data-start="{TIMES["tb_in"]}" data-duration="{round(TIMES["tb_out"] + 0.35 - TIMES["tb_in"], 2)}" data-track-index="1">
            <div class="top">{TB_A}</div>
            <div class="big">{TB_B}</div>
          </div>
          <div id="pop" class="clip" data-start="{TIMES["mg_word"]}" data-duration="{round(TIMES["mg_in"] + 0.35 - TIMES["mg_word"], 2)}" data-track-index="1">{POP}</div>
          <img id="cutout" class="clip" alt="" data-cut-ranges="{CUT_RANGES}" data-start="0" data-duration="{DURATION}" data-track-index="1" />
        </div>
      </div>

      <audio id="music" src="music.wav" data-start="0" data-duration="{DURATION}" data-track-index="6" data-volume="1"></audio>
      <audio id="sfx" src="sfx.wav" data-start="0" data-duration="{DURATION}" data-track-index="5" data-volume="0.35"></audio>


      <div class="ov clip" id="hook" data-start="0" data-duration="{round(t("וזה") + 0.2, 2)}" data-track-index="2">
        <div class="hl" id="hookL">החגים נגמרו</div>
        <div class="hl" id="hookR">חוזרים <span class="royal">לשגרה</span></div>
      </div>

      <div class="ov clip" id="g1" data-start="{TIMES["g1_in"]}" data-duration="{round(TIMES["g1_out"] - TIMES["g1_in"], 2)}" data-track-index="3">
        <div class="card" id="g1a"><span class="badge x">✕</span><span>״אתחיל מחר…״</span><i class="strike"></i></div>
        <div class="card" id="g1b"><span class="badge v">✓</span><span>עכשיו!</span></div>
      </div>

      <div class="clip" id="mg" data-start="{TIMES["mg_in"]}" data-duration="{round(TIMES["mg_out"] - TIMES["mg_in"], 2)}" data-track-index="3">
        <div id="mgIn">
          <div class="glow"></div>
          <div class="glow2" id="mgGlow2"></div>
          <div id="mgMarq">בקבוצות קטנות</div>
          <div id="mgBand"><div id="mgType"><span id="mgTypeTxt"></span><i id="mgCursor"></i></div></div>
          <div id="mgCard">
            <div class="ttl" id="mgTtl">תכנית אישית</div>
            <div class="ring r1">{RING.format(id="ring1", icon=ICON_DUMBBELL)}</div>
            <div class="ring r2">{RING.format(id="ring2", icon=ICON_PEOPLE)}</div>
            <div class="lbl" id="mgLbl">לכל מתאמן</div>
          </div>
        </div>
      </div>
      <div class="clip" id="leakClip" data-start="{round(TIMES["mg_out"] - 0.2, 2)}" data-duration="0.5" data-track-index="4"><div id="leak"></div></div>
      <div class="clip" id="lines" data-start="{TIMES["ln_in"]}" data-duration="{round(TIMES["tb_in"] - TIMES["ln_in"], 2)}" data-track-index="3">
        <svg width="0" height="0" style="position:absolute"><filter id="rough"><feTurbulence id="roughNoise" type="fractalNoise" baseFrequency="0.012 0.9" numOctaves="2" seed="4"/>
          <feDisplacementMap id="roughDisp" in="SourceGraphic" scale="9"/></filter></svg>
        <div class="grid"></div>
        <div class="txt">
          <div class="l1"><span class="w" id="lw1">מלווה</span> <span class="w" id="lw2">אתכם</span></div>
          <div class="l2"><span class="w" id="lw3">לאורך</span> <span class="w red" id="lw4">כל הדרך</span></div>
        </div>
        <div class="beam"><i class="shine"></i></div>
        <div class="dot"></div>
      </div>

      <div class="clip" id="marq" data-start="{TIMES["mq_in"]}" data-duration="{round(TIMES["sp_in"] + 0.9 - TIMES["mq_in"], 2)}" data-track-index="3">יצאתי במבצע</div>

      <div class="ov clip" id="g6" data-start="{TIMES["g6_in"]}" data-duration="{round(DURATION - TIMES["g6_in"], 2)}" data-track-index="3">
        <div id="dm">
          <div class="av"><img src="avatar.png" alt="" /></div>
          <div class="body">
            <div class="top"><span class="when">עכשיו</span><span>idoamarr</span></div>
            <div class="msg">שלחו לי הודעה</div>
          </div>
          <i class="dot"></i>
        </div>
        <div class="here" id="here">ונשמור לכם מקום</div>
      </div>

{cap_html}
    </div>

    <script>
      // Critically damped spring: fast start, settles on the target, never overshoots.
      const spring = (p) => (1 - (1 + 7 * p) * Math.exp(-7 * p)) / (1 - 8 * Math.exp(-7));

      const FACE_FPS = {face["fps"]};
      const FACE_X = {json.dumps([round(p["x"], 1) for p in face["track"]])};
      const FACE_Y = {json.dumps([round(p["y"], 1) for p in face["track"]])};
      const ZOOM = {json.dumps(ZOOM)};
      const HOOK_T = {json.dumps([w["t"] for w in HOOK])};
      const CAPS = {json.dumps([c["start"] for c in captions])};
      const T = {json.dumps({k: round(v, 2) for k, v in TIMES.items()})};

      const tl = gsap.timeline({{ paused: true }});

      // Zoom center follows the face every frame, in percent of the frame.
      tl.set("#frame", {{ transformOrigin: `${{FACE_X[0]}}% ${{FACE_Y[0]}}%` }}, 0);
      for (let i = 1; i < FACE_X.length; i++) {{
        tl.set("#frame", {{ transformOrigin: `${{FACE_X[i]}}% ${{FACE_Y[i]}}%` }}, i / FACE_FPS);
      }}

      let cur = 1;
      for (const [kind, at, scale, dur] of ZOOM) {{
        if (kind === "set") tl.set("#frame", {{ scale }}, at);
        else {{
          const ease = kind === "punch" || kind === "snap" ? spring : kind === "back" ? "power3.inOut" : kind === "ease" ? "power2.inOut" : "sine.inOut";
          // A snap gets a short motion-blur kick so the jump reads as a camera move.
          if (kind === "snap") tl.fromTo("#frame", {{ filter: "blur(5px)" }}, {{ filter: "blur(0px)", duration: 0.16, ease: "power2.out", immediateRender: false }}, at);
          tl.fromTo("#frame", {{ scale: cur }}, {{ scale, duration: dur, ease, immediateRender: false }}, at);
        }}
        cur = scale;
      }}

      // Opening: each phrase comes in whole from a soft blur and rises into place; both leave together before "וזה הזמן".
      const phraseIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, y: 34, scale: 0.94, filter: "blur(12px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out", immediateRender: false }}, at);
      phraseIn("#hookL", Math.max(0, HOOK_T[0] - 0.1));
      phraseIn("#hookR", HOOK_T[2] - 0.06);
      tl.fromTo("#hookR .royal", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.4, ease: spring, immediateRender: false }}, HOOK_T[3]);
      tl.set("#hookR .royal", {{ display: "inline-block" }}, 0);
      tl.to(["#hookL", "#hookR"], {{ opacity: 0, y: -24, filter: "blur(12px)", duration: 0.2, ease: "power2.in" }}, {round(t("וזה") - 0.18, 2)});

      // Captions pop in.
      CAPS.forEach((at, i) => {{
        tl.fromTo(`#cap${{i}} .cap-in`, {{ opacity: 0, scale: 0.82, y: 24 }},
          {{ opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2.2)", immediateRender: false }}, at);
      }});

      // Hidden from t=0: a clip's later children would otherwise show at full opacity
      // from the clip's start until their own pop-in, then pop a second time.
      tl.set(["#hookL", "#hookR", "#g1a", "#g1b", "#lines", "#pop span", "#mgCard", "#mgTtl", "#mgLbl", "#mgBand", "#lw1", "#lw2", "#lw3", "#lw4", "#deal .big span", "#deal .s1",
              "#dm", "#here"], {{ opacity: 0 }}, 0);
      const CARD_FROM = {{ opacity: 0, y: 320, rotationX: 48, rotation: -8, scale: 1.25, filter: "blur(10px)", transformPerspective: 900 }};
      const CARD_TO = {{ opacity: 1, y: 0, rotationX: 0, rotation: 0, scale: 1, filter: "blur(0px)", transformPerspective: 900 }};
      const cardIn = (sel, at) => tl.fromTo(sel, CARD_FROM, {{ ...CARD_TO, duration: 0.6, ease: "power3.out", immediateRender: false }}, at);
      const cardOut = (sel, at) => tl.to(sel, {{ opacity: 0, y: 260, rotationX: 40, rotation: -6, scale: 0.92, filter: "blur(12px)",
        transformPerspective: 900, duration: 0.35, stagger: 0.04, ease: "power2.in" }}, at);
      const popIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, scale: 0.6 }},
        {{ opacity: 1, scale: 1, duration: 0.4, ease: spring, immediateRender: false }}, at);

      // G1: "I'll start tomorrow" gets struck out, then "now!" checks in.
      // "אתחיל מחר" / "עכשיו!" (fix 14: client found the 3D entrance jumpy): a smooth glide-and-fade instead.
      const smoothIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, y: 70, scale: 0.97, filter: "blur(6px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.7, ease: "sine.out", immediateRender: false }}, at);
      smoothIn("#g1a", T.g1_in);
      tl.fromTo("#g1a .strike", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, T.g1_strike);
      tl.to("#g1a", {{ opacity: 0.55, duration: 0.3 }}, T.g1_strike + 0.3);
      smoothIn("#g1b", T.g1_b);
      tl.fromTo("#g1b .badge", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.5, ease: "back.out(1.6)", immediateRender: false }}, T.g1_b + 0.3);
      tl.to("#g1 .card", {{ opacity: 0, y: 50, filter: "blur(6px)", duration: 0.4, ease: "sine.in", stagger: 0.05 }}, T.g1_out - 0.4);

      // Motion-graphics sequence (client reference) on "אימוני כוח בקבוצות קטנות עד 6 ... תכנית אישית".
      // A) "אימוני כוח" pops letter by letter on the video, tracking closing in.
      tl.fromTo("#pop span", {{ opacity: 0, scale: 0.4, y: 40 }},
        {{ opacity: 1, scale: 1, y: 0, duration: 0.22, stagger: 0.035, ease: "back.out(2.4)", immediateRender: false }}, T.mg_word);
      tl.fromTo("#pop", {{ letterSpacing: "34px" }}, {{ letterSpacing: "0px", duration: 0.5, ease: "power3.out", immediateRender: false }}, T.mg_word);
      // B) zoom-blur push through the shot into the dark page.
      tl.fromTo("#cam", {{ scale: 1, filter: "blur(0px)" }}, {{ scale: 2.6, filter: "blur(26px)", duration: 0.3, ease: "power2.in", immediateRender: false }}, T.mg_in - 0.2);
      tl.set("#cam", {{ scale: 1, filter: "blur(0px)" }}, T.mg_out);
      tl.fromTo("#mg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.14, ease: "power1.in", immediateRender: false }}, T.mg_in);
      tl.fromTo("#mgIn", {{ scale: 1.0 }}, {{ scale: 1.08, duration: T.mg_out - T.mg_in, ease: "none", immediateRender: false }}, T.mg_in);
      // C) "בקבוצות קטנות" streams across on a red glow, red-hot at first, cooling to white.
      tl.fromTo("#mgMarq", {{ x: -1150, color: "#ff3b45", textShadow: "0 0 30px rgba(255,40,50,.9)", filter: "blur(8px)" }},
        {{ x: 760, color: "#ffffff", textShadow: "0 0 18px rgba(255,255,255,.25)", filter: "blur(0px)", duration: T.mg_band - T.mg_in + 0.25,
           ease: "power1.inOut", immediateRender: false }}, T.mg_in + 0.02);
      tl.fromTo("#mgGlow2", {{ opacity: 0.9, scaleX: 0.6 }}, {{ opacity: 0.25, scaleX: 1.3, duration: T.mg_band - T.mg_in, ease: "none", immediateRender: false }}, T.mg_in);
      tl.to("#mgMarq", {{ opacity: 0, duration: 0.15 }}, T.mg_band + 0.1);
      // D) the red band opens and "עד 6 מתאמנים באימון" is typed with a cursor.
      tl.fromTo("#mgBand", {{ scaleY: 0, opacity: 0 }}, {{ scaleY: 1, opacity: 1, duration: 0.25, ease: "power3.out", immediateRender: false }}, T.mg_band);
      const TYPE = "עד 6 מתאמנים באימון", typ = {{ n: 0 }};
      tl.fromTo(typ, {{ n: 0 }}, {{ n: TYPE.length, duration: T.mg_type1 - T.mg_type0, ease: "none", immediateRender: false,
        onUpdate: () => {{ document.querySelector("#mgTypeTxt").textContent = TYPE.slice(0, Math.round(typ.n)); }} }}, T.mg_type0);
      tl.set("#mgTypeTxt", {{ textContent: "" }}, T.mg_band);
      [0, 1, 2, 3, 4, 5, 6].forEach((k) => tl.set("#mgCursor", {{ opacity: k % 2 ? 0 : 1 }}, T.mg_type1 + k * 0.12));
      // E) the band tips over in 3D and becomes the plan card; the rings fill.
      tl.to("#mgBand", {{ rotationX: 70, rotationZ: -6, y: 120, opacity: 0, transformPerspective: 900, duration: 0.3, ease: "power2.in" }}, T.mg_card);
      tl.fromTo("#mgCard", {{ opacity: 0, rotationX: 62, rotationY: -28, rotationZ: -9, y: 220, scale: 0.8, transformPerspective: 1100 }},
        {{ opacity: 1, rotationX: 14, rotationY: -16, rotationZ: -3, y: 0, scale: 1, transformPerspective: 1100, duration: 0.5, ease: "power3.out",
           immediateRender: false }}, T.mg_card + 0.12);
      tl.to("#mgCard", {{ rotationX: 6, rotationY: 8, rotationZ: 2, duration: T.mg_out - T.mg_card - 0.62, ease: "sine.inOut" }}, T.mg_card + 0.62);
      tl.fromTo("#ring1", {{ attr: {{ "stroke-dashoffset": 942.5 }} }}, {{ attr: {{ "stroke-dashoffset": 942.5 * 0.18 }}, duration: 0.9, ease: "power2.out", immediateRender: false }}, T.mg_card + 0.35);
      tl.fromTo("#ring2", {{ attr: {{ "stroke-dashoffset": 942.5 }} }}, {{ attr: {{ "stroke-dashoffset": 942.5 * 0.32 }}, duration: 0.9, ease: "power2.out", immediateRender: false }}, T.mg_card + 0.45);
      tl.fromTo("#mgLbl", {{ opacity: 0, filter: "blur(10px)", scale: 0.8 }}, {{ opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, T.mg_lbl);
      tl.fromTo("#mgTtl", {{ opacity: 0, y: -30, filter: "blur(12px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out", immediateRender: false }}, T.mg_title - 0.05);
      // F) light-leak flash back to the video.
      tl.fromTo("#leak", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1.15, duration: 0.2, ease: "power2.in", immediateRender: false }}, T.mg_out - 0.2);
      tl.to("#leak", {{ opacity: 0, scale: 1.4, duration: 0.3, ease: "power2.out" }}, T.mg_out);

      // Line page: words resolve from grey blur, the red dot runs the full line, "כל הדרך" glitches in red.
      // Wide card across the top (client: keep the trainer in view), same approved card entrance and exit.
      cardIn("#lines", T.ln_in);
      cardOut("#lines", T.tb_in - 0.35);
      tl.fromTo("#lines .grid", {{ scale: 1.0 }}, {{ scale: 1.06, duration: T.tb_in - T.ln_in, ease: "none", immediateRender: false }}, T.ln_in);
      tl.fromTo("#lines .beam", {{ scaleX: 0.15, opacity: 0.4 }}, {{ scaleX: 1, opacity: 1, duration: 0.22, ease: "power3.out", immediateRender: false }}, T.ln_in);
      tl.fromTo("#lines .dot", {{ x: -60 }}, {{ x: 1080, duration: T.tb_in - T.ln_in - 0.4, ease: "sine.inOut", immediateRender: false }}, T.ln_in);
      // The line lives on its own: its rough edge crackles, it waves gently, the glow breathes,
      // and a bright pulse rides along it with the red dot.
      const beamEl = document.querySelector("#lines .beam"), noise = document.querySelector("#roughNoise"),
            disp = document.querySelector("#roughDisp"), shine = document.querySelector("#lines .shine");
      const live = {{ k: 0 }};
      const LN_DUR = T.tb_in - T.ln_in;
      tl.fromTo(live, {{ k: 0 }}, {{ k: 1, duration: LN_DUR, ease: "none", immediateRender: false, onUpdate: () => {{
        const s = live.k * LN_DUR;
        noise.setAttribute("seed", String(4 + Math.floor(s * 18)));
        noise.setAttribute("baseFrequency", `${{(0.010 + 0.004 * Math.sin(s * 5.3)).toFixed(4)}} 0.9`);
        disp.setAttribute("scale", String((11 + 8 * Math.sin(s * 9.1)).toFixed(2)));
        const glow = 0.75 + 0.25 * Math.sin(s * 11);
        beamEl.style.boxShadow = `0 0 ${{10 + 6 * glow}}px #fff, 0 0 ${{30 + 14 * glow}}px rgba(255,255,255,${{0.55 + 0.25 * glow}}), 0 0 ${{80 + 30 * glow}}px rgba(255,255,255,${{0.25 + 0.15 * glow}})`;
        beamEl.style.translate = `0 ${{(9 * Math.sin(s * 3.4)).toFixed(2)}}px`;
        beamEl.style.rotate = `${{(0.8 * Math.sin(s * 2.1)).toFixed(3)}}deg`;
        shine.style.left = `${{(-10 + 125 * (s / LN_DUR)).toFixed(2)}}%`;
      }} }}, T.ln_in);
      tl.fromTo("#lines .dot", {{ y: 0 }}, {{ y: 0, duration: LN_DUR, ease: "none", immediateRender: false,
        onUpdate: function () {{ const s = this.progress() * LN_DUR; gsap.set("#lines .dot", {{ y: 9 * Math.sin(s * 3.4) + (Math.min(1, s / (LN_DUR - 0.35)) * 1140 - 510) * Math.tan(0.8 * Math.sin(s * 2.1) * Math.PI / 180) }}); }} }}, T.ln_in);
      const wordIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, color: "#8a8a8a", filter: "blur(10px)", y: 10 }},
        {{ opacity: 1, color: "#ffffff", filter: "blur(0px)", y: 0, duration: 0.3, ease: "power2.out", immediateRender: false }}, at);
      wordIn("#lw1", T.ln_w1); wordIn("#lw2", T.ln_w2); wordIn("#lw3", T.ln_b);
      tl.fromTo("#lw4", {{ opacity: 0, x: -30, skewX: -14, textShadow: "-10px 0 rgba(0,220,255,.8), 10px 0 rgba(255,0,60,.9)" }},
        {{ opacity: 1, x: 0, skewX: 0, textShadow: "0px 0 rgba(0,220,255,0), 0px 0 rgba(255,0,60,0)", duration: 0.28, ease: "steps(5)", immediateRender: false }}, T.ln_red);
      tl.fromTo("#lw4", {{ scale: 1.15 }}, {{ scale: 1, duration: 0.35, ease: spring, immediateRender: false }}, T.ln_red + 0.28);

      // Text behind the subject: letters resolve from the left with tracking closing in,
      // the block drifts in shallow 3D, then whips out to the right with a smear.
      tl.set(["#behind .la", "#behind .lb"], {{ opacity: 0 }}, 0);
      tl.fromTo("#behind .top", {{ letterSpacing: "26px" }}, {{ letterSpacing: "0px", duration: 0.6, ease: "power3.out", immediateRender: false }}, T.tb_in);
      tl.fromTo([...document.querySelectorAll("#behind .la")].reverse(), {{ opacity: 0, x: -40, filter: "blur(10px)" }},
        {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.32, stagger: 0.035, ease: "power3.out", immediateRender: false }}, T.tb_in);
      tl.fromTo([...document.querySelectorAll("#behind .lb")].reverse(), {{ opacity: 0, x: -70, scale: 1.25, filter: "blur(14px)" }},
        {{ opacity: 1, x: 0, scale: 1, filter: "blur(0px)", duration: 0.4, stagger: 0.055, ease: "power3.out", immediateRender: false }}, T.tb_big);
      tl.fromTo("#behind", {{ x: 6, rotationY: 7, transformPerspective: 1200 }},
        {{ x: 26, rotationY: 3, transformPerspective: 1200, duration: T.tb_out - T.tb_in, ease: "none", immediateRender: false }}, T.tb_in);
      tl.to("#behind", {{ x: 300, scaleX: 1.35, opacity: 0, filter: "blur(22px)", duration: 0.3, ease: "power2.in" }}, T.tb_out);

      // Offer: "יצאתי במבצע" streams in from the left over the video, the whole shot slides off to the right
      // with motion blur onto the star page, "199₪" lands letter by letter, the two lines resolve, the block
      // drifts right; hard cut back to the video on "רוצים".
      tl.fromTo("#marq", {{ x: -1100, filter: "blur(6px)" }}, {{ x: -60, filter: "blur(0px)", duration: T.sp_in - T.mq_in, ease: "power2.out", immediateRender: false }}, T.mq_in);
      tl.to("#marq", {{ x: 1500, filter: "blur(16px)", duration: 0.85, ease: "power2.in" }}, T.sp_in);
      tl.fromTo("#cam", {{ x: 0, filter: "blur(0px)" }}, {{ x: 1300, filter: "blur(18px)", duration: 0.4, ease: "power2.in", immediateRender: false }}, T.sp_in);
      // Back from the star page (client's transition reference): hard cut, the shot opens over-exposed and a touch
      // soft (+35% brightness), holds two frames, then settles in ~0.2 s.
      tl.set("#cam", {{ x: 0, filter: "brightness(1.35) blur(1.2px)" }}, T.sp_out);
      tl.to("#cam", {{ filter: "brightness(1) blur(0px)", duration: 0.22, ease: "power2.out" }}, T.sp_out + 0.035);
      tl.fromTo("#stars", {{ x: -30 }}, {{ x: 40, duration: T.sp_out - T.sp_in, ease: "none", immediateRender: false }}, T.sp_in);
      document.querySelectorAll("#space .streak").forEach((el, i) => {{
        tl.fromTo(el, {{ x: 0, opacity: 0.9 }}, {{ x: 2600, opacity: 0, duration: 0.5 + (i % 3) * 0.12, ease: "power1.in", immediateRender: false }}, T.sp_in + i * 0.04);
      }});
      tl.fromTo([...document.querySelectorAll("#deal .big span")].reverse(), {{ opacity: 0, x: -260, filter: "blur(16px)", scaleX: 1.4 }},
        {{ opacity: 1, x: 0, filter: "blur(0px)", scaleX: 1, duration: 0.42, stagger: 0.07, ease: "power3.out", immediateRender: false }}, T.sp_num);
      tl.fromTo("#deal .s1", {{ opacity: 0, x: -60, filter: "blur(14px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "power3.out", immediateRender: false }}, T.sp_sub);
      tl.fromTo("#deal", {{ x: -30 }}, {{ x: 30, duration: T.sp_out - T.sp_num, ease: "none", immediateRender: false }}, T.sp_num);

      // G6: call to action with a bouncing arrow.
      // DM notification drops in from the top of its slot like a real banner, then the line under it.
      tl.fromTo("#dm", {{ opacity: 0, y: -90, scale: 0.92, filter: "blur(8px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: spring, immediateRender: false }}, T.g6_in - 0.05);
      tl.fromTo("#dm .dot", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false }}, T.g6_in + 0.35);
      tl.fromTo("#here", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "back.out(2)", immediateRender: false }}, T.g6_here);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(OUT, "w").write(html)

# Sound cues, rendered to sfx.wav by tools/sfx.py.
G = TIMES
events = [("whoosh_soft", t("חוזרים"))]
events += [("thump", at) for kind, at, *_ in ZOOM if kind in ("snap", "punch")]
events += [("whoosh", G["g1_in"]), ("scratch", G["g1_strike"]), ("whoosh", G["g1_b"]), ("ding", G["g1_b"] + 0.3)]
events += [("whoosh_out", G["g1_out"] - 0.35)]
events += [("pop", G["mg_word"] + k * 0.07) for k in range(3)] + [("whoosh", G["mg_in"] - 0.2), ("thump", G["mg_in"])]
events += [("whoosh_soft", G["mg_in"] + 0.05), ("whoosh", G["mg_band"])]
events += [("tick", G["mg_type0"] + k * (G["mg_type1"] - G["mg_type0"]) / 10) for k in range(10)]
events += [("whoosh", G["mg_card"]), ("ding", G["mg_card"] + 0.5), ("pop", G["mg_lbl"]), ("pop", G["mg_title"])]
events += [("whoosh_out", G["mg_out"] - 0.2), ("whoosh", G["ln_in"]), ("whoosh_soft", G["ln_in"] + 0.15)]
events += [("tick", G[k]) for k in ("ln_w1", "ln_w2", "ln_b")] + [("scratch", G["ln_red"]), ("pop", G["ln_red"] + 0.28), ("whoosh_out", G["tb_in"] - 0.35)]
events += [("whoosh_soft", G["tb_in"]), ("whoosh", G["tb_big"]), ("whoosh_soft", G["mq_in"]), ("whoosh", G["sp_in"])]
events += [("tick", G["sp_num"] + i * 0.07) for i in range(4)] + [("thump", G["sp_num"] + 0.25)]
events += [("pop", G["sp_sub"]), ("thump", G["sp_out"])]
events += [("whoosh_soft", G["g6_in"] - 0.05), ("ding", G["g6_in"] + 0.3), ("pop", G["g6_here"])]
json.dump({"duration": DURATION, "events": [[n, round(a, 3)] for n, a in sorted(events, key=lambda e: e[1])]},
          open(os.path.join(os.path.dirname(OUT), "sfx.json"), "w"))
print("wrote", OUT, len(captions), "captions")
