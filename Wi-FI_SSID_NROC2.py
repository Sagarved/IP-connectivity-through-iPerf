import subprocess
import time
from datetime import datetime
TARGET_IP = "192.168.10.1"
GOOGLE_IP = "8.8.8.8"
RESULT = []
MAX_FAILED_PINGS = 2
LOG_FILE = "ping_failure_log.txt"
PING_INTERVAL = 5  # seconds between pings


def is_ping_successful():
    try:
        result = subprocess.run(["ping", "-n", "1", TARGET_IP],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print(result)

        result_google = subprocess.run(["ping", "-n", "1", GOOGLE_IP],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result_google.returncode != 0:
            print(result_google)
        return result.returncode == 0 and result_google.returncode == 0
    except Exception:
        return False

def log_failure(failed_count):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] Ping failed more than {failed_count} times."
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def main():
    failed_count = 0
    print(f"Monitoring ping to {TARGET_IP, GOOGLE_IP}... (press Ctrl+C to stop)")

    while True:
        if is_ping_successful():
            # print(f"[{datetime.now().strftime('%H:%M:%S')}] Ping successful.")
            failed_count = 0
        else:
            failed_count += 1
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping failed ({failed_count})")

            if failed_count > MAX_FAILED_PINGS:
                log_failure(failed_count)
                # failed_count = 0  # reset counter after logging

        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()