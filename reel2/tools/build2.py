"""Generate reel2/index.html: dynamic face-centered zooms, kinetic hook, captions
and content graphics, in the style of the reference reel.

usage: build2.py <face.json> <words.json> <out index.html> <video src>
"""
import json
import sys

face = json.load(open(sys.argv[1]))
words = json.load(open(sys.argv[2]))
OUT, VIDEO = sys.argv[3], sys.argv[4]
DURATION = 18.5
KEYWORDS = {"מאות", "6", "דואגים", "הודעה", "להתחזק"}
# Keyword color class; anything not listed is red.
KEY_COLOR = {"6": "key-green", "דואגים": "key-cyan"}


def t(word, nth=1):
    hits = [w["t"] for w in words if w["w"] == word]
    return hits[nth - 1]


# Caption chunks of 2-4 words; the hook (first 9 words) gets its own big treatment.
CHUNKS = [
    ["תקשיבו", "לי"],
    ["אצלנו", "אין"], ["מאות", "אנשים"], ["או", "מכשירים"], ["שאתם", "לא", "יודעים"], ["מה", "לעשות", "איתם"],
    ["עד", "6", "אנשים"], ["בקבוצה"],
    ["תכנית", "אישית"], ["ומאמן", "שמלווה", "אתכם"], ["לאורך", "כל", "הדרך"],
    ["אתם", "לא", "צריכים", "לדעת"], ["איזה", "תרגיל", "לעשות"], ["כמה", "משקל"], ["או", "כמה", "חזרות"],
    ["אתם", "מגיעים"], ["מקבלים", "תכנית"], ["שמתאימה", "לכם"], ["ואנחנו", "דואגים"], ["לכל", "השאר"],
    ["רוצה", "להצטרף?"], ["שלחי", "לי", "הודעה"], ["פה", "למטה"],
]
flat = [w["w"] for w in words][9:]
idx, captions = 9, []
for ch in CHUNKS:
    start = words[idx]["t"]
    idx += len(ch)
    end = words[idx]["t"] if idx < len(words) else DURATION
    seg_end = next((w["segEnd"] for w in words[idx - len(ch):idx] if "segEnd" in w), None)
    if seg_end is not None:
        end = min(end, seg_end + 0.25)
    captions.append({"words": ch, "start": round(start, 2), "end": round(end, 2)})

HOOK = [w for w in words[:9]]

# Zoom keyframes: (kind, time, scale, duration)
ZOOM = [
    ("set", 0.0, 1.00, 0),
    ("push", 0.27, 1.18, t("תקשיבו") - 0.27),
    # "תקשיבו לי": sharp snap in, then glide back out.
    ("snap", t("תקשיבו"), 1.32, 0.2),
    ("back", t("לי"), 1.00, t("אצלנו") - t("לי") + 0.05),
    ("punch", t("מאות"), 1.24, 0.45),
    ("ease", t("איתם"), 1.00, 0.4),
    ("push", t("עד"), 1.08, 3.9),
    ("set", t("אתם", 2), 1.18, 0),
    ("ease_slow", t("אתם", 2), 1.00, 2.8),
    ("push", t("אתם", 3), 1.05, t("ואנחנו") - t("אתם", 3)),
    # "ואנחנו דואגים לכל השאר": sharp snap in, small kick on "דואגים", then glide back out.
    ("snap", t("ואנחנו"), 1.26, 0.2),
    ("snap", t("דואגים"), 1.32, 0.18),
    ("back", t("לכל"), 1.00, t("רוצה") - t("לכל")),
    ("push", t("רוצה"), 1.18, DURATION - t("רוצה")),
]

TIMES = {
    "g1_in": t("מאות") - 0.05, "g1_b": t("מכשירים") - 0.05, "g1_out": t("איתם") + 0.15,
    "g2_in": t("עד"), "g2_lit": t("6"), "g2_c1": t("תכנית", 1), "g2_c2": t("ומאמן"), "g2_out": t("הדרך") + 0.55,
    "g3_a": t("תרגיל"), "g3_b": t("משקל"), "g3_c": t("חזרות"), "g3_check": t("מקבלים"), "g3_out": t("דואגים") - 0.1,
    "g4_in": t("שלחי"), "g4_here": t("פה"),
}


def esc_words(ws):
    return " ".join(
        f'<span class="w{" key " + KEY_COLOR.get(w.strip("?"), "") if w.strip("?") in KEYWORDS else ""}">{w}</span>' for w in ws)


