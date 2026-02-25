# Sport Palace Calendar Sync — User Guide

## How to Run

```bash
python run.py
```

That's it! The script will:
1. Fetch events from the Sport Palace website
2. Create them in your Google Calendar
3. Mark them with your chosen color
4. Send invitations to your configured email

---

## How to Customize Settings

Open **`config.json`** in any text editor (Notepad, VS Code, etc.) and modify:

```json
{
  "url": "https://www.sportpalace.co.il/menora-mivtachim/...",
  "target_email": "your-email@gmail.com",
  "event_duration_minutes": 30,
  "event_color": "11",
  "event_location": "Menora Mivtachim Arena, Tel Aviv",
  "reminder_minutes": [60, 1440]
}
```

### Settings Explained

| Setting | What it does | Examples |
|---|---|---|
| **url** | The webpage to scrape events from | Any Sport Palace events page |
| **target_email** | Who receives calendar invitations | `your@email.com` |
| **event_duration_minutes** | How long each event lasts | `30` = 30 min, `60` = 1 hour |
| **event_color** | Calendar color (Google color IDs) | `11` = Red, `9` = Blue, `10` = Green |
| **event_location** | Where the event takes place | Any address or venue name |
| **reminder_minutes** | When to send reminders before event | `[60, 1440]` = 1 hour + 1 day before |

---

## Google Calendar Color IDs

- `1` — Lavender
- `2` — Sage
- `3` — Grape
- `4` — Flamingo (Pink)
- `5` — Banana (Yellow)
- `6` — Tangerine (Orange)
- `7` — Peacock (Cyan)
- `8` — Graphite (Gray)
- `9` — Blueberry (Blue)
- `10` — Basil (Green)
- `11` — Tomato (Red) ⭐ Default

---

## Common Customizations

### Change the email
```json
"target_email": "newaddress@gmail.com"
```

### Change event duration to 1 hour
```json
"event_duration_minutes": 60
```

### Change color to blue
```json
"event_color": "9"
```

### Add more reminders
```json
"reminder_minutes": [30, 60, 1440]
```

---

## Running Automatically

### Windows Task Scheduler
1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name it: `Sport Palace Sync`
4. Trigger: **Weekly** (or Monthly)
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `run.py`
   - Start in: full path to this project folder
6. Click **Finish**

### macOS / Linux (cron)
```bash
# Every Sunday at 10:00 AM
0 10 * * 0 cd /path/to/sportpalace-calendar-sync && python3 run.py
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "No events found" | Run `python test_scraper.py` to inspect what's on the page |
| Authentication errors | Delete `token.pickle` and run again |
| Events created twice | Safe to ignore — the script skips existing events |
| `credentials.json not found` | Follow the Google API Setup in README.md |

---

## Files Reference

| File | Purpose | Edit? |
|---|---|---|
| `config.json` | Your settings | ✅ Yes — your main customization file |
| `event_scraper.py` | Main sync script | ⚠️ Only if you know Python |
| `test_scraper.py` | Preview events (no calendar changes) | ⚠️ Only if you know Python |
| `run.py` | Entry point | ✅ You can run this directly |
| `setup.py` | Install dependencies | Run once after cloning |
| `credentials.json` | Google API credentials | ❌ Do not edit — provided by Google |
| `token.pickle` | Saved authentication | ❌ Auto-generated |
| `requirements.txt` | Python packages | ❌ Do not edit |

---

## Tips

1. **Run it monthly** to get all upcoming events
2. **Check your calendar** after running to confirm events were created
3. **Adjust reminders** based on how far you travel to events
4. **Keep credentials.json safe** — it is your Google access key, never share it
