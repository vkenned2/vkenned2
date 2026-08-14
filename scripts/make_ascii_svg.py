#!/usr/bin/env python3
"""
make_ascii_svg.py
Converts prepped photo (source-prepped.png) or a stylized fallback placeholder into an animated SVG ASCII portrait.
Output: vishal-ascii.svg
"""

import sys
import os
from PIL import Image

RAMP = " .`:-=+*cs#%@"

def generate_placeholder_ascii(cols=60, rows=34):
    """
    Generates a stylized, high-quality ASCII terminal avatar placeholder for Vishal Kennedy
    when source-photo.jpg is not yet provided.
    """
    lines = []
    
    avatar_art = [
        "       .-------------------------------------------.       ",
        "      /   _______________________________________   \\      ",
        "     |   |                                       |   |     ",
        "     |   |    _____   _____     __  __ _  ___    |   |     ",
        "     |   |   /  _  \\ /  _  \\   |  |/  | |/   |   |   |     ",
        "     |   |   | |_| | | |_| |   |  '  /| ' /| |   |   |     ",
        "     |   |   |  _  | |  _  |   |    < |  < | |   |   |     ",
        "     |   |   |_| |_| |_| |_|   |__|\\_\\|__|\\|_|   |   |     ",
        "     |   |                                       |   |     ",
        "     |   |        [ VISHAL KENNEDY PROFILE ]     |   |     ",
        "     |   |_______________________________________|   |     ",
        "      \\_____________________________________________/      ",
        "                           |   |                           ",
        "                        .--;---;--.                        ",
        "                       /  [ONLINE] \\                       ",
        "                      /  UTK ECOLOGY\\                      ",
        "                     /  POLICY+DATA  \\                     ",
        "                    '-----------------'                    ",
        "             .---------------------------------.           ",
        "            /  researcher @ energy + enviro    \\          ",
        "           /   gis | spatial analysis | ai      \\         ",
        "          '---------------------------------------'        "
    ]

    # Center lines inside grid
    for line in avatar_art:
        pad_left = (cols - len(line)) // 2
        pad_right = cols - len(line) - pad_left
        lines.append(" " * max(0, pad_left) + line + " " * max(0, pad_right))

    while len(lines) < rows:
        lines.append(" " * cols)

    return lines[:rows]

def image_to_ascii(img_path: str, cols=70, rows=42):
    if not os.path.exists(img_path):
        return None

    try:
        img = Image.open(img_path).convert("L")
    except Exception as e:
        print(f"Error opening prepped photo: {e}", file=sys.stderr)
        return None

    # Aspect ratio adjustment (font chars are ~ 2:1 height to width)
    img_w, img_h = img.size
    aspect = (img_h / img_w) * 0.55
    target_h = int(cols * aspect)
    if target_h > rows:
        target_h = rows

    img_resized = img.resize((cols, target_h), Image.Resampling.LANCZOS)
    pixels = img_resized.getdata()

    ascii_lines = []
    ramp_len = len(RAMP)

    for r in range(target_h):
        line_chars = []
        for c in range(cols):
            val = pixels[r * cols + c]
            # Map white/near-white (>240) to space
            if val > 235:
                char = " "
            else:
                idx = int((255 - val) / 255.0 * (ramp_len - 1))
                char = RAMP[idx]
            line_chars.append(char)
        ascii_lines.append("".join(line_chars))

    return ascii_lines

