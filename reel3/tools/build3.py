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
KEY_COLOR = {"6": "key-green", "מלווה": "key-cyan"}


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
    ("push", 0.0, 1.14, t("וזה")),
    # "לאימונים": sharp snap in, then glide back out before the next sentence.
    ("snap", t("לאימונים"), 1.30, 0.2),
    ("back", after("לאימונים"), 1.00, t("אם") - after("לאימונים") + 0.25),
    ("push", t("אם") + 0.25, 1.12, t("עכשיו") - t("אם") - 0.25),
    # "עכשיו": the second snap.
    ("snap", t("עכשיו"), 1.30, 0.2),
    ("back", t("סיבה"), 1.00, t("אימוני") - t("סיבה")),
    ("push", t("אימוני"), 1.08, t("6") - t("אימוני")),
    ("punch", t("6"), 1.22, 0.45),
    ("ease", t("אני"), 1.00, 0.45),
    ("push", t("אני") + 0.45, 1.08, t("מלווה") - t("אני") - 0.45),
    ("punch", t("מלווה"), 1.20, 0.45),
    ("back", t("לאורך"), 1.00, t("לכבוד") - t("לאורך")),
    ("push", t("לכבוד"), 1.10, t("199") - t("לכבוד")),
    # "199": the hardest snap of the reel.
    ("snap", t("199"), 1.32, 0.2),
    ("back", t("לחודש"), 1.00, t("רוצים") - t("לחודש")),
    ("push", t("רוצים"), 1.16, DURATION - t("רוצים")),
]

TIMES = {
    "g1_in": t("אומרים") - 0.05, "g1_strike": t("לעצמכם") + 0.1, "g1_b": t("עכשיו") - 0.05, "g1_out": after("להתחיל", 2) + 0.1,
    "g2_in": t("אימוני"), "g2_tag": t("בקבוצות"), "g2_lit": t("עד"), "g2_num": t("6"), "g2_out": t("אני") - 0.05,
    "g3_in": t("בונה") - 0.05, "g3_check": t("תכנית"), "g3_out": t("מלווה") - 0.05,
    "g4_in": t("מלווה"), "g4_draw": t("לאורך"), "g4_flag": t("הדרך"), "g4_out": t("לכבוד") - 0.05,
    "tb_in": t("לכבוד") - 0.12, "tb_big": t("לשגרה", 2) - 0.2, "tb_out": t("199") - 0.5 - 0.2,
    "g5_in": t("199") - 0.5, "g5_num": t("199"), "g5_tag": t("לחודש"), "g5_out": t("רוצים") - 0.05,
    "g6_in": t("שלחו"), "g6_here": t("ונשמור"),
}


def esc_words(ws):
    return " ".join(
        f'<span class="w{" key " + KEY_COLOR.get(w.strip("?"), "") if w.strip("?") in KEYWORDS else ""}">{w}</span>' for w in ws)


# The CTA pill and "פה למטה" cover the last two chunks, so their captions are dropped.
captions = [c for c in captions if c["words"] not in (["שלחו", "לי", "הודעה"], ["ונשמור", "לכם", "מקום"])]
# The price card shows "199₪", so that caption is dropped too.
captions = [c for c in captions if c["words"] != ["של", "199", "ש״ח"]]
# The big text behind the trainer already says "לכבוד החזרה / לשגרה" (client: no duplicate at the bottom).
captions = [c for c in captions if c["words"] not in (["לכבוד", "החזרה"], ["לשגרה"])]
cap_html = "\n".join(
    f'      <div class="cap clip" id="cap{i}" data-start="{c["start"]}" data-duration="{round(c["end"] - c["start"], 2)}"'
    f' data-track-index="2"><div class="cap-in">{esc_words(c["words"])}</div></div>'
    for i, c in enumerate(captions)
)
# Beat A: "החגים נגמרו"; beat B replaces it alone: "חוזרים לשגרה".
HOOK_BEATS = [("hookA", [(0, 2)]), ("hookB", [(2, 4)])]
def hook_line(a, b):
    return "<div>" + " ".join(
        f'<span class="hw{" key" if HOOK[i]["w"] in KEYWORDS else ""}" id="hw{i}">{HOOK[i]["w"]}</span>' for i in range(a, b)) + "</div>"
hook_html = "\n".join(
    f'        <div class="beat" id="{bid}">' + "".join(hook_line(a, b) for a, b in lines) + "</div>" for bid, lines in HOOK_BEATS)