# The CTA pill already says "שלחי לי הודעה", so that caption is dropped.
captions = [c for c in captions if c["words"] not in (["שלחי", "לי", "הודעה"], ["פה", "למטה"])]
# On-screen wording differs from the spoken "רוצה להצטרף".
for c in captions:
    if c["words"] == ["רוצה", "להצטרף?"]:
        c["words"] = ["רוצה", "לנסות", "גם?"]
cap_html = "\n".join(
    f'      <div class="cap clip" id="cap{i}" data-start="{c["start"]}" data-duration="{round(c["end"] - c["start"], 2)}"'
    f' data-track-index="2"><div class="cap-in">{esc_words(c["words"])}</div></div>'
    for i, c in enumerate(captions)
)
# Hook in three balanced lines: "אם אתם לא אוהבים" / "חדרי כושר" / "אבל רוצים להתחזק".
# Beat A: "אם אתם לא אוהבים / חדרי כושר"; beat B replaces it alone: "אבל רוצים להתחזק".
HOOK_BEATS = [("hookA", [(0, 4), (4, 6)]), ("hookB", [(6, 9)])]
def hook_line(a, b):
    return "<div>" + " ".join(
        f'<span class="hw{" key" if HOOK[i]["w"] in KEYWORDS else ""}" id="hw{i}">{HOOK[i]["w"]}</span>' for i in range(a, b)) + "</div>"
hook_html = "\n".join(
    f'        <div class="beat" id="{bid}">' + "".join(hook_line(a, b) for a, b in lines) + "</div>" for bid, lines in HOOK_BEATS)

