def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "John@Example.com",
            "password": "securepass123",
            "role": "user",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data


def test_get_all_users(client):
    client.post(
        "/users",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "password123",
            "role": "user",
        },
    )

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_user_by_id(client):
    create_response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "test@example.com"


# TODO: Add test for user not found
