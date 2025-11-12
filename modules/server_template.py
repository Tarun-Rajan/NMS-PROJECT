from flask import Flask, jsonify, request
import threading
import requests

# Store running threads for reference
running_servers = {}


def create_app(port):
    """Factory to create a Flask app bound to a specific port."""
    app = Flask(__name__)

    @app.route("/")
    def index():
        return f"✅ Server running on port {port}"

    @app.route("/health")
    def health():
        return jsonify({"status": "UP", "port": port}), 200

    @app.route("/shutdown", methods=["POST", "GET"])
    def shutdown():
        """Gracefully stop this Flask app."""
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        func()
        return "Server shutting down..."

    return app


def run_server(port):
    """Run a Flask app on the given port in its own thread."""
    app = create_app(port)
    print(f"[Server-{port}] ✅ started at http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def stop_server(port):
    """Stop a running Flask server via /shutdown."""
    try:
        requests.post(f"http://127.0.0.1:{port}/shutdown", timeout=1)
        print(f"[Server-{port}] 🟥 Shutdown command sent.")
    except Exception as e:
        print(f"[Server-{port}] ⚠️ Could not stop: {e}")
