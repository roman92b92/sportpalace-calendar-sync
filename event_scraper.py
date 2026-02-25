#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sport Palace Event Calendar Scraper
Extracts events from Sport Palace website and creates Google Calendar invitations
"""

import os
import sys
import pickle
import re
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict
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
    except:
        pass

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Load configuration from config.json
def load_config(config_file='config.json'):
    """Load configuration from a JSON file."""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"Error: Config file '{config_file}' not found.")
        print("Copy config.example.json to config.json and fill in your details.")
        return None

import json
CONFIG = load_config()

# Configuration values
TARGET_EMAIL = CONFIG['target_email']
RED_COLOR_ID = CONFIG['event_color']


class SportPalaceEventScraper:
    """Scraper for Sport Palace events"""

    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }

    def fetch_page(self) -> str:
        """Fetch the webpage content"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_hebrew_month(self, month_str: str) -> int:
        """Convert Hebrew month name to month number"""
        hebrew_months = {
            'ינואר': 1, 'פברואר': 2, 'מרץ': 3, 'אפריל': 4,
            'מאי': 5, 'יוני': 6, 'יולי': 7, 'אוגוסט': 8,
            'ספטמבר': 9, 'אוקטובר': 10, 'נובמבר': 11, 'דצמבר': 12
        }
        for heb, num in hebrew_months.items():
            if heb in month_str:
                return num
        return None

    def parse_events(self, html: str) -> List[Dict]:
        """Parse events from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        events = []

        # Find all event entries - adapt selector based on actual HTML structure
        event_items = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'event|item|post|entry', re.I))

        if not event_items:
            # Try alternative selectors
            event_items = soup.find_all(['div'], class_=re.compile(r'wpb_wrapper|elementor|content'))

        current_year = datetime.now().year

        for item in event_items:
            try:
                # Extract text content
                text = item.get_text(strip=True, separator=' ')

                # Skip if too short or doesn't contain time pattern
                if len(text) < 10 or not re.search(r'\d{1,2}:\d{2}', text):
                    continue

                # Extract date pattern (e.g., "25.1" or "9-10.2")
                date_match = re.search(r'(\d{1,2})(?:-\d{1,2})?\.(\d{1,2})', text)
                if not date_match:
                    continue

                day = int(date_match.group(1))
                month = int(date_match.group(2))

                # Extract time (e.g., "21:00" or "20:45")
                time_match = re.search(r'(\d{1,2}):(\d{2})', text)
                if not time_match:
                    continue

                hour = int(time_match.group(1))
                minute = int(time_match.group(2))

                # Extract event name (text before the date/time)
                # Remove date and time parts to get clean event name
                event_name = re.sub(r'\d{1,2}(?:-\d{1,2})?\.(\d{1,2})', '', text)
                event_name = re.sub(r'\d{1,2}:\d{2}', '', event_name)
                event_name = event_name.strip()

                # Clean up event name
                event_name = re.sub(r'\s+', ' ', event_name)

                if not event_name or len(event_name) < 3:
                    continue

                # Create datetime object
                try:
                    event_date = datetime(current_year, month, day, hour, minute)
                except ValueError:
                    continue

                events.append({
                    'name': event_name,
                    'date': event_date,
                    'time': f"{hour:02d}:{minute:02d}"
                })

            except Exception as e:
                print(f"Error parsing event item: {e}")
                continue

        # Remove duplicates based on name and date
        unique_events = []
        seen = set()
        for event in events:
            key = (event['name'], event['date'].strftime('%Y-%m-%d %H:%M'))
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        return unique_events


class GoogleCalendarManager:
    """Manages Google Calendar operations"""

    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticate with Google Calendar API"""
        # Token file stores the user's access and refresh tokens
        token_path = 'token.pickle'
        creds_path = 'credentials.json'

        # Check if token exists
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    print(f"\n❌ Error: {creds_path} not found!")
                    print("Please follow the setup instructions to download your credentials.")
                    return False

                # Read credentials file to get client config
                import json
                with open(creds_path, 'r') as f:
                    client_config = json.load(f)

                # Check if this is a desktop app that supports urn:ietf:wg:oauth:2.0:oob
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)

                print("\n" + "="*70)
                print("AUTHENTICATION REQUIRED")
                print("="*70)
                print("\nA browser window will open (or a URL will be shown)")
                print("Please sign in with your Google account in your browser")
                print("and click 'Allow' to grant calendar access")
                print("\n" + "="*70 + "\n")

                # Use local server flow with fixed port
                # Desktop apps support localhost automatically
                try:
                    # Try port 8080 first
                    print("Starting local server on port 8080...")
                    print("Please open this URL in Firefox if browser doesn't open:")
                    print(f"http://localhost:8080")
                    self.creds = flow.run_local_server(
                        port=8080,
                        open_browser=False,
                        authorization_prompt_message='Please visit this URL: {url}',
                        success_message='Authentication successful! You can close this window.',
                    )
                except OSError:
                    # Port busy, try 8090
                    print("\nPort 8080 busy, trying 8090...")
                    print("Please open this URL in Firefox:")
                    print(f"http://localhost:8090")
                    self.creds = flow.run_local_server(
                        port=8090,
                        open_browser=False,
                        authorization_prompt_message='Please visit this URL: {url}',
                        success_message='Authentication successful! You can close this window.',
                    )

            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Error building calendar service: {e}")
            return False

    def create_event(self, event_data: Dict) -> bool:
        """Create a calendar event"""
        try:
            # Calculate end time (configurable duration)
            start_time = event_data['date']
            end_time = start_time + timedelta(minutes=CONFIG['event_duration_minutes'])

            # Create event object
            event = {
                'summary': event_data['name'],
                'location': CONFIG['event_location'],
                'description': f"Event from Sport Palace\n{event_data['name']}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Jerusalem',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Jerusalem',
                },
                'attendees': [
                    {'email': TARGET_EMAIL}
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': mins}
                        for mins in CONFIG['reminder_minutes']
                    ],
                },
                'colorId': RED_COLOR_ID,  # Red color
            }

            # Insert event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send invitation email
            ).execute()

            print(f"✅ Created: {event_data['name']} - {start_time.strftime('%Y-%m-%d %H:%M')}")
            return True

        except HttpError as e:
            print(f"❌ Error creating event '{event_data['name']}': {e}")
            return False

    def event_exists(self, event_name: str, event_date: datetime) -> bool:
        """Check if event already exists to avoid duplicates"""
        try:
            # Search for events on the same day
            time_min = event_date.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
            time_max = event_date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                q=event_name,
                singleEvents=True
            ).execute()

            events = events_result.get('items', [])

            for event in events:
                if event.get('summary') == event_name:
                    return True

            return False
        except HttpError:
            return False


