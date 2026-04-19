"""
gps_tracker.py
──────────────
Runs on MacBook. Logs Apple Watch / iPhone GPS via iCloud
and posts location readings to the Flask website every 10 seconds.

Usage:
    pip install pyicloud requests
    python gps_tracker.py
"""

import time
import requests
from datetime import datetime
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException

# ── Config ────────────────────────────────────────────────────────────────
WEBSITE_URL   = "http://<WINDOWS_LAPTOP_IP>:5000/api/location"
# Replace <WINDOWS_LAPTOP_IP> with the actual IP of the Windows laptop
# running the Flask server (e.g. "http://192.168.1.42:5000/api/location")
# Both machines must be on the same WiFi network.

SAMPLE_INTERVAL = 10    # seconds between GPS pings — matches temp reader
TOTAL_DURATION  = 300   # 5 minutes — matches temp reader session length
# ─────────────────────────────────────────────────────────────────────────


def login():
    """Prompt for Apple ID credentials with retry on failure."""
    while True:
        apple_id = input("Enter Apple ID: ")
        password = input("Enter Password: ")
        try:
            api = PyiCloudService(apple_id, password)
            print("✓ Login successful!")
            return api
        except PyiCloudFailedLoginException:
            print("✗ Wrong email or password, please try again.\n")


def main():
    print("=" * 60)
    print("  UCSD Heat Study — GPS Tracker")
    print(f"  Session: {TOTAL_DURATION}s | Interval: {SAMPLE_INTERVAL}s")
    print(f"  Posting to: {WEBSITE_URL}")
    print("=" * 60)

    api = login()

    # Handle 2FA
    if api.requires_2fa:
        code = input("Enter 2FA code sent to your device: ")
        result = api.validate_2fa_code(code)
        if not result:
            print("✗ 2FA validation failed.")
            return
        print("✓ 2FA validated")

    # List devices
    print("\nAvailable devices:")
    for device in api.devices:
        print(f"  - {device}")

    device_name = input("\nEnter the exact name of the device to track: ")

    # Confirm device exists
    target = None
    for device in api.devices:
        if device_name in str(device):
            target = device
            break

    if not target:
        print(f"✗ Device '{device_name}' not found. Check spelling.")
        return

    start_time = datetime.now()
    print(f"\n✓ Tracking '{device_name}' started at {start_time.strftime('%H:%M:%S')}")
    print(f"  Will stop after {TOTAL_DURATION // 60} minutes\n")

    sample_count = 0
    readings_sent = 0

    while True:
        elapsed = datetime.now() - start_time
        elapsed_s = elapsed.total_seconds()

        if elapsed_s >= TOTAL_DURATION:
            print(f"\n✓ Session complete after {TOTAL_DURATION // 60} minutes.")
            print(f"  {readings_sent} GPS readings sent to website.")
            break

        hours, remainder = divmod(int(elapsed_s), 3600)
        minutes, seconds = divmod(remainder, 60)
        running_for = f"{hours:02}:{minutes:02}:{seconds:02}"
        remaining   = TOTAL_DURATION - elapsed_s

        print(f"[{running_for}] Fetching location... ({int(remaining)}s remaining)")

        try:
            location = target.location
            if callable(location):
                location = location()

            if not location:
                print("  ⚠ Device may be offline or location unavailable, retrying...")
                time.sleep(SAMPLE_INTERVAL)
                continue

            payload = {
                "latitude":    location["latitude"],
                "longitude":   location["longitude"],
                "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "unix_time":   time.time(),       # for interpolation with temp data
                "running_for": running_for,
                "device_name": device_name
            }

            # Post to Flask website
            try:
                r = requests.post(WEBSITE_URL, json=payload, timeout=5)
                if r.status_code == 200:
                    readings_sent += 1
                    print(f"  ✓ Lat: {payload['latitude']:.5f} | Lon: {payload['longitude']:.5f} → Posted ✓")
                else:
                    print(f"  ⚠ Website returned {r.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"  ⚠ Website not reachable at {WEBSITE_URL}")
                print(f"    Check that Flask is running and IP is correct.")

            sample_count += 1

        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(SAMPLE_INTERVAL)


if __name__ == "__main__":
    main()
