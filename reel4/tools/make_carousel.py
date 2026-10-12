"""Make reel4/tools/build4c.py from build4.py: the solution page becomes the 3D app-carousel copied from the client's
reference (422f8911-….mov on main). Same four blocks, same wording."""
src = open('/home/claude/qa/reel4/tools/build4.py').read()
s = src

def rep(a, b, count=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, count)

rep('    ("push", T_["rs_out"], 1.14, T_["sol_in"] - T_["rs_out"]),', '    ("push", T_["rs_out"], 1.0, T_["sol_in"] - T_["rs_out"]),')
rep('    "sol_out": t("אם") - 0.03,', '    "sol_out": t("אם") - 0.03, "prog": t("והתקדמות"),')
rep('"""Generate reel4/index.html', '"""(carousel version) Generate reel4/index.html')

# --- cutouts cover the carousel segment too
rep('CUT_A, CUT_B = int(sys.argv[5]), int(sys.argv[6])',
    'CUT_A, CUT_B = int(sys.argv[5]), int(sys.argv[6])\nCAR_A, CAR_B = int(sys.argv[7]), int(sys.argv[8])  # person cutouts over the carousel')

# --- zoom: frame back to 1.0 during the carousel (the reframe is done on #side)
rep('''    ("set", T_["sol_out"], 1.00, 0),''', '''    ("set", T_["sol_out"], 1.00, 0),''')

# --- tiles + text (same wording as the blue page)
rep('SOLUTION = "\\n".join(', '''ITEMS = [("עד 6 מתאמנים", "בקבוצה קטנה", VIS_SIX), ("תכנית אישית", "לכל מתאמן", VIS_PLAN),
         ("מעקב משקלים", "בכל אימון", VIS_KG), ("והתקדמות", "שרואים בעיניים", VIS_GRAPH)]
TILES = "\\n".join(
    f'<div class="tile" id="s{k + 1}">' + "".join(f'<i class="fc fc{j}"></i>' for j in range(7)) + f'<div class="face">{vis}</div></div>'
    for k, (_, _, vis) in enumerate(ITEMS))


def words_html(txt, cls):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in txt.split())


CTEXT = "\\n".join(
    f'<div class="ct" id="ct{k + 1}"><div class="m"><span class="badge v">✓</span>{words_html(m, "cw")}</div>'
    f'<div class="s">{words_html(sub, "cw")}</div></div>' for k, (m, sub, _) in enumerate(ITEMS))
SOLUTION = "\\n".join(''')

# --- markup: two camera stacks (video below the carousel, person cutout above it)
rep('''          <img id="cutout" class="clip" alt="" data-cut-ranges="{CUT_A}-{CUT_B}" data-start="0" data-duration="{DURATION}" data-track-index="1" />
        </div>
        </div>
      </div>
''', '''        </div>
        </div>
      </div>
      <div class="clip" id="carousel" data-start="{round(T_["sol_in"], 2)}" data-duration="{round(T_["sol_out"] - T_["sol_in"], 2)}" data-track-index="1">
        <div id="ring">
{TILES}
        </div>
      </div>
      <div class="clip" id="bgwrap" data-start="{round(T_["sol_in"], 2)}" data-duration="{round(T_["sol_out"] - T_["sol_in"], 2)}" data-track-index="1">
        <img id="bgA" class="feed" alt="" /><img id="bgB" class="feed" alt="" />
      </div>
      <div class="clip" id="fgwrap" data-start="{round(T_["sol_in"], 2)}" data-duration="{round(T_["sol_out"] - T_["sol_in"], 2)}" data-track-index="1">
        <img id="fgimg" class="feed" alt="" />
      </div>
      <div id="cam2" class="camS">
        <div id="side2" class="sideS">
        <div id="frame2" class="frameS">
          <img id="cutout" class="clip" alt="" data-cut-ranges="{CUT_A}-{CUT_B}" data-start="0" data-duration="{DURATION}" data-track-index="1" />
        </div>
        </div>
      </div>
      <div class="ov clip" id="ctext" data-start="{round(T_["sol_in"], 2)}" data-duration="{round(T_["sol_out"] - T_["sol_in"], 2)}" data-track-index="2">
{CTEXT}
      </div>
''')
rep('''      <div id="cam">
        <div id="side">
        <div id="frame">''', '''      <div id="cam" class="camS">
        <div id="side" class="sideS">
        <div id="frame" class="frameS">''')
