from fastapi import status


def _create_workout_and_catalog_exercise(authenticated_client):
    """
    Helper to create:
    - A catalog exercise
    - A workout

    Returns: (workout_id, catalog_exercise_id)
    """
    # 1) Create catalog exercise
    exercise_resp = authenticated_client(
        "POST",
        "/exercises",
        json={
            "name": "Barbell Squat",
            "description": "Back squat",
            "muscle_group": "legs",
            "equipment": "barbell",
        },
    )
    assert exercise_resp.status_code == 201
    catalog_exercise_id = exercise_resp.json()["data"]["id"]

    # 2) Create workout
    workout_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "Leg Day", "notes": "Heavy squats", "user_id": 1},
    )
    assert workout_resp.status_code == 201
    workout_id = workout_resp.json()["data"]["id"]

    return workout_id, catalog_exercise_id


def test_create_workout_exercise(authenticated_client):
    """Test creating a workout exercise"""
    workout_id, catalog_exercise_id = _create_workout_and_catalog_exercise(
        authenticated_client
    )

    resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": catalog_exercise_id,
            "order_index": 1,
            "notes": "First exercise",
            "workout_id": workout_id,
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["exercise_id"] == catalog_exercise_id
    assert data["workout_id"] == workout_id
    assert data["order_index"] == 1
    assert data["notes"] == "First exercise"


def test_get_workout_exercise_by_id(authenticated_client):
    """Test fetching a workout exercise by ID"""
    workout_id, catalog_exercise_id = _create_workout_and_catalog_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": catalog_exercise_id,
            "order_index": 1,
            "notes": "Test notes",
            "workout_id": workout_id,
        },
    )
    assert create_resp.status_code == 201
    workout_exercise_id = create_resp.json()["data"]["id"]

    get_resp = authenticated_client(
        "GET",
        f"/workout/{workout_id}/exercise/{workout_exercise_id}",
    )
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert data["id"] == workout_exercise_id
    assert data["exercise_id"] == catalog_exercise_id


def test_get_workout_exercise_not_found(authenticated_client):
    """Test 404 when workout exercise does not exist"""
    workout_id, _ = _create_workout_and_catalog_exercise(authenticated_client)

    resp = authenticated_client(
        "GET",
        f"/workout/{workout_id}/exercise/999999",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()


def test_update_workout_exercise(authenticated_client):
    """Test updating a workout exercise"""
    workout_id, catalog_exercise_id = _create_workout_and_catalog_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": catalog_exercise_id,
            "order_index": 1,
            "notes": "Initial notes",
            "workout_id": workout_id,
        },
    )
    assert create_resp.status_code == 201
    workout_exercise_id = create_resp.json()["data"]["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}/exercise/{workout_exercise_id}",
        json={
            "order_index": 2,
            "notes": "Updated notes",
        },
    )
    assert update_resp.status_code == 200
    data = update_resp.json()["data"]
    assert data["order_index"] == 2
    assert data["notes"] == "Updated notes"


def test_update_workout_exercise_no_fields(authenticated_client):
    """Test update fails when no fields provided"""
    workout_id, catalog_exercise_id = _create_workout_and_catalog_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": catalog_exercise_id,
            "order_index": 1,
            "notes": "Initial",
            "workout_id": workout_id,
        },
    )
    assert create_resp.status_code == 201
    workout_exercise_id = create_resp.json()["data"]["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}/exercise/{workout_exercise_id}",
        json={},
    )
    assert update_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "no fields" in update_resp.json()["detail"].lower()


def test_delete_workout_exercise(authenticated_client):
    """Test deleting a workout exercise"""
    workout_id, catalog_exercise_id = _create_workout_and_catalog_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": catalog_exercise_id,
            "order_index": 1,
            "notes": "To delete",
            "workout_id": workout_id,
        },
    )
    assert create_resp.status_code == 201
    workout_exercise_id = create_resp.json()["data"]["id"]

    delete_resp = authenticated_client(
        "DELETE",
        f"/workout/{workout_id}/exercise/{workout_exercise_id}",
    )
    assert delete_resp.status_code == 200

    get_resp = authenticated_client(
        "GET",
        f"/workout/{workout_id}/exercise/{workout_exercise_id}",
    )
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_create_workout_exercise_with_invalid_exercise_id(authenticated_client):
    """Test creating workout exercise with non-existent catalog exercise"""
    workout_resp = authenticated_client(
        "POST",
        "/workout",
        json={
            "name": "Test Workout",
            "notes": "Test workout for invalid exercise test",
        },
    )
    assert workout_resp.status_code == 201
    workout_id = workout_resp.json()["data"]["id"]

    resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": 999999,
            "order_index": 1,
            "notes": "Should fail - catalog exercise not found",
            "workout_id": workout_id,
        },
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()
