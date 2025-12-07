def test_create_user(client):
    """Test to check if creating a user works"""
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
    """Test to check if fetching all users works"""
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
    """Test to check if fetching a user works"""
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


def test_duplicate_user(client):
    """Test to check if creating a user with duplicate email throws an error"""
    first_response = client.post(
        "/users",
        json={
            "name": "jane doe",
            "email": "jane@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    assert first_response.status_code == 200

    response = client.post(
        "/users",
        json={
            "name": "jane doe",
            "email": "jane@example.com",
            "password": "password123",
            "role": "user",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already exists"


def test_user_not_found(client):
    """Test to fetch a user that does not exist"""
    response = client.get("/users/999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User with id 999 not found."


def test_wrong_role(client):
    response = client.post(
        "/users",
        json={
            "name": "jane doe",
            "email": "jane@example.com",
            "password": "password123",
            "role": "test",
        },
    )
    assert response.status_code == 422


def test_delete_user(client):
    first_response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "John@Example.com",
            "password": "securepass123",
            "role": "user",
        },
    )

    assert first_response.status_code == 200
    user_id = first_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200


def test_update_user(client):
    first_response = client.post(
        "/users",
        json={
            "name": "jane doe",
            "email": "jane@example.com",
            "password": "password123",
            "role": "coach",
        },
    )
    assert first_response.status_code == 200
    user_id = first_response.json()["id"]
    response = client.put(
        f"/users/{user_id}",
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
    assert data["role"] == "user"
