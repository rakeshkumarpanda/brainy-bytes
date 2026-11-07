# 3.2 Real Flask apps: structure, database, login and tests
# Example "testing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from flask import Flask, request


def create_app(settings=None):
    app = Flask(__name__)
    app.config.update(settings or {})
    notes = []

    @app.get("/api/notes")
    def list_notes():
        return notes

    @app.post("/api/notes")
    def add_note():
        text = (request.get_json(silent=True) or {}).get("text", "").strip()
        if not text:
            return {"error": "text is required"}, 422
        notes.append({"id": len(notes) + 1, "text": text})
        return notes[-1], 201

    return app


# ---------- tests/conftest.py: with pytest this is a fixture (see the note below) ----------
def make_client():
    return create_app({"TESTING": True}).test_client()     # a NEW app, so every test starts clean


# ---------- tests/test_notes.py ----------
def test_starts_empty(client):
    assert client.get("/api/notes").get_json() == []


def test_add_note(client):
    r = client.post("/api/notes", json={"text": " milk "})
    assert r.status_code == 201
    assert client.get("/api/notes").get_json() == [{"id": 1, "text": "milk"}]


def test_empty_text_is_rejected(client):
    r = client.post("/api/notes", json={"text": "   "})
    assert r.status_code == 422
    assert r.get_json()["error"] == "text is required"


def test_wrong_on_purpose(client):
    assert client.get("/api/notes").status_code == 201, "a list answers 200, not 201"


# ---------- what pytest does for you: find test_ functions, give each a fresh client ----------
tests = [test_starts_empty, test_add_note, test_empty_text_is_rejected, test_wrong_on_purpose]
passed = 0
for test in tests:
    try:
        test(make_client())
        print("PASSED", test.__name__)
        passed += 1
    except AssertionError as error:
        print("FAILED", test.__name__, "-", error)
print(passed, "passed,", len(tests) - passed, "failed")
