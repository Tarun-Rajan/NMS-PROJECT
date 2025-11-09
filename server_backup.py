from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "Backup Server Active 🟢"

@app.route("/health")
def health():
    return {"role": "BACKUP", "status": "UP", "timestamp": time.time()}

if __name__ == "__main__":
    # Run on a different port (5001)
    app.run(host="127.0.0.1", port=5001)
