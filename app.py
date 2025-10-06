from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/")
def index():
    return jsonify({
        "message": "plataforma-checker: no poller scaffolded yet",
        "env": {
            "POLL_INTERVAL": os.getenv("POLL_INTERVAL", "20"),
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
