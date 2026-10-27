import json
import os

from flask import Flask, request, jsonify

REPORT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-report.json")

app = Flask(__name__)


@app.route("/report", methods=["POST"])
def receive_report():
    report = request.get_json(silent=True)
    if report is None:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Report received and saved to test-report.json")
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def home():
    return "Receiver is running. Send reports to POST /report"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)