import copy
import os
import uuid
from unittest.mock import patch

os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")

from fastapi.testclient import TestClient

from app.dependencies import SupabaseUser, get_current_user
from app.main import app
from app.services.chunking_service import split_note_into_chunks
from app.services.rag_service import answer_question
from app.services.retrieval_service import retrieve_relevant_chunks
from app.supabase_client import get_supabase

client = TestClient(app)

TEST_USER_ID = str(uuid.uuid4())
TEST_USER_EMAIL = "test@example.com"


def _override_get_current_user() -> SupabaseUser:
    return SupabaseUser(id=TEST_USER_ID, email=TEST_USER_EMAIL)


# --- A minimal in-memory stand-in for supabase-py's fluent query builder ---------
# Implements just the .table()/.select()/.insert()/.update()/.delete()/.eq()/.execute()
# and .rpc()/.execute() chains that app/services/*.py actually calls, backed by plain
# Python dicts instead of a real Postgres connection. Keeps tests fully offline.


class _FakeResponse:
    def __init__(self, data):
        self.data = data


class _FakeQuery:
    def __init__(self, store: dict[str, list[dict]], table_name: str):
        self._store = store
        self._table_name = table_name
        self._op: str | None = None
        self._payload = None
        self._filters: list[tuple[str, object]] = []

    def select(self, *_args, **_kwargs):
        self._op = "select"
        return self

    def insert(self, payload):
        self._op = "insert"
        self._payload = payload
        return self

    def update(self, payload):
        self._op = "update"
        self._payload = payload
        return self

    def delete(self):
        self._op = "delete"
        return self

    def eq(self, column: str, value):
        self._filters.append((column, value))
        return self

    def _matches(self, row: dict) -> bool:
        return all(row.get(col) == val for col, val in self._filters)

    def execute(self) -> _FakeResponse:
        rows = self._store.setdefault(self._table_name, [])

        if self._op == "select":
            return _FakeResponse([copy.deepcopy(r) for r in rows if self._matches(r)])

        if self._op == "insert":
            payload = self._payload if isinstance(self._payload, list) else [self._payload]
            inserted = []
            for row in payload:
                new_row = dict(row)
                new_row.setdefault("id", uuid.uuid4().hex)
                rows.append(new_row)
                inserted.append(copy.deepcopy(new_row))
            return _FakeResponse(inserted)

        if self._op == "update":
            updated = []
            for row in rows:
                if self._matches(row):
                    row.update(self._payload)
                    updated.append(copy.deepcopy(row))
            return _FakeResponse(updated)

        if self._op == "delete":
            deleted = [copy.deepcopy(r) for r in rows if self._matches(r)]
            self._store[self._table_name] = [r for r in rows if not self._matches(r)]
            return _FakeResponse(deleted)

        raise AssertionError("no operation set before execute()")


class _FakeRpcResult:
    def __init__(self, data):
        self._data = data

    def execute(self) -> _FakeResponse:
        return _FakeResponse(self._data)


class FakeSupabaseClient:
    """Stands in for the real supabase.Client in tests - no network, no Postgres."""

    def __init__(self):
        self._store: dict[str, list[dict]] = {}

    def table(self, name: str) -> _FakeQuery:
        return _FakeQuery(self._store, name)

    def rpc(self, name: str, params: dict) -> _FakeRpcResult:
        assert name == "match_notes", f"unexpected RPC: {name}"
        notes_by_id = {n["id"]: n for n in self._store.get("note", [])}
        matches = []
        for chunk in self._store.get("note_chunk", []):
            note = notes_by_id.get(chunk["note_id"])
            if not note or note.get("user_id") != params["match_user_id"]:
                continue
            matches.append(
                {
                    "id": chunk["id"],
                    "note_id": chunk["note_id"],
                    "note_title": note["title"],
                    "chunk_text": chunk["chunk_text"],
                }
            )
        return _FakeRpcResult(matches[: params.get("match_count", 3)])


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