def main():
    """Main execution function"""
    print("🎯 Sport Palace Event Calendar Sync")
    print("=" * 50)

    # Load configuration
    config = load_config()
    if not config:
        return
    url = config['url']

    print(f"\n📍 Source: {url}")
    print(f"📧 Target: {config['target_email']}")

    # Initialize scraper
    print("\n📥 Fetching events from Sport Palace...")
    scraper = SportPalaceEventScraper(url)

    # Fetch page
    html = scraper.fetch_page()
    if not html:
        print("❌ Failed to fetch page")
        return

    # Parse events
    events = scraper.parse_events(html)

    if not events:
        print("⚠️  No events found on the page")
        print("This might mean the page structure has changed.")
        return

    print(f"\n✅ Found {len(events)} events")
    print("\nEvents to be added:")
    print("-" * 50)
    for event in events:
        print(f"  • {event['name']}")
        print(f"    📅 {event['date'].strftime('%Y-%m-%d')} ⏰ {event['time']}")

    # Authenticate with Google Calendar
    print("\n🔐 Authenticating with Google Calendar...")
    calendar = GoogleCalendarManager()

    if not calendar.authenticate():
        print("❌ Authentication failed")
        return

    print("✅ Authentication successful")

    # Create events
    print("\n📅 Creating calendar events...")
    created_count = 0
    skipped_count = 0

    for event in events:
        # Check if event already exists
        if calendar.event_exists(event['name'], event['date']):
            print(f"⏭️  Skipped (already exists): {event['name']}")
            skipped_count += 1
            continue

        # Create event
        if calendar.create_event(event):
            created_count += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Successfully created {created_count} events")
    if skipped_count > 0:
        print(f"⏭️  Skipped {skipped_count} existing events")
    print(f"📧 Invitations sent to: {TARGET_EMAIL}")
    print("🎨 Events marked with RED color")


if __name__ == "__main__":
    main()