PERSON = ('<svg viewBox="0 0 24 24" class="person"><circle cx="12" cy="7" r="4"/>'
          '<path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8z"/></svg>')

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
      .ov {{ position: absolute; inset: 0; direction: rtl; font-family: "Heebo", sans-serif; color: #fff; pointer-events: none; }}

      /* Hook: big condensed lines at chest height, words resolve from blur. */
      #hook {{ top: 1000px; bottom: auto; text-align: center; font-family: "Karantina", "Heebo", sans-serif; font-weight: 700;
               font-size: 132px; line-height: 0.95; white-space: nowrap; text-shadow: 0 6px 30px rgba(0,0,0,.55); }}
      .hw {{ display: inline-block; opacity: 0; }}
      #hook .beat {{ position: absolute; left: 0; right: 0; top: 0; }}
      #hookB {{ font-size: 150px; }}
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

      #g1 {{ display: flex; flex-direction: column; align-items: center; gap: 22px; top: 250px; bottom: auto; }}
      #g1 .card {{ position: relative; }}
      #g1 .strike {{ position: absolute; right: 120px; left: 30px; top: 50%; height: 7px; background: var(--red); border-radius: 4px; transform-origin: right center; }}

      #g2 {{ top: 210px; bottom: auto; display: flex; flex-direction: column; align-items: center; gap: 26px; }}
      #people {{ display: flex; gap: 18px; background: var(--glass); border: 2px solid var(--line); border-radius: 36px; padding: 26px 36px; backdrop-filter: blur(14px); align-items: center; }}
      .person {{ width: 74px; height: 74px; fill: rgba(255,255,255,.28); }}
      #people .num {{ font-family: "Karantina", sans-serif; font-weight: 700; font-size: 120px; line-height: .8; color: var(--green); margin-inline-start: 10px; }}
      #chips {{ display: flex; gap: 20px; }}
      #chips .card {{ font-size: 48px; padding: 16px 26px; }}
      #chips .badge {{ width: 56px; height: 56px; font-size: 34px; }}

      #g3 {{ top: 250px; bottom: auto; display: flex; justify-content: center; gap: 20px; }}
      #g3 .card {{ flex-direction: column; gap: 12px; padding: 26px 30px; font-size: 52px; min-width: 250px; }}
      #g3 .mark {{ position: relative; width: 84px; height: 84px; }}
      #g3 .mark span {{ position: absolute; inset: 0; border-radius: 50%; display: grid; place-items: center; font-size: 52px; font-weight: 900; }}
      #g3 .q {{ background: rgba(255,255,255,.18); }}
      #g3 .ok {{ background: var(--green); color: #0b1a10; opacity: 0; }}

      #g4 {{ top: auto; bottom: 440px; display: flex; flex-direction: column; align-items: center; gap: 10px; }}
      #g4 .pill {{ background: var(--cyan); text-shadow: 0 2px 8px rgba(0,60,90,.45); border-radius: 999px; padding: 22px 54px; font-weight: 900; font-size: 64px; box-shadow: 0 16px 50px rgba(41,196,246,.45); }}
      #g4 .here {{ font-weight: 900; font-size: 62px; text-shadow: 0 4px 18px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.9); margin-top: 6px; }}
      #g4 .arrow {{ font-size: 90px; font-weight: 900; line-height: 1; text-shadow: 0 4px 18px rgba(0,0,0,.6); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}" data-width="1080" data-height="1920">
      <div id="cam">
        <div id="frame">
          <video id="a-roll" class="clip" src="{VIDEO}" playsinline data-start="0" data-duration="{DURATION}" data-track-index="0"
                 data-has-audio="true" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>
        </div>
      </div>

      <audio id="music" src="music.wav" data-start="0" data-duration="{DURATION}" data-track-index="6" data-volume="1"></audio>
      <audio id="sfx" src="sfx.wav" data-start="0" data-duration="{DURATION}" data-track-index="5" data-volume="1"></audio>

      <div class="ov clip" id="hook" data-start="0" data-duration="{round(t("תקשיבו") + 0.1, 2)}" data-track-index="1">
{hook_html}
      </div>

      <div class="ov clip" id="g1" data-start="{TIMES["g1_in"]}" data-duration="{round(TIMES["g1_out"] - TIMES["g1_in"], 2)}" data-track-index="3">
        <div class="card" id="g1a"><span class="badge x">✕</span><span>מאות אנשים</span><i class="strike"></i></div>
        <div class="card" id="g1b"><span class="badge x">✕</span><span>מכשירים מבלבלים</span><i class="strike"></i></div>
      </div>

      <div class="ov clip" id="g2" data-start="{TIMES["g2_in"]}" data-duration="{round(TIMES["g2_out"] - TIMES["g2_in"], 2)}" data-track-index="3">
        <div id="people">{"".join(PERSON for _ in range(6))}<span class="num">6</span></div>
        <div id="chips">
          <div class="card" id="c1"><span class="badge v">✓</span><span>תכנית אישית</span></div>
          <div class="card" id="c2"><span class="badge v">✓</span><span>מאמן צמוד</span></div>
        </div>
      </div>

      <div class="ov clip" id="g3" data-start="{TIMES["g3_a"] - 0.05}" data-duration="{round(TIMES["g3_out"] - TIMES["g3_a"] + 0.05, 2)}" data-track-index="3">
        <div class="card" id="q1"><div class="mark"><span class="q">?</span><span class="ok">✓</span></div><span>תרגיל</span></div>
        <div class="card" id="q2"><div class="mark"><span class="q">?</span><span class="ok">✓</span></div><span>משקל</span></div>
        <div class="card" id="q3"><div class="mark"><span class="q">?</span><span class="ok">✓</span></div><span>חזרות</span></div>
      </div>

      <div class="ov clip" id="g4" data-start="{TIMES["g4_in"]}" data-duration="{round(DURATION - TIMES["g4_in"], 2)}" data-track-index="3">
        <div class="pill" id="pill">שלחי לי הודעה</div>
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

      // Hook words resolve from blur as they are spoken, then blur away.
      HOOK_T.forEach((at, i) => {{
        tl.fromTo(`#hw${{i}}`, {{ opacity: 0, y: 40, filter: "blur(18px)" }},
          {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.28, ease: "power3.out", immediateRender: false }}, Math.max(0, at - 0.06));
      }});
      tl.fromTo("#hw8", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.4, ease: spring, immediateRender: false }}, HOOK_T[8]);
      tl.to("#hookA .hw", {{ opacity: 0, filter: "blur(16px)", y: -30, duration: 0.16, ease: "power2.in" }}, HOOK_T[6] - 0.18);
      tl.to("#hookB .hw", {{ opacity: 0, filter: "blur(16px)", y: -30, duration: 0.18, ease: "power2.in" }}, {round(t("תקשיבו") - 0.12, 2)});

      // Captions pop in.
      CAPS.forEach((at, i) => {{
        tl.fromTo(`#cap${{i}} .cap-in`, {{ opacity: 0, scale: 0.82, y: 24 }},
          {{ opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2.2)", immediateRender: false }}, at);
      }});

      // G1: the crowd and the confusing machines get struck out.
      // Hidden from t=0: a clip's later children would otherwise show at full opacity
      // from the clip's start until their own pop-in, then pop a second time.
      tl.set(["#g1a", "#g1b", "#people", "#c1", "#c2", "#q1", "#q2", "#q3", "#pill", "#here", "#arrow", "#people .num"], {{ opacity: 0 }}, 0);
      const CARD_FROM = {{ opacity: 0, y: 320, rotationX: 48, rotation: -8, scale: 1.25, filter: "blur(10px)", transformPerspective: 900 }};
      const CARD_TO = {{ opacity: 1, y: 0, rotationX: 0, rotation: 0, scale: 1, filter: "blur(0px)", transformPerspective: 900 }};
      const cardIn = (sel, at) => tl.fromTo(sel, CARD_FROM, {{ ...CARD_TO, duration: 0.6, ease: "power3.out", immediateRender: false }}, at);
      const cardOut = (sel, at) => tl.to(sel, {{ opacity: 0, y: 260, rotationX: 40, rotation: -6, scale: 0.92, filter: "blur(12px)",
        transformPerspective: 900, duration: 0.35, stagger: 0.04, ease: "power2.in" }}, at);
      const popIn = (sel, at) => tl.fromTo(sel, {{ opacity: 0, scale: 0.7, y: -30 }},
        {{ opacity: 1, scale: 1, y: 0, duration: 0.35, ease: spring, immediateRender: false }}, at);
      cardIn("#g1a", T.g1_in);
      tl.fromTo("#g1a .strike", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, T.g1_in + 0.25);
      cardIn("#g1b", T.g1_b);
      tl.fromTo("#g1b .strike", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, T.g1_b + 0.25);
      cardOut("#g1 .card", T.g1_out - 0.35);

      // G2: six people light up, then the two promises check in.
      cardIn("#people", T.g2_in);
      tl.fromTo("#people .person", {{ fill: "rgba(255,255,255,0.28)", scale: 1 }},
        {{ fill: "#39e46b", scale: 1.12, duration: 0.18, stagger: 0.07, ease: "power2.out", immediateRender: false }}, T.g2_lit);
      tl.fromTo("#people .num", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: spring, immediateRender: false }}, T.g2_lit + 0.42);
      cardIn("#c1", T.g2_c1);
      cardIn("#c2", T.g2_c2);
      cardOut(["#people", "#c1", "#c2"], T.g2_out - 0.35);

      // G3: the three questions appear, then all turn into checks.
      cardIn("#q1", T.g3_a); cardIn("#q2", T.g3_b); cardIn("#q3", T.g3_c);
      ["#q1", "#q2", "#q3"].forEach((q, i) => {{
        const at = T.g3_check + i * 0.12;
        tl.to(`${{q}} .q`, {{ opacity: 0, rotation: 90, duration: 0.18 }}, at);
        tl.fromTo(`${{q}} .ok`, {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: spring, immediateRender: false }}, at + 0.05);
        tl.to(q, {{ borderColor: "#39e46b", duration: 0.2 }}, at + 0.05);
      }});
      cardOut("#g3 .card", T.g3_out - 0.35);

      // G4: call to action with a bouncing arrow.
      cardIn("#pill", T.g4_in);
      tl.fromTo("#here", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "back.out(2)", immediateRender: false }}, T.g4_here);
      tl.fromTo("#arrow", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, T.g4_here + 0.15);
      tl.fromTo("#arrow", {{ y: -10 }}, {{ y: 26, duration: 0.32, ease: "sine.inOut", yoyo: true, repeat: 2, immediateRender: false }}, T.g4_here + 0.15);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(OUT, "w").write(html)

