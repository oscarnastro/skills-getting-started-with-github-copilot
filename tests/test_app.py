from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    result = response.json()
    assert "Basketball Team" in result
    assert {"description", "schedule", "max_participants", "participants"} <= set(
        result["Basketball Team"]
    )


def test_signup_adds_participant(client):
    activity_name = "Basketball Team"
    email = "new-student@example.com"

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Basketball Team"
    email = "new-student@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 400
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert participants.count(email) == 1


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "new-student@example.com"},
    )

    assert response.status_code == 404


def test_delete_removes_participant(client):
    activity_name = "Basketball Team"
    email = "new-student@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_delete_returns_404_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Basketball%20Team/signup",
        params={"email": "missing-student@example.com"},
    )

    assert response.status_code == 404


def test_delete_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "new-student@example.com"},
    )

    assert response.status_code == 404
