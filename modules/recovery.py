# recovery.py
def switch_to_backup():
    with open("active_server.txt", "w") as f:
        f.write("BACKUP")
    print("🧭 Routing traffic to BACKUP server (port 5001).")
    print("✅ Disaster Recovery action completed.")

def switch_to_primary():
    with open("active_server.txt", "w") as f:
        f.write("PRIMARY")
    print("🔁 Switching back to PRIMARY server (port 5000).")
    print("✅ Primary restored.")
