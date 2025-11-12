import time

class RecoveryManager:
    def __init__(self):
        self.active_server = None

    def switch_to_backup(self, servers, event_log):
        """Switch traffic to an available backup server."""
        backups = [s for s in servers if s["status"].upper() == "UP" and s["role"] == "Backup"]
        if not backups:
            event_log.append(f"[{time.strftime('%H:%M:%S')}] 🚨 No backup servers available for failover!")
            return None

        active = backups[0]
        self.active_server = active["name"]

        with open("active_server.txt", "w") as f:
            f.write(active["name"])

        event_log.append(f"[{time.strftime('%H:%M:%S')}] 🧭 Routing traffic to {active['name']} (port {active['port']})")
        return active
