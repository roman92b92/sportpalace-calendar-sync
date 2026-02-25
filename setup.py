#!/usr/bin/env python3
"""
Setup script — check Python version and install dependencies.
Cross-platform replacement for INSTALL_PYTHON.bat
"""

import sys
import subprocess
import webbrowser
from pathlib import Path


REQUIRED_PYTHON = (3, 8)
PYTHON_DOWNLOAD_URL = "https://www.python.org/downloads/"


def check_python_version():
    current = sys.version_info[:2]
    if current < REQUIRED_PYTHON:
        print(f"Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ is required.")
        print(f"Current version: {sys.version}")
        print(f"\nOpening download page: {PYTHON_DOWNLOAD_URL}")
        webbrowser.open(PYTHON_DOWNLOAD_URL)
        return False
    print(f"Python {sys.version.split()[0]} — OK")
    return True


def install_dependencies():
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("requirements.txt not found!")
        return False

    print("\nInstalling dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        capture_output=True, text=True
    )
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        text=True
    )
    return result.returncode == 0


def main():
    print("=" * 50)
    print("Sport Palace Calendar Sync — Setup")
    print("=" * 50)

    if not check_python_version():
        sys.exit(1)

    if not install_dependencies():
        print("\nFailed to install dependencies.")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Copy config.example.json to config.json")
    print("     and set your email address")
    print("  2. Follow the Google API setup in README.md")
    print("     to get your credentials.json")
    print("  3. Run: python run.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
