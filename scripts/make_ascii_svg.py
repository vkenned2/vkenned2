#!/usr/bin/env python3
"""
make_ascii_svg.py
Converts prepped photo (source-prepped.png) into an animated SVG ASCII portrait.
Uses ONLY inline SVG presentation attributes + native SMIL <animate> elements.
No CSS classes — GitHub strips <style> blocks when serving SVGs via <img>.
Output: vishal-ascii.svg
"""

import sys
import os
from PIL import Image

RAMP = " .`:-=+*cs#%@"

# Colors — all inline
BG       = "#0d1117"
BG2      = "#111722"
TITLEBAR = "#161b22"
BORDER   = "#30363d"
TEXT     = "#c9d1d9"
BRIGHT   = "#e6edf3"
MUTED    = "#7d8590"
GREEN    = "#39d353"
CYAN     = "#22d3ee"
RED      = "#ff5f56"
YELLOW   = "#ffbd2e"
BTNGRN   = "#27c93f"

MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def generate_placeholder_ascii(cols=62, rows=26):
    """Stylized ASCII placeholder when source-prepped.png is not available."""
    art = [
        "     .----------------------------------------------.     ",
        "    /   __________________________________________   \\    ",
        "   |   |                                          |   |   ",
        "   |   |   ___  ___  ___  ___  _  _  __   ___   |   |   ",
        "   |   |  | \\/ || __||   || \\/ || |/ / | | \\  \\  |   |   ",
        "   |   |  | || || |_ | _ ||    || |< <  | |  \\ \\ |   |   ",
        "   |   |  |_||_||___||___||_/\\_||_|\\_\\ |_|  /_/ |   |   ",
        "   |   |                                          |   |   ",
        "   |   |   PhD Candidate @ Univ. of Tennessee    |   |   ",
        "   |   |   Energy & Environmental Policy         |   |   ",
        "   |   |   Knoxville, Tennessee                  |   |   ",
        "   |   |__________________________________________|   |   ",
        "    \\_________________________________________________/   ",
        "                         |   |                            ",
        "                      .----+----.                         ",
        "                     / RESEARCHER \\                       ",
        "                    / GIS | POLICY \\                      ",
        "                   /  DATA | AI | ML \\                    ",
        "                  '-------------------'                   ",
        "           .-----------------------------------------.    ",
        "          / Energy · Conservation · Evidence Policy  \\   ",
        "         '-------------------------------------------'    ",
        "                                                           ",
        "          [ vkenned2 ] [ UTK Knoxville ] [ 2022-2027 ]    ",
        "                                                           ",
        "              Source photo not yet processed.             ",
    ]
    pad_cols = cols
    lines = []
    for line in art:
        if len(line) < pad_cols:
            line = line + " " * (pad_cols - len(line))
        elif len(line) > pad_cols:
            line = line[:pad_cols]
        lines.append(line)
    while len(lines) < rows:
        lines.append(" " * pad_cols)
    return lines[:rows]


def image_to_ascii(img_path: str, cols=68, rows=30):
    if not os.path.exists(img_path):
        return None
    try:
        img = Image.open(img_path).convert("L")
    except Exception as e:
        print(f"Error opening prepped photo: {e}", file=sys.stderr)
        return None

    img_w, img_h = img.size
    # Monospace chars are ~0.55 as wide as tall → compensate aspect
    aspect      = (img_h / img_w) * 0.52
    target_h    = min(rows, int(cols * aspect))

    img_resized = img.resize((cols, target_h), Image.Resampling.LANCZOS)
    pixels      = list(img_resized.getdata())
    ramp_len    = len(RAMP)

    ascii_lines = []
    for r in range(target_h):
        row_chars = []
        for c in range(cols):
            val = pixels[r * cols + c]
            if val > 230:
                ch = " "
            else:
                idx = int((255 - val) / 255.0 * (ramp_len - 1))
                ch = RAMP[max(0, min(idx, ramp_len - 1))]
            row_chars.append(ch)
        ascii_lines.append("".join(row_chars))

    return ascii_lines


