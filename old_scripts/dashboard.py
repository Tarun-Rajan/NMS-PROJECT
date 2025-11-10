from flask import Flask, render_template
import requests

app = Flask(__name__)

NODES = {
    "Primary": "http://127.0.0.1:5000/health",
    "Backup":  "http://127.0.0.1:5001/health"
}

def is_up(url):
    try:
        r = requests.get(url, timeout=1.5)
        return r.status_code == 200
    except:
        return False

@app.route("/")
def dashboard():
    data = {name: {"ip": url, "status": is_up(url)} for name, url in NODES.items()}
    return render_template("dashboard.html", devices=data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
