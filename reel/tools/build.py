"""Generate reel/index.html: spring punch-in zooms on the face, one per sentence.

usage: build.py <face.json> <out index.html>
"""
import json
import sys

face = json.load(open(sys.argv[1]))
DURATION = 18.5

# One emphasis word per sentence. `reset` = first word of the next sentence
# (the clip has no cuts), where the zoom snaps back to 100%.
ZOOMS = [
    {"word": "להתחזק", "t": 1.92, "scale": 1.12, "reset": 3.40},
    {"word": "מאות", "t": 3.70, "scale": 1.12, "reset": 6.13},
    {"word": "6", "t": 6.28, "scale": 1.15, "reset": 10.50},
    {"word": "דואגים", "t": 15.27, "scale": 1.14, "reset": 16.33},
    {"word": "הודעה", "t": 17.33, "scale": 1.12, "reset": None},
]
# Slow push-in through the long sentence, before its punch-in.
PUSHES = [{"from": 10.50, "to": 15.27, "scale": 1.03}]
SPRING_DURATION = 0.7

xs = [p["x"] for p in face["track"]]
ys = [p["y"] for p in face["track"]]

html = f"""<!doctype html>
<html lang="he" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #cam {{ position: absolute; inset: 0; overflow: hidden; }}
      #frame {{ position: absolute; inset: 0; will-change: transform; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}"
         data-width="1080" data-height="1920">
      <div id="cam">
        <div id="frame">
          <video id="a-roll" class="clip" src="in.mov" playsinline data-start="0" data-track-index="0" data-duration="{DURATION}"
                 data-has-audio="true"
                 style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>
        </div>
      </div>
    </div>

    <script>
      // Critically damped spring: fast start, settles on the target, never overshoots.
      const spring = (p) => (1 - (1 + 7 * p) * Math.exp(-7 * p)) / (1 - 8 * Math.exp(-7));

      // Smoothed face center per source frame, in percent of the frame.
      const FACE_FPS = {face["fps"]};
      const FACE_X = {json.dumps([round(v, 1) for v in xs])};
      const FACE_Y = {json.dumps([round(v, 1) for v in ys])};

      const ZOOMS = {json.dumps(ZOOMS, ensure_ascii=False)};
      const PUSHES = {json.dumps(PUSHES)};
      const SPRING_DURATION = {SPRING_DURATION};

      const tl = gsap.timeline({{ paused: true }});
      tl.set("#frame", {{ scale: 1, transformOrigin: `${{FACE_X[0]}}% ${{FACE_Y[0]}}%` }}, 0);

      // Zoom center follows the face every frame, so the face never leaves the frame.
      for (let i = 1; i < FACE_X.length; i++) {{
        tl.set("#frame", {{ transformOrigin: `${{FACE_X[i]}}% ${{FACE_Y[i]}}%` }}, i / FACE_FPS);
      }}

      for (const p of PUSHES) {{
        tl.fromTo("#frame", {{ scale: 1 }}, {{ scale: p.scale, duration: p.to - p.from, ease: "none", immediateRender: false }}, p.from);
      }}

      for (const z of ZOOMS) {{
        const push = PUSHES.find((p) => p.to === z.t);
        tl.fromTo("#frame", {{ scale: push ? push.scale : 1 }},
          {{ scale: z.scale, duration: SPRING_DURATION, ease: spring, immediateRender: false }}, z.t);
        if (z.reset !== null) tl.set("#frame", {{ scale: 1 }}, z.reset);
      }}

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(sys.argv[2], "w").write(html)
print("wrote", sys.argv[2])