# Sound cues, rendered to sfx.wav by tools/sfx.py.
G = TIMES
events = [("whoosh_soft", t("אבל"))]
events += [("thump", at) for kind, at, *_ in ZOOM if kind in ("snap", "punch")]
for k in ("g1_in", "g1_b"):
    events += [("whoosh", G[k]), ("scratch", G[k] + 0.25)]
events += [("whoosh_out", G["g1_out"] - 0.35), ("whoosh", G["g2_in"])]
events += [("tick", G["g2_lit"] + i * 0.07) for i in range(6)]
events += [("pop", G["g2_lit"] + 0.42)]
for k in ("g2_c1", "g2_c2"):
    events += [("whoosh", G[k]), ("ding", G[k] + 0.3)]
events += [("whoosh_out", G["g2_out"] - 0.35)]
events += [("whoosh", G[k]) for k in ("g3_a", "g3_b", "g3_c")]
events += [("ding", G["g3_check"] + i * 0.12 + 0.05) for i in range(3)]
events += [("whoosh_out", G["g3_out"] - 0.35), ("whoosh", G["g4_in"]), ("pop", G["g4_here"])]
json.dump({"duration": DURATION, "events": [[n, round(a, 3)] for n, a in sorted(events, key=lambda e: e[1])]},
          open(OUT.rsplit("/", 1)[0] + "/sfx.json", "w"))
print("wrote", OUT, len(captions), "captions")
