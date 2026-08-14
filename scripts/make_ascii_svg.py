#!/usr/bin/env python3
"""
make_ascii_svg.py  —  Deep Navy × Sky Blue × Gold premium theme
GitHub-safe: inline SVG attributes + SMIL <animate>, no CSS classes.
Output: vishal-ascii.svg
"""
import sys
import os
from PIL import Image

RAMP = " .`:-=+*cs#%@"

MONO  = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
BG1   = "#040d18"
BG2   = "#0a1628"
BAR   = "#060e1e"
BDR   = "#1a3452"
TEXT  = "#c0d4e8"
BRIGHT= "#e8f4ff"
MUTED = "#4a6a8a"
BLUE  = "#38bdf8"
CYAN  = "#22d3ee"
GOLD  = "#f59e0b"
RED   = "#ff5f56"
YELL  = "#ffbd2e"
GRND  = "#27c93f"


def placeholder_ascii(cols=62, rows=24):
    art = [
        "    .------------------------------------------------.   ",
        "   /                                                  \\  ",
        "  |   ____   ____  __  ____   _   _  __   __          | ",
        "  |  |    \\ |    ||  ||    \\ | |_| ||  \\ /  |         | ",
        "  |  |  |) || || ||  ||  |) ||  _  ||   v   |         | ",
        "  |  |____/ |____||__||____/ |_| |_||_|   |_|         | ",
        "  |                                                    | ",
        "  |         PhD Candidate · Policy Analyst             | ",
        "  |         University of Tennessee · Knoxville        | ",
        "  |                                                    | ",
        "  |  .------------------------------------------------.| ",
        "  |  | Energy + Environmental Policy                   || ",
        "  |  | Geospatial Analysis · Conservation · AI         || ",
        "  |  | Python · R · JavaScript · SQL                   || ",
        "  |  '------------------------------------------------'| ",
        "  |                                                    | ",
        "  |    [  Add source-photo.jpg to generate your        | ",
        "  |       personalized ASCII portrait  ]               | ",
        "  |                                                    | ",
        "   \\                                                  /  ",
        "    '------------------------------------------------'   ",
        "                                                          ",
        "         vkenned2 · github.com/vkenned2                  ",
        "                                                          ",
    ]
    lines = []
    for ln in art:
        if len(ln) < cols:
            ln = ln + " " * (cols - len(ln))
        lines.append(ln[:cols])
    while len(lines) < rows:
        lines.append(" " * cols)
    return lines[:rows]


def image_to_ascii(img_path: str, cols=68, rows=30):
    if not os.path.exists(img_path):
        return None
    try:
        img = Image.open(img_path).convert("L")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

    img_w, img_h = img.size
    target_h = min(rows, int(cols * (img_h / img_w) * 0.52))
    img_r = img.resize((cols, target_h), Image.Resampling.LANCZOS)
    px = list(img_r.getdata())
    rlen = len(RAMP)

    lines = []
    for r in range(target_h):
        row = []
        for c in range(cols):
            v = px[r * cols + c]
            if v > 230:
                row.append(" ")
            else:
                row.append(RAMP[max(0, min(int((255 - v) / 255.0 * (rlen - 1)), rlen - 1))])
        lines.append("".join(row))
    return lines


