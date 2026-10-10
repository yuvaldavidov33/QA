"""Frame-accurate render of the HyperFrames composition without the hyperframes CLI
(npm registry is unreachable in this session). Plays the same index.html in headless
Chrome: per frame, shows the matching source frame in place of the <video>, seeks the
GSAP timeline, applies clip visibility (data-start / data-duration), screenshots.
Audio is mixed in ffmpeg: voice + music.wav + sfx.wav x data-volume.

usage: render.py <reel dir> <frames dir (%05d.jpg, 1-based; cutouts in ../cutout)> <voice source video> <out.mp4> [fps]
"""
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REEL, FRAMES, VOICE, OUT = map(Path, sys.argv[1:5])
FPS = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
SRC_FPS = 29.955223880597014
CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"

nframes = len(list(FRAMES.glob("*.jpg")))
silent = OUT.with_suffix(".silent.mp4")
enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", str(silent)],
    stdin=subprocess.PIPE)

SETUP = """([framesUrl, cutUrl]) => {
  const v = document.querySelector('#a-roll');
  const img = document.createElement('img');
  img.id = 'a-roll-img';
  img.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover';
  v.replaceWith(img);
  window.__frames = framesUrl;
  window.__clips = [...document.querySelectorAll('.clip')].filter(e => e.id !== 'a-roll');
  window.__cutDir = cutUrl;
}"""
SEEK = """async ([t, idx]) => {
  const img = document.querySelector('#a-roll-img');
  const src = window.__frames + String(idx).padStart(5, '0') + '.jpg';
  if (!img.src.endsWith(src)) { img.src = src; await img.decode(); }
  for (const c of window.__clips) {
    const s = parseFloat(c.dataset.start), d = parseFloat(c.dataset.duration);
    c.style.visibility = (t >= s && t < s + d) ? 'visible' : 'hidden';
  }
  const cut = document.querySelector('#cutout');
  if (cut) {
    const inRange = cut.dataset.cutRanges.split(',').some(r => { const [a, b] = r.split('-').map(Number); return idx >= a && idx <= b; });
    if (inRange) {
      const cs = window.__cutDir + String(idx).padStart(5, '0') + '.png';
      if (!cut.src.endsWith(cs)) { cut.src = cs; await cut.decode(); }
      cut.style.visibility = 'visible';
    } else cut.style.visibility = 'hidden';
  }
  window.__timelines.main.seek(t, false);
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, args=["--allow-file-access-from-files"])
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.goto((REEL / "index.html").resolve().as_uri())
    page.wait_for_function("!!(window.__timelines && window.__timelines.main)", polling=100)
    page.evaluate("document.fonts.ready")
    page.evaluate(SETUP, [FRAMES.resolve().as_uri() + "/", (FRAMES.parent / "cutout").resolve().as_uri() + "/"])
    dur = float(page.evaluate("document.querySelector('#root').dataset.duration"))
    n = int(dur * FPS)
    for i in range(n):
        t = i / FPS
        idx = min(nframes, int(round(t * SRC_FPS)) + 1)
        page.evaluate(SEEK, [t, idx])
        enc.stdin.write(page.screenshot(type="jpeg", quality=93))
        if i % 60 == 0:
            print(f"frame {i}/{n}", flush=True)
    browser.close()
enc.stdin.close()
enc.wait()

sfx_vol = 0.55
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(VOICE), "-i", str(REEL / "music.wav"), "-i", str(REEL / "sfx.wav"),
     "-filter_complex",
     f"[1:a]aresample=48000,aformat=channel_layouts=stereo[v];[3:a]volume={sfx_vol}[s];"
     "[v][2:a][s]amix=inputs=3:duration=first:normalize=0,volume=2.6dB,alimiter=limit=0.95[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
     "-movflags", "+faststart", str(OUT)], check=True)
silent.unlink()
print("wrote", OUT)
