from fastapi.testclient import TestClient
from app.main import app
import requests
import json

client = TestClient(app)

SAMPLE_GISTS = [
    {
        "id": "1",
        "html_url": "https://gist.github.com/1",
        "description": "example gist",
        "created_at": "2020-01-01T00:00:00Z",
        "files": {"file1.txt": {"filename": "file1.txt"}},
    }
]


class DummyResp:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or []

    def json(self):
        return self._json


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    #assert r.json() == {"status": "ok"}


def test_get_gists_monkeypatch(monkeypatch):
    # Patch requests.get so no real network is used.
    def fake_get(url, params=None, timeout=None):
        assert "users/octocat/gists" in url
        return DummyResp(200, SAMPLE_GISTS)

    monkeypatch.setattr(requests, "get", fake_get)

    r = client.get("/octocat")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "1"
    assert data[0]["files"] == ["file1.txt"]


def test_user_not_found(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return DummyResp(404, {"message": "Not Found"})

    monkeypatch.setattr(requests, "get", fake_get)
    r = client.get("/nonexistentuser")
    assert r.status_code == 404