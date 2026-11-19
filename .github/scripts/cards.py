#!/usr/bin/env python3
"""Draws the profile README's cards as animated SVGs: the name card, the contribution heatmap,
the last twelve months in numbers, three highlight cards and the repos I'm working on.

The numbers come from GitHub's API each run (.github/workflows/cards.yml, daily). Paper cards,
an editorial serif (Instrument Serif, OFL, embedded so it renders inside an <img>), and one blue.

A README can't run scripts, but an SVG shown through <img> still plays its own CSS and SMIL
animations, so every card moves on its own: the name types itself and a blue letter walks along
it, the portrait draws in from the top, the heatmap fills left to right and a light sweeps it,
bars grow, numbers count up, and every card plays again every 14 s. All of it is CSS, which every browser plays inside an <img>. Viewers who ask for reduced motion get the still cards.
Standard library only.

    GITHUB_TOKEN=... python .github/scripts/cards.py <user> <out dir>
"""

import base64
import datetime
import html
import json
import os
import sys
import textwrap
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cards"

# ------------------------------------------------------------------ what the cards say
KICKER = "WEB & AI DEVELOPER  ·  B.TECH CSE (DATA SCIENCE) ’28"
FIRST, LAST = "Suyash", "Shukla"
BIO = (
    "I build AI products that do the work: RAG that cites its sources,",
    "voice agents that run your phone, and models that forecast attacks.",
)
SITE = "howsuyash.github.io"

# (file, kicker, headline frames (the last is what stays; earlier ones count up to it), text, background, ink)
HIGHLIGHTS = [
    ("card-ship", "SHIP", ["Quenaire, live"],
     "AI SaaS that answers security questionnaires from a company's own docs. quenaire.com",
     "#1f3bff", "#ffffff"),
    ("card-hack", "HACK", ["1st at HackIIITD", "2nd at HackIIITD", "3rd at HackIIITD", "4th at HackIIITD"],
     "Diplo, a Hindi voice agent that runs your phone. And SIH 2026 with AttackForecast.",
     "#e3122d", "#ffffff"),
    ("card-work", "WORK", ["0 internships", "1 internship", "2 internships"],
     "IBM and Tryhosting so far. Open to internships, remote from India.",
     "#ffc915", "#16171d"),
]
REPOS = ["Diplo", "shadow-play", "PolicyLens"]

# ------------------------------------------------------------------ the look
W = 840
PAPER, BORDER = "#fafaf7", "#e7e5df"
INK, BODY, MUTED, FAINT, RULE = "#16171d", "#3d4049", "#6b6f7a", "#a3a6ad", "#e4e2dc"
BLUE = "#1f3bff"
HEAT = ["#e9eaf6", "#c3c8f7", "#929bf3", "#5c67ee", "#1f3bff"]
PAST_MONTH, THIS_MONTH = INK, "#d9d8d2"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
EASE = "cubic-bezier(.2,.7,.2,1)"
# Every card plays its entrance, holds it, fades out and plays it again, every CYCLE seconds, so
# the page is always moving, whenever someone scrolls to a card.
CYCLE = 14.0


def pct(seconds: float) -> str:
    return f"{100 * seconds / CYCLE:.2f}%"


def font(name: str) -> str:
    return base64.b64encode((HERE / name).read_bytes()).decode()


