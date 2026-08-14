#!/usr/bin/env python3
"""
make_info_card.py  —  Deep Navy × Sky Blue × Gold premium theme
GitHub-safe: inline SVG attributes + SMIL <animate>, no CSS classes.
Output: info-card.svg
"""
import os

MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
SANS = "'-apple-system', 'BlinkMacSystemFont', 'Segoe UI', Helvetica, Arial, sans-serif"

# Palette
BG1    = "#040d18"
BG2    = "#0a1628"
BAR    = "#060e1e"
BDR    = "#1a3452"
BDR2   = "#243f60"
TEXT   = "#c0d4e8"
BRIGHT = "#e8f4ff"
MUTED  = "#4a6a8a"
BLUE   = "#38bdf8"
CYAN   = "#22d3ee"
GOLD   = "#f59e0b"
GOLD2  = "#fbbf24"
TEAL   = "#2dd4bf"
RED    = "#ff5f56"
YELL   = "#ffbd2e"
GRND   = "#27c93f"


def render(out_path: str):
    W, H = 490, 360

    fields = [
        ("Degree",    "PhD Candidate · Ecology"),
        ("Policy",    "Energy + Environmental Policy"),
        ("Methods",   "Geospatial · Conservation · AI"),
        ("Stack",     "Python · R · JavaScript · SQL"),
        ("Eval",      "Spatial Analysis · Causal Inference"),
        ("Building",  "Evidence-to-decision systems"),
        ("Affil.",    "University of Tennessee"),
        ("Location",  "Knoxville, Tennessee"),
    ]

    o = []

    # ── Root ──────────────────────────────────────────────────────────────────
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # ── Defs: gradients ───────────────────────────────────────────────────────
    o.append('<defs>')
    # Main background gradient
    o.append(f'  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">')
    o.append(f'    <stop offset="0%"   stop-color="{BG1}"/>')
    o.append(f'    <stop offset="100%" stop-color="{BG2}"/>')
    o.append(f'  </linearGradient>')
    # Accent strip gradient (blue → cyan → teal)
    o.append(f'  <linearGradient id="acc" x1="0%" y1="0%" x2="100%" y2="0%">')
    o.append(f'    <stop offset="0%"   stop-color="#0369a1"/>')
    o.append(f'    <stop offset="50%"  stop-color="{BLUE}"/>')
    o.append(f'    <stop offset="100%" stop-color="{TEAL}"/>')
    o.append(f'  </linearGradient>')
    # Name gold gradient
    o.append(f'  <linearGradient id="gld" x1="0%" y1="0%" x2="100%" y2="0%">')
    o.append(f'    <stop offset="0%"   stop-color="{GOLD}"/>')
    o.append(f'    <stop offset="100%" stop-color="{GOLD2}"/>')
    o.append(f'  </linearGradient>')
    o.append('</defs>')

    # ── Main window ───────────────────────────────────────────────────────────
    o.append(f'<rect width="{W}" height="{H}" rx="12" ry="12" '
             f'fill="url(#bg)" stroke="{BDR}" stroke-width="1.5"/>')

    # ── Title bar ─────────────────────────────────────────────────────────────
    o.append(f'<rect width="{W}" height="36" rx="12" ry="12" fill="{BAR}"/>')
    o.append(f'<rect y="22" width="{W}" height="14" fill="{BAR}"/>')
    o.append(f'<line x1="0" y1="36" x2="{W}" y2="36" stroke="{BDR}" stroke-width="1"/>')

    # Window dots
    o.append(f'<circle cx="20" cy="18" r="5.5" fill="{RED}"/>')
    o.append(f'<circle cx="39" cy="18" r="5.5" fill="{YELL}"/>')
    o.append(f'<circle cx="58" cy="18" r="5.5" fill="{GRND}"/>')

    # Title text
    o.append(f'<text y="23" font-family={MONO!r} font-size="11.5" font-weight="600">')
    o.append(f'  <tspan x="78"  fill="{BLUE}">vkenned2</tspan>'
             f'<tspan fill="{MUTED}"> — </tspan>'
             f'<tspan fill="{TEXT}">profile.json</tspan>')
    o.append('</text>')

    # ── Accent strip ──────────────────────────────────────────────────────────
    o.append(f'<rect x="0" y="36" width="{W}" height="4" fill="url(#acc)"/>')

    # ── Name block ────────────────────────────────────────────────────────────
    o.append(f'<text x="24" y="72" font-family={MONO!r} font-size="22" '
             f'font-weight="800" fill="url(#gld)" letter-spacing="1.5">')
    o.append('  <animate attributeName="opacity" from="0" to="1" '
             'dur="0.5s" begin="0.1s" fill="freeze"/>')
    o.append('  VISHAL KENNEDY')
    o.append('</text>')

    # Subtitle
    o.append(f'<text x="26" y="90" font-family={SANS!r} font-size="12" fill="{MUTED}">')
    o.append('  <animate attributeName="opacity" from="0" to="1" '
             'dur="0.4s" begin="0.2s" fill="freeze"/>')
    o.append(f'  <tspan fill="{BLUE}">PhD Candidate</tspan>'
             f'<tspan fill="{MUTED}">  ·  Policy Analyst  ·  Researcher</tspan>')
    o.append('</text>')

    # Separator
    o.append(f'<line x1="24" y1="100" x2="{W - 24}" y2="100" '
             f'stroke="{BDR}" stroke-width="1">')
    o.append('  <animate attributeName="opacity" from="0" to="1" '
             'dur="0.3s" begin="0.25s" fill="freeze"/>')
    o.append('</line>')

    # ── Field rows ────────────────────────────────────────────────────────────
    y0   = 120
    step = 26

    for i, (label, val) in enumerate(fields):
        y     = y0 + i * step
        delay = round(0.3 + i * 0.07, 2)

        # Row background on hover (static subtle bg for even rows)
        if i % 2 == 0:
            o.append(f'<rect x="14" y="{y - 15}" width="{W - 28}" height="22" '
                     f'rx="4" fill="{BDR}" opacity="0.3">')
            o.append(f'  <animate attributeName="opacity" from="0" to="0.3" '
                     f'dur="0.3s" begin="{delay}s" fill="freeze"/>')
            o.append('</rect>')

        o.append(f'<text y="{y}" font-family={MONO!r} font-size="11.5">')
        o.append(f'  <animate attributeName="opacity" from="0" to="1" '
                 f'dur="0.3s" begin="{delay}s" fill="freeze"/>')
        o.append(f'  <tspan x="24" fill="{BLUE}" font-weight="700">'
                 f'{label:<9}</tspan>'
                 f'<tspan fill="{BDR2}">  ›  </tspan>'
                 f'<tspan fill="{TEXT}">{val}</tspan>')
        o.append('</text>')

    # ── Bottom quote / separator ──────────────────────────────────────────────
    sep_y = y0 + len(fields) * step + 8
    o.append(f'<line x1="24" y1="{sep_y}" x2="{W - 24}" y2="{sep_y}" '
             f'stroke="{BDR}" stroke-width="1">')
    o.append('  <animate attributeName="opacity" from="0" to="1" '
             'dur="0.3s" begin="0.95s" fill="freeze"/>')
    o.append('</line>')

    # Prompt line
    prom_y = sep_y + 22
    o.append(f'<text y="{prom_y}" font-family={MONO!r} font-size="11.5">')
    o.append('  <animate attributeName="opacity" from="0" to="1" '
             'dur="0.3s" begin="1.0s" fill="freeze"/>')
    o.append(f'  <tspan x="24" fill="{BLUE}">vkenned2@github</tspan>'
             f'<tspan fill="{TEXT}">:</tspan>'
             f'<tspan fill="{CYAN}">~$</tspan>'
             f'<tspan fill="{MUTED}"> _</tspan>')
    o.append('</text>')

    # Blinking cursor
    cur_x = 176
    o.append(f'<rect x="{cur_x}" y="{prom_y - 11}" width="7" height="13" fill="{BLUE}">')
    o.append('  <animate attributeName="opacity" values="1;1;0;1" '
             'dur="1.2s" begin="1.1s" repeatCount="indefinite"/>')
    o.append('</rect>')

    o.append('</svg>')
    svg = "\n".join(o)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated info card → {out_path}")


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    render(os.path.join(base, "info-card.svg"))

if __name__ == "__main__":
    main()
