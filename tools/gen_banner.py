"""Generates an animated synthwave banner SVG for the GitHub profile README."""
import random, sys

W, H = 1200, 340
HZ = 222          # horizon y
VPX = 600         # vanishing point x
random.seed(7)

out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('''<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#07021a"/>
    <stop offset="0.55" stop-color="#1c0638"/>
    <stop offset="1" stop-color="#4a0e5c"/>
  </linearGradient>
  <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2a0640"/>
    <stop offset="1" stop-color="#07021a"/>
  </linearGradient>
  <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe259"/>
    <stop offset="0.45" stop-color="#ff8a5c"/>
    <stop offset="1" stop-color="#ff2e93"/>
  </linearGradient>
  <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="420" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="#ff79c6"/>
    <stop offset="0.55" stop-color="#ffb86c"/>
    <stop offset="0.8" stop-color="#fff1c1"/>
    <stop offset="1" stop-color="#ff79c6"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="840 0" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="meteor" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#fff"/>
  </linearGradient>
  <linearGradient id="scan" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="250" y2="0">
    <stop offset="0" stop-color="#ff79c6" stop-opacity="0.35"/>
    <stop offset="0.5" stop-color="#ffffff"/>
    <stop offset="1" stop-color="#ff79c6" stop-opacity="0.35"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-250 0;250 0" dur="2.4s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-40%" width="140%" height="180%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="18"/>
  </filter>
  <clipPath id="aboveHz"><rect x="0" y="0" width="1200" height="''' + str(HZ) + '''"/></clipPath>
  <clipPath id="belowHz"><rect x="0" y="''' + str(HZ) + '''" width="1200" height="''' + str(H - HZ) + '''"/></clipPath>
  <mask id="sunStripes">
    <rect x="0" y="0" width="1200" height="340" fill="#fff"/>''')
# stripes cut out of the lower half of the sun, thickening toward the horizon
sy, gap = 150, 3
while sy < HZ:
    a(f'    <rect x="0" y="{sy}" width="1200" height="{gap:.1f}" fill="#000"/>')
    sy += 14 - (sy - 150) * 0.06
    gap += 1.4
a('''  </mask>
</defs>
<style>
  .tw{animation:tw 3s ease-in-out infinite}
  @keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
  .sun{animation:pulse 6s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:.9}50%{opacity:1}}
  .cur{animation:blink 1s steps(1) infinite}
  @keyframes blink{50%{opacity:0}}
  .flk{animation:flk 5s linear infinite}
  @keyframes flk{0%,18%,22%,25%,53%,57%,100%{opacity:1}20%,24%,55%{opacity:.55}}
  .rise{animation:rise 6s linear infinite}
  @keyframes rise{0%{transform:translateY(0);opacity:0}15%{opacity:1}100%{transform:translateY(-120px);opacity:0}}
</style>''')
a(f'<rect width="{W}" height="{HZ}" fill="url(#sky)"/>')
a(f'<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#ground)"/>')