STYLE = (
    f"@font-face{{font-family:'Serif';src:url(data:font/ttf;base64,{font('InstrumentSerif-Regular.ttf')}) format('truetype')}}"
    f"@font-face{{font-family:'SerifItalic';src:url(data:font/ttf;base64,{font('InstrumentSerif-Italic.ttf')}) format('truetype')}}"
    ".s{font-family:'Serif',Georgia,serif}.i{font-family:'SerifItalic',Georgia,serif;font-style:italic}"
    f".m{{font-family:{MONO};letter-spacing:1.4px}}.t{{font-family:{SANS}}}"
    # Each plays in its first moments of the cycle, holds, and fades out at the end of it.
    # rise: fades in from a few px below. pop: fades in. grow: a bar rising from its base.
    # type: a letter appearing. draw: the portrait drawn from the top down.
    f"@keyframes rise{{0%{{opacity:0;transform:translateY(8px)}}{pct(.7)},96%{{opacity:1;transform:none}}100%{{opacity:0;transform:none}}}}"
    f"@keyframes pop{{0%{{opacity:0}}{pct(.45)},96%{{opacity:1}}100%{{opacity:0}}}}"
    f"@keyframes grow{{0%{{transform:scaleY(0)}}{pct(.9)},96%{{transform:scaleY(1)}}100%{{transform:scaleY(0)}}}}"
    f"@keyframes type{{0%{{fill-opacity:0}}{pct(.12)},96%{{fill-opacity:1}}100%{{fill-opacity:0}}}}"
    f"@keyframes draw{{0%{{clip-path:inset(0 0 100% 0)}}{pct(2.6)},96%{{clip-path:inset(0 0 0 0)}}100%{{clip-path:inset(0 0 100% 0)}}}}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}"
    f".r{{animation:rise {CYCLE}s {EASE} infinite both}}.p{{animation:pop {CYCLE}s ease-out infinite both}}"
    f".g{{transform-box:fill-box;transform-origin:50% 100%;animation:grow {CYCLE}s {EASE} infinite both}}"
    # no motion wanted: the finished card, still
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.last{visibility:visible!important}}"
)


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def delay(seconds: float) -> str:
    return f' style="animation-delay:{seconds:.2f}s"'


def svg(width: int, height: int, body: list[str], label: str, paper: str | None = PAPER,
        border: str | None = BORDER, style: str = "") -> str:
    card = f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{paper}" stroke="{border}"/>' if paper else ""
    return "\n".join(
        [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">',
         f"<style>{STYLE}{style}</style>", card, *body, "</svg>"]
    )


def kicker(x: float, y: float, text: str, fill: str = MUTED, dot: str | None = BLUE, at: float = 0) -> str:
    square = f'<rect x="{x}" y="{y - 7}" width="6" height="6" fill="{dot}"/>' if dot else ""
    shift = 14 if dot else 0
    return (f'<g class="p"{delay(at)}>' + square +
            f'<text class="m" x="{x + shift}" y="{y}" font-size="10" fill="{fill}">{esc(text)}</text></g>')


COUNTERS = [0]


def count_up(frames: list[str], start: float, length: float = 1.1) -> tuple[list[str], str]:
    """Shows [frames] one after another from [start] over [length] s, easing out, then holds the
    last until the cycle ends, every cycle. CSS can't change what a text says, so every frame is
    drawn hidden and shown only for its moment. [frames] are whole <text> tags. Returns the tags
    and the keyframes they need."""
    if len(frames) == 1:
        return [frames[0]], ""
    out, css = [], ""
    n = len(frames)
    times = [start + length * (1 - (1 - k / (n - 1)) ** 2) for k in range(n)]
    for k, frame in enumerate(frames):
        # visible from its moment until the next frame's, or, for the last, until the fade-out
        shown = (times[k + 1] - times[k]) if k + 1 < n else (CYCLE * .96 - (times[k] - times[0]))
        COUNTERS[0] += 1
        name = f"c{COUNTERS[0]}"
        css += f"@keyframes {name}{{0%{{visibility:visible}}{pct(shown)},100%{{visibility:hidden}}}}"
        tag = frame.replace(
            "<text ", f'<text visibility="hidden" style="animation:{name} {CYCLE}s step-end {times[k]:.3f}s infinite" ', 1)
        if k + 1 == n:
            tag = tag.replace('class="', 'class="last ', 1)
        out.append(tag)
    return out, css


def counting(value: int, steps: int = 14) -> list[int]:
    return sorted({round(value * k / steps) for k in range(steps + 1)})


# ------------------------------------------------------------------ GitHub
def api(token: str, path: str, query: dict | None = None):
    url = "https://api.github.com" + path
    body = json.dumps(query).encode() if query else None
    request = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if isinstance(data, dict) and data.get("errors"):
        sys.exit(f"GitHub said: {data['errors']}")
    return data


