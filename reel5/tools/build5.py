"""Generate reel5/index.html ("4 תרגילי ישבן"): same approved style as reel4 (face-centered smooth zooms,
whole-phrase opening, 2-4 word captions, royal-blue key words, smooth glide-in cards, text behind the subject,
Instagram CTA). Content: the trainer talks at the start and the end; in between, four silent exercise clips,
each with a wide top card (number, name, live stick-figure animation of the move, glute target pulsing).

usage: build5.py <face.json> <words.json> <out index.html> <video src> <first cutout frame> <last cutout frame>
"""
import json
import math
import os
import sys

face = json.load(open(sys.argv[1]))
words = json.load(open(sys.argv[2]))
OUT, VIDEO = sys.argv[3], sys.argv[4]
CUT_A, CUT_B = int(sys.argv[5]), int(sys.argv[6])
SRC_END = 29.73
DURATION = 30.0  # last frame holds a moment so the follow card stays readable
CUTS = [3.267, 8.9, 16.7, 20.767, 26.6]  # scene changes in the source (ffmpeg scene > 0.25)
EXERCISES = ["קיק בק", "לאנג בולגרי", "סומו סקוואט", "דדליפט רומני<br>רגל רגל"]
KEYWORDS = {"שורפים", "ומחטבים"}


def t(word, nth=1):
    return [w["t"] for w in words if w["w"] == word][nth - 1]


def smooth_segments(vals, fps, segs, sigma=14):
    """Smooth the face track (~0.5 s) inside each talking segment; clips use a fixed body-centre origin."""
    out = []
    n = len(vals)
    r = int(sigma * 3)
    k = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-r, r + 1)]
    for i in range(n):
        tt = i / fps
        seg = next(((a, b) for a, b in segs if a <= tt < b), None)
        if seg is None:
            out.append(None)
            continue
        lo, hi = int(seg[0] * fps), min(n - 1, int(seg[1] * fps))
        acc = ws = 0.0
        for j, w in zip(range(i - r, i + r + 1), k):
            acc += vals[min(hi, max(lo, j))] * w
            ws += w
        out.append(round(acc / ws, 2))
    return out


TALK = [(0, CUTS[0]), (CUTS[4], 40)]
fps = face["fps"]
FX = [v if v is not None else 50 for v in smooth_segments([p["x"] for p in face["track"]], fps, TALK)]
FY = [v if v is not None else 52 for v in smooth_segments([p["y"] for p in face["track"]], fps, TALK)]

# Captions only on the closing part (the opening is the hook; the CTA card carries "תעקבי אחרי העמוד").
T_ = {
    "hk_a": 0.16, "hk_a2": t("ארבעה") - 0.06, "hk_b": t("ממוקדי") - 0.06, "hk_b2": t("במיוחד") - 0.06,
    "hk_out": CUTS[0] - 0.24, "ana_in": t("ממוקדי") - 0.11,
    "tb_in": CUTS[0] + 0.12, "tb_out": 5.35,
    "cta": t("תעקבי") - 0.05, "tap": t("העמוד") + 0.3,
}
LAB_IN = [T_["tb_out"] + 0.2] + [c + 0.3 for c in CUTS[1:4]]
LAB_OUT = [c - 0.35 for c in CUTS[1:5]]
captions = [
    {"words": ["לעוד", "תרגילים"], "start": CUTS[4] + 0.06, "end": t("שורפים") - 0.02},
    {"words": ["שורפים", "ומחטבים"], "start": t("שורפים") - 0.04, "end": T_["cta"] - 0.02},
]


def esc_words(ws):
    return " ".join(f'<span class="w{" key key-royal" if w in KEYWORDS else ""}">{w}</span>' for w in ws)


cap_html = "\n".join(
    f'      <div class="cap clip" id="cap{i}" data-start="{round(c["start"], 2)}" data-duration="{round(c["end"] - c["start"], 2)}"'
    f' data-track-index="2"><div class="cap-in">{esc_words(c["words"])}</div></div>' for i, c in enumerate(captions))

ZOOM = [("set", 0.0, 1.00, 0), ("push", 0.0, 1.10, CUTS[0])]
for k in range(4):  # each clip: soft whip-in from 1.08 (with blur in JS), then a slow push
    a, b = CUTS[k], CUTS[k + 1]
    ZOOM += [("set", a, 1.08, 0), ("settle", a, 1.0, 0.4), ("push", a + 0.4, 1.06, b - a - 0.4)]
ZOOM += [("set", CUTS[4], 1.0, 0), ("push", CUTS[4], 1.13, DURATION - CUTS[4])]

