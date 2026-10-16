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


# Use a separate in-memory database so tests don't affect the actual application data.
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


# Give the tests their own database session instead of using the normal one.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Make the application use our test database whenever an endpoint needs a DB session.
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Start each test with an empty database so previous tests don't affect the results.
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Register a user and log in to get a valid token for protected endpoints.
@pytest.fixture
def token():
    r = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "TestPass123!",
        },
    )
    assert r.status_code == 201

    r = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "TestPass123!",
        },
    )
    assert r.status_code == 200

    return r.json()["access_token"]


# Add the token to the Authorization header for authenticated requests.
@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# Check that the application's home endpoint is working.
def test_home():
    r = client.get("/")
    assert r.status_code == 200


# A logged-in user should be able to create a complaint.
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


# Create a complaint first, then check whether it can be retrieved by its ID.
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


# Check that a complaint's status can be updated.
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


# Check that a user can delete their own complaint.
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


# Requesting a complaint ID that doesn't exist should return 404.
def test_missing_complaint(auth_headers):
    r = client.get(
        "/complaints/99999",
        headers=auth_headers,
    )

    assert r.status_code == 404


# Make sure one user cannot view, update, or delete another user's complaint.
def test_user_cannot_access_another_users_complaint():
    # Register and log in User A.
    client.post(
        "/auth/register",
        json={"username": "user_a", "password": "Pass123!"},
    )

    r = client.post(
        "/auth/login",
        json={"username": "user_a", "password": "Pass123!"},
    )
    token_a = r.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A creates a complaint.
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

    # Register and log in User B.
    client.post(
        "/auth/register",
        json={"username": "user_b", "password": "Pass456!"},
    )

    r = client.post(
        "/auth/login",
        json={"username": "user_b", "password": "Pass456!"},
    )
    token_b = r.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B should get 404 when trying to access User A's complaint.
    r = client.get(f"/complaints/{cid}", headers=headers_b)
    assert r.status_code == 404

    # User B should not be able to change its status either.
    r = client.patch(
        f"/complaints/{cid}",
        headers=headers_b,
        json={"status": "Resolved"},
    )
    assert r.status_code == 404

    # User B should not be able to delete it.
    r = client.delete(f"/complaints/{cid}", headers=headers_b)
    assert r.status_code == 404


# Protected endpoints should reject requests without an access token.
def test_missing_token():
    r = client.get("/complaints")
    assert r.status_code == 401


# A token with an invalid signature or format should be rejected.
def test_invalid_token():
    headers = {"Authorization": "Bearer fake.invalid.token"}

    r = client.get("/complaints", headers=headers)

    assert r.status_code == 401


# An expired token should no longer grant access to protected endpoints.
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


# Passwords shorter than the minimum allowed length should fail validation.
def test_register_short_password():
    r = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "123",
        },
    )

    assert r.status_code == 422
