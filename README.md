# Sport Palace Event Calendar Sync

Automatically extracts events from Sport Palace Menora Mivtachim Arena calendar and creates Google Calendar invitations.

## Features

- ✅ Scrapes events from Sport Palace website dynamically
- ✅ Creates 30-minute calendar events
- ✅ Marks events with RED color category
- ✅ Sends invitations to roman92b92@gmail.com
- ✅ Avoids duplicate events
- ✅ Uses exact event names and times from the website
- ✅ Mobile-optimized scraping

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Enable the **Google Calendar API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app"
   - Download the credentials file
   - Rename it to `credentials.json`
   - Place it in the project directory

### 3. Run the Script

```bash
python event_scraper.py
```

On first run:
- A browser window will open for Google authentication
- Sign in with your Google account
- Grant calendar access permissions
- The script will save the token for future runs

## How It Works

1. **Scrapes** the Sport Palace events page using mobile user agent
2. **Extracts** event details:
   - Event name (exactly as shown on website)
   - Date and time
   - Location (Menora Mivtachim Arena)

3. **Creates** Google Calendar events:
   - Duration: 30 minutes
   - Color: RED category
   - Attendee: roman92b92@gmail.com
   - Reminders: 1 hour before and 1 day before

4. **Sends** calendar invitations via email

## File Structure

```
sportpalace-calendar-sync/
├── event_scraper.py      # Main script
├── requirements.txt      # Python dependencies
├── credentials.json      # Google API credentials (you must add this)
├── token.pickle          # Auto-generated auth token
└── README.md            # This file
```

## Event Details

- **Duration**: 30 minutes from start time
- **Color**: Red (Google Calendar color ID 11)
- **Location**: Menora Mivtachim Arena, Tel Aviv
- **Timezone**: Asia/Jerusalem
- **Reminders**:
  - 1 hour before event
  - 1 day before event

## Running Periodically

To automatically sync events, you can:

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., weekly)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\Users\Roman\sportpalace-calendar-sync\event_scraper.py`

### Linux/Mac (cron)
```bash
# Run every week on Sunday at 10:00 AM
0 10 * * 0 cd /path/to/sportpalace-calendar-sync && python3 event_scraper.py
```

## Troubleshooting

### No events found
- The website structure might have changed
- Check if the URL is accessible
- Try running with verbose logging

### Authentication errors
- Make sure `credentials.json` is in the project directory
- Delete `token.pickle` and re-authenticate
- Verify Google Calendar API is enabled in your project

### Duplicate events
- The script checks for existing events before creating
- Events with the same name on the same day will be skipped

## Notes

- Events are extracted dynamically based on the current month
- The script handles Hebrew date formats
- Mobile version of the site is used for better structure
- All times are in Israel timezone (Asia/Jerusalem)

## Support

For issues or questions, check the script output for error messages.
