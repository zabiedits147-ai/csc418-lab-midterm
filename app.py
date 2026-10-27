import json
import os
from urllib.parse import urlparse

from flask import Flask, request, render_template_string

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions.json")

PAGE = """
<!doctype html>
<html>
<head><title>Assignment Submission Portal</title></head>
<body>
  <h1>Assignment Submission Portal</h1>

  {% if error %}<p id="message" style="color:red">{{ error }}</p>{% endif %}
  {% if success %}<p id="message" style="color:green">{{ success }}</p>{% endif %}

  <form method="post" action="/">
    <p>Name: <input name="name" value="{{ form.get('name', '') }}"></p>
    <p>Registration No: <input name="reg_no" value="{{ form.get('reg_no', '') }}"></p>
    <p>Assignment Title: <input name="title" value="{{ form.get('title', '') }}"></p>
    <p>Submission URL: <input name="url" value="{{ form.get('url', '') }}"></p>
    <button type="submit">Submit</button>
  </form>

  <h2>Saved Submissions</h2>
  <table border="1" cellpadding="5">
    <tr><th>Name</th><th>Reg No</th><th>Title</th><th>URL</th></tr>
    {% for s in submissions %}
    <tr><td>{{ s.name }}</td><td>{{ s.reg_no }}</td><td>{{ s.title }}</td><td>{{ s.url }}</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def validate(form):
    labels = {
        "name": "Name",
        "reg_no": "Registration number",
        "title": "Assignment title",
        "url": "Submission URL",
    }
    for field, label in labels.items():
        if not form.get(field, "").strip():
            return f"{label} is required."
    if not is_valid_url(form["url"].strip()):
        return "Submission URL is invalid."
    return None


def load_submissions(data_file):
    if not os.path.exists(data_file):
        return []
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_submission(data_file, submission):
    items = load_submissions(data_file)
    items.append(submission)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def create_app(data_file=DEFAULT_DATA_FILE):
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        error = None
        success = None
        form = {}
        status = 200

        if request.method == "POST":
            form = request.form
            error = validate(form)
            if error:
                status = 400
            else:
                save_submission(data_file, {
                    "name": form["name"].strip(),
                    "reg_no": form["reg_no"].strip(),
                    "title": form["title"].strip(),
                    "url": form["url"].strip(),
                })
                success = "Submission saved successfully."
                form = {}

        html = render_template_string(
            PAGE,
            error=error,
            success=success,
            form=form,
            submissions=load_submissions(data_file),
        )
        return html, status

    return app


if __name__ == "__main__":
    create_app().run(debug=True)