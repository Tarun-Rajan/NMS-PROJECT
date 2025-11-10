import time, requests, os
from modules.recovery import switch_to_backup, switch_to_primary

PRIMARY = "http://127.0.0.1:5000/health"
BACKUP  = "http://127.0.0.1:5001/health"

primary_was_up = True
using_backup = False

def check(url, timeout=2):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Monitor started (Ctrl+C to stop)")

    # start with primary active
    with open("active_server.txt", "w") as f:
        f.write("PRIMARY")

    while True:
        print("\n🔍 Polling servers...")
        p_up = check(PRIMARY)
        b_up = check(BACKUP)

        if p_up:
            print("Primary is 🟢 UP")
            if using_backup:
                switch_to_primary()
                using_backup = False
            primary_was_up = True
        else:
            print("Primary is 🔴 DOWN")
            if primary_was_up:
                print("❌ Primary just went DOWN. Initiating failover...")
                if b_up:
                    switch_to_backup()
                    using_backup = True
                else:
                    print("🚨 Both servers are DOWN!")
                primary_was_up = False

        if b_up:
            print("Backup is 🟢 UP")
        else:
            print("Backup is 🔴 DOWN")

        time.sleep(4)
