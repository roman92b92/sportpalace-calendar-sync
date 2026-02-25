#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sport Palace Event Calendar Scraper
Extracts events from Sport Palace website and creates Google Calendar invitations.
"""

import os
import sys
import json
import pickle
import re
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


def load_config(config_file: str = 'config.json') -> Optional[dict]:
    """Load configuration from a JSON file."""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"Error: Config file '{config_file}' not found.")
    print("Copy config.example.json to config.json and fill in your details.")
    return None


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

HEBREW_MONTHS = {
    'ינואר': 1, 'פברואר': 2, 'מרץ': 3, 'אפריל': 4,
    'מאי': 5, 'יוני': 6, 'יולי': 7, 'אוגוסט': 8,
    'ספטמבר': 9, 'אוקטובר': 10, 'נובמבר': 11, 'דצמבר': 12,
}

# Matches: "פברואר 22, 2026 20:55"  or  "מרץ 3, 2026 21:00"
HEBREW_DATE_RE = re.compile(
    r'([\u05D0-\u05EA]+)\s+(\d{1,2}),?\s*(\d{4})\s+(\d{1,2}):(\d{2})'
)


class SportPalaceEventScraper:
    """Scraper for Sport Palace events — handles Hebrew dates and multi-month fetching."""

    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/14.0 Mobile/15E148 Safari/604.1'
        )
    }

    def __init__(self, url: str):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        # Preserve the calendar widget ID — required by the My Calendar plugin
        self.cid = params.get('cid', [None])[0]
        self.base_url = parsed.scheme + '://' + parsed.netloc + parsed.path.rstrip('/')

    def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch a single URL and return the HTML text."""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _month_url(self, year: int, month: int) -> str:
        """Build the URL for a specific year/month, preserving the cid."""
        url = f"{self.base_url}/?yr={year}&month={month}&dy="
        if self.cid:
            url += f"&cid={self.cid}"
        return url

    def fetch_page(self) -> Optional[str]:
        """Fetch only the base URL (single month). Kept for backwards compatibility."""
        return self._fetch_url(self.base_url + '/')

    def fetch_months(self, months_ahead: int = 1) -> Optional[str]:
        """
        Fetch HTML for the current month plus *months_ahead* future months.
        Returns the concatenated HTML of all pages, or None if all failed.
        """
        now = datetime.now()
        all_html = ''

        for offset in range(months_ahead + 1):
            m = now.month + offset
            y = now.year
            while m > 12:
                m -= 12
                y += 1
            url = self._month_url(y, m)
            print(f"  Fetching {y}-{m:02d} …")
            html = self._fetch_url(url)
            if html:
                all_html += html

        return all_html if all_html else None

    @staticmethod
    def _parse_hebrew_month(token: str) -> Optional[int]:
        """Return the month number for a Hebrew month token, or None."""
        for heb, num in HEBREW_MONTHS.items():
            if heb in token:
                return num
        return None

    def parse_events(self, html: str) -> List[Dict]:
        """
        Parse events from page text.

        The My Calendar plugin renders dates as:
            "פברואר 22, 2026 20:55"

        Strategy: strip scripts/styles, split the page into lines, find every
        line containing a Hebrew date, and look at the surrounding lines for
        the event name.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove noise
        for tag in soup(['script', 'style', 'head', 'nav', 'footer']):
            tag.decompose()

        # Split into clean lines
        lines = [
            ln.strip()
            for ln in soup.get_text(separator='\n').splitlines()
            if ln.strip()
        ]

        events = []

        for i, line in enumerate(lines):
            match = HEBREW_DATE_RE.search(line)
            if not match:
                continue

            heb_month = match.group(1)
            day       = int(match.group(2))
            year      = int(match.group(3))
            hour      = int(match.group(4))
            minute    = int(match.group(5))

            month = self._parse_hebrew_month(heb_month)
            if not month:
                continue

            # Try to get the event name from the same line (text before the date)
            name = HEBREW_DATE_RE.sub('', line).strip()
            name = re.sub(r'\s+', ' ', name).strip()

            # If the line only contained the date, look at nearby lines
            if not name or len(name) < 2:
                for j in range(i - 1, max(i - 6, -1), -1):
                    candidate = lines[j]
                    # Skip lines that are just dates, numbers, or punctuation
                    if (candidate
                            and not HEBREW_DATE_RE.search(candidate)
                            and len(candidate) > 2
                            and not re.fullmatch(r'[\d\s\:\.\,\-\|/]+', candidate)):
                        name = candidate
                        break

            if not name or len(name) < 2:
                continue

            try:
                event_date = datetime(year, month, day, hour, minute)
            except ValueError:
                continue

            events.append({
                'name': name,
                'date': event_date,
                'time': f"{hour:02d}:{minute:02d}",
            })

        # Deduplicate and sort chronologically
        seen: set = set()
        unique: List[Dict] = []
        for ev in sorted(events, key=lambda e: e['date']):
            key = (ev['name'], ev['date'].strftime('%Y-%m-%d %H:%M'))
            if key not in seen:
                seen.add(key)
                unique.append(ev)

        return unique


# ---------------------------------------------------------------------------
# Google Calendar
# ---------------------------------------------------------------------------

class GoogleCalendarManager:
    """Manages Google Calendar API operations."""

    def __init__(self, config: dict):
        self.config = config
        self.creds = None
        self.service = None

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        token_path = 'token.pickle'
        creds_path = 'credentials.json'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as f:
                self.creds = pickle.load(f)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    print(f"\n❌ {creds_path} not found!")
                    print("Follow the Google API Setup in README.md.")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)

                print("\n" + "=" * 70)
                print("AUTHENTICATION REQUIRED")
                print("=" * 70)
                print("A browser URL will be shown — open it, sign in, and click Allow.")
                print("=" * 70 + "\n")

                for port in (8080, 8090):
                    try:
                        print(f"Starting local server on port {port}…")
                        self.creds = flow.run_local_server(
                            port=port,
                            open_browser=False,
                            authorization_prompt_message='Please visit this URL: {url}',
                            success_message='Authentication successful! You can close this window.',
                        )
                        break
                    except OSError:
                        print(f"Port {port} busy, trying next…")

            with open(token_path, 'wb') as f:
                pickle.dump(self.creds, f)

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Error building calendar service: {e}")
            return False

    def create_event(self, event_data: Dict) -> bool:
        """Create a single calendar event."""
        try:
            start = event_data['date']
            end   = start + timedelta(minutes=self.config['event_duration_minutes'])

            body = {
                'summary':  event_data['name'],
                'location': self.config['event_location'],
                'description': f"Sport Palace event\n{event_data['name']}",
                'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Jerusalem'},
                'end':   {'dateTime': end.isoformat(),   'timeZone': 'Asia/Jerusalem'},
                'attendees': [{'email': self.config['target_email']}],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': m}
                        for m in self.config['reminder_minutes']
                    ],
                },
                'colorId': self.config['event_color'],
            }

            self.service.events().insert(
                calendarId='primary', body=body, sendUpdates='all'
            ).execute()
            print(f"✅ Created: {event_data['name']} — {start.strftime('%Y-%m-%d %H:%M')}")
            return True

        except HttpError as e:
            print(f"❌ Failed: {event_data['name']}: {e}")
            return False

    def event_exists(self, name: str, date: datetime) -> bool:
        """Return True if an event with this name already exists on this day."""
        try:
            time_min = date.replace(hour=0,  minute=0,  second=0).isoformat() + 'Z'
            time_max = date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
            result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min, timeMax=time_max,
                q=name, singleEvents=True,
            ).execute()
            return any(e.get('summary') == name for e in result.get('items', []))
        except HttpError:
            return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("🎯 Sport Palace Event Calendar Sync")
    print("=" * 50)

    config = load_config()
    if not config:
        return

    months_ahead = config.get('months_ahead', 1)
    url          = config['url']

    print(f"\n📍 Source  : {url}")
    print(f"📧 Target  : {config['target_email']}")
    print(f"📆 Months  : current + {months_ahead} ahead\n")

    scraper = SportPalaceEventScraper(url)
    print("📥 Fetching events…")
    html = scraper.fetch_months(months_ahead)
    if not html:
        print("❌ Failed to fetch any pages.")
        return

    events = scraper.parse_events(html)
    if not events:
        print("⚠️  No events found. The page structure may have changed.")
        print("Try: python test_scraper.py")
        return

    print(f"\n✅ Found {len(events)} events:")
    print("-" * 50)
    for ev in events:
        print(f"  • {ev['name']}")
        print(f"    📅 {ev['date'].strftime('%Y-%m-%d')}  ⏰ {ev['time']}")

    print("\n🔐 Authenticating with Google Calendar…")
    calendar = GoogleCalendarManager(config)
    if not calendar.authenticate():
        print("❌ Authentication failed.")
        return
    print("✅ Authenticated")

    print("\n📅 Creating events…")
    created = skipped = 0
    for ev in events:
        if calendar.event_exists(ev['name'], ev['date']):
            print(f"⏭️  Skipped (exists): {ev['name']}")
            skipped += 1
        elif calendar.create_event(ev):
            created += 1

    print("\n" + "=" * 50)
    print(f"✅ Created : {created}")
    print(f"⏭️  Skipped : {skipped}")
    print(f"📧 Invitations → {config['target_email']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