class _FakeSupabaseAuthResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def _fake_supabase_auth_post(url, *, json=None, headers=None, params=None, timeout=None):
    email = (json or {}).get("email")
    if url.endswith("/auth/v1/signup"):
        return _FakeSupabaseAuthResponse(200, {"user": {"id": TEST_USER_ID, "email": email}})
    if url.endswith("/auth/v1/token"):
        return _FakeSupabaseAuthResponse(200, {"access_token": "fake-jwt-token", "user": {"id": TEST_USER_ID, "email": email}})
    raise AssertionError(f"unexpected Supabase Auth call: {url}")


@patch("app.services.auth_service.httpx.post", side_effect=_fake_supabase_auth_post)
def test_register_and_login_proxy_to_supabase(mock_post):
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"

    register = client.post("/auth/register", json={"email": email, "password": "secret123"})
    assert register.status_code == 201, register.text
    assert register.json()["email"] == email

    login = client.post("/auth/login", json={"email": email, "password": "secret123"})
    assert login.status_code == 200, login.text
    assert login.json()["access_token"] == "fake-jwt-token"

    assert mock_post.call_count == 2


@patch("app.services.auth_service.httpx.post")
def test_register_maps_supabase_error_to_400(mock_post):
    mock_post.return_value = _FakeSupabaseAuthResponse(400, {"msg": "User already registered"})

    response = client.post("/auth/register", json={"email": "dupe@example.com", "password": "secret123"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_notes_flow_for_authenticated_user():
    fake_supabase = FakeSupabaseClient()
    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_supabase] = lambda: fake_supabase
    try:
        notes = client.get("/notes")
        assert notes.status_code == 200
        assert notes.json() == []

        create_note = client.post(
            "/notes",
            json={"title": "My first note", "content": "This is a test note."},
        )
        assert create_note.status_code == 201, create_note.text
        note = create_note.json()
        assert note["id"]
        assert note["user_id"] == TEST_USER_ID

        notes = client.get("/notes")
        assert notes.status_code == 200
        assert len(notes.json()) == 1

        other_user_notes = client.get(f"/notes/{note['id']}")
        assert other_user_notes.status_code == 200

        deleted = client.delete(f"/notes/{note['id']}")
        assert deleted.status_code == 204

        missing = client.get(f"/notes/{note['id']}")
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_supabase, None)


def test_notes_route_requires_auth():
    # No dependency override and no Authorization header - exercises the real
    # HTTPBearer check, which never reaches JWKS verification, so this stays offline.
    response = client.get("/notes")
    assert response.status_code == 401


def test_split_note_into_chunks():
    text = " ".join([f"Sentence {index} about notes and retrieval and embeddings." for index in range(60)])
    chunks = split_note_into_chunks(text)

    assert len(chunks) >= 2
    assert all(chunk.strip() for chunk in chunks)
    assert all(len(chunk) > 0 for chunk in chunks)
    assert isinstance(chunks, list)


def test_retrieve_relevant_chunks_uses_match_notes_rpc():
    fake_supabase = FakeSupabaseClient()
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())

    fake_supabase.table("note").insert({"id": "note-1", "user_id": user_id, "title": "Mine"}).execute()
    fake_supabase.table("note").insert({"id": "note-2", "user_id": other_user_id, "title": "Not mine"}).execute()
    fake_supabase.table("note_chunk").insert(
        {"id": "chunk-1", "note_id": "note-1", "chunk_text": "alpha"}
    ).execute()
    fake_supabase.table("note_chunk").insert(
        {"id": "chunk-2", "note_id": "note-2", "chunk_text": "beta"}
    ).execute()

    results = retrieve_relevant_chunks(fake_supabase, user_id, [1.0, 0.0], limit=3)

    assert len(results) == 1
    assert results[0]["chunk_text"] == "alpha"
    assert results[0]["note_title"] == "Mine"


def test_answer_question_without_gemini_key_returns_structured_response():
    response = answer_question(question="What are my notes about?", context_chunks=[{"chunk_text": "Alpha note"}], api_key_missing=True)
    assert response["answer"]
    assert "not configured" in response["answer"].lower() or "gemini" in response["answer"].lower()
