from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "Main Server Active 🟢"

@app.route("/health")
def health():
    return {"role": "PRIMARY", "status": "UP", "timestamp": time.time()}

if __name__ == "__main__":
    # Run on port 5000 to represent the main server
    app.run(host="127.0.0.1", port=5000)
