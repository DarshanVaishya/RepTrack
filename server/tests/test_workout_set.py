from fastapi import status


def _create_workout_and_exercise(authenticated_client):
    """
    Create:
    - an exercise in the catalog
    - a workout for the current user
    - a workout_exercise linking them

    Returns: (workout_id, exercise_id, workout_exercise_id)
    """
    # 1) Create exercise
    exercise_resp = authenticated_client(
        "POST",
        "/exercises",
        json={
            "name": "Bench Press",
            "description": "Flat barbell bench press",
            "muscle_group": "chest",
            "equipment": "barbell",
        },
    )
    assert exercise_resp.status_code == 201
    exercise_id = exercise_resp.json()["data"]["id"]

    # 2) Create workout
    workout_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "Upper body", "notes": "Test workout", "user_id": 1},
    )
    assert workout_resp.status_code == 201
    workout_id = workout_resp.json()["data"]["id"]

    # 3) Create workout_exercise
    we_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise",
        json={
            "exercise_id": exercise_id,
            "order_index": 1,
            "notes": "First exercise",
            "workout_id": workout_id,
        },
    )
    assert we_resp.status_code == 201
    workout_exercise_id = we_resp.json()["data"]["id"]

    return workout_id, exercise_id, workout_exercise_id


def test_create_workout_set(authenticated_client):
    """Test creating a workout set"""
    workout_id, exercise_id, workout_exercise_id = _create_workout_and_exercise(
        authenticated_client
    )

    resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise/{exercise_id}/set",
        json={
            "reps": 10,
            "weight": 100,
            "set_type": "normal",
            "order_index": 1,
            "notes": "Warmup set",
            "workout_exercise_id": workout_exercise_id,
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["reps"] == 10
    assert data["weight"] == 100
    assert data["set_type"] == "normal"
    assert data["workout_exercise_id"] == workout_exercise_id


def test_get_workout_set_by_id(authenticated_client):
    """Test fetching a workout set by ID"""
    workout_id, exercise_id, workout_exercise_id = _create_workout_and_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise/{exercise_id}/set",
        json={
            "reps": 8,
            "weight": 120,
            "set_type": "failure",
            "order_index": 1,
            "notes": "To failure",
            "workout_exercise_id": workout_exercise_id,
        },
    )
    assert create_resp.status_code == 201
    set_id = create_resp.json()["data"]["id"]

    get_resp = authenticated_client(
        "GET",
        f"/workout/{workout_id}/exercise/{exercise_id}/set/{set_id}",
    )
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert data["id"] == set_id
    assert data["set_type"] == "failure"


def test_get_workout_set_not_found(authenticated_client):
    """Test 404 when workout set does not exist"""
    # need a valid workout_id and exercise_id in the path, even if set_id is bogus
    workout_id, exercise_id, _ = _create_workout_and_exercise(authenticated_client)

    resp = authenticated_client(
        "GET",
        f"/workout/{workout_id}/exercise/{exercise_id}/set/999999",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()


def test_update_workout_set(authenticated_client):
    """Test updating a workout set"""
    workout_id, exercise_id, workout_exercise_id = _create_workout_and_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise/{exercise_id}/set",
        json={
            "reps": 10,
            "weight": 100,
            "set_type": "normal",
            "order_index": 1,
            "notes": "Initial",
            "workout_exercise_id": workout_exercise_id,
        },
    )
    assert create_resp.status_code == 201
    set_id = create_resp.json()["data"]["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}/exercise/{exercise_id}/set/{set_id}",
        json={
            "reps": 12,
            "weight": 110,
            "notes": "Updated notes",
        },
    )
    assert update_resp.status_code == 200
    data = update_resp.json()["data"]
    assert data["reps"] == 12
    assert data["weight"] == 110
    assert data["notes"] == "Updated notes"


def test_update_workout_set_no_fields(authenticated_client):
    """Test update fails when no fields provided"""
    workout_id, exercise_id, workout_exercise_id = _create_workout_and_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise/{exercise_id}/set",
        json={
            "reps": 10,
            "weight": 100,
            "set_type": "normal",
            "order_index": 1,
            "notes": "Initial",
            "workout_exercise_id": workout_exercise_id,
        },
    )
    assert create_resp.status_code == 201
    set_id = create_resp.json()["data"]["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}/exercise/{exercise_id}/set/{set_id}",
        json={},
    )
    assert update_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "no fields" in update_resp.json()["detail"].lower()


def test_delete_workout_set(authenticated_client):
    """Test deleting a workout set"""
    workout_id, exercise_id, workout_exercise_id = _create_workout_and_exercise(
        authenticated_client
    )

    create_resp = authenticated_client(
        "POST",
        f"/workout/{workout_id}/exercise/{exercise_id}/set",
        json={
            "reps": 8,
            "weight": 120,
            "set_type": "normal",
            "order_index": 1,
            "notes": "To delete",
            "workout_exercise_id": workout_exercise_id,
        },
    )
    assert create_resp.status_code == 201
    set_id = create_resp.json()["data"]["id"]

    delete_resp = authenticated_client(
        "DELETE",
        f"/workout/{workout_id}/exercise/{exercise_id}/set/{set_id}",
    )
    assert delete_resp.status_code == 200

    get_resp = authenticated_client(
        "GET",
        f"/workout/{workout_id}/exercise/{exercise_id}/set/{set_id}",
    )
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
