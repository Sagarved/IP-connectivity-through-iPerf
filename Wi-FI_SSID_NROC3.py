# This will captured netsh Wi-Fi parameters

import subprocess
import time
import re
from datetime import datetime
TARGET_IP = "192.168.10.1"
GOOGLE_IP = "8.8.8.8"
RESULT = []
MAX_FAILED_PINGS = 2
PING_INTERVAL = 5  # seconds between pings
LOG_FILE = "ping_failure_with_wifi_log_12_2025.txt"

LAST_CONNECTED =  []

def is_ping_successful():
    try:
        result = subprocess.run(["ping", "-n", "1", TARGET_IP],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            # print(result)
            # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping failed {result}")
            pass
            

        result_google = subprocess.run(["ping", "-n", "1", GOOGLE_IP],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result_google.returncode != 0:
            # print(result_google)
            # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping failed {result_google}")
            pass

        return result.returncode == 0 and result_google.returncode == 0
    except Exception as e:
        return False

def wifi_param():
    try:
        result_wifi = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, encoding="utf-8")
        # print(result)
        # print(type(result))
        # print(result.stdout, type(result.stdout))
        output = result_wifi.stdout
        # print(output[:2000])
        def find(pattern):
            m = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            return m.group(1).strip() if m else None

        ssid    = find(r"^\s*SSID\s*:\s*(.+)$")
        rssi = find(r"^\s*Rssi\s*:\s*(-?\d+)")

        # to keep it flexible if netsh prints BSSID or BSSID 1 etc:
        # bssid   = find(r"^\s*BSSID(?:\s*\d*)?\s*:\s*([0-9A-Fa-f:-]+)")
        bssid = find(r"^\s*(?:AP\s+)?BSSID(?:\s*\d*)?\s*:\s*([0-9A-Fa-f:-]+)")

        channel = find(r"^\s*Channel\s*:\s*(\d+)")
        return {
        "SSID": ssid,
        "signal_RSSI": rssi,   # percent as reported by netsh
        "BSSID": bssid,                 # AP MAC
        "channel": int(channel) if channel else None
        }
    except:
        return False
        
def log_failure(failed_count, wifi):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] Ping failed more than {failed_count} times{wifi}."
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def main():
    failed_count = 0
    print(f"Monitoring ping to {TARGET_IP, GOOGLE_IP}... (press Ctrl+C to stop)")

    while True:
        if is_ping_successful():
            if is_ping_successful(): # Measuring twice before clearing
                # print(f"[{datetime.now().strftime('%H:%M:%S')}] Ping successful.")
                failed_count = 0
        else:
            failed_count += 1
            if not is_ping_successful(): # Measuring twice
                wifi_x = wifi_param()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping failed ({failed_count}, {wifi_x})")

            if failed_count > MAX_FAILED_PINGS:
                log_failure(failed_count, wifi_x)
                # failed_count = 0  # reset counter after logging

        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()
    # print(is_ping_successful(), wifi_param())