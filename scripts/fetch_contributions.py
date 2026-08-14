#!/usr/bin/env python3
"""
fetch_contributions.py
Fetches public GitHub contribution data for a given user and calculates statistics.
Saves output to data/contributions.json.
"""

import json
import os
import re
import sys
from datetime import datetime, date, timedelta
import requests
from bs4 import BeautifulSoup

def fetch_github_contributions(username: str):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    print(f"Fetching contributions from {url}...")
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch contributions HTML: HTTP {resp.status_code}")
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Parse contribution days from the HTML
    # GitHub uses <td class="ContributionCalendar-day" ...> or <rect class="ContributionCalendar-day" ...>
    # and tooltips like <tool-tip ...>N contributions on Month Day, Year</tool-tip> or id="contribution-day-component-..."
    
    day_nodes = soup.find_all(attrs={"data-date": True})
    if not day_nodes:
        # Fallback search for any element with data-date
        day_nodes = soup.select("[data-date]")
        
    if not day_nodes:
        raise ValueError("Could not find any contribution day elements in GitHub response")

    # Map tooltips if present
    tooltips = {}
    for tt in soup.find_all(["tool-tip", "div", "span"]):
        tt_for = tt.get("for") or tt.get("id") or ""
        text = tt.get_text(strip=True)
        if text and ("contribution" in text or "No contribution" in text):
            tooltips[tt_for] = text

    days_data = []
    
    for node in day_nodes:
        d_str = node.get("data-date")
        if not d_str:
            continue
            
        level = 0
        if node.get("data-level"):
            try:
                level = int(node["data-level"])
            except ValueError:
                level = 0

        # Try getting count directly from attributes
        count = None
        if node.get("data-count") is not None:
            try:
                count = int(node["data-count"])
            except ValueError:
                pass

        # Try finding count from tooltip
        node_id = node.get("id", "")
        tt_text = tooltips.get(node_id, "")
        if count is None and tt_text:
            match = re.search(r"(\d+)\s+contribution", tt_text)
            if match:
                count = int(match.group(1))
            elif "No contribution" in tt_text:
                count = 0

        # Try finding count in aria-label or inner text or tooltip elements associated by ID
        if count is None:
            aria = node.get("aria-label", "")
            if aria:
                match = re.search(r"(\d+)\s+contribution", aria)
                if match:
                    count = int(match.group(1))
                elif "No contribution" in aria or "0 contribution" in aria:
                    count = 0

        # If count still not found, estimate based on level
        if count is None:
            if level == 0:
                count = 0
            elif level == 1:
                count = 1
            elif level == 2:
                count = 3
            elif level == 3:
                count = 6
            elif level == 4:
                count = 10

        days_data.append({
            "date": d_str,
            "count": count,
            "level": level
        })

    # Sort days chronologically
    days_data.sort(key=lambda x: x["date"])
    
    return days_data

def calculate_stats(days_data, username):
    if not days_data:
        return {}

    total_contributions = sum(d["count"] for d in days_data)
    active_days_list = [d for d in days_data if d["count"] > 0]
    active_days_count = len(active_days_list)
    avg_per_active = round(total_contributions / active_days_count, 1) if active_days_count > 0 else 0.0

    # Best day
    best_day = max(days_data, key=lambda x: x["count"]) if days_data else {"date": None, "count": 0}

    # Streaks calculation
    longest_streak = {"length": 0, "start": None, "end": None}
    current_streak = {"length": 0, "start": None, "end": None}

    temp_streak = 0
    temp_start = None

    today_str = date.today().isoformat()

    for i, d in enumerate(days_data):
        if d["count"] > 0:
            if temp_streak == 0:
                temp_start = d["date"]
            temp_streak += 1
            if temp_streak > longest_streak["length"]:
                longest_streak = {
                    "length": temp_streak,
                    "start": temp_start,
                    "end": d["date"]
                }
        else:
            temp_streak = 0
            temp_start = None

    # Current streak check (backwards from today or latest available date)
    # Note: today might be 0 so far, so check today and yesterday
    reversed_days = list(reversed(days_data))
    cur_count = 0
    cur_start = None
    cur_end = None

    # If the latest day in data has 0 contributions, but it's today, check if yesterday was active
    latest_day = reversed_days[0] if reversed_days else None
    
    idx = 0
    if latest_day and latest_day["count"] == 0 and latest_day["date"] == today_str:
        # User hasn't committed today yet, start checking from yesterday
        idx = 1

    for d in reversed_days[idx:]:
        if d["count"] > 0:
            if cur_count == 0:
                cur_end = d["date"]
            cur_count += 1
            cur_start = d["date"]
        else:
            break

    current_streak = {
        "length": cur_count,
        "start": cur_start,
        "end": cur_end
    }

    # Monthly aggregation
    monthly_map = {}
    for d in days_data:
        m_key = d["date"][:7] # YYYY-MM
        monthly_map[m_key] = monthly_map.get(m_key, 0) + d["count"]
        
    monthly_list = [{"month": k, "count": v} for k, v in sorted(monthly_map.items())]

    start_date = days_data[0]["date"]
    end_date = days_data[-1]["date"]

    result = {
        "username": username,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "range": {
            "start": start_date,
            "end": end_date
        },
        "total_contributions": total_contributions,
        "active_days": active_days_count,
        "avg_per_active_day": avg_per_active,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {
            "date": best_day["date"],
            "count": best_day["count"]
        },
        "monthly": monthly_list,
        "days": days_data
    }

    return result

def main():
    username = os.environ.get("GH_PROFILE_USER", "vkenned2")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "contributions.json")

    try:
        days_data = fetch_github_contributions(username)
        stats = calculate_stats(days_data, username)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        print(f"Successfully saved contribution data for {username} ({stats['total_contributions']} total contributions across {len(days_data)} days) to {output_file}")
    except Exception as e:
        print(f"Error fetching contributions for {username}: {e}", file=sys.stderr)
        if os.path.exists(output_file):
            print("Preserving existing data/contributions.json", file=sys.stderr)
            sys.exit(0)
        else:
            # Create minimal fallback data if no network / file exists
            print("Creating fallback contributions.json", file=sys.stderr)
            fallback_days = []
            today = date.today()
            start = today - timedelta(days=364)
            cur = start
            while cur <= today:
                fallback_days.append({"date": cur.isoformat(), "count": 0, "level": 0})
                cur += timedelta(days=1)
            stats = calculate_stats(fallback_days, username)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)

if __name__ == "__main__":
    main()
