# modules/recovery.py
import time

class RecoveryManager:
    def __init__(self):
        self.active_server = None

    def switch_to_backup(self, servers, event_log):
        """Switch to the next available backup and swap roles dynamically."""
        # Find primary and backup
        primary = next((s for s in servers if s["role"] == "Primary"), None)
        backups = [s for s in servers if s["status"].upper() == "UP" and s["role"] == "Backup"]

        if not backups:
            event_log.append(f"[{time.strftime('%H:%M:%S')}] 🚨 No backup servers available for failover!")
            return None

        # Promote first available backup
        new_primary = backups[0]
        old_primary = primary

        if old_primary:
            old_primary["role"] = "Backup"
            old_primary["status"] = "DOWN"

        new_primary["role"] = "Primary"
        self.active_server = new_primary["name"]

        with open("active_server.txt", "w") as f:
            f.write(new_primary["name"])

        event_log.append(f"[{time.strftime('%H:%M:%S')}] 🔁 Failover activated — {new_primary['name']} promoted to Primary")
        event_log.append(f"[{time.strftime('%H:%M:%S')}] 🧭 Routing traffic to {new_primary['name']} (port {new_primary['port']})")

        return new_primary

    def restore_primary(self, servers, event_log):
        """When the old primary comes back, switch roles back."""
        primary = next((s for s in servers if s["role"] == "Primary"), None)
        recovered = next((s for s in servers if s["status"].upper() == "UP" and s["role"] == "Backup"), None)

        if primary and recovered:
            event_log.append(f"[{time.strftime('%H:%M:%S')}] 🔄 Old primary recovered — restoring roles...")

            # Swap roles back
            primary["role"], recovered["role"] = "Backup", "Primary"
            self.active_server = recovered["name"]

            event_log.append(f"[{time.strftime('%H:%M:%S')}] 🟢 {recovered['name']} restored as Primary server.")
            return recovered

        return None