# stars
for i in range(70):
    x, y = random.uniform(0, W), random.uniform(0, HZ - 50)
    r = random.choice([0.7, 0.9, 1.1, 1.5])
    d = random.uniform(0, 3)
    a(f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" style="animation-delay:-{d:.2f}s"/>')

# sun (right side)
SX, SY, SR = 965, 160, 105
a(f'<circle cx="{SX}" cy="{SY}" r="{SR + 30}" fill="#ff2e93" opacity="0.35" filter="url(#softglow)">'
  f'<animate attributeName="r" values="{SR + 18};{SR + 45};{SR + 18}" dur="4s" repeatCount="indefinite"/>'
  f'<animate attributeName="opacity" values="0.3;0.6;0.3" dur="4s" repeatCount="indefinite"/></circle>')

# shooting stars: a streak that slides diagonally and fades, staggered
for (x0, y0, dl, dur) in [(80, 20, 0, 3.6), (520, 6, 1.3, 4.2), (760, 40, 2.6, 3.9), (300, 60, 3.4, 5.0)]:
    a(f'<g opacity="0"><line x1="0" y1="0" x2="90" y2="0" stroke="url(#meteor)" stroke-width="2" stroke-linecap="round" '
      f'transform="translate({x0} {y0}) rotate(25)"/>'
      f'<animateTransform attributeName="transform" type="translate" values="0 0;260 120" keyTimes="0;1" dur="{dur}s" begin="{dl}s" repeatCount="indefinite"/>'
      f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;0.12;0.3;1" dur="{dur}s" begin="{dl}s" repeatCount="indefinite"/></g>')
a(f'<g clip-path="url(#aboveHz)"><circle class="sun" cx="{SX}" cy="{SY}" r="{SR}" fill="url(#sun)" mask="url(#sunStripes)"/></g>')

# mountains silhouette on the horizon
def ridge(x0, x1, peak, color, op):
    pts = [(x0, HZ)]
    n = 9
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        h = peak * (1 - abs(i - n / 2) / (n / 2)) * random.uniform(0.55, 1.0)
        pts.append((x, HZ - h))
    pts.append((x1, HZ))
    a('<polygon points="' + ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts) + f'" fill="{color}" opacity="{op}"/>')
ridge(-40, 380, 70, '#12052a', 1)
ridge(280, 620, 40, '#1a0733', 1)
ridge(1060, 1260, 40, '#12052a', 1)

# grid: vertical lines converging to the vanishing point
a('<g clip-path="url(#belowHz)" stroke="#ff2e93" stroke-width="1.3" opacity="0.85">')
for k in range(-26, 27):
    x_top = VPX + k * 22
    x_bot = VPX + k * 150
    a(f'<line x1="{x_top}" y1="{HZ}" x2="{x_bot}" y2="{H}"/>')
# horizontal lines scrolling toward the viewer (SMIL, ease-in for perspective)
N, DUR = 8, 4.0
for i in range(N):
    begin = -DUR * i / N
    a(f'<line x1="0" x2="{W}" y1="{HZ}" y2="{HZ}">'
      f'<animate attributeName="y1" values="{HZ};{H}" dur="{DUR}s" begin="{begin:.2f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.55 0 1 0.6"/>'
      f'<animate attributeName="y2" values="{HZ};{H}" dur="{DUR}s" begin="{begin:.2f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.55 0 1 0.6"/>'
      f'<animate attributeName="stroke-opacity" values="0.15;1" dur="{DUR}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
      '</line>')
a('</g>')
# horizon glow line
a(f'<rect x="0" y="{HZ - 1}" width="{W}" height="2.5" fill="#ff79c6" filter="url(#glow)">'
  f'<animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/></rect>')
# embers rising off the horizon
for i in range(16):
    x = random.uniform(20, W - 20)
    d = random.uniform(0, 6)
    r = random.choice([1.2, 1.6, 2])
    a(f'<circle class="rise" cx="{x:.0f}" cy="{HZ + 4}" r="{r}" fill="#ff9bd5" style="animation-delay:-{d:.2f}s"/>')

# text block (left)
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', Consolas, 'Courier New', monospace"
a(f'<text class="flk" x="70" y="118" font-family="{FONT}" font-size="76" font-weight="900" font-style="italic" '
  f'fill="url(#name)" filter="url(#glow)" letter-spacing="1">Suyash Shukla</text>')
a(f'<text x="74" y="160" font-family="{MONO}" font-size="22" fill="#8be9fd" letter-spacing="2">'
  f'&gt; Web &amp; AI Developer<tspan class="cur">_</tspan></text>')
a(f'<rect x="74" y="178" width="250" height="3" fill="url(#scan)"/>')
a(f'<text x="1180" y="330" text-anchor="end" font-family="{MONO}" font-size="14" fill="#ffb3e0" opacity="0.8">'
  f'howsuyash.github.io</text>')
a('</svg>')

open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(out))
print('ok', sum(len(s) for s in out), 'bytes')