PERSON = ('<svg viewBox="0 0 24 24" class="person"><circle cx="12" cy="7" r="4"/>'
          '<path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8z"/></svg>')
ROW = '<div class="row"><span class="tick"><b>✓</b></span><i class="bar" style="width:{w}px"></i></div>'
# Road from start dot to finish flag (drawn right-to-left, like the text).
ROAD = "M 600 150 C 470 150, 450 40, 320 60 S 140 150, 60 70"

def letters(word_list, cls):
    """One span per letter (Hebrew letters don't join), words kept apart."""
    return "&nbsp;".join("".join(f'<span class="{cls}">{ch}</span>' for ch in w) for w in word_list)


TB_A, TB_B = letters(["לכבוד", "החזרה"], "la"), letters(["לשגרה"], "lb")
# Person cutouts (RGBA PNGs from tools/cutout.py) cover the text while it is on screen.
CUT_A, CUT_B = int(sys.argv[5]), int(sys.argv[6])

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

      /* G2: strength training in small groups, up to 6. */
      #g2 {{ top: 210px; bottom: auto; display: flex; flex-direction: column; align-items: center; gap: 22px; }}
      #g2 .tag {{ font-size: 50px; padding: 16px 30px; }}
      #people {{ display: flex; gap: 16px; background: var(--glass); border: 2px solid var(--line); border-radius: 36px; padding: 24px 34px; backdrop-filter: blur(14px); align-items: center; }}
      .person {{ width: 72px; height: 72px; fill: rgba(255,255,255,.28); }}
      #people .num {{ font-family: "Karantina", sans-serif; font-weight: 700; font-size: 104px; line-height: .8; color: var(--green); margin-inline-start: 12px; white-space: nowrap; }}

      /* G3: personal plan, rows check off. */
      #g3 {{ top: 230px; bottom: auto; display: flex; justify-content: center; }}
      #plan {{ flex-direction: column; align-items: stretch; gap: 20px; padding: 28px 40px 34px; min-width: 560px; }}
      #plan .title {{ display: flex; align-items: center; gap: 16px; font-size: 56px; font-weight: 900; }}
      #plan .title .clip-ico {{ font-size: 50px; }}
      #plan .row {{ display: flex; align-items: center; gap: 20px; }}
      #plan .tick {{ width: 58px; height: 58px; border-radius: 16px; border: 3px solid rgba(255,255,255,.35); position: relative; flex: none; }}
      #plan .tick b {{ position: absolute; inset: -3px; border-radius: 16px; background: var(--green); color: #0b1a10; display: grid; place-items: center; font-size: 38px; font-weight: 900; opacity: 0; }}
      #plan .bar {{ height: 18px; border-radius: 9px; background: rgba(255,255,255,.3); display: block; }}

      /* G4: the road, walked together to the flag. */
      #g4 {{ top: 230px; bottom: auto; display: flex; justify-content: center; }}
      #road {{ flex-direction: column; gap: 6px; padding: 22px 30px 18px; }}
      #road .lbl {{ font-size: 50px; font-weight: 900; }}
      #road svg {{ width: 660px; height: 210px; overflow: visible; }}
      #road .track {{ fill: none; stroke: rgba(255,255,255,.18); stroke-width: 14; stroke-linecap: round; stroke-dasharray: 2 26; }}
      #road .done {{ fill: none; stroke: var(--cyan); stroke-width: 14; stroke-linecap: round; }}

      /* G5: the offer. */
      #g5 {{ top: 150px; bottom: auto; display: flex; justify-content: center; }}
      #offer {{ flex-direction: column; gap: 0; padding: 26px 64px 34px; border-color: rgba(255,51,64,.55); }}
      #offer .lbl {{ font-size: 46px; font-weight: 800; background: var(--red); border-radius: 999px; padding: 6px 30px; }}
      #offer .price {{ display: flex; align-items: baseline; gap: 10px; direction: ltr; font-family: "Karantina", sans-serif; font-weight: 700; line-height: .9; margin-top: 10px; }}
      #offer .price .n {{ font-size: 200px; min-width: 250px; text-align: center; }}
      #offer .price .cur {{ font-size: 110px; color: var(--red); }}
      #offer .sub {{ font-size: 54px; font-weight: 900; }}

      /* G6: call to action. */
      #g6 {{ top: auto; bottom: 440px; display: flex; flex-direction: column; align-items: center; gap: 10px; }}
      #g6 .pill {{ background: var(--cyan); text-shadow: 0 2px 8px rgba(0,60,90,.45); border-radius: 999px; padding: 22px 54px; font-weight: 900; font-size: 64px; box-shadow: 0 16px 50px rgba(41,196,246,.45); }}
      #g6 .here {{ font-weight: 900; font-size: 62px; text-shadow: 0 4px 18px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.9); margin-top: 6px; }}
      #g6 .arrow {{ font-size: 90px; font-weight: 900; line-height: 1; text-shadow: 0 4px 18px rgba(0,0,0,.6); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}" data-width="1080" data-height="1920">
      <div id="cam">
        <div id="frame">
          <video id="a-roll" class="clip" src="{VIDEO}" playsinline data-start="0" data-duration="{DURATION}" data-track-index="0"
                 data-has-audio="true" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>
          <div id="behind" class="clip" data-start="{TIMES["tb_in"]}" data-duration="{round(TIMES["tb_out"] + 0.35 - TIMES["tb_in"], 2)}" data-track-index="1">
            <div class="top">{TB_A}</div>
            <div class="big">{TB_B}</div>
          </div>
          <img id="cutout" class="clip" alt="" data-cut-first="{CUT_A}" data-cut-last="{CUT_B}"
               data-start="{round((CUT_A - 1) / face["fps"], 3)}" data-duration="{round((CUT_B - CUT_A + 1) / face["fps"], 3)}" data-track-index="1" />
        </div>
      </div>

      <audio id="music" src="music.wav" data-start="0" data-duration="{DURATION}" data-track-index="6" data-volume="1"></audio>
      <audio id="sfx" src="sfx.wav" data-start="0" data-duration="{DURATION}" data-track-index="5" data-volume="0.55"></audio>

      <div class="ov clip" id="hook" data-start="0" data-duration="{round(t("וזה") + 0.05, 2)}" data-track-index="1">
{hook_html}
      </div>

      <div class="ov clip" id="g1" data-start="{TIMES["g1_in"]}" data-duration="{round(TIMES["g1_out"] - TIMES["g1_in"], 2)}" data-track-index="3">
        <div class="card" id="g1a"><span class="badge x">✕</span><span>״אתחיל מחר…״</span><i class="strike"></i></div>
        <div class="card" id="g1b"><span class="badge v">✓</span><span>עכשיו!</span></div>
      </div>

      <div class="ov clip" id="g2" data-start="{TIMES["g2_in"]}" data-duration="{round(TIMES["g2_out"] - TIMES["g2_in"], 2)}" data-track-index="3">
        <div class="card tag" id="g2t">💪 אימוני כוח בקבוצות קטנות</div>
        <div id="people">{"".join(PERSON for _ in range(6))}<span class="num">עד 6</span></div>
      </div>

      <div class="ov clip" id="g3" data-start="{TIMES["g3_in"]}" data-duration="{round(TIMES["g3_out"] - TIMES["g3_in"], 2)}" data-track-index="3">
        <div class="card" id="plan">
          <div class="title"><span class="clip-ico">📋</span><span>תכנית אישית</span></div>
          {ROW.format(w=330)}{ROW.format(w=260)}{ROW.format(w=300)}
        </div>
      </div>

      <div class="ov clip" id="g4" data-start="{TIMES["g4_in"]}" data-duration="{round(TIMES["g4_out"] - TIMES["g4_in"], 2)}" data-track-index="3">
        <div class="card" id="road">
          <div class="lbl">לאורך כל הדרך</div>
          <svg viewBox="0 0 660 210">
            <path class="track" d="{ROAD}"/>
            <path class="done" id="roadDone" d="{ROAD}"/>
            <circle cx="600" cy="150" r="20" fill="#fff"/>
            <g id="flag" transform="translate(60 70)">
              <line x1="0" y1="10" x2="0" y2="-80" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
              <path d="M 0 -80 L -70 -60 L 0 -40 Z" fill="var(--red)"/>
            </g>
            <g id="walker"><circle r="26" fill="var(--cyan)" stroke="#fff" stroke-width="6"/></g>
          </svg>
        </div>
      </div>

      <div class="ov clip" id="g5" data-start="{TIMES["g5_in"]}" data-duration="{round(TIMES["g5_out"] - TIMES["g5_in"], 2)}" data-track-index="3">
        <div class="card" id="offer">
          <div class="lbl">מבצע חזרה לשגרה</div>
          <div class="price"><span class="n" id="priceN">0</span><span class="cur">₪</span></div>
          <div class="sub" id="offerSub">לחודש הראשון</div>
        </div>
      </div>

      <div class="ov clip" id="g6" data-start="{TIMES["g6_in"]}" data-duration="{round(DURATION - TIMES["g6_in"], 2)}" data-track-index="3">
        <div class="pill" id="pill">שלחו לי הודעה</div>
        <div class="here" id="here">פה למטה</div>
        <div class="arrow" id="arrow">↓</div>
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

      // Hook words resolve from blur as they are spoken; beat B replaces beat A.
      HOOK_T.forEach((at, i) => {{
        tl.fromTo(`#hw${{i}}`, {{ opacity: 0, y: 40, filter: "blur(18px)" }},
          {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, Math.max(0, at - 0.06));
      }});
      tl.fromTo("#hw3", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.4, ease: spring, immediateRender: false }}, HOOK_T[3]);
      tl.to("#hookA .hw", {{ opacity: 0, filter: "blur(16px)", y: -30, duration: 0.16, ease: "power2.in" }}, HOOK_T[2] - 0.18);
      tl.to("#hookB .hw", {{ opacity: 0, filter: "blur(16px)", y: -30, duration: 0.18, ease: "power2.in" }}, {round(t("וזה") - 0.14, 2)});

      // Captions pop in.
      CAPS.forEach((at, i) => {{
        tl.fromTo(`#cap${{i}} .cap-in`, {{ opacity: 0, scale: 0.82, y: 24 }},
          {{ opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2.2)", immediateRender: false }}, at);
      }});

      // Hidden from t=0: a clip's later children would otherwise show at full opacity
      // from the clip's start until their own pop-in, then pop a second time.
      tl.set(["#g1a", "#g1b", "#g2t", "#people", "#people .num", "#plan", "#road", "#walker", "#offer", "#offer .price", "#offerSub",
              "#pill", "#here", "#arrow"], {{ opacity: 0 }}, 0);
      const CARD_FROM = {{ opacity: 0, y: 320, rotationX: 48, rotation: -8, scale: 1.25, filter: "blur(10px)", transformPerspective: 900 }};
      const CARD_TO = {{ opacity: 1, y: 0, rotationX: 0, rotation: 0, scale: 1, filter: "blur(0px)", transformPerspective: 900 }};
      const cardIn = (sel, at) => tl.fromTo(sel, CARD_FROM, {{ ...CARD_TO, duration: 0.6, ease: "power3.out", immediateRender: false }}, at);
      const cardOut = (sel, at) => tl.to(sel, {{ opacity: 0, y: 260, rotationX: 40, rotation: -6, scale: 0.92, filter: "blur(12px)",
        transformPerspective: 900, duration: 0.35, stagger: 0.04, ease: "power2.in" }}, at);
      const popIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, scale: 0.6 }},
        {{ opacity: 1, scale: 1, duration: 0.4, ease: spring, immediateRender: false }}, at);

      // G1: "I'll start tomorrow" gets struck out, then "now!" checks in.
      cardIn("#g1a", T.g1_in);
      tl.fromTo("#g1a .strike", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, T.g1_strike);
      tl.to("#g1a", {{ opacity: 0.55, duration: 0.3 }}, T.g1_strike + 0.3);
      cardIn("#g1b", T.g1_b);
      tl.fromTo("#g1b .badge", {{ scale: 0.4 }}, {{ scale: 1, duration: 0.4, ease: spring, immediateRender: false }}, T.g1_b + 0.3);
      cardOut("#g1 .card", T.g1_out - 0.35);

      // G2: the tag, then six people light up one by one and "עד 6" lands in green.
      cardIn("#g2t", T.g2_in);
      cardIn("#people", T.g2_tag);
      tl.fromTo("#people .person", {{ fill: "rgba(255,255,255,0.28)", scale: 1 }},
        {{ fill: "#39e46b", scale: 1.12, duration: 0.16, stagger: 0.08, ease: "power2.out", immediateRender: false }}, T.g2_lit);
      popIn("#people .num", T.g2_num);
      cardOut(["#g2t", "#people"], T.g2_out - 0.35);

      // G3: the plan card; its three rows check off one after another.
      cardIn("#plan", T.g3_in);
      [0, 1, 2].forEach((i) => {{
        const at = T.g3_check + i * 0.2;
        tl.fromTo(`#plan .row:nth-of-type(${{i + 2}}) .tick b`, {{ opacity: 0, scale: 0.4 }},
          {{ opacity: 1, scale: 1, duration: 0.35, ease: spring, immediateRender: false }}, at);
        tl.to(`#plan .row:nth-of-type(${{i + 2}}) .bar`, {{ backgroundColor: "rgba(57,228,107,.75)", duration: 0.2 }}, at + 0.05);
      }});
      cardOut("#plan", T.g3_out - 0.35);

      // G4: the road draws from the start dot to the flag, the walker rides its tip.
      cardIn("#road", T.g4_in);
      const road = document.querySelector("#roadDone");
      const LEN = road.getTotalLength();
      const prog = {{ p: 0 }};
      const placeWalker = () => {{
        road.style.strokeDasharray = `${{LEN}}`;
        road.style.strokeDashoffset = `${{LEN * (1 - prog.p)}}`;
        const pt = road.getPointAtLength(LEN * prog.p);
        document.querySelector("#walker").setAttribute("transform", `translate(${{pt.x}} ${{pt.y}})`);
      }};
      placeWalker();
      tl.set("#walker", {{ opacity: 1 }}, T.g4_in);
      tl.fromTo(prog, {{ p: 0 }}, {{ p: 1, duration: T.g4_flag - T.g4_draw + 0.3, ease: "power1.inOut", onUpdate: placeWalker,
        immediateRender: false }}, T.g4_draw);
      tl.fromTo("#flag", {{ scale: 1 }}, {{ scale: 1.25, duration: 0.4, ease: spring, transformOrigin: "50% 100%",
        immediateRender: false }}, T.g4_flag + 0.3);
      cardOut("#road", T.g4_out - 0.35);

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

      // G5: the price card, the number rolls up to 199, then "לחודש הראשון".
      cardIn("#offer", T.g5_in);
      const price = {{ v: 0 }};
      tl.fromTo("#offer .price", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power2.out", immediateRender: false }}, T.g5_num - 0.15);
      tl.fromTo(price, {{ v: 0 }}, {{ v: 199, duration: 0.7, ease: "power3.out", immediateRender: false,
        onUpdate: () => {{ document.querySelector("#priceN").textContent = Math.round(price.v); }} }}, T.g5_num - 0.15);
      tl.fromTo("#offer .price", {{ scale: 1 }}, {{ scale: 1.1, duration: 0.45, ease: spring, immediateRender: false }}, T.g5_num + 0.55);
      tl.fromTo("#offerSub", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, T.g5_tag);
      cardOut("#offer", T.g5_out - 0.35);

      // G6: call to action with a bouncing arrow.
      cardIn("#pill", T.g6_in);
      tl.fromTo("#here", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "back.out(2)", immediateRender: false }}, T.g6_here);
      tl.fromTo("#arrow", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, T.g6_here + 0.15);
      tl.fromTo("#arrow", {{ y: -10 }}, {{ y: 26, duration: 0.32, ease: "sine.inOut", yoyo: true, repeat: 3, immediateRender: false }}, T.g6_here + 0.15);

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
events += [("whoosh", G["g2_in"]), ("whoosh", G["g2_tag"])]
events += [("tick", G["g2_lit"] + i * 0.08) for i in range(6)]
events += [("pop", G["g2_num"]), ("whoosh_out", G["g2_out"] - 0.35)]
events += [("whoosh", G["g3_in"])]
events += [("ding", G["g3_check"] + i * 0.2) for i in range(3)]
events += [("whoosh_out", G["g3_out"] - 0.35), ("whoosh", G["g4_in"]), ("whoosh_soft", G["g4_draw"]), ("ding", G["g4_flag"] + 0.3)]
events += [("whoosh_out", G["g4_out"] - 0.35)]
events += [("whoosh_soft", G["tb_in"]), ("whoosh", G["tb_big"]), ("whoosh_out", G["tb_out"]), ("whoosh", G["g5_in"])]
events += [("tick", G["g5_num"] - 0.15 + i * 0.07) for i in range(8)]
events += [("ding", G["g5_num"] + 0.55), ("pop", G["g5_tag"]), ("whoosh_out", G["g5_out"] - 0.35)]
events += [("whoosh", G["g6_in"]), ("pop", G["g6_here"])]
json.dump({"duration": DURATION, "events": [[n, round(a, 3)] for n, a in sorted(events, key=lambda e: e[1])]},
          open(os.path.join(os.path.dirname(OUT), "sfx.json"), "w"))
print("wrote", OUT, len(captions), "captions")
