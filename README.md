# Sport Palace Calendar Sync

> Automatically scrape events from Sport Palace Menora Mivtachim Arena and add them to Google Calendar — either via the API (direct sync) or via an ICS file (bulk import).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## Table of Contents

- [What It Does](#what-it-does)
- [Two Ways to Sync](#two-ways-to-sync)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Method 1 — Direct API Sync](#method-1--direct-api-sync)
- [Method 2 — ICS File Export](#method-2--ics-file-export)
- [Customization](#customization)
- [Running Automatically](#running-automatically)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

## What It Does

Sport Palace Calendar Sync scrapes the Sport Palace events page, extracts upcoming events (name, date, time), and adds them to your Google Calendar. You choose how:

| Method | How it works | Google API needed? |
|---|---|---|
| **Direct API sync** | Creates events in your calendar instantly via the Google Calendar API | Yes |
| **ICS file export** | Generates a `.ics` file you import manually into any calendar app | No |

---

## Two Ways to Sync

### Method 1 — Direct API (`event_scraper.py`)
- Requires Google API credentials (`credentials.json`)
- Creates events instantly in your calendar
- Sends email invitations to your configured address
- Skips duplicates automatically on re-runs

### Method 2 — ICS Export (`ics_exporter.py`)
- **No Google API setup required**
- Generates a standard `.ics` file
- Import into Google Calendar, Outlook, Apple Calendar — any app
- Useful for bulk imports or sharing with others

---

## Prerequisites

- **Python 3.8+** — [Download Python](https://www.python.org/downloads/)
- For **Method 1 only**: A Google account + Google Calendar API credentials (see setup below)

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/roman92b92/sportpalace-calendar-sync.git
cd sportpalace-calendar-sync

# 2. Install dependencies
python setup.py

# 3. Create your config file
cp config.example.json config.json        # macOS / Linux
copy config.example.json config.json      # Windows
# Edit config.json — set your email address

# 4a. ICS export (no API needed)
python ics_exporter.py

# 4b. OR direct API sync (requires credentials.json — see below)
python run.py
```

> **Note:** `config.json`, `credentials.json`, and `token.pickle` are all in `.gitignore` — your credentials will never be committed.

---

## Configuration

Copy `config.example.json` to `config.json` and fill in your values:

```json
{
  "url": "https://www.sportpalace.co.il/menora-mivtachim/%D7%9C%D7%95%D7%97-%D7%90%D7%A8%D7%95%D7%A2%D7%99%D7%9D/",
  "target_email": "your-email@gmail.com",
  "event_duration_minutes": 30,
  "event_color": "11",
  "event_location": "Menora Mivtachim Arena, Tel Aviv",
  "reminder_minutes": [60, 1440]
}
```

| Key | Description |
|---|---|
| `url` | The Sport Palace events page to scrape |
| `target_email` | Your email — receives calendar invitations (Method 1 only) |
| `event_duration_minutes` | How long each event lasts (default: 30 minutes) |
| `event_color` | Google Calendar color ID (see [Color IDs](#color-ids)) |
| `event_location` | Location shown on calendar events |
| `reminder_minutes` | List of reminder times in minutes before the event |

---

## Method 1 — Direct API Sync

Uses the Google Calendar API to create events directly. Requires a one-time credentials setup.

### Google API Setup

#### Step 1 — Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name it (e.g. `Sport Palace Calendar`) and click **Create**

#### Step 2 — Enable the Google Calendar API

1. Go to **APIs & Services** → **Library**
2. Search for **Google Calendar API** → click **Enable**

#### Step 3 — Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure the consent screen:
   - User Type: **External**
   - App name: `Sport Palace Calendar`
   - Fill in your email for support and developer contact
   - Click through all steps
4. Application type: **Desktop app** → Click **Create**
5. Click **Download** (⬇️) → save as **`credentials.json`** in this folder

#### Step 4 — Run

```bash
python run.py
```

On first run, a URL will be printed — open it in your browser, sign in, and click Allow. The token is saved automatically for future runs.

---

## Method 2 — ICS File Export

No Google API credentials needed. Generates a `.ics` file you can import into any calendar app.

### Run

```bash
python ics_exporter.py
```

### Options

```bash
# Custom output filename
python ics_exporter.py --output march_events.ics

# Custom config file
python ics_exporter.py --config my_config.json --output events.ics
```

### How to import into Google Calendar

1. Run `python ics_exporter.py` — a file like `sportpalace_2025-03-01.ics` is created
2. Open [calendar.google.com](https://calendar.google.com)
3. Click the **gear icon** → **Settings**
4. In the left sidebar click **"Import & Export"**
5. Click **"Select file from your computer"** and choose the `.ics` file
6. Select which calendar to add events to
7. Click **Import**

All events are added at once. Reminders are included in the file.

### How to import into other calendar apps

| App | Steps |
|---|---|
| **Outlook** | File → Open & Export → Import/Export → Import an iCalendar file |
| **Apple Calendar** | File → Import → select the `.ics` file |
| **Thunderbird** | Calendar → Events and Tasks → Import |

---

## Usage Summary

| Command | What it does |
|---|---|
| `python setup.py` | Install dependencies |
| `python test_scraper.py` | Preview events without touching your calendar |
| `python run.py` | Run the full API sync (requires credentials.json) |
| `python event_scraper.py` | Same as run.py but without pre-flight checks |
| `python ics_exporter.py` | Generate an `.ics` file for bulk import |

---

## Customization

### Color IDs

| ID | Color |
|---|---|
| `1` | Lavender |
| `2` | Sage |
| `3` | Grape |
| `4` | Flamingo (Pink) |
| `5` | Banana (Yellow) |
| `6` | Tangerine (Orange) |
| `7` | Peacock (Cyan) |
| `8` | Graphite (Gray) |
| `9` | Blueberry (Blue) |
| `10` | Basil (Green) |
| `11` | Tomato (Red) |

### Reminder examples

```json
"reminder_minutes": [30]           // 30 minutes before
"reminder_minutes": [60, 1440]     // 1 hour and 1 day before
"reminder_minutes": [30, 60, 1440] // 30 min, 1 hour, and 1 day before
```

---

## Running Automatically

### Windows — Task Scheduler

1. Open **Task Scheduler** → **Create Basic Task**
2. Name: `Sport Palace Sync` | Trigger: **Weekly**
3. Action: Start a program
   - Program: `python`
   - Arguments: `run.py` (or `ics_exporter.py`)
   - Start in: full path to this folder
4. Click Finish

### macOS / Linux — cron

```bash
# Every Sunday at 10:00 AM — API sync
0 10 * * 0 cd /path/to/sportpalace-calendar-sync && python3 run.py

# Or generate ICS file weekly
0 10 * * 0 cd /path/to/sportpalace-calendar-sync && python3 ics_exporter.py
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `credentials.json not found` | Follow [Google API Setup](#google-api-setup) |
| No events found | Run `python test_scraper.py` to inspect what's on the page |
| Authentication errors | Delete `token.pickle` and run again |
| Events created twice | Safe — the script skips existing events automatically |
| Encoding errors on Windows | Use Python 3.8+ — encoding is set automatically |

---

## Project Structure

```
sportpalace-calendar-sync/
├── event_scraper.py       # Method 1 — scrape + create events via Google Calendar API
├── ics_exporter.py        # Method 2 — scrape + export to .ics file for bulk import
├── test_scraper.py        # Preview events without touching your calendar
├── run.py                 # Entry point for Method 1 (pre-flight checks + run)
├── setup.py               # Install dependencies (checks Python version)
├── config.example.json    # Config template (copy to config.json and edit)
├── requirements.txt       # Python dependencies
├── .gitignore             # Excludes credentials, tokens, and config from git
├── USER_GUIDE.md          # Quick reference guide
└── README.md              # This file
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Disclaimer

> **Use at your own risk.**

This tool scrapes publicly available event information from the Sport Palace website. Ensure your usage complies with the website's terms of service.
