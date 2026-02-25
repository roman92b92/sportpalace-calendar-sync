#!/usr/bin/env python3
"""
Test script to preview events before syncing to calendar
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def fetch_and_preview_events():
    """Fetch events and display them without creating calendar entries"""

    url = "https://www.sportpalace.co.il/menora-mivtachim/%D7%9C%D7%95%D7%97-%D7%90%D7%A8%D7%95%D7%A2%D7%99%D7%9D/"

    print("🔍 Fetching events from Sport Palace...")
    print(f"URL: {url}\n")

    # Use mobile user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        print(f"✅ Page fetched successfully (Status: {response.status_code})\n")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all text content
        all_text = soup.get_text()

        print("=" * 70)
        print("📋 RAW PAGE CONTENT PREVIEW (First 2000 chars)")
        print("=" * 70)
        print(all_text[:2000])
        print("\n" + "=" * 70)

        # Find patterns that look like events
        print("\n🔎 SEARCHING FOR EVENT PATTERNS...\n")

        # Pattern 1: Date patterns (e.g., "25.1" or "9-10.2")
        date_patterns = re.findall(r'\d{1,2}(?:-\d{1,2})?\.(\d{1,2})', all_text)
        print(f"📅 Found {len(date_patterns)} date patterns")

        # Pattern 2: Time patterns (e.g., "21:00" or "20:45")
        time_patterns = re.findall(r'\d{1,2}:\d{2}', all_text)
        print(f"⏰ Found {len(time_patterns)} time patterns")

        # Extract potential events
        print("\n" + "=" * 70)
        print("🎯 EXTRACTED EVENTS")
        print("=" * 70)

        # Split by common delimiters
        lines = re.split(r'\n+', all_text)

        events_found = 0
        current_year = datetime.now().year

        for line in lines:
            line = line.strip()

            # Skip empty or very short lines
            if len(line) < 10:
                continue

            # Look for lines with both date and time
            date_match = re.search(r'(\d{1,2})(?:-\d{1,2})?\.(\d{1,2})', line)
            time_match = re.search(r'(\d{1,2}):(\d{2})', line)

            if date_match and time_match:
                events_found += 1

                day = date_match.group(1)
                month = date_match.group(2)
                time = f"{time_match.group(1)}:{time_match.group(2)}"

                # Extract event name
                event_name = line
                event_name = re.sub(r'\d{1,2}(?:-\d{1,2})?\.(\d{1,2})', '', event_name)
                event_name = re.sub(r'\d{1,2}:\d{2}', '', event_name)
                event_name = re.sub(r'\s+', ' ', event_name).strip()

                print(f"\n{events_found}. {event_name}")
                print(f"   📅 Date: {day}/{month}/{current_year}")
                print(f"   ⏰ Time: {time}")
                print(f"   📍 Duration: 30 minutes")
                print(f"   🎨 Color: RED")
                print(f"   ✉️  Invitation: (your configured email)")

        print("\n" + "=" * 70)
        print(f"\n✅ Total events found: {events_found}")

        if events_found == 0:
            print("\n⚠️  WARNING: No events found!")
            print("This might mean:")
            print("  • The page structure has changed")
            print("  • The page requires JavaScript to load content")
            print("  • The URL is incorrect or the page is empty")
            print("\nSaving full page HTML for inspection...")

            with open('page_dump.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ Saved to: page_dump.html")

    except requests.RequestException as e:
        print(f"❌ Error fetching page: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_and_preview_events()
