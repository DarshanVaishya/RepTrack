def test_create_exercise(authenticated_client):
    """Test to check if creating a exercise works"""
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


def test_create_exercise_wrong_info(authenticated_client):
    response = authenticated_client(
        "POST",
        "/exercises",
        json={
            "name": "Lat Pulldown",
            "description": "Lat pulldown cable",
            "muscle_group": "WRONG_INFO",
            "equipment": "WRONG_INFO",
        },
    )
    assert response.status_code == 422


def test_create_non_admin(client):
    """Test non-admin cannot create exercise (uses regular user)"""
    email = "regular@example.com"
    client.post(
        "/users",
        json={
            "name": "Regular User",
            "email": email,
            "password": "password123",
            "role": "user",
        },
    )

    login_response = client.post(
        "/users/login", data={"username": email, "password": "password123"}
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/exercises",
        json={
            "name": "Lat Pulldown",
            "description": "Lat pulldown cable",
            "muscle_group": "back",
            "equipment": "cable_machine",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only method"


def test_get_all_exercises(created_exercise):
    """Test to check if fetching all exercises works"""
    authenticated_client, _ = created_exercise
    response = authenticated_client(
        "GET",
        "/exercises",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_exercise_by_id(created_exercise):
    authenticated_client, exercise_id = created_exercise

    response = authenticated_client("GET", f"/exercises/{exercise_id}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, dict)


def test_get_exercise_not_found(authenticated_client):
    response = authenticated_client("GET", "/exercises/999")
    assert response.status_code == 404
    assert "Exercise with id 999 not found" in response.json()["detail"]


def test_update_exercise(created_exercise):
    """Test admin can update exercise"""
    authenticated_client, exercise_id = created_exercise

    response = authenticated_client(
        "PUT",
        f"/exercises/{exercise_id}",
        json={
            "name": "Chest Press",
            "description": "Updated description",
            "muscle_group": "chest",
            "equipment": "barbell",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Chest Press"
    assert data["description"] == "Updated description"
    assert data["muscle_group"] == "chest"
    assert data["equipment"] == "barbell"


def test_delete_exercise(created_exercise):
    """Test admin can delete exercise"""
    authenticated_client, exercise_id = created_exercise

    response = authenticated_client("DELETE", f"/exercises/{exercise_id}")
    assert response.status_code == 200

    check_response = authenticated_client("GET", f"/exercises/{exercise_id}")
    assert check_response.status_code == 404
