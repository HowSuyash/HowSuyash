#!/usr/bin/env python3
"""Draws the profile README's cards as SVGs: the name card, the contribution heatmap, the
last twelve months in numbers, three highlight cards and the repos I'm working on.

The numbers come from GitHub's API each run (.github/workflows/cards.yml, daily). Paper cards,
an editorial serif (Instrument Serif, OFL, embedded so it renders inside an <img>), and one blue.
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
FIRST, LAST, ACCENT_AT = "Suyash", "Shukla", 3  # the letter of the last name in blue
BIO = (
    "I build AI products that do the work: RAG that cites its sources,",
    "voice agents that run your phone, and models that forecast attacks.",
)
SITE = "howsuyash.github.io"

HIGHLIGHTS = [  # (file, kicker, headline, text, background, ink)
    ("card-ship", "SHIP", "Quenaire, live",
     "AI SaaS that answers security questionnaires from a company's own docs. quenaire.com",
     "#1f3bff", "#ffffff"),
    ("card-hack", "HACK", "4th at HackIIITD",
     "Diplo, a Hindi voice agent that runs your phone. And SIH 2026 with AttackForecast.",
     "#e3122d", "#ffffff"),
    ("card-work", "WORK", "2 internships",
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


def font(name: str) -> str:
    return base64.b64encode((HERE / name).read_bytes()).decode()


FONTS = (
    "<style>"
    f"@font-face{{font-family:'Serif';src:url(data:font/ttf;base64,{font('InstrumentSerif-Regular.ttf')}) format('truetype')}}"
    f"@font-face{{font-family:'SerifItalic';src:url(data:font/ttf;base64,{font('InstrumentSerif-Italic.ttf')}) format('truetype')}}"
    ".s{font-family:'Serif',Georgia,serif}.i{font-family:'SerifItalic',Georgia,serif;font-style:italic}"
    f".m{{font-family:{MONO};letter-spacing:1.4px}}.t{{font-family:{SANS}}}"
    "</style>"
)


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def svg(width: int, height: int, body: list[str], label: str, paper: str | None = PAPER, border: str | None = BORDER) -> str:
    card = f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{paper}" stroke="{border}"/>' if paper else ""
    return "\n".join(
        [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">',
         FONTS, card, *body, "</svg>"]
    )


def kicker(x: float, y: float, text: str, fill: str = MUTED, dot: str | None = BLUE) -> str:
    square = f'<rect x="{x}" y="{y - 7}" width="6" height="6" fill="{dot}"/>' if dot else ""
    shift = 14 if dot else 0
    return square + f'<text class="m" x="{x + shift}" y="{y}" font-size="10" fill="{fill}">{esc(text)}</text>'


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
def hero() -> str:
    portrait = base64.b64encode((HERE / "portrait-ink.png").read_bytes()).decode()
    last = (esc(LAST[:ACCENT_AT]) + f'<tspan fill="{BLUE}">{esc(LAST[ACCENT_AT])}</tspan>' + esc(LAST[ACCENT_AT + 1:]))
    body = [
        f'<image x="560" y="34" width="250" height="250" href="data:image/png;base64,{portrait}"/>',
        kicker(40, 52, KICKER),
        f'<text class="s" x="36" y="138" font-size="84" fill="{INK}">{esc(FIRST)}</text>',
        f'<text class="i" x="38" y="214" font-size="84" fill="{INK}">{last}</text>',
        *[f'<text class="t" x="40" y="{252 + 21 * n}" font-size="14" fill="{BODY}">{esc(line)}</text>' for n, line in enumerate(BIO)],
        f'<text class="m" x="40" y="{252 + 21 * len(BIO) + 18}" font-size="10" fill="{INK}">{esc(SITE)}  ↗</text>',
    ]
    return svg(W, 330, body, f"{FIRST} {LAST}")


def heatmap(cal: dict) -> str:
    weeks = cal["weeks"]
    left, top = 40, 88
    step = (W - 2 * left) / len(weeks)
    cell = step * 0.78
    body = [
        f'<text class="s" x="40" y="62" font-size="30" fill="{INK}">Every day, <tspan class="i" fill="{BLUE}">in blue</tspan></text>',
        f'<text class="m" x="{W - 40}" y="58" font-size="9" fill="{FAINT}" text-anchor="end">REFRESHED DAILY</text>',
    ]
    last_month = None
    for i, week in enumerate(weeks):
        first = datetime.date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and i < len(weeks) - 2:
            if last_month is not None or first.day <= 7:
                body.append(f'<text class="m" x="{left + i * step:.1f}" y="{top + 7 * step + 16:.1f}" font-size="9" fill="{FAINT}">{first:%b}</text>')
            last_month = first.month
        for day in week["contributionDays"]:
            n = day["contributionCount"]
            date = datetime.date.fromisoformat(day["date"])
            body.append(
                f'<rect x="{left + i * step:.1f}" y="{top + day["weekday"] * step:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" '
                f'fill="{HEAT[LEVEL.get(day["contributionLevel"], 0)]}"><title>{n} on {date:%d %b %Y}</title></rect>'
            )
    y = top + 7 * step + 38  # under the month names, so the last months keep theirs
    right = W - 40
    body.append(f'<text class="m" x="{right}" y="{y:.1f}" font-size="9" fill="{FAINT}" text-anchor="end">MORE</text>')
    start = right - 40 - 5 * 13
    for n, color in enumerate(HEAT):
        body.append(f'<rect x="{start + n * 13}" y="{y - 9:.1f}" width="10" height="10" rx="2" fill="{color}"/>')
    body.append(f'<text class="m" x="{start - 8}" y="{y:.1f}" font-size="9" fill="{FAINT}" text-anchor="end">LESS</text>')
    return svg(W, int(y + 26), body, f"{cal['totalContributions']} contributions in the last year")


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
    body = [
        kicker(40, 50, "THE LAST 12 MONTHS ON GITHUB", dot=None),
        f'<text class="s" x="40" y="96" font-size="38" fill="{INK}">{n["total"]:,} <tspan class="i">contributions</tspan></text>',
    ]
    left, base, span, tall = 40, 222, 480, 92
    slot = span / len(n["months"])
    top = max((v for _, v in n["months"]), default=0) or 1
    best = max(n["months"], key=lambda m: m[1])[0] if n["months"] else None
    for i, ((year, month), value) in enumerate(n["months"]):
        h = max(2, tall * value / top)
        x = left + i * slot
        color = BLUE if (year, month) == best and value else (THIS_MONTH if (year, month) == n["this_month"] else PAST_MONTH)
        body.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{slot * .72:.1f}" height="{h:.1f}" fill="{color}"><title>{value} in {datetime.date(year, month, 1):%B %Y}</title></rect>')
        if (year, month) == best and value:
            body.append(f'<text class="m" x="{x + slot * .36:.1f}" y="{base - h - 6:.1f}" font-size="8" fill="{BLUE}" text-anchor="middle">{value:,}</text>')
        body.append(f'<text class="m" x="{x + slot * .36:.1f}" y="{base + 16}" font-size="8" fill="{FAINT}" text-anchor="middle">{datetime.date(year, month, 1):%b}</text>')

    x = 590
    streak = "current streak, and the longest" if n["current"] == n["longest"] else f"current streak · longest {n['longest']}"
    rows = [
        (f'{n["current"]} <tspan class="i">day{"s" if n["current"] != 1 else ""}</tspan>', streak),
        (f'{n["active"]} <tspan fill="{FAINT}">/ {n["days"]}</tspan>', "days with a commit"),
        (f'{n["busiest"]}', "on the busiest day"),
    ]
    for k, (big, small) in enumerate(rows):
        y = 84 + k * 68
        body.append(f'<text class="s" x="{x}" y="{y}" font-size="30" fill="{INK}">{big}</text>')
        body.append(f'<text class="t" x="{x}" y="{y + 18}" font-size="11" fill="{MUTED}">{esc(small)}</text>')
        if k < len(rows) - 1:
            body.append(f'<line x1="{x}" y1="{y + 34}" x2="{W - 40}" y2="{y + 34}" stroke="{RULE}"/>')
    return svg(W, 262, body, f"{n['total']} contributions in the last 12 months")


def highlight(kick: str, headline: str, text: str, bg: str, ink: str) -> str:
    lines = textwrap.wrap(text, 40)[:3]
    soft = "rgba(255,255,255,0.78)" if ink == "#ffffff" else "rgba(22,23,29,0.72)"
    body = [
        f'<text class="m" x="22" y="32" font-size="9" fill="{ink}">{esc(kick)}</text>',
        f'<text class="t" x="250" y="33" font-size="14" fill="{ink}" text-anchor="end">→</text>',
        f'<text class="i" x="22" y="98" font-size="31" fill="{ink}">{esc(headline)}</text>',
        *[f'<text class="t" x="22" y="{126 + 16 * k}" font-size="11.5" fill="{soft}">{esc(line)}</text>' for k, line in enumerate(lines)],
    ]
    return svg(272, 180, body, headline, paper=bg, border=bg)


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


def repo_card(repo: dict) -> str:
    lines = textwrap.wrap(repo.get("description") or "", 42)[:3]
    if len(textwrap.wrap(repo.get("description") or "", 42)) > 3:
        lines[-1] = lines[-1].rstrip(".,; ") + "…"
    meta = "  ·  ".join(x for x in [repo.get("language") or "", f"★ {repo['stargazers_count']}", ago(repo["pushed_at"])] if x)
    body = [
        f'<circle cx="25" cy="31" r="3.5" fill="{BLUE}"/>',
        f'<text class="m" x="36" y="35" font-size="11" fill="{INK}" style="letter-spacing:0.4px">{esc(repo["name"])}</text>',
        *[f'<text class="t" x="22" y="{62 + 17 * k}" font-size="11.5" fill="{MUTED}">{esc(line)}</text>' for k, line in enumerate(lines)],
        f'<text class="m" x="22" y="134" font-size="8.5" fill="{FAINT}" style="letter-spacing:0.6px">{esc(meta)}</text>',
    ]
    return svg(272, 154, body, repo["name"])


def title(regular: str, italic: str, name: str) -> str:
    body = [f'<text class="s" x="2" y="38" font-size="30" fill="#8b8f98">{esc(regular)}<tspan class="i">{esc(italic)}</tspan></text>']
    return svg(W, 52, body, regular + italic, paper=None)


def main() -> None:
    user, out = sys.argv[1], Path(sys.argv[2])
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
    out.mkdir(parents=True, exist_ok=True)
    cal = calendar(token, user)
    cards = {"hero": hero(), "heatmap": heatmap(cal), "stats": stats(cal), "coding": title("What I’m ", "coding", "coding")}
    for name, kick, headline, text, bg, ink in HIGHLIGHTS:
        cards[name] = highlight(kick, headline, text, bg, ink)
    for name in REPOS:
        cards[f"repo-{name}"] = repo_card(api(token, f"/repos/{user}/{name}"))
    for name, content in cards.items():
        (out / f"{name}.svg").write_text(content, encoding="utf-8")
    print("wrote", ", ".join(sorted(cards)))


if __name__ == "__main__":
    main()
