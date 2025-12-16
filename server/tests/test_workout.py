from fastapi import status


def test_create_workout(authenticated_client):
    """Test creating a workout"""
    resp = authenticated_client(
        "POST",
        "/workout",
        json={
            "name": "Upper Body Day",
            "notes": "Focus on chest and shoulders",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["name"] == "Upper Body Day"
    assert data["notes"] == "Focus on chest and shoulders"
    assert data["user_id"] == 1
    assert "id" in data
    assert "created_at" in data


def test_create_workout_without_notes(authenticated_client):
    """Test creating a workout without optional notes"""
    resp = authenticated_client(
        "POST",
        "/workout",
        json={
            "name": "Quick Workout",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["name"] == "Quick Workout"
    assert data["notes"] is None


def test_get_all_workouts_for_user(authenticated_client):
    """Test fetching all workouts for current user"""
    authenticated_client(
        "POST",
        "/workout",
        json={"name": "Workout 1", "notes": "First workout"},
    )
    authenticated_client(
        "POST",
        "/workout",
        json={"name": "Workout 2", "notes": "Second workout"},
    )
    authenticated_client(
        "POST",
        "/workout",
        json={"name": "Workout 3", "notes": "Third workout"},
    )

    resp = authenticated_client("GET", "/workout")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 3
    assert all(w["user_id"] == 1 for w in data)
    workout_names = [w["name"] for w in data]
    assert "Workout 1" in workout_names
    assert "Workout 2" in workout_names
    assert "Workout 3" in workout_names


def test_get_all_workouts_empty(authenticated_client):
    """Test fetching workouts when user has none"""
    resp = authenticated_client("GET", "/workout")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data == []


def test_get_workout_by_id(authenticated_client):
    """Test fetching a specific workout by ID"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "Leg Day", "notes": "Squats and deadlifts"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    get_resp = authenticated_client("GET", f"/workout/{workout_id}")
    assert get_resp.status_code == status.HTTP_200_OK
    data = get_resp.json()
    assert data["id"] == workout_id
    assert data["name"] == "Leg Day"
    assert data["notes"] == "Squats and deadlifts"


def test_get_workout_not_found(authenticated_client):
    """Test 404 when workout doesn't exist"""
    resp = authenticated_client("GET", "/workout/999999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()


def test_get_workout_invalid_id(authenticated_client):
    """Test 400 for invalid workout ID"""
    resp = authenticated_client("GET", "/workout/0")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid" in resp.json()["detail"].lower()

    resp = authenticated_client("GET", "/workout/-1")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid" in resp.json()["detail"].lower()


def test_update_workout(authenticated_client):
    """Test updating a workout"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "Original Name", "notes": "Original notes"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}",
        json={
            "name": "Updated Name",
            "notes": "Updated notes",
        },
    )
    assert update_resp.status_code == status.HTTP_200_OK
    data = update_resp.json()
    assert data["name"] == "Updated Name"
    assert data["notes"] == "Updated notes"
    assert data["id"] == workout_id


def test_update_workout_partial(authenticated_client):
    """Test updating only some fields"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "Original Name", "notes": "Original notes"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}",
        json={"name": "New Name"},
    )
    assert update_resp.status_code == status.HTTP_200_OK
    data = update_resp.json()
    assert data["name"] == "New Name"
    assert data["notes"] == "Original notes"


def test_update_workout_no_fields(authenticated_client):
    """Test update fails when no fields provided"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "Test Workout", "notes": "Test notes"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    update_resp = authenticated_client(
        "PUT",
        f"/workout/{workout_id}",
        json={},
    )
    assert update_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "no fields" in update_resp.json()["detail"].lower()


def test_update_workout_not_found(authenticated_client):
    """Test 404 when updating non-existent workout"""
    resp = authenticated_client(
        "PUT",
        "/workout/999999",
        json={"name": "Updated Name"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()


def test_delete_workout(authenticated_client):
    """Test deleting a workout"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "To Delete", "notes": "Will be deleted"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    delete_resp = authenticated_client("DELETE", f"/workout/{workout_id}")
    assert delete_resp.status_code == status.HTTP_200_OK
    assert "deleted" in delete_resp.json()["detail"].lower()

    get_resp = authenticated_client("GET", f"/workout/{workout_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_workout_not_found(authenticated_client):
    """Test 404 when deleting non-existent workout"""
    resp = authenticated_client("DELETE", "/workout/999999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp.json()["detail"].lower()


def test_workout_ownership_isolation(authenticated_client, client):
    """Test that users can only see their own workouts"""
    user1_workout = authenticated_client(
        "POST",
        "/workout",
        json={"name": "User 1 Workout", "notes": "Private"},
    )
    assert user1_workout.status_code == status.HTTP_200_OK

    user2_resp = client.post(
        "/users",
        json={
            "name": "User 2",
            "email": "user2@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    assert user2_resp.status_code == status.HTTP_200_OK

    login_resp = client.post(
        "/users/login",
        data={"username": "user2@example.com", "password": "password123"},
    )
    assert login_resp.status_code == status.HTTP_200_OK
    user2_token = login_resp.json()["access_token"]

    user2_workout = client.post(
        "/workout",
        json={"name": "User 2 Workout", "notes": "Also private"},
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert user2_workout.status_code == status.HTTP_200_OK

    user2_workouts = client.get(
        "/workout",
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert user2_workouts.status_code == status.HTTP_200_OK
    data = user2_workouts.json()
    assert len(data) == 1
    assert data[0]["name"] == "User 2 Workout"

    user1_workouts = authenticated_client("GET", "/workout")
    assert user1_workouts.status_code == status.HTTP_200_OK
    data = user1_workouts.json()
    assert len(data) == 1
    assert data[0]["name"] == "User 1 Workout"


def test_update_workout_wrong_owner(authenticated_client, client):
    """Test 403 when trying to update another user's workout"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "User 1 Workout"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    client.post(
        "/users",
        json={
            "name": "User 2",
            "email": "user2@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    login_resp = client.post(
        "/users/login",
        data={"username": "user2@example.com", "password": "password123"},
    )
    user2_token = login_resp.json()["access_token"]

    update_resp = client.put(
        f"/workout/{workout_id}",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert update_resp.status_code == status.HTTP_403_FORBIDDEN
    assert "creator" in update_resp.json()["detail"].lower()


def test_delete_workout_wrong_owner(authenticated_client, client):
    """Test 403 when trying to delete another user's workout"""
    create_resp = authenticated_client(
        "POST",
        "/workout",
        json={"name": "User 1 Workout"},
    )
    assert create_resp.status_code == status.HTTP_200_OK
    workout_id = create_resp.json()["id"]

    client.post(
        "/users",
        json={
            "name": "User 2",
            "email": "user2@example.com",
            "password": "password123",
            "role": "user",
        },
    )
    login_resp = client.post(
        "/users/login",
        data={"username": "user2@example.com", "password": "password123"},
    )
    user2_token = login_resp.json()["access_token"]

    delete_resp = client.delete(
        f"/workout/{workout_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert delete_resp.status_code == status.HTTP_403_FORBIDDEN
    assert "creator" in delete_resp.json()["detail"].lower()
