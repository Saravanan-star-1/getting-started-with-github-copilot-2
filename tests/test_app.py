from fastapi.testclient import TestClient
from src import app as application_module
import copy

client = TestClient(application_module.app)

# Use a deep copy of the original activities to restore state between tests
_original_activities = copy.deepcopy(application_module.activities)


def setup_function():
    # Reset activities before each test
    application_module.activities = copy.deepcopy(_original_activities)


def teardown_function():
    # Reset activities after each test
    application_module.activities = copy.deepcopy(_original_activities)


def test_signup_and_unregister_flow():
    activity_name = "Basketball Club"
    test_email = "test_student@mergington.edu"

    # Ensure the test email is not already in participants
    assert test_email not in application_module.activities[activity_name]["participants"]

    # Sign up
    signup_resp = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify participant present in in-memory data
    assert test_email in application_module.activities[activity_name]["participants"]

    # Unregister
    unregister_resp = client.delete(f"/activities/{activity_name}/participants?email={test_email}")
    assert unregister_resp.status_code == 200
    assert "Unregistered" in unregister_resp.json().get("message", "")

    # Verify participant removed
    assert test_email not in application_module.activities[activity_name]["participants"]


def test_signup_duplicate_fails():
    activity_name = "Soccer Team"
    existing_email = application_module.activities[activity_name]["participants"][0]

    # Try signing up same email again
    resp = client.post(f"/activities/{activity_name}/signup?email={existing_email}")
    assert resp.status_code == 400
    assert resp.json().get("detail") is not None
