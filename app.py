from flask import Flask, jsonify
import os
from datetime import datetime
import threading
import time

from poller import run_once

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
        "message": "plataforma-checker: poller running",
        "env": {
            "POLL_INTERVAL": os.getenv("POLL_INTERVAL", "20"),
        }
    })


@app.route('/run-poll')
def run_poll():
    ok = run_once()
    return jsonify({'ran': ok})


def _background_poller():
    interval = int(os.getenv('POLL_INTERVAL', '20'))
    while True:
        try:
            run_once()
        except Exception:
            pass
        time.sleep(interval * 60)


def start_background_poller():
    t = threading.Thread(target=_background_poller, daemon=True)
    t.start()


if __name__ == "__main__":
    # start poller thread when running locally
    start_background_poller()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
