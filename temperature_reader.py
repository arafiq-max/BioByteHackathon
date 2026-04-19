"""
temperature_reader.py
─────────────────────
Runs on Windows laptop connected to Arduino Uno R3 via USB.
Reads temperature + humidity from Modulino Thermo over Serial,
posts each reading to the Flask website every 10 seconds.

Usage:
    pip install pyserial requests
    python temperature_reader.py
"""

import serial
import time
import requests
import csv
import os

# ── Config ────────────────────────────────────────────────────────────────
COM_PORT       = 'COM4'           # adjust if Arduino appears on different port
BAUD_RATE      = 9600
SAMPLE_INTERVAL = 10              # seconds between readings
TOTAL_DURATION  = 300             # 5 minutes total session
MAX_SAMPLES     = TOTAL_DURATION // SAMPLE_INTERVAL  # 30 readings
WEBSITE_URL     = "http://127.0.0.1:5000/api/temperature"
CSV_OUTPUT      = "temperature_session.csv"
HEAT_THRESHOLD  = 34.0            # °C — flag as heat event above this
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  UCSD Heat Study — Temperature Reader")
    print(f"  Port: {COM_PORT} | Baud: {BAUD_RATE}")
    print(f"  Session: {MAX_SAMPLES} readings over {TOTAL_DURATION}s")
    print(f"  Posting to: {WEBSITE_URL}")
    print("=" * 60)

    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=10)
    except Exception as e:
        print(f"❌ Could not open {COM_PORT}: {e}")
        print("   Check Device Manager for the correct COM port.")
        return

    time.sleep(3)
    ser.flushInput()

    readings = []
    sample_count = 0
    start_time = time.time()
    consecutive_hot = 0
    heat_event_active = False

    print(f"\nListening for data...\n")

    while sample_count < MAX_SAMPLES:
        elapsed   = time.time() - start_time
        remaining = TOTAL_DURATION - elapsed
        print(f"[{sample_count+1}/{MAX_SAMPLES}] Waiting... ({int(remaining)}s remaining)")

        try:
            raw  = ser.readline()
            line = raw.decode('utf-8', errors='ignore').strip()

            if not line:
                continue

            if line.startswith('#'):
                print(f"  Arduino: {line}")
                continue

            parts = line.split(',')

            # Arduino sends: timestamp_ms,temp_c,temp_f,humidity,heat_event
            # OR the simple example sketch: just temperature and humidity lines
            # Handle both formats
            temp_c = None
            humidity = None

            if len(parts) == 5:
                # Full CSV format from our custom sketch
                temp_c   = float(parts[1])
                temp_f   = float(parts[2])
                humidity = float(parts[3])
            elif len(parts) == 1:
                # Sometimes the simple sketch sends bare values — skip label lines
                try:
                    temp_c = float(parts[0])
                    temp_f = temp_c * 9.0 / 5.0 + 32.0
                    humidity = 0.0
                except ValueError:
                    print(f"  Skipping non-numeric line: {line}")
                    continue
            else:
                print(f"  ⚠ Unexpected format ({len(parts)} parts): {line}")
                continue

            if temp_c is None:
                continue

            # Heat event detection
            if temp_c >= HEAT_THRESHOLD:
                consecutive_hot += 1
            else:
                consecutive_hot = 0
                heat_event_active = False

            if consecutive_hot >= 3:
                heat_event_active = True

            payload = {
                "timestamp":   time.time(),
                "temp_c":      round(temp_c, 2),
                "temp_f":      round(temp_c * 9.0 / 5.0 + 32.0, 2),
                "humidity":    round(humidity, 2),
                "heat_event":  1 if heat_event_active else 0,
                # Field names website expects:
                "temperature": round(temp_c, 2),
                "device_name": "Arduino-Thermo"
            }

            readings.append(payload)
            sample_count += 1

            heat_label = " 🔥 HEAT EVENT" if heat_event_active else ""
            print(f"  ✓ Temp: {temp_c:.1f}°C | Humidity: {humidity:.1f}% | Heat: {heat_event_active}{heat_label}")

            # Post to website
            try:
                r = requests.post(WEBSITE_URL, json=payload, timeout=5)
                if r.status_code == 200:
                    print(f"  → Posted to website ✓")
                else:
                    print(f"  → Website returned {r.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"  → Website not reachable, saving locally only")

            time.sleep(SAMPLE_INTERVAL)

        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(1)

    # ── Session summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Session complete — {len(readings)} readings collected")
    print("=" * 60)

    if readings:
        temps  = [r['temp_c'] for r in readings]
        print(f"  Avg temp   : {sum(temps)/len(temps):.2f}°C")
        print(f"  Max temp   : {max(temps):.2f}°C")
        print(f"  Min temp   : {min(temps):.2f}°C")
        heat_n = sum(1 for r in readings if r['heat_event'] == 1)
        print(f"  Heat events: {heat_n}/{len(readings)} readings")

    # Save to CSV
    fieldnames = ["timestamp", "temp_c", "temp_f", "humidity", "heat_event"]
    with open(CSV_OUTPUT, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(readings)
    print(f"\n  Data saved to {CSV_OUTPUT}")

    ser.close()


if __name__ == "__main__":
    main()
