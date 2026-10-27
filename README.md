# CSC418 Lab Midterm - Assignment Submission Portal

A simple Flask portal where students submit their name, registration number, assignment title and submission URL. Every push is tested automatically by GitHub Actions, and the test report is sent to a local receiver which saves it as `test-report.json`.

## Setup

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt

## Run the application

    python app.py

Open http://127.0.0.1:5000 in the browser.

## Run the tests

    python -m pytest -v

Tests included:
1. Complete details and valid URL: submission is saved and listed
2. Missing registration number: rejected with validation message
3. Invalid URL: rejected and not saved

## Start the local report receiver

    python receiver.py

The receiver listens on http://localhost:5001/report and saves every received report to `test-report.json`.

## CI pipeline

The workflow `.github/workflows/ci.yml` runs on every push on a self-hosted runner (my own computer), so the runner can reach localhost:5001 directly. Steps:
1. Install dependencies
2. Run pytest (a failing test fails the pipeline)
3. Run `send_report.py`, which builds the JSON report (repository, branch, commit SHA, run ID, timestamp, each test result, totals and overall status) and sends it to the receiver. This step uses `if: always()`, so the report is sent for both passing and failing runs.

To start the runner (from the runner folder):

    .\run.cmd

Keep both the receiver and the runner running during the demonstration.