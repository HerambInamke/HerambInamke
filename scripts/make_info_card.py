"""Neofetch-style info card -> info-card.svg. Edit LINES to change content. STATIC=1 for a frozen frame."""
import os
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
KEY, VAL, DIM, ACC = "#39d353", "#c9d1d9", "#7d8590", "#58a6ff"

# (key, value); key None = section header, ("", "") = blank line
LINES = [
    ("heramb", "@github"),
    (None, "-" * 34),
    ("Role", "Software Engineer · FinOps · Full Stack"),
    ("FDE", "Forward Deployed Engineer"),
    ("Now", "Atomity GmbH — FinOps Engineering"),
    ("Prev", "DevQor Tech · IISPPR (Team Lead)"),
    ("Edu", "B.Tech CSE · MIT ADT · Kalvium"),
    ("", ""),
    ("Lang", "TypeScript · Python · Java · C++"),
    ("Backend", "Node · Express · FastAPI · Spring"),
    ("Frontend", "React · Next.js · Angular"),
    ("Data", "PostgreSQL · MongoDB · Redis"),
    ("Cloud", "AWS · Docker · Nginx · Actions"),
    ("Focus", "Distributed systems · AI apps"),
    ("", ""),
    ("Repos", "100+ public · 10+ prod apps"),
    ("OSS", "GSSoC · Hacktoberfest · C4GT"),
    ("Hacks", "1st Kod-E-Thon '25 · 3rd Udaan '25"),
    ("", ""),
    ("LinkedIn", "in/herambinamke1501"),
    ("Mail", "heramb15012006@gmail.com"),
]

W, LH, PAD, KW = 490, 21, 22, 92
H = PAD * 2 + 26 + LH * len(LINES) + 24
static = os.environ.get("STATIC") == "1"

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13">',
       "<style>.l{animation:in .35s ease-out both}"
       "@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}</style>"
       if not static else "",
       f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
       *(f'<circle cx="{PAD + i * 16}" cy="{PAD}" r="5" fill="{c}"/>'
         for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f"))),
       f'<text x="{W / 2}" y="{PAD + 4}" fill="{DIM}" text-anchor="middle" font-size="12">heramb@github: ~</text>']

for i, (k, v) in enumerate(LINES):
    y = PAD + 26 + LH * (i + 1) - 6
    attr = "" if static else f' class="l" style="animation-delay:{0.6 + i * 0.09:.2f}s"'
    if i == 0:
        body = f'<tspan fill="{ACC}" font-weight="bold">{k}</tspan><tspan fill="{VAL}">{escape(v)}</tspan>'
    elif k is None:
        body = f'<tspan fill="{DIM}">{v}</tspan>'
    elif not k:
        continue
    else:
        body = f'<tspan fill="{KEY}" font-weight="bold">{k}</tspan><tspan x="{PAD + KW}" fill="{VAL}">{escape(v)}</tspan>'
    out.append(f'<text x="{PAD}" y="{y}"{attr}>{body}</text>')

palette_y = H - PAD + 2
out += [f'<rect x="{PAD + i * 22}" y="{palette_y - 12}" width="18" height="10" rx="2" fill="{c}"/>'
        for i, c in enumerate(("#ff7b72", "#ffa657", "#d2a8ff", "#58a6ff", "#39d353", "#c9d1d9"))]
out.append("</svg>")
OUT.write_text("\n".join(x for x in out if x), encoding="utf-8")
print(f"wrote {OUT.name} ({W}x{H})")
