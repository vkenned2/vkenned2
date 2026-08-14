#!/usr/bin/env python3
"""
render_heatmap_svg.py  —  Deep Navy × Sky Blue × Gold premium theme
GitHub-safe: inline SVG attributes + SMIL <animate>, no CSS classes.
Output: contrib-heatmap.svg
"""
import json
import os
import sys
from datetime import datetime, date, timedelta

# Blue contribution palette (not GitHub green)
PALETTE = [
    "#0a1628",  # 0: no contribution
    "#0c3057",  # 1
    "#0d5799",  # 2
    "#1e7bc4",  # 3
    "#38bdf8",  # 4 vivid sky blue
    "#93c5fd",  # 5 peak — pale blue highlight
]

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_LABELS  = ["","Mon","","Wed","","Fri",""]

BG1  = "#040d18"
BG2  = "#0a1628"
BAR  = "#060e1e"
BDR  = "#1a3452"
BDR2 = "#243f60"
TEXT = "#c0d4e8"
MUTED= "#4a6a8a"
BLUE = "#38bdf8"
CYAN = "#22d3ee"
GOLD = "#f59e0b"
TEAL = "#2dd4bf"
RED  = "#ff5f56"
YELL = "#ffbd2e"
GRND = "#27c93f"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
SANS = "'-apple-system', 'BlinkMacSystemFont', 'Segoe UI', Helvetica, Arial, sans-serif"


def color(count: int, level: int) -> str:
    if level is not None and 0 <= level <= 4:
        return PALETTE[5] if count > 15 else PALETTE[level]
    if count == 0:  return PALETTE[0]
    if count <= 2:  return PALETTE[1]
    if count <= 5:  return PALETTE[2]
    if count <= 9:  return PALETTE[3]
    if count <= 15: return PALETTE[4]
    return PALETTE[5]


