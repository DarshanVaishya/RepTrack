# TODO: Invalid email
# TODO: Empty fields


def test_create_user(client):
    """Test to check if creating a user works"""
    response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "John@Example.com",
            "password": "password123",
            "role": "user",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data


def test_get_all_users(authenticated_client):
    """Test to check if fetching all users works"""
    response = authenticated_client("GET", "/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_user_by_id(authenticated_client):
    """Test to check if fetching a user works"""
    create_response = authenticated_client(
        "POST",
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = authenticated_client("GET", f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "john@example.com"


def test_duplicate_user(client):
    """Test to check if creating a user with duplicate email throws an error"""
    first_response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    assert first_response.status_code == 200

    response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "user",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already exists"


def test_user_not_found(authenticated_client):
    """Test to fetch a user that does not exist"""
    response = authenticated_client("GET", "/users/999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User with id 999 not found"


def test_wrong_role(client):
    response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "test",
        },
    )
    assert response.status_code == 422


def test_delete_user(authenticated_client):
    create_response = authenticated_client(
        "POST",
        "/users",
        json={
            "name": "John Doe",
            "email": "John@Example.com",
            "password": "password123",
            "role": "user",
        },
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = authenticated_client("DELETE", f"/users/{user_id}")
    assert response.status_code == 200


def test_update_user(authenticated_client):
    create_response = authenticated_client(
        "POST",
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "coach",
        },
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = authenticated_client(
        "PUT",
        f"/users/{user_id}",
        json={
            "name": "John Doe",
            "email": "John@Example.com",
            "password": "password123",
            "role": "user",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["role"] == "user"


def test_login_success(client):
    """Test successful login returns valid token"""
    create_response = client.post(
        "/users",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    assert create_response.status_code == 200

    response = client.post(
        "/users/login",
        data={"username": "john@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_invalid_credentials(client):
    """Test login fails with wrong password"""
    response = client.post(
        "/users/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_login_nonexistent_user(client):
    """Test login fails with non-existent user"""
    response = client.post(
        "/users/login",
        data={"username": "nonexistent@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
