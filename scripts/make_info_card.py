#!/usr/bin/env python3
"""
make_info_card.py
Generates an animated neofetch-style terminal info card for Vishal Kennedy.
Output: info-card.svg
"""

import os
import sys

def generate_info_card_svg(output_path: str):
    width = 490
    height = 360

    fields = [
        ("Role", "PhD Candidate | Policy Analyst"),
        ("Research", "Energy + Environmental Policy"),
        ("Focus", "Geospatial | Conservation | AI"),
        ("Stack", "Python | R | JavaScript | SQL"),
        ("Methods", "Spatial Analysis | Program Evaluation"),
        ("Building", "Evidence-to-decision systems"),
        ("Location", "Knoxville, Tennessee"),
        ("Education", "University of Tennessee, Knoxville"),
        ("Field", "Ecology + Energy & Environmental Policy"),
    ]

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="infoBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#111722" />
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.5" />
    </filter>
  </defs>

  <style>
    .window {{
      fill: url(#infoBg);
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
    .name-title {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 20px;
      font-weight: 800;
      fill: #e6edf3;
      letter-spacing: 1px;
    }}
    .label {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 11.5px;
      font-weight: 700;
      fill: #22d3ee;
    }}
    .value {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 11.5px;
      fill: #c9d1d9;
    }}
    .separator {{
      stroke: #30363d;
      stroke-width: 1px;
    }}
    .cursor {{
      fill: #39d353;
      animation: blink 1s step-end infinite;
    }}
    .anim-line {{
      opacity: 0;
      animation: fadeInLine 0.4s ease-out forwards;
    }}
    @keyframes fadeInLine {{
      from {{
        opacity: 0;
        transform: translateY(4px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .anim-line {{
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
  <rect x="2" y="2" width="{width - 4}" height="{height - 4}" class="window" filter="url(#cardShadow)" />

  <!-- Title Bar -->
  <path d="M 2 12 Q 2 2 12 2 L {width - 12} 2 Q {width - 2} 2 {width - 2} 12 L {width - 2} 34 L 2 34 Z" class="title-bar" />

  <!-- Window Controls -->
  <circle cx="18" cy="18" r="5.5" fill="#ff5f56" />
  <circle cx="36" cy="18" r="5.5" fill="#ffbd2e" />
  <circle cx="54" cy="18" r="5.5" fill="#27c93f" />

  <!-- Window Title -->
  <text x="74" y="22" class="title-text">
    <tspan class="prompt-user">vkenned2@github</tspan>:<tspan class="prompt-path">~$</tspan> neofetch
  </text>

  <!-- Header Identity -->
  <g class="anim-line" style="animation-delay: 0.05s;">
    <text x="24" y="62" class="name-title">VISHAL KENNEDY</text>
  </g>

  <!-- Separator Line -->
  <line x1="24" y1="74" x2="{width - 24}" y2="74" class="separator anim-line" style="animation-delay: 0.1s;" />

  <!-- Neofetch Details Grid -->'''

    y_start = 96
    y_step = 24
    
    for idx, (label, val) in enumerate(fields):
        y_pos = y_start + idx * y_step
        delay = round(0.15 + idx * 0.05, 2)
        svg_content += f'''
  <g class="anim-line" style="animation-delay: {delay}s;">
    <text x="24" y="{y_pos}">
      <tspan class="label">{label.ljust(10)}</tspan>
      <tspan fill="#7d8590">› </tspan>
      <tspan class="value">{val}</tspan>
    </text>
  </g>'''

    cursor_y = y_start + len(fields) * y_step + 10
    cursor_delay = round(0.15 + len(fields) * 0.05, 2)

    svg_content += f'''

  <!-- Bottom Command Prompt & Blinking Cursor -->
  <g class="anim-line" style="animation-delay: {cursor_delay}s;">
    <line x1="24" y1="{cursor_y - 12}" x2="{width - 24}" y2="{cursor_y - 12}" class="separator" />
    <text x="24" y="{cursor_y + 8}" class="title-text" font-size="11.5px">
      <tspan class="prompt-user">vkenned2@github</tspan>:<tspan class="prompt-path">~$</tspan> 
      <tspan fill="#7d8590">ready_</tspan>
    </text>
    <rect x="180" y="{cursor_y - 2}" width="7" height="13" class="cursor" />
  </g>
</svg>'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated info card SVG at {output_path}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_svg = os.path.join(base_dir, "info-card.svg")
    generate_info_card_svg(output_svg)

if __name__ == "__main__":
    main()
