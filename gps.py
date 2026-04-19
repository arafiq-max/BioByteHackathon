import time
import requests
from datetime import datetime
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException

YOUR_WEBSITE_URL = "http://127.0.0.1:5000/api/location"
LIMIT_MINUTES = 5

def login():
    while True:
        apple_id = input("Enter Apple ID: ")
        password = input("Enter Password: ")
        
        try:
            api = PyiCloudService(apple_id, password)
            print("Login successful!")
            return api  
        except PyiCloudFailedLoginException:
            print("Wrong email or password, please try again.\n")

def main():
    api = login()

    # Handle 2FA
    if api.requires_2fa:
        code = input("Enter 2FA code sent to your device: ")
        api.validate_2fa_code(code)

    # Print all devices so user can verify exact name
    print("\nAvailable devices:")
    for device in api.devices:
        print(f" - {device}")
        
    device_name = input("\nEnter the exact name of the device to track: ")

    # Start timer when script runs
    start_time = datetime.now()
    print(f"\nTracking started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Will stop after {LIMIT_MINUTES} minutes\n")

    while True:
        # Calculate how long script has been running
        elapsed = datetime.now() - start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        running_for = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Stop after 5 minutes
        if elapsed.total_seconds() >= LIMIT_MINUTES * 60:
            print(f"\nStopped after {LIMIT_MINUTES} minutes.")
            print("Tracking complete!")
            break

        for device in api.devices:
            if device_name in str(device):
                try:
                    location = device.location
                    if callable(location):
                        location = location()

                    if not location:
                        print("Device may be offline, retrying in 10s...")
                        continue

                    payload = {
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "running_for": running_for
                    }
                    requests.post(YOUR_WEBSITE_URL, json=payload)
                    print(f"[{running_for}] Sent: {payload}")

                except Exception as e:
                    print(f"Error: {e}")

        time.sleep(10)

main()