import threading
import time
import requests

class Monitor(threading.Thread):
    def __init__(self, servers, event_log, recovery_manager):
        super().__init__(daemon=True)
        self.servers = servers
        self.event_log = event_log
        self.recovery_manager = recovery_manager

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]")
        entry = f"{timestamp} {message}"
        print(entry)
        self.event_log.append(entry)

    def run(self):
        print("[DEBUG] Monitor thread running and polling servers...")
        time.sleep(5)  # allow all servers to boot before monitoring starts

        while True:
            # If no servers are currently UP, wait and retry
            if not any(s["status"].upper() == "UP" for s in self.servers):
                time.sleep(2)
                continue

            for srv in self.servers:
                name = srv["name"]
                port = srv["port"]
                status = srv["status"]

                try:
                    print(f"[DEBUG] Checking {name} /health ...")
                    res = requests.get(f"http://127.0.0.1:{port}/health", timeout=1.5)
                    print(f"[DEBUG] Response from {name}: {res.status_code}")
                    if res.status_code == 200:
                        if status != "UP":
                            srv["status"] = "UP"
                            self.log(f"🟢 {name} on port {port} is UP again")
                        continue
                except Exception:
                    if srv["status"] == "UP":  # only mark it down once
                        srv["status"] = "DOWN"
                        self.log(f"❌ {name} on port {port} failed (stopped)")

                        # Trigger automatic recovery
                        new_active = self.recovery_manager.switch_to_backup(self.servers, self.event_log)
                        if new_active:
                            self.log(f"🔁 Switched active server to {new_active['name']}")
                            self.log(f"🧭 Routing traffic to {new_active['name']} (port {new_active['port']})")

            time.sleep(2)
