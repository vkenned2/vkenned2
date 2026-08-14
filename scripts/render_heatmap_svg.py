#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and generates a GitHub-compatible animated heatmap SVG.
Uses ONLY inline SVG presentation attributes + native SMIL <animate> elements.
No CSS classes — GitHub strips <style> blocks when serving SVGs via <img>.
Output: contrib-heatmap.svg
"""

import json
import os
import sys
from datetime import datetime, date, timedelta

# Green contribution palette
PALETTE = [
    "#161b22",  # 0: no contribution
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
    "#69f0a0",  # 5: peak
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS  = ["", "Mon", "", "Wed", "", "Fri", ""]

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
MONO     = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
SANS     = "'-apple-system', 'BlinkMacSystemFont', 'Segoe UI', Helvetica, Arial, sans-serif"


def get_color(count: int, level: int) -> str:
    if level is not None and 0 <= level <= 4:
        if count > 15:
            return PALETTE[5]
        return PALETTE[level]
    if count == 0:   return PALETTE[0]
    if count <= 2:   return PALETTE[1]
    if count <= 5:   return PALETTE[2]
    if count <= 9:   return PALETTE[3]
    if count <= 15:  return PALETTE[4]
    return PALETTE[5]


def render_svg(data: dict) -> str:
    username   = data.get("username", "vkenned2")
    total      = data.get("total_contributions", 0)
    cur_streak = data.get("current_streak", {}).get("length", 0)
    lon_streak = data.get("longest_streak", {}).get("length", 0)
    best_count = data.get("best_day", {}).get("count", 0)
    best_date  = data.get("best_day", {}).get("date", "N/A")
    r_start    = data.get("range", {}).get("start", "")
    r_end      = data.get("range", {}).get("end", "")

    days     = data.get("days", [])
    day_map  = {d["date"]: d for d in days}

    # Determine grid boundaries (53 weeks ending at latest Saturday)
    end_d        = datetime.strptime(r_end, "%Y-%m-%d").date() if r_end else date.today()
    dow_end      = (end_d.weekday() + 1) % 7   # Sun=0 … Sat=6
    saturday_end = end_d + timedelta(days=(6 - dow_end))
    sunday_start = saturday_end - timedelta(days=(53 * 7 - 1))

    # Build weeks[53][7]
    weeks        = []
    month_labels = []  # (week_idx, month_name)
    prev_month   = None
    cur          = sunday_start

    for w in range(53):
        week = []
        for d in range(7):
            d_str  = cur.isoformat()
            d_mon  = cur.month
            if d_mon != prev_month:
                if d == 0 or not month_labels or month_labels[-1][0] < w - 1:
                    month_labels.append((w, MONTH_NAMES[d_mon - 1]))
                prev_month = d_mon
            info = day_map.get(d_str, {"date": d_str, "count": 0, "level": 0})
            week.append({
                "date":      d_str,
                "count":     info.get("count", 0),
                "level":     info.get("level", 0),
                "is_future": cur > end_d,
            })
            cur += timedelta(days=1)
        weeks.append(week)

    # Layout constants
    W = 860
    cell  = 11
    gap   = 3
    step  = cell + gap   # 14
    gx    = 54           # grid x origin
    gy    = 84           # grid y origin

    # Dynamic height
    grid_h  = 7 * step   # 98px
    stats_y = gy + grid_h + 26
    H       = stats_y + 36

    total_str = f"{total:,}"
    best_str  = f"{best_count} on {best_date}" if best_count else "0"

    out = []

    # ── SVG root ──────────────────────────────────────────────────────────────
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    out.append('<defs>')
    out.append(f'  <linearGradient id="hbg" x1="0%" y1="0%" x2="100%" y2="100%">')
    out.append(f'    <stop offset="0%"   stop-color="{BG}"/>')
    out.append(f'    <stop offset="100%" stop-color="{BG2}"/>')
    out.append(f'  </linearGradient>')
    out.append('</defs>')

    # ── Main window ───────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" ry="10" '
               f'fill="url(#hbg)" stroke="{BORDER}" stroke-width="1.5"/>')

    # ── Title bar ─────────────────────────────────────────────────────────────
    out.append(f'<rect x="0" y="0" width="{W}" height="34" rx="10" ry="10" '
               f'fill="{TITLEBAR}" stroke="{BORDER}" stroke-width="1"/>')
    out.append(f'<rect x="0" y="20" width="{W}" height="14" fill="{TITLEBAR}"/>')
    out.append(f'<line x1="0" y1="34" x2="{W}" y2="34" stroke="{BORDER}" stroke-width="1"/>')

    out.append(f'<circle cx="18" cy="17" r="5.5" fill="{RED}"/>')
    out.append(f'<circle cx="36" cy="17" r="5.5" fill="{YELLOW}"/>')
    out.append(f'<circle cx="54" cy="17" r="5.5" fill="{BTNGRN}"/>')

    out.append(f'<text y="22" font-family={MONO!r} font-size="13" font-weight="600">')
    out.append(f'  <tspan x="74" fill="{GREEN}">vkenned2@github</tspan>'
               f'<tspan fill="{TEXT}">:</tspan>'
               f'<tspan fill="{CYAN}">~$</tspan>'
               f'<tspan fill="{TEXT}"> ./contributions.sh</tspan>')
    out.append('</text>')

    # ── Summary line ──────────────────────────────────────────────────────────
    out.append(f'<text x="{gx}" y="60" font-family={MONO!r} font-size="12" font-weight="600">')
    out.append(f'  <tspan fill="{GREEN}" font-size="13">{total_str}</tspan>'
               f'<tspan fill="{TEXT}"> contributions in the last year</tspan>'
               f'<tspan fill="{MUTED}" font-size="10">  ({r_start} &#x2192; {r_end})</tspan>')
    out.append('</text>')

    # ── Month labels ──────────────────────────────────────────────────────────
    for w_idx, m_name in month_labels:
        mx = gx + w_idx * step
        out.append(f'<text x="{mx}" y="{gy - 6}" '
                   f'font-family={SANS!r} font-size="10" fill="{MUTED}">{m_name}</text>')

    # ── Day-of-week labels ────────────────────────────────────────────────────
    for d_idx, d_name in enumerate(DAY_LABELS):
        if d_name:
            dy = gy + d_idx * step + 9
            out.append(f'<text x="{gx - 8}" y="{dy}" '
                       f'font-family={SANS!r} font-size="10" fill="{MUTED}" '
                       f'text-anchor="end">{d_name}</text>')

    # ── Heatmap cells — inline fill + rx/ry + SMIL animate ───────────────────
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            if day["is_future"]:
                continue
            cx    = gx + w_idx * step
            cy    = gy + d_idx * step
            color = get_color(day["count"], day["level"])
            delay = round(w_idx * 0.007 + d_idx * 0.003, 3)

            out.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" '
                f'rx="2.5" ry="2.5" fill="{color}">'
                f'<title>{day["count"]} contributions on {day["date"]}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="0.3s" begin="{delay}s" fill="freeze"/>'
                f'</rect>'
            )

    # ── Divider ───────────────────────────────────────────────────────────────
    out.append(f'<line x1="24" y1="{stats_y - 12}" x2="{W - 24}" y2="{stats_y - 12}" '
               f'stroke="{BORDER}" stroke-width="1" stroke-dasharray="4,4"/>')

    # ── Stats row ─────────────────────────────────────────────────────────────
    out.append(f'<text x="{gx}" y="{stats_y}" font-family={SANS!r} font-size="11" fill="{MUTED}">')
    out.append(
        f'  current streak: <tspan font-family={MONO!r} fill="{GREEN}" font-weight="700">{cur_streak} days</tspan>'
        f'<tspan fill="{BORDER}" font-size="13">  |  </tspan>'
        f'longest streak: <tspan font-family={MONO!r} fill="{TEXT}" font-weight="700">{lon_streak} days</tspan>'
        f'<tspan fill="{BORDER}" font-size="13">  |  </tspan>'
        f'best day: <tspan font-family={MONO!r} fill="{TEXT}" font-weight="700">{best_str}</tspan>'
    )
    out.append('</text>')

    # ── Legend ────────────────────────────────────────────────────────────────
    leg_x = W - 196
    leg_y = stats_y - 10
    out.append(f'<text x="{leg_x}" y="{leg_y + 9}" font-family={SANS!r} font-size="10" fill="{MUTED}">Less</text>')
    for i, c in enumerate(PALETTE):
        bx = leg_x + 30 + i * 14
        out.append(f'<rect x="{bx}" y="{leg_y}" width="10" height="10" rx="2" '
                   f'fill="{c}" stroke="{BORDER}" stroke-width="0.5"/>')
    out.append(f'<text x="{leg_x + 30 + 6*14}" y="{leg_y + 9}" '
               f'font-family={SANS!r} font-size="10" fill="{MUTED}">More</text>')

    out.append('</svg>')
    return "\n".join(out)


def main():
    base      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base, "data", "contributions.json")
    out_path  = os.path.join(base, "contrib-heatmap.svg")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run fetch_contributions.py first.",
              file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    svg = render_svg(data)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated heatmap SVG: {out_path}")


if __name__ == "__main__":
    main()
