import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def authenticated_client(client):
    """Fixture that creates user + logs in + returns client with token"""
    email = "test@example.com"
    user_response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": email,
            "password": "password123",
            "role": "admin",
        },
    )
    assert user_response.status_code == 201

    login_response = client.post(
        "/users/login", data={"username": email, "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    def auth_request(method, url, **kwargs):
        kwargs["headers"] = kwargs.get("headers", {})
        kwargs["headers"]["Authorization"] = f"Bearer {token}"
        return client.request(method, url, **kwargs)

    return auth_request


@pytest.fixture
def created_exercise(authenticated_client):
    """Fixture that creates an exercise and returns its ID + client"""
    create_response = authenticated_client(
        "POST",
        "/exercises",
        json={
            "name": "Lat Pulldown",
            "description": "Lat pulldown cable",
            "muscle_group": "back",
            "equipment": "cable_machine",
        },
    )
    assert create_response.status_code == 201
    exercise_id = create_response.json()["data"]["id"]

    return authenticated_client, exercise_id
