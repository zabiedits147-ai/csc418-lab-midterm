import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

RECEIVER_URL = os.environ.get("RECEIVER_URL", "http://localhost:5001/report")
RESULTS_FILE = "results.xml"


def parse_results(path):
    tests = []
    if not os.path.exists(path):
        return tests
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is not None:
            tests.append({
                "name": case.get("name"),
                "result": "failed",
                "failure_message": (problem.get("message") or "").strip(),
            })
        else:
            tests.append({"name": case.get("name"), "result": "passed"})
    return tests


def build_report():
    tests = parse_results(RESULTS_FILE)
    failed = sum(1 for t in tests if t["result"] == "failed")
    passed = len(tests) - failed
    overall = "passed" if tests and failed == 0 else "failed"
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "summary": {"total": len(tests), "passed": passed, "failed": failed},
        "overall_status": overall,
    }


if __name__ == "__main__":
    report = build_report()
    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    try:
        response = requests.post(RECEIVER_URL, json=report, timeout=10)
        response.raise_for_status()
        print("Report sent successfully.")
    except Exception as exc:
        print(f"Failed to send report: {exc}")
        sys.exit(1)