CALENDAR = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date weekday contributionCount contributionLevel } } } } } }"""


def calendar(token: str, user: str) -> dict:
    data = api(token, "/graphql", {"query": CALENDAR, "variables": {"login": user}})
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


# ------------------------------------------------------------------ the cards
TYPE_EVERY = 0.075  # s per letter as the name types itself
WALK_EVERY = 0.55  # s the blue letter stays on each letter of the last name


def hero() -> str:
    portrait = base64.b64encode((HERE / "portrait-ink.png").read_bytes()).decode()
    t = 0.35
    first = ""
    for ch in FIRST:
        first += f'<tspan style="animation:type {CYCLE}s linear {t:.2f}s infinite both">{esc(ch)}</tspan>'
        t += TYPE_EVERY
    t += 0.15
    # The blue letter walks along the last name, one letter at a time, for good.
    walk = len(LAST) * WALK_EVERY
    share = 100 / len(LAST)
    style = f"@keyframes walk{{0%,{share - 0.5:.2f}%{{fill:{BLUE}}}{share:.2f}%,100%{{fill:{INK}}}}}"
    walk_from = t + len(LAST) * TYPE_EVERY + 0.3
    last = ""
    for k, ch in enumerate(LAST):
        last += (f'<tspan style="animation:type {CYCLE}s linear {t:.2f}s infinite both,walk {walk:.2f}s linear '
                 f'{walk_from + k * WALK_EVERY:.2f}s infinite">{esc(ch)}</tspan>')
        t += TYPE_EVERY
    body = [
        # the portrait draws in from the top, like the pen going down the page
        f'<image x="560" y="34" width="250" height="250" style="animation:draw {CYCLE}s cubic-bezier(.3,.1,.3,1) .4s infinite both" '
        f'href="data:image/png;base64,{portrait}"/>',
        kicker(40, 52, KICKER, at=0.1),
        f'<text class="s" x="36" y="138" font-size="84" fill="{INK}">{first}</text>',
        f'<text class="i" x="38" y="214" font-size="84" fill="{INK}">{last}</text>',
        *[f'<text class="t r" x="40" y="{252 + 21 * n}" font-size="14" fill="{BODY}"{delay(t + 0.1 + 0.12 * n)}>{esc(line)}</text>'
          for n, line in enumerate(BIO)],
        f'<text class="m r" x="40" y="{252 + 21 * len(BIO) + 18}" font-size="10" fill="{INK}"{delay(t + 0.45)}>{esc(SITE)}  ↗</text>',
    ]
    return svg(W, 330, body, f"{FIRST} {LAST}", style=style)


def heatmap(cal: dict) -> str:
    weeks = cal["weeks"]
    left, top = 40, 88
    step = (W - 2 * left) / len(weeks)
    cell = step * 0.78
    grid_w, grid_h = len(weeks) * step, 7 * step
    body = [
        f'<text class="s r" x="40" y="62" font-size="30" fill="{INK}">Every day, <tspan class="i" fill="{BLUE}">in blue</tspan></text>',
        f'<text class="m p" x="{W - 40}" y="58" font-size="9" fill="{FAINT}" text-anchor="end"{delay(0.3)}>REFRESHED DAILY</text>',
    ]
    last_month = None
    for i, week in enumerate(weeks):
        first = datetime.date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and i < len(weeks) - 2:
            if last_month is not None or first.day <= 7:
                body.append(f'<text class="m p" x="{left + i * step:.1f}" y="{top + grid_h + 16:.1f}" font-size="9" fill="{FAINT}"{delay(0.3 + i * 0.025)}>{first:%b}</text>')
            last_month = first.month
        for day in week["contributionDays"]:
            n = day["contributionCount"]
            date = datetime.date.fromisoformat(day["date"])
            # the year fills in left to right, each week a beat after the one before
            body.append(
                f'<rect class="p" x="{left + i * step:.1f}" y="{top + day["weekday"] * step:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" '
                f'fill="{HEAT[LEVEL.get(day["contributionLevel"], 0)]}"{delay(0.35 + i * 0.025 + day["weekday"] * 0.012)}>'
                f'<title>{n} on {date:%d %b %Y}</title></rect>'
            )
    # then a soft light sweeps across it every few seconds, for as long as the page is open
    body.append(
        f'<clipPath id="grid"><rect x="{left}" y="{top}" width="{grid_w:.1f}" height="{grid_h:.1f}"/></clipPath>'
        '<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<g clip-path="url(#grid)"><rect x="{left - 120}" y="{top}" width="120" height="{grid_h:.1f}" fill="url(#sweep)" '
        'style="animation:sweep 6s linear 2.2s infinite"/></g>'
    )
    y = top + grid_h + 38
    right = W - 40
    body.append(f'<text class="m p" x="{right}" y="{y:.1f}" font-size="9" fill="{FAINT}" text-anchor="end"{delay(1.6)}>MORE</text>')
    start = right - 40 - 5 * 13
    for n, color in enumerate(HEAT):
        body.append(f'<rect class="p" x="{start + n * 13}" y="{y - 9:.1f}" width="10" height="10" rx="2" fill="{color}"{delay(1.6 + n * 0.08)}/>')
    body.append(f'<text class="m p" x="{start - 8}" y="{y:.1f}" font-size="9" fill="{FAINT}" text-anchor="end"{delay(1.6)}>LESS</text>')
    sweep = f"@keyframes sweep{{0%{{transform:translateX(0)}}45%,100%{{transform:translateX({grid_w + 120:.0f}px)}}}}"
    return svg(W, int(y + 26), body, f"{cal['totalContributions']} contributions in the last year", style=sweep)


def numbers(cal: dict) -> dict:
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    today = datetime.date.fromisoformat(days[-1]["date"])
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # today not done yet doesn't break the streak, as on GitHub
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1
    months: dict[tuple[int, int], int] = {}
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        months[(date.year, date.month)] = months.get((date.year, date.month), 0) + d["contributionCount"]
    last12 = list(months.items())[-12:]
    return {
        "total": cal["totalContributions"], "current": current, "longest": longest,
        "active": sum(1 for c in counts if c), "days": len(counts), "busiest": max(counts, default=0),
        "months": last12, "this_month": (today.year, today.month),
    }


def stats(cal: dict) -> str:
    n = numbers(cal)
    body = [kicker(40, 50, "THE LAST 12 MONTHS ON GITHUB", dot=None, at=0.1)]
    style = ""
    tags, css = count_up(
        [f'<text class="s" x="40" y="96" font-size="38" fill="{INK}">{v:,} <tspan class="i">contributions</tspan></text>'
         for v in counting(n["total"])],
        start=0.3, length=1.4,
    )
    body += tags
    style += css
    left, base, span, tall = 40, 222, 480, 92
    slot = span / len(n["months"])
    top = max((v for _, v in n["months"]), default=0) or 1
    best = max(n["months"], key=lambda m: m[1])[0] if n["months"] else None
    for i, ((year, month), value) in enumerate(n["months"]):
        h = max(2, tall * value / top)
        x = left + i * slot
        color = BLUE if (year, month) == best and value else (THIS_MONTH if (year, month) == n["this_month"] else PAST_MONTH)
        body.append(f'<rect class="g" x="{x:.1f}" y="{base - h:.1f}" width="{slot * .72:.1f}" height="{h:.1f}" fill="{color}"{delay(0.4 + i * 0.07)}>'
                    f'<title>{value} in {datetime.date(year, month, 1):%B %Y}</title></rect>')
        if (year, month) == best and value:
            body.append(f'<text class="m r" x="{x + slot * .36:.1f}" y="{base - h - 6:.1f}" font-size="8" fill="{BLUE}" text-anchor="middle"{delay(1.5)}>{value:,}</text>')
        body.append(f'<text class="m p" x="{x + slot * .36:.1f}" y="{base + 16}" font-size="8" fill="{FAINT}" text-anchor="middle"{delay(0.4 + i * 0.07)}>{datetime.date(year, month, 1):%b}</text>')

    x = 590
    streak = "current streak, and the longest" if n["current"] == n["longest"] else f"current streak · longest {n['longest']}"
    rows = [
        (lambda v: f'{v} <tspan class="i">day{"s" if v != 1 else ""}</tspan>', n["current"], streak),
        (lambda v: f'{v} <tspan fill="{FAINT}">/ {n["days"]}</tspan>', n["active"], "days with a commit"),
        (lambda v: f"{v}", n["busiest"], "on the busiest day"),
    ]
    for k, (big, value, small) in enumerate(rows):
        y = 84 + k * 68
        at = 0.5 + k * 0.25
        tags, css = count_up([f'<text class="s" x="{x}" y="{y}" font-size="30" fill="{INK}">{big(v)}</text>' for v in counting(value, 10)],
                             start=at, length=1.0)
        body += tags
        style += css
        body.append(f'<text class="t p" x="{x}" y="{y + 18}" font-size="11" fill="{MUTED}"{delay(at + 0.2)}>{esc(small)}</text>')
        if k < len(rows) - 1:
            body.append(f'<line class="p" x1="{x}" y1="{y + 34}" x2="{W - 40}" y2="{y + 34}" stroke="{RULE}"{delay(at + 0.3)}/>')
    return svg(W, 262, body, f"{n['total']} contributions in the last 12 months", style=style)


def highlight(kick: str, headlines: list[str], text: str, bg: str, ink: str, at: float) -> str:
    lines = textwrap.wrap(text, 40)[:3]
    headline, css = count_up([f'<text class="i" x="22" y="98" font-size="31" fill="{ink}">{esc(h)}</text>' for h in headlines],
                             start=at + 0.15, length=0.9)
    soft = "rgba(255,255,255,0.78)" if ink == "#ffffff" else "rgba(22,23,29,0.72)"
    body = [
        f'<text class="m p" x="22" y="32" font-size="9" fill="{ink}"{delay(at)}>{esc(kick)}</text>',
        f'<text class="t p" x="250" y="33" font-size="14" fill="{ink}" text-anchor="end"{delay(at)}>→</text>',
        *headline,
        *[f'<text class="t r" x="22" y="{126 + 16 * k}" font-size="11.5" fill="{soft}"{delay(at + 0.3 + 0.08 * k)}>{esc(line)}</text>'
          for k, line in enumerate(lines)],
    ]
    if len(headlines) == 1:  # nothing to count: the headline rises in instead
        body[2] = body[2].replace('class="i"', 'class="i r"').replace("<text ", f"<text{delay(at + 0.15)} ", 1)
    return svg(272, 180, body, headlines[-1], paper=bg, border=bg, style=css)


def ago(stamp: str) -> str:
    then = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    days = (datetime.datetime.now(datetime.timezone.utc) - then).days
    if days <= 0:
        return "updated today"
    if days == 1:
        return "updated yesterday"
    if days < 31:
        return f"updated {days} days ago"
    return f"updated {then:%b %Y}"


def repo_card(repo: dict, at: float) -> str:
    wrapped = textwrap.wrap(repo.get("description") or "", 42)
    lines = wrapped[:3]
    if len(wrapped) > 3:
        lines[-1] = lines[-1].rstrip(".,; ") + "…"
    meta = "  ·  ".join(x for x in [repo.get("language") or "", f"★ {repo['stargazers_count']}", ago(repo["pushed_at"])] if x)
    # the blue dot breathes: work in progress
    body = [
        f'<circle cx="25" cy="31" r="3.5" fill="{BLUE}" style="animation:pulse 2.4s ease-in-out {at:.2f}s infinite"/>',
        f'<text class="m r" x="36" y="35" font-size="11" fill="{INK}" style="letter-spacing:0.4px;animation-delay:{at:.2f}s">{esc(repo["name"])}</text>',
        *[f'<text class="t r" x="22" y="{62 + 17 * k}" font-size="11.5" fill="{MUTED}"{delay(at + 0.12 + 0.07 * k)}>{esc(line)}</text>'
          for k, line in enumerate(lines)],
        f'<text class="m p" x="22" y="134" font-size="8.5" fill="{FAINT}" style="letter-spacing:0.6px;animation-delay:{at + 0.4:.2f}s">{esc(meta)}</text>',
    ]
    return svg(272, 154, body, repo["name"])


def title(regular: str, italic: str) -> str:
    body = [f'<text class="s r" x="2" y="38" font-size="30" fill="#8b8f98">{esc(regular)}<tspan class="i">{esc(italic)}</tspan></text>']
    return svg(W, 52, body, regular + italic, paper=None)


def main() -> None:
    user, out = sys.argv[1], Path(sys.argv[2])
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
    out.mkdir(parents=True, exist_ok=True)
    cal = calendar(token, user)
    cards = {"hero": hero(), "heatmap": heatmap(cal), "stats": stats(cal), "coding": title("What I’m ", "coding")}
    for k, (name, kick, headlines, text, bg, ink) in enumerate(HIGHLIGHTS):
        cards[name] = highlight(kick, headlines, text, bg, ink, at=0.15 + 0.15 * k)
    for k, name in enumerate(REPOS):
        cards[f"repo-{name}"] = repo_card(api(token, f"/repos/{user}/{name}"), at=0.15 + 0.15 * k)
    for name, content in cards.items():
        (out / f"{name}.svg").write_text(content, encoding="utf-8")
    print("wrote", ", ".join(sorted(cards)))


if __name__ == "__main__":
    main()