def render(data: dict) -> str:
    total   = data.get("total_contributions", 0)
    c_str   = data.get("current_streak",  {}).get("length", 0)
    l_str   = data.get("longest_streak",  {}).get("length", 0)
    b_cnt   = data.get("best_day", {}).get("count", 0)
    b_date  = data.get("best_day", {}).get("date",  "N/A")
    r_start = data.get("range",    {}).get("start", "")
    r_end   = data.get("range",    {}).get("end",   "")
    days    = data.get("days", [])
    day_map = {d["date"]: d for d in days}

    # Grid
    end_d        = datetime.strptime(r_end, "%Y-%m-%d").date() if r_end else date.today()
    dow          = (end_d.weekday() + 1) % 7
    sat_end      = end_d + timedelta(days=(6 - dow))
    sun_start    = sat_end - timedelta(days=53 * 7 - 1)

    weeks        = []
    month_labels = []
    prev_m       = None
    cur          = sun_start

    for w in range(53):
        week = []
        for d in range(7):
            ds   = cur.isoformat()
            dm   = cur.month
            if dm != prev_m:
                if d == 0 or not month_labels or month_labels[-1][0] < w - 1:
                    month_labels.append((w, MONTH_NAMES[dm - 1]))
                prev_m = dm
            info = day_map.get(ds, {"count": 0, "level": 0})
            week.append({"date": ds, "count": info.get("count",0),
                         "level": info.get("level",0), "future": cur > end_d})
            cur += timedelta(days=1)
        weeks.append(week)

    # Layout
    W    = 860
    cell = 11
    gap  = 3
    step = cell + gap
    gx   = 54
    gy   = 82
    grid_h   = 7 * step
    stats_y  = gy + grid_h + 26
    H        = stats_y + 36

    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # Defs
    o.append('<defs>')
    o.append(f'  <linearGradient id="hbg" x1="0%" y1="0%" x2="100%" y2="100%">')
    o.append(f'    <stop offset="0%"   stop-color="{BG1}"/>')
    o.append(f'    <stop offset="100%" stop-color="{BG2}"/>')
    o.append(f'  </linearGradient>')
    o.append(f'  <linearGradient id="hacc" x1="0%" y1="0%" x2="100%" y2="0%">')
    o.append(f'    <stop offset="0%"   stop-color="#0369a1"/>')
    o.append(f'    <stop offset="60%"  stop-color="{BLUE}"/>')
    o.append(f'    <stop offset="100%" stop-color="{TEAL}"/>')
    o.append(f'  </linearGradient>')
    o.append('</defs>')

    # Window
    o.append(f'<rect width="{W}" height="{H}" rx="12" ry="12" '
             f'fill="url(#hbg)" stroke="{BDR}" stroke-width="1.5"/>')

    # Title bar
    o.append(f'<rect width="{W}" height="36" rx="12" ry="12" fill="{BAR}"/>')
    o.append(f'<rect y="22" width="{W}" height="14" fill="{BAR}"/>')
    o.append(f'<line x1="0" y1="36" x2="{W}" y2="36" stroke="{BDR}" stroke-width="1"/>')
    o.append(f'<circle cx="20" cy="18" r="5.5" fill="{RED}"/>')
    o.append(f'<circle cx="39" cy="18" r="5.5" fill="{YELL}"/>')
    o.append(f'<circle cx="58" cy="18" r="5.5" fill="{GRND}"/>')

    o.append(f'<text y="23" font-family={MONO!r} font-size="12" font-weight="600">')
    o.append(f'  <tspan x="78"  fill="{BLUE}">vkenned2</tspan>'
             f'<tspan fill="{MUTED}"> — </tspan>'
             f'<tspan fill="{TEXT}">contributions.json</tspan>')
    o.append('</text>')

    # Accent strip
    o.append(f'<rect x="0" y="36" width="{W}" height="4" fill="url(#hacc)"/>')

    # Summary line
    total_str = f"{total:,}"
    o.append(f'<text x="{gx}" y="62" font-family={MONO!r} font-size="12">')
    o.append(f'  <tspan fill="{GOLD}" font-size="14" font-weight="800">{total_str}</tspan>'
             f'<tspan fill="{TEXT}"> contributions in the last year</tspan>'
             f'<tspan fill="{MUTED}" font-size="10">   {r_start} &#x2192; {r_end}</tspan>')
    o.append('</text>')

    # Month labels
    for wi, mn in month_labels:
        mx = gx + wi * step
        o.append(f'<text x="{mx}" y="{gy - 6}" '
                 f'font-family={SANS!r} font-size="10" fill="{MUTED}">{mn}</text>')

    # Day labels
    for di, dn in enumerate(DAY_LABELS):
        if dn:
            dy = gy + di * step + 9
            o.append(f'<text x="{gx - 8}" y="{dy}" '
                     f'font-family={SANS!r} font-size="10" fill="{MUTED}" '
                     f'text-anchor="end">{dn}</text>')

    # Cells
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day["future"]:
                continue
            cx    = gx + wi * step
            cy    = gy + di * step
            c     = color(day["count"], day["level"])
            delay = round(wi * 0.007 + di * 0.003, 3)
            o.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" '
                f'rx="2.5" ry="2.5" fill="{c}">'
                f'<title>{day["count"]} contributions on {day["date"]}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="0.28s" begin="{delay}s" fill="freeze"/>'
                f'</rect>'
            )

    # Divider
    o.append(f'<line x1="24" y1="{stats_y - 12}" x2="{W - 24}" y2="{stats_y - 12}" '
             f'stroke="{BDR}" stroke-width="1" stroke-dasharray="4,3"/>')

    # Stats
    best_str = f"{b_cnt} on {b_date}" if b_cnt else "—"
    o.append(f'<text x="{gx}" y="{stats_y}" font-family={SANS!r} font-size="11.5" fill="{MUTED}">')
    o.append(
        f'current streak  '
        f'<tspan font-family={MONO!r} fill="{BLUE}" font-weight="700">{c_str} days</tspan>'
        f'<tspan fill="{BDR2}">   |   </tspan>'
        f'longest  '
        f'<tspan font-family={MONO!r} fill="{TEXT}" font-weight="700">{l_str} days</tspan>'
        f'<tspan fill="{BDR2}">   |   </tspan>'
        f'best day  '
        f'<tspan font-family={MONO!r} fill="{TEXT}" font-weight="700">{best_str}</tspan>'
    )
    o.append('</text>')

    # Legend
    leg_x = W - 200
    leg_y = stats_y - 11
    o.append(f'<text x="{leg_x}" y="{leg_y + 9}" '
             f'font-family={SANS!r} font-size="10" fill="{MUTED}">Less</text>')
    for i, pal in enumerate(PALETTE):
        bx = leg_x + 33 + i * 14
        border_color = BDR if i == 0 else pal
        o.append(f'<rect x="{bx}" y="{leg_y}" width="10" height="10" rx="2" '
                 f'fill="{pal}" stroke="{border_color}" stroke-width="0.5"/>')
    last_x = leg_x + 33 + len(PALETTE) * 14
    o.append(f'<text x="{last_x}" y="{leg_y + 9}" '
             f'font-family={SANS!r} font-size="10" fill="{MUTED}">More</text>')

    o.append('</svg>')
    return "\n".join(o)


def main():
    base     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jf       = os.path.join(base, "data", "contributions.json")
    out      = os.path.join(base, "contrib-heatmap.svg")
    if not os.path.exists(jf):
        print(f"Missing {jf} — run fetch_contributions.py first", file=sys.stderr); sys.exit(1)
    with open(jf) as f: data = json.load(f)
    svg = render(data)
    with open(out, "w", encoding="utf-8") as f: f.write(svg)
    print(f"Generated heatmap → {out}")

if __name__ == "__main__":
    main()