STICK = '<svg viewBox="0 0 220 180" class="fig" id="fig{k}"><g class="props"></g><circle class="glute" r="13"/><g class="body"></g></svg>'
DOTS = '<div class="dots">' + "".join('<i></i>' for _ in range(4)) + '</div>'


def label(k, name):
    return (f'<div class="lab clip" id="lab{k}" data-start="{round(LAB_IN[k] - 0.05, 2)}" '
            f'data-duration="{round(LAB_OUT[k] + 0.5 - LAB_IN[k], 2)}" data-track-index="3">'
            f'<div class="card"><div class="txt"><span class="num">{k + 1}</span><div><div class="m">{name}</div><div class="sr"><b>3</b> סטים · <b>8-12</b> חזרות</div></div></div>'
            f'{STICK.format(k=k)}</div>{DOTS}</div>')


LABELS = "\n".join(label(k, n) for k, n in enumerate(EXERCISES))

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
      :root {{ --royal: #3a64f0; --blue: #5b86ff; }}
      #cam {{ position: absolute; inset: 0; overflow: hidden; }}
      #frame {{ position: absolute; inset: 0; will-change: transform; }}
      #cutout {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .ov {{ position: absolute; inset: 0; direction: rtl; font-family: "Heebo", sans-serif; color: #fff; pointer-events: none; }}

      /* Opening: plain centered text, each phrase enters whole. */
      #hook {{ top: 1060px; bottom: auto; }}
      #hook .beat {{ position: absolute; left: 0; right: 0; top: 0; display: flex; flex-direction: column; align-items: center; gap: 6px; }}
      #hook .hl {{ opacity: 0; font-weight: 900; font-size: 84px; line-height: 1.08; color: #fff; white-space: nowrap;
                   text-shadow: 0 6px 26px rgba(0,0,0,.65), 0 0 2px rgba(0,0,0,.9); }}
      #hook .royal {{ color: var(--royal); display: inline-block; text-shadow: 0 0 2px rgba(255,255,255,.45), 0 6px 26px rgba(0,0,0,.6); }}

      /* "ממוקדי ישבן": full-screen anatomy page (client's image), a blue target locks on the glutes,
         they light up in colour while the camera pushes in. Beat B of the opening sits at the top of the page. */
      #hook #hookB {{ top: -850px; }}
      .page {{ position: absolute; inset: 0; overflow: hidden; background: #000; }}
      #anaIn {{ position: absolute; left: -100px; top: 0; width: 1280px; height: 1920px; transform-origin: 642px 1250px; will-change: transform; }}
      #anaIn img {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
      #anaGray {{ filter: grayscale(1) brightness(.92); }}
      #anaCol {{ clip-path: circle(0% at 50.2% 65.1%); }}
      #anaGlow {{ position: absolute; left: 342px; top: 1000px; width: 600px; height: 500px; border-radius: 50%; mix-blend-mode: screen;
                  background: radial-gradient(closest-side, rgba(255,70,60,.55), rgba(255,70,60,0)); opacity: 0; }}
      #reticle {{ position: absolute; left: 322px; top: 930px; width: 640px; height: 640px; overflow: visible; }}
      #reticle .ring {{ fill: none; stroke: var(--blue); stroke-width: 5; stroke-dasharray: 18 14; filter: drop-shadow(0 0 10px rgba(91,134,255,.9)); }}
      #reticle .ring2 {{ fill: none; stroke: rgba(255,255,255,.7); stroke-width: 2.5; }}
      #reticle .br path {{ fill: none; stroke: var(--blue); stroke-width: 12; stroke-linecap: round; stroke-linejoin: round;
                           filter: drop-shadow(0 0 12px rgba(91,134,255,.95)); }}
      #reticle .tick {{ stroke: #fff; stroke-width: 5; stroke-linecap: round; }}
      #anaShade {{ position: absolute; left: 0; right: 0; top: 0; height: 700px;
                   background: linear-gradient(rgba(0,0,0,.82), rgba(0,0,0,.45) 55%, rgba(0,0,0,0)); }}

      /* Captions */
      .cap {{ position: absolute; left: 0; right: 0; top: 1150px; display: flex; justify-content: center; direction: rtl; }}
      .cap-in {{ font-family: "Heebo", sans-serif; font-weight: 900; font-size: 74px; color: #fff; letter-spacing: -0.5px;
                 text-shadow: 0 4px 18px rgba(0,0,0,.75), 0 0 2px rgba(0,0,0,.95); white-space: nowrap; }}
      .cap .w {{ display: inline-block; }}
      .key.key-royal {{ color: var(--royal); text-shadow: 0 0 2px rgba(255,255,255,.4), 0 4px 18px rgba(0,0,0,.7); }}

      /* "4 תרגילי ישבן" behind the athlete on the first clip: the kicking leg sweeps across the big 4. */
      #behind {{ position: absolute; inset: 0; direction: rtl; font-family: "Heebo", sans-serif; color: #fff; }}
      #behind .ttl {{ position: absolute; left: 0; right: 0; top: 410px; text-align: center; font-weight: 900; font-size: 116px; line-height: 1;
                      white-space: nowrap; text-shadow: 0 4px 22px rgba(0,0,0,.55), 0 0 2px rgba(0,0,0,.6); }}
      #behind .ttl span {{ display: inline-block; }}
      #big4 {{ position: absolute; left: 150px; top: 560px; width: 340px; text-align: center; font-weight: 900; font-size: 560px; line-height: .86;
               color: var(--royal); text-shadow: 0 0 3px rgba(255,255,255,.45), 0 12px 40px rgba(0,0,0,.35); }}

      /* Exercise cards: wide top card so the athlete stays visible. */
      .lab {{ position: absolute; left: 50px; right: 50px; top: 215px; direction: rtl; font-family: "Heebo", sans-serif; color: #fff; }}
      .lab .card {{ height: 236px; border-radius: 40px; background: rgba(20,21,24,.55); border: 2px solid rgba(255,255,255,.16);
                    backdrop-filter: blur(18px) saturate(1.2); box-shadow: 0 24px 60px rgba(0,0,0,.35);
                    display: flex; align-items: center; justify-content: space-between; padding: 0 34px 0 22px; }}
      .lab .txt {{ display: flex; align-items: center; gap: 28px; min-width: 0; }}
      .lab .num {{ width: 96px; height: 96px; border-radius: 50%; background: var(--royal); display: grid; place-items: center; flex: none;
                   font-size: 60px; font-weight: 900; box-shadow: 0 0 34px rgba(58,100,240,.65); }}
      .lab .m {{ font-weight: 900; font-size: 74px; line-height: 1.02; white-space: nowrap; }}
      #lab3 .m {{ font-size: 52px; white-space: normal; width: 430px; }}
      .lab .sr {{ margin-top: 8px; font-weight: 700; font-size: 36px; line-height: 1.1; color: #fff; white-space: nowrap; }}
      .lab .sr b {{ font-weight: 900; color: #fff; }}
      .lab .fig {{ width: 280px; height: 228px; flex: none; overflow: visible; }}
      .fig .body line, .fig .body path {{ stroke: #fff; stroke-width: 11; stroke-linecap: round; stroke-linejoin: round; fill: none; }}
      .fig .body circle {{ fill: #fff; }}
      .fig .props rect, .fig .props path {{ fill: rgba(255,255,255,.16); stroke: rgba(255,255,255,.4); stroke-width: 3; }}
      .fig .glute {{ fill: var(--blue); filter: drop-shadow(0 0 10px rgba(91,134,255,.95)); }}
      .lab .dots {{ display: flex; justify-content: center; gap: 12px; margin-top: 20px; direction: ltr; }}
      .lab .dots i {{ width: 46px; height: 10px; border-radius: 6px; background: rgba(255,255,255,.35); box-shadow: 0 2px 8px rgba(0,0,0,.35); }}
      #leak {{ position: absolute; inset: -10%; pointer-events: none; mix-blend-mode: screen;
               background: radial-gradient(60% 50% at 50% 55%, rgba(255,255,255,.95), rgba(200,215,255,.7) 45%, rgba(110,140,255,.25) 75%, rgba(90,120,255,0)); }}

      /* CTA: Instagram follow notification, low-opacity glass, round profile picture, "מעקב" gets tapped. */
      #cta {{ top: auto; bottom: 440px; display: flex; flex-direction: column; align-items: center; }}
      #fw {{ display: flex; align-items: center; gap: 24px; width: 980px; padding: 24px 28px; border-radius: 46px;
             background: rgba(255,255,255,.14); border: 1.5px solid rgba(255,255,255,.28); backdrop-filter: blur(22px) saturate(1.3);
             box-shadow: 0 20px 60px rgba(0,0,0,.28); }}
      #fw .av {{ width: 124px; height: 124px; border-radius: 50%; flex: none; padding: 5px;
                 background: conic-gradient(from 200deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5, #feda75); }}
      #fw .av img {{ width: 100%; height: 100%; border-radius: 50%; display: block; border: 4px solid rgba(20,20,22,.9); }}
      #fw .body {{ flex: 1; min-width: 0; text-align: right; }}
      #fw .top {{ font-size: 38px; font-weight: 800; color: rgba(255,255,255,.85); direction: ltr; text-align: right; }}
      #fw .msg {{ font-size: 56px; font-weight: 900; color: #fff; margin-top: 4px; line-height: 1.1; white-space: nowrap; text-shadow: 0 2px 10px rgba(0,0,0,.25); }}
      #btn {{ position: relative; flex: none; width: 200px; height: 84px; border-radius: 22px; background: #0095f6; display: grid; place-items: center;
              font-size: 42px; font-weight: 800; color: #fff; }}
      #btn b {{ position: absolute; inset: 0; display: grid; place-items: center; font-weight: 800; }}
      #btnOn {{ opacity: 0; }}
      #tapRing {{ position: absolute; left: 50%; top: 50%; width: 120px; height: 120px; margin: -60px 0 0 -60px; border-radius: 50%;
                  border: 6px solid rgba(255,255,255,.9); opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}" data-width="1080" data-height="1920">
      <div id="cam">
        <div id="frame">
          <video id="a-roll" class="clip" src="{VIDEO}" playsinline data-start="0" data-duration="{DURATION}" data-track-index="0"
                 data-has-audio="true" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>
          <div id="behind" class="clip" data-start="{T_["tb_in"]}" data-duration="{round(T_["tb_out"] + 0.4 - T_["tb_in"], 2)}" data-track-index="1">
            <div class="ttl"><span id="ttlA">תרגילי</span> <span id="ttlB">ישבן</span></div>
            <div id="big4">1</div>
          </div>
          <img id="cutout" class="clip" alt="" data-cut-ranges="{CUT_A}-{CUT_B}" data-start="0" data-duration="{DURATION}" data-track-index="1" />
        </div>
      </div>

      <audio id="music" src="music.wav" data-start="0" data-duration="{DURATION}" data-track-index="6" data-volume="1"></audio>
      <audio id="sfx" src="sfx.wav" data-start="0" data-duration="{DURATION}" data-track-index="5" data-volume="0.35"></audio>

      <div class="clip page" id="ana" data-start="{round(T_["ana_in"], 2)}" data-duration="{round(CUTS[0] - T_["ana_in"], 2)}" data-track-index="3">
        <div id="anaIn">
          <img id="anaGray" src="anatomy.jpg" alt="" /><img id="anaCol" src="anatomy.jpg" alt="" /><div id="anaGlow"></div>
          <svg id="reticle" viewBox="-320 -320 640 640">
            <circle class="ring" r="250"/><circle class="ring2" r="214"/>
            <line class="tick" x1="0" y1="-290" x2="0" y2="-236"/><line class="tick" x1="0" y1="236" x2="0" y2="290"/>
            <line class="tick" x1="-290" y1="0" x2="-236" y2="0"/><line class="tick" x1="236" y1="0" x2="290" y2="0"/>
            <g class="br"><path id="brTL" d="M-300 -200 V-300 H-200"/><path id="brTR" d="M300 -200 V-300 H200"/>
            <path id="brBL" d="M-300 200 V300 H-200"/><path id="brBR" d="M300 200 V300 H200"/></g>
          </svg>
        </div>
        <div id="anaShade"></div>
      </div>

      <div class="ov clip" id="hook" data-start="0" data-duration="{round(T_["hk_out"] + 0.25, 2)}" data-track-index="2">
        <div class="beat" id="hookA"><div class="hl" id="hookL">הכנתי לך</div><div class="hl" id="hookL2"><span class="royal">ארבעה</span> תרגילים</div></div>
        <div class="beat" id="hookB"><div class="hl" id="hookR">ממוקדי <span class="royal">ישבן</span></div><div class="hl" id="hookR2">במיוחד בשבילך</div></div>
      </div>

{LABELS}
      <div class="clip" id="leakClip" data-start="{round(CUTS[4] - 0.2, 2)}" data-duration="0.5" data-track-index="4"><div id="leak"></div></div>

      <div class="ov clip" id="cta" data-start="{round(T_["cta"] - 0.05, 2)}" data-duration="{round(DURATION - T_["cta"] + 0.05, 2)}" data-track-index="3">
        <div id="fw">
          <div class="av"><img src="avatar.png" alt="" /></div>
          <div class="body">
            <div class="top">idoamarr</div>
            <div class="msg">תעקבי אחרי העמוד</div>
          </div>
          <div id="btn"><b id="btnOff">מעקב</b><b id="btnOn">במעקב</b><i id="tapRing"></i></div>
        </div>
      </div>

{cap_html}
    </div>

    <script>
      const spring = (p) => (1 - (1 + 7 * p) * Math.exp(-7 * p)) / (1 - 8 * Math.exp(-7));
      const FACE_FPS = {fps};
      const FACE_X = {json.dumps(FX)};
      const FACE_Y = {json.dumps(FY)};
      const ZOOM = {json.dumps(ZOOM)};
      const CUTS = {json.dumps(CUTS)};
      const LAB_IN = {json.dumps([round(x, 2) for x in LAB_IN])};
      const LAB_OUT = {json.dumps([round(x, 2) for x in LAB_OUT])};
      const CAPS = {json.dumps([round(c["start"], 2) for c in captions])};
      const T = {json.dumps({k: round(v, 2) for k, v in T_.items()})};
      const tl = gsap.timeline({{ paused: true }});

      // Zoom centre: smoothed face while the trainer talks, body centre on the clips.
      for (let i = 0; i < FACE_X.length; i++) tl.set("#frame", {{ transformOrigin: `${{FACE_X[i]}}% ${{FACE_Y[i]}}%` }}, i / FACE_FPS);
      let cur = 1;
      for (const [kind, at, scale, dur] of ZOOM) {{
        if (kind === "set") tl.set("#frame", {{ scale }}, at);
        else {{
          const ease = kind === "settle" ? "power3.out" : "sine.inOut";
          if (kind === "settle") tl.fromTo("#frame", {{ filter: "blur(7px)" }}, {{ filter: "blur(0px)", duration: 0.3, ease: "power2.out", immediateRender: false }}, at);
          tl.fromTo("#frame", {{ scale: cur }}, {{ scale, duration: dur, ease, immediateRender: false }}, at);
        }}
        cur = scale;
      }}

      tl.set(["#hookL", "#hookL2", "#hookR", "#hookR2", ".lab", "#fw", "#ttlA", "#ttlB", "#big4"], {{ opacity: 0 }}, 0);

      // ===== Opening: each phrase enters whole from a soft blur =====
      const phraseIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, y: 34, scale: 0.94, filter: "blur(12px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "power3.out", immediateRender: false }}, at);
      phraseIn("#hookL", T.hk_a);
      phraseIn("#hookL2", T.hk_a2);
      tl.fromTo("#hookL2 .royal", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.45, ease: spring, immediateRender: false }}, T.hk_a2 + 0.3);
      tl.to("#hookA", {{ opacity: 0, y: -24, filter: "blur(12px)", duration: 0.18, ease: "power2.in" }}, T.hk_b - 0.18);
      phraseIn("#hookR", T.hk_b);
      phraseIn("#hookR2", T.hk_b2);
      tl.fromTo("#hookR .royal", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.45, ease: spring, immediateRender: false }}, T.hk_b + 0.3);
      tl.to("#hookB", {{ opacity: 0, y: -24, filter: "blur(12px)", duration: 0.22, ease: "power2.in" }}, T.hk_out);

      // ===== "ממוקדי ישבן": anatomy page — zoom-blur in, target locks on the glutes, they light up, push in =====
      const A = T.ana_in, lock = A + 0.62;
      tl.fromTo("#cam", {{ scale: 1, filter: "blur(0px)" }}, {{ scale: 2.4, filter: "blur(24px)", duration: 0.28, ease: "power2.in", immediateRender: false }}, A - 0.2);
      tl.set("#cam", {{ scale: 1, filter: "blur(0px)" }}, A + 0.2);
      tl.fromTo("#ana", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.14, ease: "power1.in", immediateRender: false }}, A);
      tl.fromTo("#anaIn", {{ scale: 1.12, filter: "blur(10px)" }}, {{ scale: 1.0, filter: "blur(0px)", duration: 0.35, ease: "power3.out", immediateRender: false }}, A);
      tl.to("#anaIn", {{ scale: 1.42, duration: CUTS[0] - 0.15 - lock, ease: "sine.inOut" }}, lock);
      tl.set("#reticle", {{ opacity: 0 }}, 0);
      tl.fromTo("#reticle", {{ opacity: 0, scale: 1.9, rotation: -90, transformOrigin: "50% 50%" }},
        {{ opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, A + 0.12);
      tl.fromTo("#reticle .ring", {{ rotation: 0, transformOrigin: "50% 50%" }}, {{ rotation: 120, duration: CUTS[0] - A, ease: "none", immediateRender: false }}, A);
      [["#brTL", -1, -1], ["#brTR", 1, -1], ["#brBL", -1, 1], ["#brBR", 1, 1]].forEach(([sel, sx, sy]) =>
        tl.fromTo(sel, {{ x: sx * 90, y: sy * 90 }}, {{ x: sx * 20, y: sy * 20, duration: 0.3, ease: "back.out(2.5)", immediateRender: false }}, lock - 0.3));
      tl.fromTo("#reticle .br path", {{ stroke: "#5b86ff" }}, {{ stroke: "#ffffff", duration: 0.08, yoyo: true, repeat: 3, ease: "none", immediateRender: false }}, lock);
      tl.fromTo("#reticle", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.4, ease: spring, immediateRender: false }}, lock);
      tl.fromTo("#anaCol", {{ clipPath: "circle(0% at 50.2% 65.1%)" }}, {{ clipPath: "circle(48% at 50.2% 65.1%)", duration: 0.6, ease: "power2.out", immediateRender: false }}, lock);
      tl.fromTo("#anaGlow", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1.1, duration: 0.45, ease: "power2.out", immediateRender: false }}, lock + 0.05);
      tl.to("#anaGlow", {{ opacity: 0.55, scale: 1, duration: 0.45, yoyo: true, repeat: 3, ease: "sine.inOut" }}, lock + 0.5);
      // leave forward into the first clip
      tl.to("#anaIn", {{ scale: 2.1, filter: "blur(16px)", duration: 0.15, ease: "power2.in" }}, CUTS[0] - 0.15);

      // ===== "4 תרגילי ישבן" behind the athlete =====
      tl.fromTo(["#ttlB", "#ttlA"], {{ opacity: 0, y: -30, filter: "blur(12px)", letterSpacing: "18px" }},
        {{ opacity: 1, y: 0, filter: "blur(0px)", letterSpacing: "0px", duration: 0.45, stagger: 0.12, ease: "power3.out", immediateRender: false }}, T.tb_in);
      tl.fromTo("#big4", {{ opacity: 0, scale: 1.3, filter: "blur(16px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "power3.out", immediateRender: false }}, T.tb_in + 0.2);
      [1, 2, 3, 4].forEach((n, i) => tl.set("#big4", {{ textContent: String(n) }}, T.tb_in + 0.2 + i * 0.17));
      tl.set("#big4", {{ textContent: "1" }}, 0);
      tl.fromTo("#big4", {{ scale: 1 }}, {{ scale: 1.1, duration: 0.5, ease: spring, immediateRender: false }}, T.tb_in + 0.75);
      tl.to("#behind", {{ x: -380, opacity: 0, filter: "blur(20px)", duration: 0.32, ease: "power2.in" }}, T.tb_out);

      // ===== Exercise cards: glide + fade in (sine.out), number pops, leave upward before the next cut =====
      document.querySelectorAll(".lab").forEach((el, k) => {{
        tl.fromTo(el, {{ opacity: 0, y: -70, scale: 0.97, filter: "blur(6px)" }},
          {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "sine.out", immediateRender: false }}, LAB_IN[k]);
        tl.fromTo(el.querySelector(".sr"), {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "sine.out", immediateRender: false }}, LAB_IN[k] + 0.35);
        tl.fromTo(el.querySelector(".num"), {{ scale: 0.4, rotation: -30 }}, {{ scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2)", immediateRender: false }}, LAB_IN[k] + 0.25);
        el.querySelectorAll(".dots i").forEach((d, j) => {{
          tl.set(d, {{ background: j < k ? "rgba(91,134,255,.55)" : "rgba(255,255,255,.35)" }}, 0);
          if (j === k) tl.fromTo(d, {{ background: "rgba(255,255,255,.35)", width: 46 }}, {{ background: "#5b86ff", width: 86, duration: 0.4, ease: "power2.out", immediateRender: false }}, LAB_IN[k] + 0.4);
        }});
        tl.to(el, {{ opacity: 0, y: -50, filter: "blur(6px)", duration: 0.35, ease: "sine.in" }}, LAB_OUT[k]);
      }});

      // ===== Stick-figure rigs: one per move, looped across its clip; the glute dot lights at the squeeze =====
      const lerp = (a, b, p) => a + (b - a) * p;
      const knee = (h, f, L1, L2, side) => {{
        const dx = f[0] - h[0], dy = f[1] - h[1], d = Math.min(L1 + L2 - 0.01, Math.hypot(dx, dy));
        const a = (L1 * L1 - L2 * L2 + d * d) / (2 * d), hh = Math.sqrt(Math.max(0, L1 * L1 - a * a));
        const ux = dx / Math.hypot(dx, dy), uy = dy / Math.hypot(dx, dy);
        return [h[0] + ux * a - side * uy * hh, h[1] + uy * a + side * ux * hh];
      }};
      const L = 40;
      const POSES = [
        // 1 kick back on a bosu, hands on the machine; facing left, the free leg swings back and up
        (p) => {{ const hip = [118, 86], sh = [72, 64], ang = (lerp(100, -12, p)) * Math.PI / 180, foot = [hip[0] + 76 * Math.cos(ang), hip[1] + 76 * Math.sin(ang)];
                 return {{ head: [54, 50], sh, hand: [30, 78], hip, legs: [[hip, [116, 160], 0], [hip, foot, -1]], glute: [128, 84], squeeze: p,
                          props: '<path d="M80 178 Q116 146 152 178 Z"/>' }}; }},
        // 2 bulgarian split squat, rear foot on a bench; hips go down and up
        (p) => {{ const hip = [lerp(100, 106, p), lerp(92, 122, p)], sh = [hip[0] - 6, hip[1] - 46];
                 return {{ head: [sh[0] - 3, sh[1] - 18], sh, hand: [sh[0] - 16, sh[1] + 22], hip, legs: [[hip, [56, 166], 1], [hip, [164, 124], 1]],
                          glute: [hip[0] + 9, hip[1] + 2], squeeze: 1 - p, props: '<rect x="146" y="128" width="62" height="38" rx="6"/>' }}; }},
        // 3 sumo squat on two steps (front view), dumbbell between the legs
        (p) => {{ const hy = lerp(80, 114, p), sh = [110, hy - 48];
                 return {{ head: [110, sh[1] - 18], sh, hand: [110, sh[1] + 64], hip: [110, hy], legs: [[[98, hy], [60, 142], 1], [[122, hy], [160, 142], -1]],
                          shoulders: [[92, sh[1] + 2], [128, sh[1] + 2]], glute: [110, hy + 4], squeeze: 1 - p, db: true,
                          props: '<rect x="34" y="142" width="58" height="22" rx="5"/><rect x="128" y="142" width="58" height="22" rx="5"/>' }}; }},
        // 4 single-leg romanian deadlift, rear foot resting on a bench, hinge on the standing leg
        (p) => {{ const a = lerp(6, 72, p) * Math.PI / 180, hip = [lerp(118, 128, p), lerp(88, 96, p)];
                 const sh = [hip[0] - 46 * Math.sin(a), hip[1] - 46 * Math.cos(a)];
                 return {{ head: [sh[0] - 17 * Math.sin(a + 0.15), sh[1] - 17 * Math.cos(a + 0.15)], sh, hand: [sh[0], sh[1] + 40], hip,
                          legs: [[hip, [104, 166], 1], [hip, [196, 104], 1]],
                          glute: [hip[0] + 9, hip[1] + 2], squeeze: 1 - p, db: true,
                          props: '<rect x="158" y="106" width="64" height="16" rx="6"/><rect x="184" y="122" width="14" height="44" rx="3"/>' }}; }},
      ];
      const NS = "http://www.w3.org/2000/svg";
      const ln = (g, a, b) => {{ const e = document.createElementNS(NS, "line"); e.setAttribute("x1", a[0]); e.setAttribute("y1", a[1]); e.setAttribute("x2", b[0]); e.setAttribute("y2", b[1]); g.appendChild(e); }};
      const draw = (k, p) => {{
        const svg = document.querySelector(`#fig${{k}}`), g = svg.querySelector(".body"), P = POSES[k](p);
        g.innerHTML = "";
        svg.querySelector(".props").innerHTML = P.props;
        ln(g, P.hip, P.sh);
        if (P.shoulders) {{ ln(g, P.shoulders[0], P.shoulders[1]); ln(g, P.shoulders[0], P.hand); ln(g, P.shoulders[1], P.hand); }}
        else ln(g, P.sh, P.hand);
        for (const [h, f, side] of P.legs) {{ const kn = knee(h, f, L, L, side); ln(g, h, kn); ln(g, kn, f); }}
        const hd = document.createElementNS(NS, "circle"); hd.setAttribute("cx", P.head[0]); hd.setAttribute("cy", P.head[1]); hd.setAttribute("r", 14); g.appendChild(hd);
        if (P.db) {{ const r = document.createElementNS(NS, "rect"); r.setAttribute("x", P.hand[0] - 20); r.setAttribute("y", P.hand[1] - 6); r.setAttribute("width", 40); r.setAttribute("height", 12); r.setAttribute("rx", 5); r.setAttribute("fill", "#fff"); g.appendChild(r); }}
        const gl = svg.querySelector(".glute");
        gl.setAttribute("cx", P.glute[0]); gl.setAttribute("cy", P.glute[1]);
        const s = Math.pow(P.squeeze, 3);
        gl.setAttribute("r", 9 + 7 * s); gl.style.opacity = 0.35 + 0.65 * s;
      }};
      const REP = [1.5, 1.7, 1.6, 1.8];
      [0, 1, 2, 3].forEach((k) => {{
        const st = {{ p: 0 }}, start = LAB_IN[k], end = LAB_OUT[k] + 0.4;
        draw(k, 0);
        const reps = Math.max(1, Math.floor((end - start) / REP[k] * 2));
        tl.fromTo(st, {{ p: 0 }}, {{ p: 1, duration: REP[k] / 2, ease: "sine.inOut", yoyo: true, repeat: reps - 1, immediateRender: false,
          onUpdate: () => draw(k, st.p) }}, start);
      }});

      // ===== Back to the trainer: light-leak flash =====
      tl.fromTo("#leak", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1.15, duration: 0.2, ease: "power2.in", immediateRender: false }}, CUTS[4] - 0.2);
      tl.to("#leak", {{ opacity: 0, scale: 1.4, duration: 0.3, ease: "power2.out" }}, CUTS[4]);

      // Captions pop in.
      CAPS.forEach((at, i) => tl.fromTo(`#cap${{i}} .cap-in`, {{ opacity: 0, scale: 0.82, y: 24 }},
        {{ opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2.2)", immediateRender: false }}, at));

      // ===== CTA: follow notification drops in, "מעקב" is tapped and turns to "במעקב" =====
      tl.fromTo("#fw", {{ opacity: 0, y: -90, scale: 0.92, filter: "blur(8px)" }},
        {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: spring, immediateRender: false }}, T.cta);
      tl.fromTo("#btn", {{ scale: 1 }}, {{ scale: 0.88, duration: 0.1, ease: "power2.in", immediateRender: false }}, T.tap);
      tl.to("#btn", {{ scale: 1, duration: 0.35, ease: "back.out(3)" }}, T.tap + 0.1);
      tl.fromTo("#tapRing", {{ opacity: 0.9, scale: 0.3 }}, {{ opacity: 0, scale: 1.6, duration: 0.5, ease: "power2.out", immediateRender: false }}, T.tap);
      tl.set("#btn", {{ background: "#0095f6" }}, 0);
      tl.set("#btn", {{ background: "rgba(255,255,255,.22)" }}, T.tap + 0.1);
      tl.set("#btnOff", {{ opacity: 1 }}, 0);
      tl.set("#btnOff", {{ opacity: 0 }}, T.tap + 0.1);
      tl.set("#btnOn", {{ opacity: 0 }}, 0);
      tl.set("#btnOn", {{ opacity: 1 }}, T.tap + 0.1);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(OUT, "w").write(html)

# Sound cues, rendered to sfx.wav by tools/sfx.py.
ev = [("whoosh_soft", T_["hk_a"]), ("pop", T_["hk_a2"] + 0.3), ("pop", T_["hk_b"] + 0.3)]
ev += [("whoosh", T_["ana_in"] - 0.2), ("thump", T_["ana_in"]), ("whoosh_soft", T_["ana_in"] + 0.12)]
ev += [("tick", T_["ana_in"] + 0.32 + i * 0.1) for i in range(3)] + [("ding", T_["ana_in"] + 0.62), ("pop", T_["ana_in"] + 0.64)]
ev += [("whoosh", c - 0.15) for c in CUTS[:4]] + [("thump", c) for c in CUTS[:4]]
ev += [("whoosh_soft", T_["tb_in"])] + [("tick", T_["tb_in"] + 0.2 + i * 0.17) for i in range(4)]
ev += [("pop", T_["tb_in"] + 0.75), ("whoosh_out", T_["tb_out"])]
for k in range(4):
    ev += [("whoosh_soft", LAB_IN[k]), ("ding", LAB_IN[k] + 0.25), ("whoosh_out", LAB_OUT[k])]
ev += [("whoosh_out", CUTS[4] - 0.2), ("pop", captions[1]["start"])]
ev += [("whoosh_soft", T_["cta"]), ("pop", T_["tap"]), ("ding", T_["tap"] + 0.1)]
json.dump({"duration": DURATION, "events": [[n, round(a, 3)] for n, a in sorted(ev, key=lambda e: e[1]) if a < DURATION - 0.3]},
          open(os.path.join(os.path.dirname(OUT) or ".", "sfx.json"), "w"))
print("wrote", OUT, {k: round(v, 2) for k, v in T_.items()}, "labels", LAB_IN, LAB_OUT)
