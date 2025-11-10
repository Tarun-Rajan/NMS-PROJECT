from flask import Flask, jsonify, request
import threading
import requests
import time
import sys

# Dictionary to keep track of running servers
running_servers = {}

def run_server(port):
    """Starts a Flask server instance on the given port."""
    app = Flask(__name__)

    @app.route("/")
    def index():
        return f"Server running on port {port} 🟢"

    @app.route("/health")
    def health():
        return jsonify({"status": "UP", "port": port})

    @app.route("/shutdown", methods=["POST"])
    def shutdown():
        """Shutdown endpoint to stop this Flask instance gracefully."""
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        func()
        return "Server shutting down..."

    # Store a thread reference for control
    running_servers[port] = threading.current_thread()
    print(f"[Server-{port}] ✅ started at http://127.0.0.1:{port}")
    try:
        app.run(port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[Server-{port}] ❌ Error: {e}")
    finally:
        if port in running_servers:
            del running_servers[port]
        print(f"[Server-{port}] stopped")


def stop_server(port):
    """Stops the Flask server running on given port (via /shutdown)."""
    try:
        requests.post(f"http://127.0.0.1:{port}/shutdown", timeout=1)
        print(f"[Server-{port}] 🟥 shutdown command sent")
    except Exception as e:
        print(f"[Server-{port}] ⚠️ could not stop: {e}")
