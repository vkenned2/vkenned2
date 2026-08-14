#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and generates an animated GitHub dark terminal SVG heatmap.
Output: contrib-heatmap.svg
"""

import json
import os
import sys
from datetime import datetime, date, timedelta

PALETTE = [
    "#161b22",  # 0: background / no contrib
    "#0e4429",  # 1: light green
    "#006d32",  # 2: medium green
    "#26a641",  # 3: bright green
    "#39d353",  # 4: vivid green
    "#69f0a0"   # 5: highlight green for peak days
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = ["", "Mon", "", "Wed", "", "Fri", ""]

def get_color_for_count(count: int, level: int = None) -> str:
    if level is not None and 0 <= level <= 4:
        if count > 15:
            return PALETTE[5]
        return PALETTE[level]
    if count == 0:
        return PALETTE[0]
    elif count <= 2:
        return PALETTE[1]
    elif count <= 5:
        return PALETTE[2]
    elif count <= 9:
        return PALETTE[3]
    elif count <= 15:
        return PALETTE[4]
    else:
        return PALETTE[5]

def render_svg(data: dict) -> str:
    username = data.get("username", "vkenned2")
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", {}).get("length", 0)
    longest_streak = data.get("longest_streak", {}).get("length", 0)
    best_day_count = data.get("best_day", {}).get("count", 0)
    best_day_date = data.get("best_day", {}).get("date", "N/A")
    range_start = data.get("range", {}).get("start", "")
    range_end = data.get("range", {}).get("end", "")

    days = data.get("days", [])
    if not days:
        print("No days data found in JSON", file=sys.stderr)

    # Map dates to counts & levels
    day_map = {d["date"]: d for d in days}

    # Generate full 53-week grid ending at range_end or today
    if days:
        end_d = datetime.strptime(range_end, "%Y-%m-%d").date()
    else:
        end_d = date.today()

    # Find ending Saturday of the last week
    # weekday(): Mon=0, Tue=1, ..., Sat=5, Sun=6
    # We want Sunday as row 0 and Saturday as row 6.
    # In python: (dt.weekday() + 1) % 7 gives Sunday=0, Mon=1, ..., Sat=6.
    day_of_week_end = (end_d.weekday() + 1) % 7
    saturday_end = end_d + timedelta(days=(6 - day_of_week_end))
    sunday_start = saturday_end - timedelta(days=(53 * 7 - 1))

    # Build weeks array [53 weeks][7 days]
    weeks = []
    month_labels = [] # list of (week_idx, month_name)

    current_d = sunday_start
    prev_month = None

    for w in range(53):
        week_days = []
        for d in range(7):
            d_str = current_d.isoformat()
            d_month = current_d.month
            
            # Place month label on first day of a new month (or first week)
            if d_month != prev_month:
                if d == 0 or not month_labels or month_labels[-1][0] < w - 1:
                    month_labels.append((w, MONTH_NAMES[d_month - 1]))
                prev_month = d_month

            d_info = day_map.get(d_str, {"date": d_str, "count": 0, "level": 0})
            is_future = current_d > end_d
            week_days.append({
                "date": d_str,
                "count": d_info.get("count", 0),
                "level": d_info.get("level", 0),
                "is_future": is_future
            })
            current_d += timedelta(days=1)
        weeks.append(week_days)

    # SVG layout specs
    width = 860
    height = 295
    cell_size = 11
    cell_gap = 3
    cell_step = cell_size + cell_gap # 14px

    grid_x_offset = 55
    grid_y_offset = 88

    # Format header stats
    total_str = f"{total_contribs:,}"
    best_str = f"{best_day_count} on {best_day_date}" if best_day_count > 0 else "0"

    # SVG markup assembly
    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="termBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#111722" />
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.5" />
    </filter>
  </defs>

  <style>
    .window {{
      fill: url(#termBg);
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
      font-size: 13px;
      font-weight: 600;
      fill: #c9d1d9;
    }}
    .prompt-user {{ fill: #39d353; }}
    .prompt-path {{ fill: #22d3ee; }}
    .axis-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 10px;
      fill: #7d8590;
    }}
    .stat-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 11px;
      fill: #7d8590;
    }}
    .stat-val {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 12px;
      font-weight: 600;
      fill: #e6edf3;
    }}
    .stat-accent {{
      fill: #39d353;
    }}
    .cell {{
      rx: 2.5px;
      ry: 2.5px;
      opacity: 0;
      animation: revealCell 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      transform-origin: center;
    }}
    @keyframes revealCell {{
      0% {{
        opacity: 0;
        transform: scale(0.4);
      }}
      100% {{
        opacity: 1;
        transform: scale(1);
      }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .cell {{
        opacity: 1 !important;
        animation: none !important;
      }}
    }}
  </style>

  <!-- Terminal Container Window -->
  <rect x="2" y="2" width="{width - 4}" height="{height - 4}" class="window" filter="url(#shadow)" />

  <!-- Title Bar -->
  <path d="M 2 12 Q 2 2 12 2 L {width - 12} 2 Q {width - 2} 2 {width - 2} 12 L {width - 2} 36 L 2 36 Z" class="title-bar" />

  <!-- Window Control Buttons -->
  <circle cx="20" cy="19" r="6" fill="#ff5f56" />
  <circle cx="40" cy="19" r="6" fill="#ffbd2e" />
  <circle cx="60" cy="19" r="6" fill="#27c93f" />

  <!-- Window Title -->
  <text x="82" y="23" class="title-text">
    <tspan class="prompt-user">vkenned2@github</tspan>:<tspan class="prompt-path">~$</tspan> ./contributions.sh
  </text>

  <!-- Summary Line inside Terminal -->
  <text x="{grid_x_offset}" y="62" class="title-text" font-size="12px">
    <tspan font-weight="bold" fill="#39d353">{total_str}</tspan> contributions in the last year <tspan fill="#7d8590">({range_start} → {range_end})</tspan>
  </text>

  <!-- Month Labels -->''')

    for week_idx, m_name in month_labels:
        mx = grid_x_offset + week_idx * cell_step
        svg_parts.append(f'  <text x="{mx}" y="{grid_y_offset - 10}" class="axis-text">{m_name}</text>')

    svg_parts.append('\n  <!-- Day Labels -->')
    for d_idx, d_name in enumerate(DAY_NAMES):
        if d_name:
            dy = grid_y_offset + d_idx * cell_step + 9
            svg_parts.append(f'  <text x="{grid_x_offset - 12}" y="{dy}" class="axis-text" text-anchor="end">{d_name}</text>')

    svg_parts.append('\n  <!-- Heatmap Cells -->')

    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            if day["is_future"]:
                continue
            cx = grid_x_offset + w_idx * cell_step
            cy = grid_y_offset + d_idx * cell_step
            color = get_color_for_count(day["count"], day["level"])
            delay = round(w_idx * 0.008 + d_idx * 0.004, 3)

            title_str = f"{day['count']} contributions on {day['date']}"
            svg_parts.append(f'  <rect x="{cx}" y="{cy}" width="{cell_size}" height="{cell_size}" fill="{color}" class="cell" style="animation-delay: {delay}s;"><title>{title_str}</title></rect>')

    # Footer section: Stats & Legend
    footer_y = grid_y_offset + 7 * cell_step + 30 # y ~ 216

    svg_parts.append(f'''
  <!-- Divider Line -->
  <line x1="25" y1="{footer_y - 12}" x2="{width - 25}" y2="{footer_y - 12}" stroke="#30363d" stroke-width="1" stroke-dasharray="4,4" />

  <!-- Footer Stats -->
  <g transform="translate({grid_x_offset}, {footer_y})">
    <text y="0" class="stat-label">
      current streak: <tspan class="stat-val stat-accent">{current_streak} days</tspan>
      <tspan fill="#30363d" font-weight="bold">  │  </tspan>
      longest streak: <tspan class="stat-val">{longest_streak} days</tspan>
      <tspan fill="#30363d" font-weight="bold">  │  </tspan>
      best day: <tspan class="stat-val">{best_str}</tspan>
    </text>
  </g>

  <!-- Legend -->
  <g transform="translate({width - 200}, {footer_y - 8})">
    <text x="0" y="9" class="axis-text">Less</text>
    <rect x="30" y="0" width="10" height="10" rx="2" fill="{PALETTE[0]}" stroke="#30363d" stroke-width="0.5" />
    <rect x="44" y="0" width="10" height="10" rx="2" fill="{PALETTE[1]}" />
    <rect x="58" y="0" width="10" height="10" rx="2" fill="{PALETTE[2]}" />
    <rect x="72" y="0" width="10" height="10" rx="2" fill="{PALETTE[3]}" />
    <rect x="86" y="0" width="10" height="10" rx="2" fill="{PALETTE[4]}" />
    <rect x="100" y="0" width="10" height="10" rx="2" fill="{PALETTE[5]}" />
    <text x="116" y="9" class="axis-text">More</text>
  </g>
</svg>''')

    return "\n".join(svg_parts)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "contributions.json")
    output_svg = os.path.join(base_dir, "contrib-heatmap.svg")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist. Run fetch_contributions.py first.", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    svg_content = render_svg(data)
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated heatmap SVG at {output_svg}")

if __name__ == "__main__":
    main()
