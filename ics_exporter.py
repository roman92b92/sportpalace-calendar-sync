#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sport Palace ICS Exporter
Alternative to the Google Calendar API approach.

Scrapes events from the Sport Palace website and writes a standard .ics file
that can be imported in bulk into Google Calendar, Outlook, Apple Calendar,
or any other calendar application.

No Google API credentials required.

Usage:
    python ics_exporter.py
    python ics_exporter.py --output my_events.ics
    python ics_exporter.py --config my_config.json --output events.ics
"""

import sys
import uuid
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Reuse the scraper and config loader from event_scraper.py
from event_scraper import SportPalaceEventScraper, load_config


# ---------------------------------------------------------------------------
# ICS builder (no external icalendar library needed)
# ---------------------------------------------------------------------------

def format_dt(dt: datetime, tz_name: str) -> str:
    """Format a datetime for an ICS DTSTART/DTEND with TZID."""
    return dt.strftime('%Y%m%dT%H%M%S')


def escape_ics(text: str) -> str:
    """Escape special characters for ICS text fields."""
    return (text
            .replace('\\', '\\\\')
            .replace(';', '\\;')
            .replace(',', '\\,')
            .replace('\n', '\\n'))


def build_ics(events: list, config: dict) -> str:
    """
    Build a complete ICS calendar string from a list of event dicts.

    Each event dict must have:
        name  (str)      — event title
        date  (datetime) — naive local datetime in Israel timezone
    """
    tz_name = 'Asia/Jerusalem'
    duration = timedelta(minutes=config.get('event_duration_minutes', 30))
    location = escape_ics(config.get('event_location', ''))
    reminders = config.get('reminder_minutes', [60, 1440])

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//SportPalaceCalendarSync//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        # Embed the timezone definition so importers handle DST correctly
        'BEGIN:VTIMEZONE',
        f'TZID:{tz_name}',
        'BEGIN:STANDARD',
        'DTSTART:19701025T020000',
        'TZOFFSETFROM:+0300',
        'TZOFFSETTO:+0200',
        'TZNAME:IST',
        'RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10',
        'END:STANDARD',
        'BEGIN:DAYLIGHT',
        'DTSTART:19700329T020000',
        'TZOFFSETFROM:+0200',
        'TZOFFSETTO:+0300',
        'TZNAME:IDT',
        'RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3',
        'END:DAYLIGHT',
        'END:VTIMEZONE',
    ]

    for event in events:
        start = event['date']           # naive datetime
        end   = start + duration
        uid   = str(uuid.uuid4())
        name  = escape_ics(event['name'])

        lines += [
            'BEGIN:VEVENT',
            f'UID:{uid}',
            f'DTSTART;TZID={tz_name}:{format_dt(start, tz_name)}',
            f'DTEND;TZID={tz_name}:{format_dt(end, tz_name)}',
            f'SUMMARY:{name}',
            f'LOCATION:{location}',
            f'DESCRIPTION:Sport Palace event\\nScraped automatically.',
        ]

        # Add one VALARM block per reminder
        for mins in reminders:
            lines += [
                'BEGIN:VALARM',
                'ACTION:DISPLAY',
                f'DESCRIPTION:Reminder: {name}',
                f'TRIGGER:-PT{mins}M',
                'END:VALARM',
            ]

        lines.append('END:VEVENT')

    lines.append('END:VCALENDAR')

    # ICS line endings must be CRLF (RFC 5545)
    return '\r\n'.join(lines) + '\r\n'


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Export Sport Palace events to an .ics file for bulk import',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ics_exporter.py
  python ics_exporter.py --output march_events.ics
  python ics_exporter.py --config my_config.json --output events.ics

How to import into Google Calendar:
  1. Run this script to generate the .ics file
  2. Open Google Calendar in your browser
  3. Click the gear icon → Settings
  4. In the left sidebar click "Import & Export"
  5. Click "Select file from your computer" and choose the .ics file
  6. Choose which calendar to add events to
  7. Click "Import"
        """
    )
    parser.add_argument('--config', default='config.json', metavar='FILE',
                        help='Path to config file (default: config.json)')
    parser.add_argument('--output', default='', metavar='FILE',
                        help='Output .ics filename (default: sportpalace_YYYY-MM-DD.ics)')
    args = parser.parse_args()

    print('=' * 55)
    print('Sport Palace ICS Exporter')
    print(f'Started : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 55)

    # Load config
    config = load_config(args.config)
    if not config:
        sys.exit(1)

    url = config.get('url', '')
    if not url:
        print('Error: "url" is missing from config.json')
        sys.exit(1)

    print(f'\nSource  : {url}')
    print(f'Duration: {config.get("event_duration_minutes", 30)} minutes per event')
    print(f'Location: {config.get("event_location", "")}')
    print(f'Timezone: Asia/Jerusalem')

    # Scrape events
    print('\nFetching events...')
    scraper = SportPalaceEventScraper(url)
    html = scraper.fetch_page()
    if not html:
        print('Failed to fetch page.')
        sys.exit(1)

    events = scraper.parse_events(html)
    if not events:
        print('No events found on the page.')
        print('Try running python test_scraper.py to inspect the page.')
        sys.exit(1)

    print(f'\nFound {len(events)} events:')
    print('-' * 55)
    for ev in events:
        print(f"  • {ev['name']}")
        print(f"    {ev['date'].strftime('%Y-%m-%d')}  {ev['time']}")

    # Build ICS content
    ics_content = build_ics(events, config)

    # Determine output filename
    output_file = args.output or f"sportpalace_{datetime.now().strftime('%Y-%m-%d')}.ics"
    Path(output_file).write_text(ics_content, encoding='utf-8')

    print(f'\n{"=" * 55}')
    print(f'ICS file saved: {output_file}')
    print(f'Events written: {len(events)}')
    print(f'{"=" * 55}')
    print()
    print('How to import into Google Calendar:')
    print('  1. Open calendar.google.com')
    print('  2. Gear icon → Settings')
    print('  3. Left sidebar → "Import & Export"')
    print('  4. Click "Select file" and choose:', output_file)
    print('  5. Pick your calendar and click "Import"')
    print()
    print(f'Finished: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 55)


if __name__ == '__main__':
    main()
