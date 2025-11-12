from flask import Flask, render_template, jsonify, request
import threading, time, requests
from modules import server_template
from modules.monitor_thread import Monitor
from modules.recovery import RecoveryManager

app = Flask(__name__)

servers = []
logs = []
lock = threading.Lock()

BASE_PORT = 5000

def add_log(message):
    with lock:
        timestamp = time.strftime("[%H:%M:%S]")
        logs.append(f"{timestamp} {message}")
        print(f"{timestamp} {message}")

def get_next_port():
    return BASE_PORT + len(servers)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/add_server", methods=["POST"])
def add_server():
    name = request.form.get("name", f"Server {len(servers) + 1}")
    port = get_next_port()
    new_server = {
        "id": len(servers) + 1,
        "name": name,
        "port": port,
        "status": "DOWN",
        "role": "Primary" if not servers else "Backup",
        "thread": None
    }
    servers.append(new_server)
    add_log(f"🟢 Added {name} ({new_server['role']}) on port {port}")
    return jsonify({"message": f"{name} added successfully"})

@app.route("/start_server/<int:server_id>")
def start_server(server_id):
    srv = servers[server_id - 1]
    if srv["status"] == "UP":
        return jsonify({"message": "Server already running"})
    t = threading.Thread(target=server_template.run_server, args=(srv["port"],))
    t.daemon = True
    t.start()
    srv["thread"] = t
    srv["status"] = "UP"
    add_log(f"▶️ Started {srv['name']} on port {srv['port']}")
    return jsonify({"message": f"{srv['name']} started"})

@app.route("/fail_server/<int:server_id>")
def fail_server(server_id):
    srv = servers[server_id - 1]
    if srv["status"] == "DOWN":
        return jsonify({"message": "Server already down"})
    add_log(f"⚠ Simulating crash for {srv['name']} on port {srv['port']}")
    try:
        requests.get(f"http://127.0.0.1:{srv['port']}/shutdown", timeout=1)
    except Exception:
        pass
    return jsonify({"message": f"Simulated crash for {srv['name']}."})

@app.route("/recover_server/<int:server_id>")
def recover_server(server_id):
    srv = servers[server_id - 1]
    if srv["status"] == "UP":
        return jsonify({"message": "Server already running"})
    t = threading.Thread(target=server_template.run_server, args=(srv["port"],))
    t.daemon = True
    t.start()
    srv["thread"] = t
    srv["status"] = "UP"
    add_log(f"🔁 {srv['name']} recovered and restarted on port {srv['port']}")
    return jsonify({"message": f"{srv['name']} recovered"})

@app.route("/status")
def get_status():
    safe_servers = []
    for s in servers:
        safe_servers.append({
            "id": s["id"],
            "name": s["name"],
            "port": s["port"],
            "role": s["role"],
            "status": s["status"],
        })
    return jsonify({"servers": safe_servers})

@app.route("/logs")
def get_logs():
    with lock:
        return jsonify({"logs": logs[-50:]})

if __name__ == "__main__":
    add_log("🌐 Dashboard Controller started")

    recovery_manager = RecoveryManager()
    monitor_thread = Monitor(servers, logs, recovery_manager)
    monitor_thread.start()
    print("[DEBUG] Monitor thread started ✓")

    app.run(host="127.0.0.1", port=8000, debug=True)
