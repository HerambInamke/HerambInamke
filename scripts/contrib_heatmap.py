"""Scrape the public contribution calendar and render contrib-heatmap.svg. Stdlib only."""
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path

USER = "HerambInamke"
OUT = Path(__file__).resolve().parent.parent / "assets" / "contrib-heatmap.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP, LEFT, TOP = 12, 3, 34, 22
PITCH = CELL + GAP


def fetch():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": "profile-heatmap"})
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    counts = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"([\d,]+) contribution", text)
        counts[cid] = int(m.group(1).replace(",", "")) if m else 0
    days = []
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', td))
        if "data-date" not in a:
            continue
        row, col = map(int, a["id"].rsplit("-", 2)[1:])
        days.append({"date": a["data-date"], "level": int(a["data-level"]),
                     "count": counts.get(a["id"], 0), "row": row, "col": col})
    if not days:
        raise SystemExit("no contribution cells found; GitHub markup changed")
    return sorted(days, key=lambda d: d["date"])


def stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["count"]:
            current += 1
        elif current or d["date"] != date.today().isoformat():  # today may still be empty
            break
    return total, best, longest, current


def render(days):
    total, best, longest, current = stats(days)
    cols = max(d["col"] for d in days) + 1
    w, h = 860, TOP + 7 * PITCH + 56
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
           "<style>.c{animation:drop .45s cubic-bezier(.2,.8,.2,1) both}"
           "@keyframes drop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
           ".t{fill:#7d8590;font-size:11px}.s{fill:#c9d1d9;font-size:12px}.g{fill:#39d353}</style>",
           f'<rect width="{w}" height="{h}" rx="10" fill="#0d1117"/>']
    for d in days:
        if d["row"] == 0 and int(d["date"][8:]) <= 7 and d["col"] < cols - 2:  # first week of a month
            out.append(f'<text class="t" x="{LEFT + d["col"] * PITCH}" y="{TOP - 7}">'
                       f'{date.fromisoformat(d["date"]).strftime("%b")}</text>')
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text class="t" x="4" y="{TOP + row * PITCH + 10}">{name}</text>')
    for d in days:
        delay = (d["col"] + d["row"]) * 0.018
        out.append(f'<rect class="c" x="{LEFT + d["col"] * PITCH}" y="{TOP + d["row"] * PITCH}" '
                   f'width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[d["level"]]}" '
                   f'style="animation-delay:{delay:.3f}s"><title>{d["count"]} on {d["date"]}</title></rect>')
    y = TOP + 7 * PITCH + 24
    out.append(f'<text class="s" x="{LEFT}" y="{y}"><tspan class="g">{total:,}</tspan> contributions in the last year'
               f'  ·  streak <tspan class="g">{current}d</tspan>  ·  longest <tspan class="g">{longest}d</tspan>'
               f'  ·  best day <tspan class="g">{best["count"]}</tspan></text>')
    lx = LEFT + cols * PITCH - 5 * PITCH - 64
    out.append(f'<text class="t" x="{lx}" y="{y + 22}">Less</text>')
    for i, c in enumerate(PALETTE):
        out.append(f'<rect x="{lx + 32 + i * PITCH}" y="{y + 12}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    out.append(f'<text class="t" x="{lx + 36 + 5 * PITCH}" y="{y + 22}">More</text></svg>')
    OUT.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    days = fetch()
    # self-check: consecutive dates, 7 rows
    assert all(date.fromisoformat(b["date"]) - date.fromisoformat(a["date"]) == timedelta(days=1)
               for a, b in zip(days, days[1:])), "gap in calendar"
    assert {d["row"] for d in days} <= set(range(7))
    render(days)
    print(f"wrote {OUT.name}: {len(days)} days")
