import json

import pytest

from app import create_app


@pytest.fixture
def setup(tmp_path):
    data_file = str(tmp_path / "submissions.json")
    app = create_app(data_file)
    client = app.test_client()
    return client, data_file


def read_saved(data_file):
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def test_valid_submission_is_saved(setup):
    client, data_file = setup
    response = client.post("/", data={
        "name": "Muzammil Zaman",
        "reg_no": "FA23-BSE-051",
        "title": "Assignment 1",
        "url": "https://github.com/test/repo",
    })
    assert response.status_code == 200
    assert len(read_saved(data_file)) == 1
    assert b"FA23-BSE-051" in response.data


def test_missing_registration_number_is_rejected(setup):
    client, data_file = setup
    response = client.post("/", data={
        "name": "Muzammil Zaman",
        "reg_no": "",
        "title": "Assignment 1",
        "url": "https://github.com/test/repo",
    })
    assert response.status_code == 400
    assert b"Registration number is required" in response.data
    assert read_saved(data_file) == []


def test_invalid_url_is_rejected(setup):
    client, data_file = setup
    response = client.post("/", data={
        "name": "Muzammil Zaman",
        "reg_no": "FA23-BSE-051",
        "title": "Assignment 1",
        "url": "not-a-valid-url",
    })
    assert response.status_code == 400
    assert read_saved(data_file) == []