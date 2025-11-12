# modules/server_template.py
from flask import Flask, jsonify, request
import multiprocessing
import requests
import time
from waitress import serve

# Store active processes by port
active_processes = {}

def create_app(port):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return f"✅ Mini-server running on port {port}"

    @app.route("/health")
    def health():
        return jsonify({"status": "UP", "port": port}), 200

    @app.route("/shutdown", methods=["POST", "GET"])
    def shutdown():
        func = request.environ.get("werkzeug.server.shutdown")
        if func:
            func()
        print(f"[Server-{port}] 🟥 Shutting down on request")
        return "Server shutting down…", 200

    return app


def run_server_instance(port):
    """Target function for new process."""
    app = create_app(port)
    print(f"[Server-{port}] ✅ Waitress serving on http://127.0.0.1:{port}")
    serve(app, host="127.0.0.1", port=port, threads=2)


def run_server(port):
    """Start a new server process."""
    if port in active_processes:
        print(f"[Server-{port}] ⚠ Already running")
        return

    print(f"[Server-{port}] 🚀 Launching new Waitress process...")
    p = multiprocessing.Process(target=run_server_instance, args=(port,))
    p.daemon = False
    p.start()
    active_processes[port] = p
    time.sleep(2)
    print(f"[Server-{port}] ✅ Process started (PID={p.pid})")
    return p


def stop_server(port):
    """Stop the process cleanly."""
    print(f"[Server-{port}] 🟥 Attempting graceful shutdown...")
    try:
        requests.post(f"http://127.0.0.1:{port}/shutdown", timeout=1)
    except Exception:
        pass

    proc = active_processes.get(port)
    if proc and proc.is_alive():
        proc.terminate()
        proc.join(timeout=1)
        print(f"[Server-{port}] ❌ Terminated (PID={proc.pid})")

    active_processes.pop(port, None)


if __name__ == "__main__":
    run_server_instance(5000)
