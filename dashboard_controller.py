from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime

app = Flask(__name__)
servers = []
logs = []
lock = threading.Lock()

BASE_PORT = 5000
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    logs.append(entry)
    print(entry)

def assign_primary():
    """Ensure exactly ONE primary server at all times."""
    up_servers = [s for s in servers if s["status"] == "UP"]

    if not up_servers:
        return
    current_primary = next((s for s in up_servers if s["role"] == "Primary"), None)

    if current_primary:
        return
    new_primary = up_servers[0]
    new_primary["role"] = "Primary"
    log(f"⚡ AUTO-PRIMARY → {new_primary['name']} promoted to Primary")
    for s in servers:
        if s != new_primary:
            s["role"] = "Backup"

@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/add_server", methods=["POST"])
def add_server():
    name = request.form.get("name", f"Server {len(servers) + 1}")
    port = BASE_PORT + len(servers)

    new_server = {
        "id": len(servers) + 1,
        "name": name,
        "port": port,
        "role": "Backup",     
        "status": "DOWN",
        "last_updated": "--",
        "response_time": "--"
    }

    servers.append(new_server)
    log(f"🟢 Added server {name} on port {port}")
    return jsonify({"message": "Server added"})


@app.route("/start_server/<int:server_id>")
def start_server(server_id):
    srv = servers[server_id - 1]
    t0 = time.time()
    time.sleep(0.3)
    t1 = time.time()

    srv["status"] = "UP"
    srv["response_time"] = round(t1 - t0, 3)
    srv["last_updated"] = datetime.now().strftime("%H:%M:%S")

    log(f"▶ Started {srv['name']} in {srv['response_time']}s")

    assign_primary()

    return jsonify({"message": "Server started"})


@app.route("/fail_server/<int:server_id>")
def fail_server(server_id):
    srv = servers[server_id - 1]
    t0 = time.time()
    time.sleep(0.2)
    t1 = time.time()

    srv["status"] = "DOWN"
    srv["response_time"] = round(t1 - t0, 3)
    srv["last_updated"] = datetime.now().strftime("%H:%M:%S")

    log(f"❌ FAILED → {srv['name']} (response {srv['response_time']}s)")
    if srv["role"] == "Primary":
        log(f"⚠ Primary {srv['name']} failed → Attempting failover")
        assign_primary()

    return jsonify({"message": "Server failed"})


@app.route("/recover_server/<int:server_id>")
def recover_server(server_id):
    srv = servers[server_id - 1]
    t0 = time.time()
    time.sleep(0.5)
    t1 = time.time()

    srv["status"] = "UP"
    srv["response_time"] = round(t1 - t0, 3)
    srv["last_updated"] = datetime.now().strftime("%H:%M:%S")

    log(f"🔁 Recovered {srv['name']} in {srv['response_time']}s")

    assign_primary()

    return jsonify({"message": "Server recovered"})


@app.route("/status")
def status():
    return jsonify({"servers": servers})


@app.route("/logs")
def get_logs():
    return jsonify({"logs": logs[-100:]})

if __name__ == "__main__":
    log("🌐 Dashboard started")
    app.run(host="127.0.0.1", port=8000, debug=True)
