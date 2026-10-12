import pytest
from fastapi.testclient import TestClient

import app as activities_app


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Open Activity": {
            "description": "An activity with open spots",
            "schedule": "Mondays",
            "max_participants": 2,
            "participants": ["existing@example.com"],
        },
        "Full Activity": {
            "description": "An activity at capacity",
            "schedule": "Tuesdays",
            "max_participants": 1,
            "participants": ["full@example.com"],
        },
    }
    monkeypatch.setattr(activities_app, "activities", test_activities)
    return TestClient(activities_app.app)


def test_get_activities_returns_available_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities_app.activities


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Open Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.com for Open Activity"}
    assert "new@example.com" in activities_app.activities["Open Activity"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Open Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities_app.activities["Open Activity"]["participants"] == [
        "existing@example.com"
    ]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_full_activity(client):
    response = client.post(
        "/activities/Full Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert activities_app.activities["Full Activity"]["participants"] == [
        "full@example.com"
    ]


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Open Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed existing@example.com from Open Activity"
    }
    assert activities_app.activities["Open Activity"]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Open Activity/signup",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities_app.activities["Open Activity"]["participants"] == [
        "existing@example.com"
    ]