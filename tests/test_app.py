import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_success():
    response = client.post(
        "/activities/Basketball%20Club/signup",
        params={"email": "test.student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up test.student@mergington.edu for Basketball Club"
    }
    assert "test.student@mergington.edu" in activities["Basketball Club"]["participants"]


def test_signup_for_activity_with_unknown_activity_returns_404():
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "test.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_activity_with_existing_email_returns_400():
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_from_activity_success():
    response = client.delete(
        "/activities/Programming%20Class/signup",
        params={"email": "emma@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered emma@mergington.edu from Programming Class"
    }
    assert "emma@mergington.edu" not in activities["Programming Class"]["participants"]


def test_unregister_from_activity_with_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "test.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_with_not_signed_up_student_returns_404():
    response = client.delete(
        "/activities/Gym%20Class/signup",
        params={"email": "not.a.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