def render_ascii_svg(ascii_lines: list, output_path: str):
    W = 370
    font_size   = 6.8
    line_height = 8.2
    x_start     = 14
    y_start     = 50

    num_rows = len(ascii_lines)

    # Dynamic height: fit all rows + title bar + status bar
    content_h = y_start + num_rows * line_height + 4
    status_h  = 26
    H = int(content_h + status_h + 8)
    H = max(H, 320)

    status_y = H - status_h - 4

    out = []

    # ── SVG root ──────────────────────────────────────────────────────────────
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    out.append('<defs>')
    out.append(f'  <linearGradient id="abg" x1="0%" y1="0%" x2="100%" y2="100%">')
    out.append(f'    <stop offset="0%"   stop-color="{BG}"/>')
    out.append(f'    <stop offset="100%" stop-color="{BG2}"/>')
    out.append(f'  </linearGradient>')
    out.append('</defs>')

    # ── Main window ───────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" ry="10" '
               f'fill="url(#abg)" stroke="{BORDER}" stroke-width="1.5"/>')

    # ── Title bar ─────────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="0" width="{W}" height="32" rx="10" ry="10" '
               f'fill="{TITLEBAR}" stroke="{BORDER}" stroke-width="1"/>')
    out.append(f'<rect x="0" y="20" width="{W}" height="12" fill="{TITLEBAR}"/>')
    out.append(f'<line x1="0" y1="32" x2="{W}" y2="32" stroke="{BORDER}" stroke-width="1"/>')

    # Window dots
    out.append(f'<circle cx="16" cy="16" r="5.5" fill="{RED}"/>')
    out.append(f'<circle cx="33" cy="16" r="5.5" fill="{YELLOW}"/>')
    out.append(f'<circle cx="50" cy="16" r="5.5" fill="{BTNGRN}"/>')

    # Title text — inline fills
    out.append(f'<text y="21" font-family={MONO!r} font-size="11" font-weight="600">')
    out.append(f'  <tspan x="67" fill="{GREEN}">vkenned2@github</tspan>'
               f'<tspan fill="{TEXT}">:</tspan>'
               f'<tspan fill="{CYAN}">~$</tspan>'
               f'<tspan fill="{TEXT}"> ./portrait.sh</tspan>')
    out.append('</text>')

    # ── ASCII rows — inline fill, xml:space, SMIL animate ────────────────────
    for idx, line in enumerate(ascii_lines):
        y     = y_start + idx * line_height
        delay = round(0.04 + idx * 0.018, 3)
        # Escape XML special chars
        escaped = (line
                   .replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;"))
        out.append(
            f'<text x="{x_start}" y="{y:.1f}" '
            f'xml:space="preserve" '
            f'font-family={MONO!r} '
            f'font-size="{font_size}" '
            f'fill="{GREEN}">'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'dur="0.22s" begin="{delay}s" fill="freeze"/>'
            f'{escaped}</text>'
        )

    # ── Status bar ────────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="{status_y}" width="{W}" height="{H - status_y}" '
               f'rx="0" fill="{TITLEBAR}" stroke="{BORDER}" stroke-width="1"/>')
    # Round bottom corners
    out.append(f'<rect x="0" y="{status_y}" width="{W}" height="4" fill="{TITLEBAR}"/>')
    out.append(f'<rect x="0" y="{H - 10}" width="{W}" height="10" rx="6" fill="{TITLEBAR}"/>')

    prompt_y = status_y + 17
    out.append(f'<text y="{prompt_y}" font-family={MONO!r} font-size="11" font-weight="600">')
    out.append(f'  <tspan x="12" fill="{GREEN}">vkenned2@github</tspan>'
               f'<tspan fill="{TEXT}">:</tspan>'
               f'<tspan fill="{CYAN}">~$</tspan>'
               f'<tspan fill="{MUTED}"> whoami </tspan>'
               f'<tspan fill="{BRIGHT}" font-weight="800">Vishal Kennedy</tspan>')
    out.append('</text>')

    # Blinking cursor
    cursor_x = 246
    out.append(f'<rect x="{cursor_x}" y="{prompt_y - 11}" width="6" height="12" fill="{GREEN}">')
    out.append('  <animate attributeName="opacity" values="1;0;1" '
               'dur="1.1s" repeatCount="indefinite"/>')
    out.append('</rect>')

    out.append('</svg>')

    svg = "\n".join(out)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated ASCII portrait SVG: {output_path} ({len(ascii_lines)} rows, height={H})")


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    prepped = os.path.join(base, "source-prepped.png")
    output  = os.path.join(base, "vishal-ascii.svg")

    if len(sys.argv) > 1:
        prepped = sys.argv[1]
    if len(sys.argv) > 2:
        output  = sys.argv[2]

    ascii_lines = image_to_ascii(prepped, cols=68, rows=30)

    if not ascii_lines:
        print(f"Note: {prepped} not found — generating stylized placeholder...",
              file=sys.stderr)
        ascii_lines = generate_placeholder_ascii(cols=62, rows=26)

    render_ascii_svg(ascii_lines, output)


if __name__ == "__main__":
    main()
