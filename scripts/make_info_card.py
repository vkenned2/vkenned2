#!/usr/bin/env python3
"""
make_info_card.py
Generates a GitHub-compatible animated neofetch-style terminal info card.
Uses ONLY inline SVG presentation attributes + native SMIL <animate> elements.
No CSS classes — GitHub strips <style> blocks when serving SVGs via <img>.
Output: info-card.svg
"""

import os
import sys

# Fonts — inline presentation attributes only
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

# Colors
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


def render_info_card(output_path: str):
    W, H = 490, 360

    fields = [
        ("Role",      "PhD Candidate | Policy Analyst"),
        ("Research",  "Energy + Environmental Policy"),
        ("Focus",     "Geospatial | Conservation | AI"),
        ("Stack",     "Python · R · JavaScript · SQL"),
        ("Methods",   "Spatial Analysis | Causal Inference"),
        ("Building",  "Evidence-to-decision systems"),
        ("Location",  "Knoxville, Tennessee"),
        ("Education", "Univ. of Tennessee, Knoxville"),
        ("Field",     "Ecology + Energy/Env Policy"),
    ]

    out = []

    # ── SVG root ─────────────────────────────────────────────────────────────
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # ── Defs: gradient only (no filter — filters can blank SVG in proxy) ─────
    out.append('<defs>')
    out.append(f'  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">')
    out.append(f'    <stop offset="0%"   stop-color="{BG}"/>')
    out.append(f'    <stop offset="100%" stop-color="{BG2}"/>')
    out.append(f'  </linearGradient>')
    out.append('</defs>')

    # ── Main window ───────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" ry="10" '
               f'fill="url(#bg)" stroke="{BORDER}" stroke-width="1.5"/>')

    # ── Title bar ─────────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="0" width="{W}" height="34" rx="10" ry="10" '
               f'fill="{TITLEBAR}" stroke="{BORDER}" stroke-width="1"/>')
    # Square off bottom of title bar so it merges with window
    out.append(f'<rect x="0" y="20" width="{W}" height="14" fill="{TITLEBAR}"/>')
    out.append(f'<line x1="0" y1="34" x2="{W}" y2="34" stroke="{BORDER}" stroke-width="1"/>')

    # Window control dots
    out.append(f'<circle cx="18" cy="17" r="5.5" fill="{RED}"/>')
    out.append(f'<circle cx="36" cy="17" r="5.5" fill="{YELLOW}"/>')
    out.append(f'<circle cx="54" cy="17" r="5.5" fill="{BTNGRN}"/>')

    # Title text — ALL fills inline, no CSS
    out.append(f'<text y="22" font-family={MONO!r} font-size="12" font-weight="600">')
    out.append(f'  <tspan x="74" fill="{GREEN}">vkenned2@github</tspan>'
               f'<tspan fill="{TEXT}">:</tspan>'
               f'<tspan fill="{CYAN}">~$</tspan>'
               f'<tspan fill="{TEXT}"> neofetch</tspan>')
    out.append('</text>')

    # ── Name header ───────────────────────────────────────────────────────────
    out.append(f'<text x="24" y="62" font-family={MONO!r} font-size="20" '
               f'font-weight="800" fill="{BRIGHT}" letter-spacing="1">')
    out.append('  <animate attributeName="opacity" from="0" to="1" '
               'dur="0.5s" begin="0.1s" fill="freeze"/>')
    out.append('  VISHAL KENNEDY')
    out.append('</text>')

    # Separator
    out.append(f'<line x1="24" y1="72" x2="{W - 24}" y2="72" '
               f'stroke="{BORDER}" stroke-width="1">')
    out.append('  <animate attributeName="opacity" from="0" to="1" '
               'dur="0.3s" begin="0.2s" fill="freeze"/>')
    out.append('</line>')

    # ── Field rows ────────────────────────────────────────────────────────────
    y0   = 96
    step = 24

    for idx, (label, val) in enumerate(fields):
        y     = y0 + idx * step
        delay = round(0.25 + idx * 0.08, 2)

        out.append(f'<text y="{y}" font-family={MONO!r} font-size="11.5">')
        out.append(f'  <animate attributeName="opacity" from="0" to="1" '
                   f'dur="0.35s" begin="{delay}s" fill="freeze"/>')
        out.append(f'  <tspan x="24" font-weight="700" fill="{CYAN}">{label:<10}</tspan>'
                   f'<tspan fill="{MUTED}">&#x25B8; </tspan>'
                   f'<tspan fill="{TEXT}">{val}</tspan>')
        out.append('</text>')

    # ── Bottom prompt ─────────────────────────────────────────────────────────
    bot = y0 + len(fields) * step + 14
    out.append(f'<line x1="24" y1="{bot - 10}" x2="{W - 24}" y2="{bot - 10}" '
               f'stroke="{BORDER}" stroke-width="1">')
    out.append('  <animate attributeName="opacity" from="0" to="1" '
               'dur="0.3s" begin="1.1s" fill="freeze"/>')
    out.append('</line>')

    out.append(f'<text y="{bot + 8}" font-family={MONO!r} font-size="11.5">')
    out.append('  <animate attributeName="opacity" from="0" to="1" '
               'dur="0.3s" begin="1.15s" fill="freeze"/>')
    out.append(f'  <tspan x="24" fill="{GREEN}">vkenned2@github</tspan>'
               f'<tspan fill="{TEXT}">:</tspan>'
               f'<tspan fill="{CYAN}">~$</tspan>'
               f'<tspan fill="{MUTED}"> ready</tspan>')
    out.append('</text>')

    # Blinking cursor block
    out.append(f'<rect x="181" y="{bot - 1}" width="7" height="13" fill="{GREEN}">')
    out.append('  <animate attributeName="opacity" values="1;1;0;1" '
               'dur="1.2s" begin="1.2s" repeatCount="indefinite"/>')
    out.append('</rect>')

    out.append('</svg>')

    svg = "\n".join(out)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated info card: {output_path}")


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out  = os.path.join(base, "info-card.svg")
    render_info_card(out)


if __name__ == "__main__":
    main()