def render_ascii_svg(ascii_lines, output_path: str):
    width = 370
    height = 360

    # Determine font size and line height based on grid size
    num_rows = len(ascii_lines)
    num_cols = max(len(l) for l in ascii_lines) if ascii_lines else 1

    font_size = 7.2
    line_height = 8.5
    y_start = 54
    x_start = 16

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="asciiBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#111722" />
    </linearGradient>
    <filter id="asciiShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.5" />
    </filter>
  </defs>

  <style>
    .window {{
      fill: url(#asciiBg);
      stroke: #30363d;
      stroke-width: 1px;
      rx: 10px;
      ry: 10px;
    }}
    .title-bar {{
      fill: #161b22;
      stroke: #30363d;
      stroke-width: 1px;
    }}
    .title-text {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 12px;
      font-weight: 600;
      fill: #c9d1d9;
    }}
    .prompt-user {{ fill: #39d353; }}
    .prompt-path {{ fill: #22d3ee; }}
    .ascii-text {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: {font_size}px;
      fill: #39d353;
      white-space: pre;
    }}
    .status-bar {{
      fill: #161b22;
      stroke: #30363d;
      stroke-width: 1px;
    }}
    .status-text {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 11px;
      fill: #c9d1d9;
    }}
    .cursor {{
      fill: #39d353;
      animation: blink 1s step-end infinite;
    }}
    .ascii-row {{
      opacity: 0;
      animation: revealRow 0.25s ease-out forwards;
    }}
    @keyframes revealRow {{
      0% {{
        opacity: 0;
        transform: translateX(-4px);
      }}
      100% {{
        opacity: 1;
        transform: translateX(0);
      }}
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .ascii-row {{
        opacity: 1 !important;
        animation: none !important;
      }}
      .cursor {{
        animation: none !important;
        opacity: 1 !important;
      }}
    }}
  </style>

  <!-- Terminal Window -->
  <rect x="2" y="2" width="{width - 4}" height="{height - 4}" class="window" filter="url(#asciiShadow)" />

  <!-- Title Bar -->
  <path d="M 2 12 Q 2 2 12 2 L {width - 12} 2 Q {width - 2} 2 {width - 2} 12 L {width - 2} 34 L 2 34 Z" class="title-bar" />

  <!-- Window Controls -->
  <circle cx="18" cy="18" r="5.5" fill="#ff5f56" />
  <circle cx="36" cy="18" r="5.5" fill="#ffbd2e" />
  <circle cx="54" cy="18" r="5.5" fill="#27c93f" />

  <!-- Window Title -->
  <text x="74" y="22" class="title-text">
    <tspan class="prompt-user">vkenned2@github</tspan>:<tspan class="prompt-path">~$</tspan> ./portrait.sh
  </text>

  <!-- ASCII Portrait Content -->''')

    for idx, line in enumerate(ascii_lines):
        y_pos = y_start + idx * line_height
        delay = round(0.05 + idx * 0.02, 3)
        # Escape HTML entities in ASCII text
        escaped_line = (
            line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
        )
        svg_parts.append(
            f'  <text x="{x_start}" y="{y_pos}" class="ascii-text ascii-row" style="animation-delay: {delay}s;">{escaped_line}</text>'
        )

    # Bottom status bar
    status_y = height - 28
    svg_parts.append(f'''
  <!-- Bottom Status Bar -->
  <path d="M 2 {status_y} L {width - 2} {status_y} L {width - 2} {height - 12} Q {width - 2} {height - 2} {width - 12} {height - 2} L 12 {height - 2} Q 2 {height - 2} 2 {height - 12} Z" class="status-bar" />

  <text x="14" y="{status_y + 18}" class="status-text">
    <tspan class="prompt-user">vkenned2@github</tspan>:<tspan class="prompt-path">~$</tspan> whoami <tspan fill="#e6edf3" font-weight="bold">Vishal Kennedy</tspan>
  </text>
  <rect x="272" y="{status_y + 7}" width="7" height="13" class="cursor" />
</svg>''')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))

    print(f"Successfully generated ASCII portrait SVG at {output_path}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prepped_photo = os.path.join(base_dir, "source-prepped.png")
    output_svg = os.path.join(base_dir, "vishal-ascii.svg")

    if len(sys.argv) > 1:
        prepped_photo = sys.argv[1]
    if len(sys.argv) > 2:
        output_svg = sys.argv[2]

    ascii_lines = image_to_ascii(prepped_photo, cols=68, rows=32)

    if not ascii_lines:
        print(f"Note: {prepped_photo} not found. Generating stylized terminal placeholder ASCII for Vishal Kennedy...")
        ascii_lines = generate_placeholder_ascii(cols=60, rows=22)

    render_ascii_svg(ascii_lines, output_svg)

if __name__ == "__main__":
    main()
