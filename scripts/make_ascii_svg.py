"""Photo -> self-typing monochrome ASCII portrait (ascii-portrait.svg). Run locally when the photo changes:
    pip install pillow numpy "rembg[cpu]"   # rembg optional: clean background cut-out
    python scripts/make_ascii_svg.py photo.jpg
"""
import sys
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent.parent / "ascii-portrait.svg"
RAMP = " .`:-=+*cs#%@"  # dark (blank) -> bright (dense); panel is dark so this reads as a positive image
COLS, CHAR_ASPECT = 100, 0.5  # monospace glyph width / line height
W = 370
FILL, BG = "#c9d1d9", "#0d1117"


def prep(path):
    img = Image.open(path).convert("RGB")
    try:
        from rembg import remove
        alpha = np.asarray(remove(img))[..., 3] / 255.0  # isolate the subject
    except ImportError:
        # shortcut: soft oval around the subject instead of segmentation; install rembg for a clean cut-out
        h, w = img.height, img.width
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.hypot((xx - w * 0.55) / (w * 0.40), (yy - h * 0.36) / (h * 0.40))  # tuned for a centred head shot
        alpha = np.clip((1.0 - d) / 0.12, 0, 1)
    gray = np.asarray(ImageOps.equalize(img.convert("L")), dtype=float)  # stretch contrast for flat faces
    return (gray * alpha).astype(np.uint8)  # background -> black -> spaces


def to_rows(gray):
    h, w = gray.shape
    rows = round(COLS * h / w * CHAR_ASPECT)
    small = np.asarray(Image.fromarray(gray).resize((COLS, rows), Image.LANCZOS), dtype=float)
    idx = (small / 256 * len(RAMP)).astype(int)
    return ["".join(RAMP[i] for i in r).rstrip() for r in idx]


def render(lines):
    cw = W / COLS  # x advance per char, enforced via textLength
    lh = cw / CHAR_ASPECT
    fs = cw / 0.6  # 0.6 = typical monospace advance / em
    pad = 12
    h = round(len(lines) * lh + pad * 2)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">',
           f'<rect width="{W}" height="{h}" rx="10" fill="{BG}"/>',
           f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{fs:.2f}" '
           f'fill="{FILL}" xml:space="preserve">']
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = pad + (i + 1) * lh
        t0, dur = 0.3 + i * 0.05, 0.35
        out.append(f'<clipPath id="r{i}"><rect x="0" y="{y - lh:.2f}" width="0" height="{lh + 1:.2f}">'
                   f'<animate attributeName="width" from="0" to="{W}" begin="{t0:.2f}s" dur="{dur}s" fill="freeze"/>'
                   f'</rect></clipPath>'
                   f'<text x="0" y="{y - lh * 0.2:.2f}" textLength="{len(line) * cw:.2f}" lengthAdjust="spacingAndGlyphs" '
                   f'clip-path="url(#r{i})">{escape(line)}</text>')
    out.append("</g></svg>")
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT.name} ({W}x{h}, {len(lines)} rows)")


if __name__ == "__main__":
    lines = to_rows(prep(sys.argv[1]))
    assert lines and all(len(l) <= COLS for l in lines)
    render(lines)