# drop the blue page
a = s.index('      <div class="clip page" id="solution"')
b = s.index('      <div class="clip" id="leakClip"')
s = s[:a] + s[b:]

# --- CSS
rep('      #frame {{ position: absolute; inset: 0; will-change: transform; }}', '''      #frame {{ position: absolute; inset: 0; will-change: transform; }}
      #cam2 {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
      #frame2, .sideS {{ position: absolute; inset: 0; }}
      /* App carousel (client reference): the shot slides so the trainer stands on the right, background goes grey
         and soft, a ring of thick navy tiles turns on the left behind him; the block text sits above the ring. */
      #carousel {{ position: absolute; inset: 0; perspective: 1300px; perspective-origin: 324px 1000px; font-family: "Heebo", sans-serif; color: #fff; direction: rtl; }}
      #ring {{ position: absolute; left: 324px; top: 1180px; width: 0; height: 0; transform-style: preserve-3d; }}
      /* Closed round ring: each tile is a curved panel built from 7 narrow facets on the cylinder (radius 290);
         the block content sits on a plane at the panel's centre. */
      .tile {{ position: absolute; left: 0; top: 0; width: 0; height: 0; transform-style: preserve-3d; }}
      .tile .fc {{ position: absolute; left: -28.5px; top: -200px; width: 57px; height: 400px; backface-visibility: visible;
        background: linear-gradient(180deg, #2e43a6 0%, #1c2c7a 45%, #111c52 100%);
        box-shadow: inset 0 3px 0 rgba(255,255,255,.28), inset 0 -3px 0 rgba(255,255,255,.12); }}
      .tile .fc0 {{ border-radius: 38px 0 0 38px; box-shadow: inset 4px 0 0 rgba(220,230,255,.55), inset 0 3px 0 rgba(255,255,255,.28); }}
      .tile .fc6 {{ border-radius: 0 38px 38px 0; box-shadow: inset -4px 0 0 rgba(220,230,255,.55), inset 0 3px 0 rgba(255,255,255,.28); }}
      .tile .face {{ position: absolute; left: -165px; top: -200px; width: 330px; height: 400px; display: grid; place-items: center;
        backface-visibility: hidden; pointer-events: none; }}
      .tile .face .vis {{ transform: scale(.88); }}
      #ctext {{ position: absolute; inset: 0; }}
      /* The shot slides right as a whole (no zoom); the left side opens onto a grey, softly blurred copy of it. */
      /* Split screen (client): 60% grey, softly blurred gym on the left (no zoom; the strip beyond the frame edge is a
         mirror of it), 40% the trainer on the right at his normal size; the carousel stands on the grey side. */
      #bgwrap {{ position: absolute; inset: 0; overflow: hidden; filter: grayscale(1) blur(9px) brightness(.8) contrast(1.05); }}
      #bgwrap img {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #bgA {{ transform: translateX(324px); }}
      #bgB {{ transform: translateX(-756px) scaleX(-1); }}
      #fgwrap {{ position: absolute; inset: 0; overflow: hidden; }}
      #fgimg {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .ct {{ position: absolute; left: 24px; width: 600px; top: 700px; text-align: center; direction: rtl; white-space: nowrap;
             text-shadow: 0 4px 22px rgba(0,0,0,.55); }}
      .ct .m {{ font-weight: 900; font-size: 58px; line-height: 1.05; display: flex; align-items: center; gap: 14px; justify-content: center; }}
      .ct .m .badge {{ width: 50px; height: 50px; font-size: 30px; }}
      .ct .s {{ font-weight: 700; font-size: 40px; line-height: 1.2; color: rgba(255,255,255,.8); margin-top: 6px; }}
      .ct .cw {{ display: inline-block; }}''')

# --- JS: zoom/origin apply to both stacks
rep('tl.set("#frame", {{ transformOrigin: `${{FACE_X[i]}}% ${{FACE_Y[i]}}%` }}, i / FACE_FPS);',
    'tl.set(".frameS", {{ transformOrigin: `${{FACE_X[i]}}% ${{FACE_Y[i]}}%` }}, i / FACE_FPS);')
