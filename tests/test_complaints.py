import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base
from dependencies import get_db

from datetime import datetime, timedelta, timezone
import jwt

from security import SECRET_KEY, ALGORITHM

# Separate in-memory test database
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def token():
    # Register a test user
    r = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "TestPass123!",
        },
    )
    assert r.status_code == 201

    # Log in
    r = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "TestPass123!",
        },
    )
    assert r.status_code == 200

    return r.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_home():
    r = client.get("/")
    assert r.status_code == 200


def test_create_complaint(auth_headers):
    r = client.post(
        "/complaints",
        headers=auth_headers,
        json={
            "title": "Broken streetlight",
            "description": "Light is not working",
            "location": "Greater Noida",
        },
    )

    assert r.status_code == 201
    assert r.json()["title"] == "Broken streetlight"


def test_get_complaint(auth_headers):
    r = client.post(
        "/complaints",
        headers=auth_headers,
        json={
            "title": "Broken road",
            "description": "Large pothole",
            "location": "Noida",
        },
    )
    assert r.status_code == 201

    cid = r.json()["id"]

    r = client.get(
        f"/complaints/{cid}",
        headers=auth_headers,
    )

    assert r.status_code == 200
    assert r.json()["id"] == cid


def test_update_complaint(auth_headers):
    r = client.post(
        "/complaints",
        headers=auth_headers,
        json={
            "title": "Broken road",
            "description": "Large pothole",
            "location": "Noida",
        },
    )
    assert r.status_code == 201

    cid = r.json()["id"]

    r = client.patch(
        f"/complaints/{cid}",
        headers=auth_headers,
        json={"status": "Resolved"},
    )

    assert r.status_code == 200
    assert r.json()["status"] == "Resolved"


def test_delete_complaint(auth_headers):
    r = client.post(
        "/complaints",
        headers=auth_headers,
        json={
            "title": "Broken road",
            "description": "Large pothole",
            "location": "Noida",
        },
    )
    assert r.status_code == 201

    cid = r.json()["id"]

    r = client.delete(
        f"/complaints/{cid}",
        headers=auth_headers,
    )

    assert r.status_code == 204


def test_missing_complaint(auth_headers):
    r = client.get(
        "/complaints/99999",
        headers=auth_headers,
    )

    assert r.status_code == 404


def test_user_cannot_access_another_users_complaint():
    # Register User A
    client.post(
        "/auth/register",
        json={"username": "user_a", "password": "Pass123!"},
    )

    # Log in User A
    r = client.post(
        "/auth/login",
        json={"username": "user_a", "password": "Pass123!"},
    )
    token_a = r.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A creates a complaint
    r = client.post(
        "/complaints",
        headers=headers_a,
        json={
            "title": "Private complaint",
            "description": "This belongs to User A",
            "location": "Greater Noida",
        },
    )
    assert r.status_code == 201
    cid = r.json()["id"]

    # Register User B
    client.post(
        "/auth/register",
        json={"username": "user_b", "password": "Pass456!"},
    )

    # Log in User B
    r = client.post(
        "/auth/login",
        json={"username": "user_b", "password": "Pass456!"},
    )
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B must not see User A's complaint
    r = client.get(f"/complaints/{cid}", headers=headers_b)
    assert r.status_code == 404

    # User B must not update it
    r = client.patch(
        f"/complaints/{cid}",
        headers=headers_b,
        json={"status": "Resolved"},
    )
    assert r.status_code == 404

    # User B must not delete it
    r = client.delete(f"/complaints/{cid}", headers=headers_b)
    assert r.status_code == 404


def test_missing_token():
    r = client.get("/complaints")
    assert r.status_code == 401


def test_invalid_token():
    headers = {"Authorization": "Bearer fake.invalid.token"}

    r = client.get("/complaints", headers=headers)

    assert r.status_code == 401


def test_expired_token():
    token = jwt.encode(
        {
            "sub": "testuser",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/complaints", headers=headers)

    assert r.status_code == 401


def test_register_short_password():
    r = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "123",
        },
    )

    assert r.status_code == 422
