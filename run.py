#!/usr/bin/env python3
"""
Run the Sport Palace Calendar Sync.
Cross-platform replacement for RUN_SCRAPER.bat
"""

import sys
import subprocess
from pathlib import Path


def main():
    print("=" * 50)
    print("Sport Palace Calendar Sync")
    print("=" * 50)

    # Check config.json exists
    if not Path("config.json").exists():
        print("\nconfig.json not found!")
        print("Copy config.example.json to config.json and fill in your email.")
        print("\n  Windows : copy config.example.json config.json")
        print("  Mac/Linux: cp config.example.json config.json")
        sys.exit(1)

    # Check credentials.json exists
    if not Path("credentials.json").exists():
        print("\ncredentials.json not found!")
        print("Follow the Google API setup in README.md to download your credentials.")
        sys.exit(1)

    print("\nStarting scraper...\n")
    result = subprocess.run([sys.executable, "event_scraper.py"])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
