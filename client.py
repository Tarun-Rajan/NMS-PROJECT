import time
import requests
import os

def get_active():
    """Read which server is active (PRIMARY or BACKUP)."""
    if os.path.exists("active_server.txt"):
        with open("active_server.txt") as f:
            return f.read().strip()
    return "PRIMARY"

while True:
    active = get_active()

    # Choose the server URL based on active role
    if active == "PRIMARY":
        url = "http://127.0.0.1:5000"
    else:
        url = "http://127.0.0.1:5001"

    try:
        r = requests.get(url, timeout=2)
        print(f"[Client] Connected to {active} server → {r.text}")
    except Exception as e:
        print(f"[Client] ❌ Could not reach {active} server: {e}")

    time.sleep(3)