def render_ascii_svg(ascii_lines: list, out_path: str):
    W           = 370
    fs          = 6.8   # font-size
    lh          = 8.2   # line-height
    x0          = 14
    y0          = 48
    num_rows    = len(ascii_lines)
    content_h   = y0 + num_rows * lh + 4
    status_h    = 28
    H           = max(320, int(content_h + status_h + 8))
    status_y    = H - status_h - 4
    prompt_y    = status_y + 19

    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # Defs
    o.append('<defs>')
    o.append(f'  <linearGradient id="abg" x1="0%" y1="0%" x2="100%" y2="100%">')
    o.append(f'    <stop offset="0%"   stop-color="{BG1}"/>')
    o.append(f'    <stop offset="100%" stop-color="{BG2}"/>')
    o.append(f'  </linearGradient>')
    o.append(f'  <linearGradient id="aacc" x1="0%" y1="0%" x2="100%" y2="0%">')
    o.append(f'    <stop offset="0%"   stop-color="#0369a1"/>')
    o.append(f'    <stop offset="100%" stop-color="{CYAN}"/>')
    o.append(f'  </linearGradient>')
    o.append('</defs>')

    # Window
    o.append(f'<rect width="{W}" height="{H}" rx="12" ry="12" '
             f'fill="url(#abg)" stroke="{BDR}" stroke-width="1.5"/>')

    # Title bar
    o.append(f'<rect width="{W}" height="34" rx="12" ry="12" fill="{BAR}"/>')
    o.append(f'<rect y="20" width="{W}" height="14" fill="{BAR}"/>')
    o.append(f'<line x1="0" y1="34" x2="{W}" y2="34" stroke="{BDR}" stroke-width="1"/>')

    # Dots
    o.append(f'<circle cx="18" cy="17" r="5" fill="{RED}"/>')
    o.append(f'<circle cx="35" cy="17" r="5" fill="{YELL}"/>')
    o.append(f'<circle cx="52" cy="17" r="5" fill="{GRND}"/>')

    # Title text
    o.append(f'<text y="22" font-family={MONO!r} font-size="11" font-weight="600">')
    o.append(f'  <tspan x="68" fill="{BLUE}">vkenned2</tspan>'
             f'<tspan fill="{MUTED}"> — </tspan>'
             f'<tspan fill="{TEXT}">portrait.sh</tspan>')
    o.append('</text>')

    # Accent strip
    o.append(f'<rect x="0" y="34" width="{W}" height="3" fill="url(#aacc)"/>')

    # ASCII rows — sky-blue tint
    for idx, line in enumerate(ascii_lines):
        y     = y0 + idx * lh
        delay = round(0.04 + idx * 0.016, 3)
        esc   = (line
                 .replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;"))
        o.append(
            f'<text x="{x0}" y="{y:.1f}" '
            f'xml:space="preserve" '
            f'font-family={MONO!r} '
            f'font-size="{fs}" '
            f'fill="{BLUE}">'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'dur="0.2s" begin="{delay}s" fill="freeze"/>'
            f'{esc}</text>'
        )

    # Status bar
    o.append(f'<rect x="0" y="{status_y}" width="{W}" height="{H - status_y}" '
             f'fill="{BAR}" stroke="{BDR}" stroke-width="1"/>')
    o.append(f'<rect x="0" y="{H - 10}" width="{W}" height="10" rx="6" fill="{BAR}"/>')

    # Status text
    o.append(f'<text y="{prompt_y}" font-family={MONO!r} font-size="11" font-weight="600">')
    o.append(f'  <tspan x="12" fill="{BLUE}">vkenned2</tspan>'
             f'<tspan fill="{MUTED}"> — </tspan>'
             f'<tspan fill="{TEXT}">whoami  </tspan>'
             f'<tspan fill="{GOLD}" font-weight="800">Vishal Kennedy</tspan>')
    o.append('</text>')

    # Cursor
    cur_x = 224
    o.append(f'<rect x="{cur_x}" y="{prompt_y - 11}" width="7" height="13" fill="{BLUE}">')
    o.append('  <animate attributeName="opacity" values="1;0;1" '
             'dur="1.1s" repeatCount="indefinite"/>')
    o.append('</rect>')

    o.append('</svg>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print(f"Generated ASCII portrait → {out_path}  ({num_rows} rows, H={H})")


def main():
    base    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prepped = os.path.join(base, "source-prepped.png")
    out     = os.path.join(base, "vishal-ascii.svg")
    if len(sys.argv) > 1: prepped = sys.argv[1]
    if len(sys.argv) > 2: out     = sys.argv[2]

    lines = image_to_ascii(prepped, cols=68, rows=30)
    if not lines:
        print(f"source-prepped.png not found — using placeholder", file=sys.stderr)
        lines = placeholder_ascii(cols=62, rows=24)

    render_ascii_svg(lines, out)

if __name__ == "__main__":
    main()