rep('if (kind === "set") tl.set("#frame", {{ scale }}, at);', 'if (kind === "set") tl.set(".frameS", {{ scale }}, at);')
rep('tl.fromTo("#frame", {{ scale: cur }}, {{ scale, duration: dur, ease, immediateRender: false }}, at);',
    'tl.fromTo(".frameS", {{ scale: cur }}, {{ scale, duration: dur, ease, immediateRender: false }}, at);')
s = s.replace('tl.fromTo("#cam", ', 'tl.fromTo(".camS", ').replace('tl.set("#cam", ', 'tl.set(".camS", ').replace('tl.to("#cam", ', 'tl.to(".camS", ')

# --- JS: replace the blue-page timeline with the carousel
a = s.index('      // ===== Solution page =====')
b = s.index('      badgeIn("#s1 .badge", T.so_1 + 0.25);')
s = s[:a] + '''      // ===== App carousel (client reference 422f8911-….mov, measured frame by frame at 60 fps) =====
      // 1) Whip: the whole shot blurs out in ~0.06 s, the cut lands at the peak, the new framing sharpens in ~0.1 s.
      // 2) New framing: the trainer moves to the right half (frame slid left, 1.7x closer, fixed origin on the face),
      //    background grey and soft; the person cutout stays in colour above the ring.
      // 3) Ring of tiles on the left (centre x≈330, y≈1180), 60° apart; it turns right-to-left in eased steps of
      //    ~0.42 s so each block's tile reaches the front on its spoken words, and keeps drifting between steps.
      //    The first tile slides in from the left right after the cut.
      // 4) The block text sits above the ring: words resolve from blur; the old text blurs out as the next arrives.
      const SIN = T.sol_in, SOUT = T.sol_out, BT = [T.so_1, T.so_2, T.so_3, T.so_4];
      // Split screen: the shot slides right by 324 px at its normal size while its left edge (the wipe line) moves
      // from 0 to 648 px; the grey gym opens behind it on the left. Reversed just before "אם".
      const fgW = document.querySelector("#fgwrap"), fgI = document.querySelector("#fgimg");
      const split = {{ p: 0 }};
      const drawSplit = () => {{
        const L = 648 * split.p;
        fgI.style.transform = `translateX(${{(324 * split.p).toFixed(2)}}px)`;
        const m = `linear-gradient(90deg, transparent ${{L.toFixed(1)}}px, #000 ${{(L + 70).toFixed(1)}}px)`;
        fgW.style.webkitMaskImage = m; fgW.style.maskImage = m;
      }};
      tl.set(split, {{ p: 0, onComplete: drawSplit }}, 0.002);
      tl.fromTo(split, {{ p: 0 }}, {{ p: 1, duration: 0.45, ease: "power3.inOut", immediateRender: false, onUpdate: drawSplit }}, SIN);
      tl.fromTo("#fgimg", {{ filter: "blur(0px)" }}, {{ filter: "blur(5px)", duration: 0.2, ease: "power2.in", yoyo: true, repeat: 1, immediateRender: false }}, SIN + 0.02);
      tl.to(split, {{ p: 0, duration: 0.38, ease: "power3.inOut", onUpdate: drawSplit }}, SOUT - 0.38);
      tl.set("#ring", {{ opacity: 0 }}, 0);
      tl.to("#carousel, #ctext", {{ opacity: 0, duration: 0.2, ease: "power1.in" }}, SOUT - 0.3);
      tl.set("#carousel, #ctext", {{ opacity: 1 }}, 0);

      // When each tile turns to the front (client: give "מעקב משקלים" more time, turn to "והתקדמות" right on the word).
      const PROG = T.prog;
      const TURN = [SIN, BT[1] - 0.3, BT[2] - 0.55, PROG];
      const TXT_IN = [BT[0] - 0.05, BT[1] - 0.05, BT[2] - 0.2, PROG + 0.05];
      const tiles = [...document.querySelectorAll(".tile")];
      // place each tile on the ring: rotate around the ring centre, pushed out by the radius
      const R = 290, ARC = 76, NF = 7, STEP = ARC / NF;
      tiles.forEach((el, k) => {{
        el.style.transform = `rotateY(${{90 * k}}deg)`;
        el.querySelectorAll(".fc").forEach((f, j) => {{
          f.style.transform = `rotateY(${{(-ARC / 2 + STEP * (j + 0.5)).toFixed(3)}}deg) translateZ(${{R}}px)`;
        }});
        el.querySelector(".face").style.transform = `translateZ(${{R + 6}}px)`;
      }});
      const ring = {{ a: 60 }};
      const ringEl = document.querySelector("#ring");
      const drawRing = () => {{
        ringEl.style.transform = `rotateX(-6deg) rotateY(${{ring.a.toFixed(3)}}deg)`;
        tiles.forEach((el, k) => {{
          el.querySelectorAll(".fc").forEach((f, j) => {{
            const ang = (90 * k + ring.a - ARC / 2 + STEP * (j + 0.5)) * Math.PI / 180;   // facet normal vs camera
            const c = Math.cos(ang), lit = c > 0 ? 0.42 + 0.58 * Math.pow(c, 1.4) : 0.3 + 0.12 * -c;
            f.style.filter = `brightness(${{lit.toFixed(3)}})`;
          }});
          const d = Math.abs(((90 * k + ring.a) % 360 + 540) % 360 - 180);
          el.querySelector(".face").style.filter = `brightness(${{(1 - Math.min(d, 90) / 90 * 0.5).toFixed(3)}})`;
        }});
      }};
      tl.set(ring, {{ a: 60, onComplete: drawRing }}, 0.001);
      tl.fromTo(ring, {{ a: 60 }}, {{ a: 0, duration: 0.6, ease: "power3.out", immediateRender: false, onUpdate: drawRing }}, SIN + 0.2);
      tl.fromTo("#ring", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, SIN + 0.2);
      // between steps the ring keeps creeping a few degrees; steps land the next tile at the front on its words
      tl.to(ring, {{ a: -8, duration: Math.max(0.2, BT[1] - 0.3 - SIN - 0.7), ease: "none", onUpdate: drawRing }}, SIN + 0.7);
      for (let k = 1; k < 4; k++) {{
        const at = TURN[k], next = k < 3 ? TURN[k + 1] : SOUT;
        tl.to(ring, {{ a: -90 * k, duration: 0.5, ease: "power2.inOut", onUpdate: drawRing }}, at);
        tl.to(ring, {{ a: -90 * k - 8, duration: Math.max(0.2, next - at - 0.5), ease: "none", onUpdate: drawRing }}, at + 0.5);
      }}

      // text above the ring
      tl.set(".ct .cw, .ct .badge", {{ opacity: 0 }}, 0);
      for (let k = 0; k < 4; k++) {{
        const at = TXT_IN[k], sel = `#ct${{k + 1}}`;
        tl.fromTo(`${{sel}} .cw`, {{ opacity: 0, y: 14, filter: "blur(10px)" }},
          {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26, stagger: 0.06, ease: "power3.out", immediateRender: false }}, at);
        if (k < 3) tl.to(`${{sel}} .cw, ${{sel}} .badge`, {{ opacity: 0, y: -10, filter: "blur(10px)", duration: 0.2, stagger: 0.02, ease: "power2.in" }}, TXT_IN[k + 1] - 0.22);
      }}
''' + s[b:]
for k in range(1, 5):
    rep(f'badgeIn("#s{k} .badge", T.so_{k} + 0.25);', f'badgeIn("#ct{k} .badge", T.so_{k} + 0.1); tl.set("#ct{k} .badge", {{{{ opacity: 1 }}}}, T.so_{k} + 0.1);')
open('/home/claude/qa/reel4/tools/build4c.py', 'w').write(s)
print("ok")
# z-order: grey gym, then the ring, then the sliding shot
s = open('/home/claude/qa/reel4/tools/build4c.py').read()
bg = s[s.index('      <div class="clip" id="bgwrap"'):s.index('      <div class="clip" id="fgwrap"')]
s = s.replace(bg, '', 1)
car = '      <div class="clip" id="carousel"'
s = s.replace(car, bg + car, 1)
open('/home/claude/qa/reel4/tools/build4c.py', 'w').write(s)
print("reordered")
