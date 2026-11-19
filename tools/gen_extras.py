"""Animated neon section headings, a divider and a wave footer for the profile README."""
import math, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', Consolas, 'Courier New', monospace"


def write(name, body):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(body)


# ---------- section headings ----------
HEADINGS = {
    'h-about': 'ABOUT ME',
    'h-stack': 'TECH STACK',
    'h-projects': 'FEATURED PROJECTS',
    'h-analytics': 'GITHUB ANALYTICS',
    'h-graph': 'CONTRIBUTION GRAPH',
    'h-connect': "LET'S CONNECT",
}
W, H = 800, 86
for i, (fname, label) in enumerate(HEADINGS.items()):
    delay = i * 0.37  # so the headings don't flicker in lockstep
    write(f'{fname}.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="t" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="300" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="#ff79c6"/><stop offset="0.6" stop-color="#ffb86c"/><stop offset="1" stop-color="#ff79c6"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="600 0" dur="4s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="u" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#7b2ff7" stop-opacity="0"/><stop offset="0.5" stop-color="#ff79c6"/><stop offset="1" stop-color="#7b2ff7" stop-opacity="0"/>
  </linearGradient>
  <filter id="g" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<style>
  .flk{{animation:flk 6s linear infinite;animation-delay:-{delay:.2f}s}}
  @keyframes flk{{0%,40%,44%,47%,80%,100%{{opacity:1}}42%,46%{{opacity:.35}}}}
  .sp{{animation:sp 2.4s ease-in-out infinite;transform-origin:center;transform-box:fill-box}}
  @keyframes sp{{0%,100%{{transform:scale(.6) rotate(0);opacity:.5}}50%{{transform:scale(1.15) rotate(90deg);opacity:1}}}}
</style>
<text class="flk" x="{W/2}" y="46" text-anchor="middle" font-family="{FONT}" font-size="34" font-weight="800"
  font-style="italic" letter-spacing="4" fill="url(#t)" filter="url(#g)">{label.replace("'", "&#39;")}</text>
<path class="sp" d="M{W/2 - 250},34 l7,-7 7,7 -7,7z" fill="#8be9fd"/>
<path class="sp" style="animation-delay:-1.2s" d="M{W/2 + 236},34 l7,-7 7,7 -7,7z" fill="#8be9fd"/>
<rect x="{W/2 - 240}" y="66" width="480" height="2" fill="url(#u)">
  <animate attributeName="width" values="120;480;120" dur="3s" repeatCount="indefinite"/>
  <animate attributeName="x" values="{W/2 - 60};{W/2 - 240};{W/2 - 60}" dur="3s" repeatCount="indefinite"/>
</rect>
<circle cy="67" r="3.2" fill="#fff" filter="url(#g)">
  <animate attributeName="cx" values="{W/2 - 230};{W/2 + 230};{W/2 - 230}" dur="3.4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
</circle>
</svg>''')

# ---------- divider: a pulse of light running along a neon line ----------
DW = 1000
write('divider.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="{DW}" height="16" viewBox="0 0 {DW} 16">
<defs>
  <linearGradient id="l" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#7b2ff7" stop-opacity="0"/><stop offset="0.5" stop-color="#ff79c6" stop-opacity="0.6"/><stop offset="1" stop-color="#7b2ff7" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="p"><stop offset="0" stop-color="#fff"/><stop offset="0.4" stop-color="#ff79c6"/><stop offset="1" stop-color="#ff79c6" stop-opacity="0"/></radialGradient>
</defs>
<rect x="0" y="7" width="{DW}" height="2" fill="url(#l)"/>
<ellipse cy="8" rx="70" ry="6" fill="url(#p)">
  <animate attributeName="cx" values="-80;{DW + 80}" dur="3.2s" repeatCount="indefinite"/>
</ellipse>
</svg>''')

# ---------- footer: three layered waves scrolling sideways ----------
FW, FH = 1200, 210


def wave(amp, length, base, phase):
    """A periodic wave path two screens wide, so translating by FW loops seamlessly."""
    pts = []
    for x in range(0, 2 * FW + 1, 20):
        y = base + amp * math.sin(2 * math.pi * x / length + phase)
        pts.append(f'{x},{y:.1f}')
    return f'M0,{FH} L' + ' L'.join(pts) + f' L{2 * FW},{FH} Z'


layers = [
    # amp, wavelength (must divide FW), base y, phase, fill, opacity, duration, direction
    (14, 600, 120, 0.0, '#7b2ff7', 0.45, 14, -1),
    (18, 400, 140, 1.3, '#c13dd6', 0.55, 10, 1),
    (12, 300, 162, 2.4, '#ff79c6', 0.85, 7, -1),
]
paths = []
for amp, length, base, phase, fill, op, dur, dirn in layers:
    frm, to = ('0 0', f'-{FW} 0') if dirn < 0 else (f'-{FW} 0', '0 0')
    paths.append(f'<path d="{wave(amp, length, base, phase)}" fill="{fill}" opacity="{op}">'
                 f'<animateTransform attributeName="transform" type="translate" from="{frm}" to="{to}" dur="{dur}s" repeatCount="indefinite"/></path>')
write('footer.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}">
<defs>
  <filter id="g" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<style>
  .fl{{animation:fl 3s ease-in-out infinite}}
  @keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
</style>
<g class="fl"><text x="{FW/2}" y="58" text-anchor="middle" font-family="{MONO}" font-size="22" fill="#ffb3e0" filter="url(#g)">See you in the next commit
  <animate attributeName="opacity" values="0.55;1;0.55" dur="3s" repeatCount="indefinite"/></text></g>
{chr(10).join(paths)}
</svg>''')
print('ok', sorted(os.listdir(OUT)))
