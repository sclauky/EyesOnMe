"""Tests sans base : le pool est remplacé par un faux."""
import os

os.environ.setdefault("DATABASE_URL", "postgres://unused")
os.environ["CORS_ORIGINS"] = "https://site.example"

import pytest
from fastapi.testclient import TestClient

from app import main


class FakePool:
    def __init__(self, rows_by_marker):
        self.rows_by_marker = rows_by_marker
        self.calls = []

    def connection(self):
        pool = self

        class Conn:
            def __enter__(self_):
                return self_

            def __exit__(self_, *a):
                return False

            def execute(self_, query, params=()):
                pool.calls.append((query, params))
                for marker, rows in pool.rows_by_marker.items():
                    if marker in query:
                        class Cur:
                            def fetchall(_):
                                return rows
                        return Cur()
                raise AssertionError(query)

        return Conn()


@pytest.fixture
def client():
    pool = FakePool({
        "FROM gesture": [{"code": "open_hand", "label": "Main", "description": ""}],
        "FROM action_type": [{"code": "mouse.click", "label": "C", "description": "", "params_schema": {}}],
        "FROM profile": [{"?column?": 1}],
        "FROM binding": [{"gesture": "open_hand", "hand": "any", "trigger": "while_held",
                          "action": "mouse.move", "params": {"landmark": 8}}],
    })
    main.app.dependency_overrides[main.get_pool] = lambda: pool
    c = TestClient(main.app)
    c.pool = pool
    yield c
    main.app.dependency_overrides.clear()


def test_gestures(client):
    assert client.get("/gestures").json()[0]["code"] == "open_hand"


def test_actions(client):
    assert client.get("/actions").json()[0]["code"] == "mouse.click"


def test_bindings_use_bound_parameter(client):
    r = client.get("/profiles/default/bindings")
    assert r.status_code == 200
    assert r.json()["bindings"][0]["action"] == "mouse.move"
    assert all(p == ("default",) for _, p in client.pool.calls)


def test_invalid_profile_name_rejected_before_db(client):
    r = client.get("/profiles/x';DROP TABLE binding;--/bindings")
    assert r.status_code in (404, 422)
    assert client.pool.calls == []


def test_cors_allowed_and_denied(client):
    ok = client.get("/gestures", headers={"Origin": "https://site.example"})
    ko = client.get("/gestures", headers={"Origin": "https://evil.example"})
    assert ok.headers.get("access-control-allow-origin") == "https://site.example"
    assert "access-control-allow-origin" not in ko.headers


def test_wildcard_cors_refused(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(RuntimeError):
        main._allowed_origins()
