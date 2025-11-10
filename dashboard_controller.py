from flask import Flask, render_template, jsonify, request
import threading, time
from modules import server_template

# ----------------------------
# Initialize Flask app
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Global Variables
# ----------------------------
servers = []      # List of all servers in simulation
logs = []         # Event logs for dashboard
lock = threading.Lock()

BASE_PORT = 5000  # Starting port for servers


# ----------------------------
# Utility Functions
# ----------------------------
def add_log(message):
    """Append messages to log list safely."""
    with lock:
        timestamp = time.strftime("[%H:%M:%S]")
        logs.append(f"{timestamp} {message}")
        print(f"{timestamp} {message}")


def get_next_port():
    """Assign next available port dynamically."""
    return BASE_PORT + len(servers)


# ----------------------------
# Flask Routes
# ----------------------------
@app.route("/")
def index():
    """Dashboard main page."""
    return render_template("dashboard.html")


@app.route("/add_server", methods=["POST"])
def add_server():
    """Add a new server to the simulation."""
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
    """Start a specific server."""
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
    """Simulate failure (gracefully stop the Flask server)."""
    srv = servers[server_id - 1]
    if srv["status"] == "DOWN":
        return jsonify({"message": "Server already down"})

    server_template.stop_server(srv["port"])
    srv["status"] = "DOWN"
    add_log(f"💥 {srv['name']} on port {srv['port']} failed (stopped)")
    return jsonify({"message": f"{srv['name']} failed"})


@app.route("/recover_server/<int:server_id>")
def recover_server(server_id):
    """Recover a failed server by restarting its Flask app."""
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
    """Return server info safely (without sending Thread objects)."""
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
    """Return recent log entries."""
    with lock:
        return jsonify({"logs": logs[-50:]})  # Last 50 entries


# ----------------------------
# Launch Flask App
# ----------------------------
if __name__ == "__main__":
    add_log("🌐 Dashboard Controller started")
    app.run(host="127.0.0.1", port=8000, debug=True)
