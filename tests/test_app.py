"""
Tests for Mergington High School Activities API

This test suite covers all endpoints with both happy path and error case scenarios.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test"""
    # Arrange: Set up original activities state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["jacob@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater production and performance opportunities",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore science through experiments and projects",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear current activities and repopulate with original
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test (reset again for next test)
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        # Arrange
        expected_activity_count = 9
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Drama Club", "Art Studio", "Debate Team", "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that activity data has correct structure"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        test_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data[test_activity]
        
        # Assert
        assert response.status_code == 200
        for field in required_fields:
            assert field in activity, f"Missing field: {field}"
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_returns_participants(self, client):
        """Test that participants list is included and accurate"""
        # Arrange
        test_activity = "Chess Club"
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_count = 2
        
        # Act
        response = client.get("/activities")
        data = response.json()
        actual_participants = data[test_activity]["participants"]
        
        # Assert
        assert response.status_code == 200
        assert len(actual_participants) == expected_count
        for participant in expected_participants:
            assert participant in actual_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        student_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        verification_response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert student_email in verification_response.json()[activity_name]["participants"]
    
    def test_signup_multiple_students(self, client):
        """Test that multiple different students can sign up"""
        # Arrange
        activity_name = "Chess Club"
        student1_email = "student1@mergington.edu"
        student2_email = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={student1_email}"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={student2_email}"
        )
        verification_response = client.get("/activities")
        participants = verification_response.json()[activity_name]["participants"]
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student1_email in participants
        assert student2_email in participants
    
    def test_signup_duplicate_prevented(self, client):
        """Test that duplicate signup is prevented"""
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_student}"
        )
        
        # Assert
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "already" in detail or "signed up" in detail
    
    def test_signup_activity_not_found(self, client):
        """Test signup returns 404 for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_missing_email_parameter(self, client):
        """Test signup without email parameter"""
        # Arrange
        activity_name = "Chess Club"
        expected_status = 422  # Unprocessable Entity
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == expected_status


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup/{email} endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from activity"""
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{student_email}"
        )
        verification_response = client.get("/activities")
        participants = verification_response.json()[activity_name]["participants"]
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert student_email not in participants
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister returns 404 for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{student_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_participant_not_found(self, client):
        """Test unregister returns 400 when participant isn't in activity"""
        # Arrange
        activity_name = "Chess Club"
        student_email = "notamember@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{student_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_multiple_times_fails(self, client):
        """Test that unregistering twice fails the second time"""
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"
        
        # Act - First unregister
        response1 = client.delete(
            f"/activities/{activity_name}/signup/{student_email}"
        )
        
        # Act - Second unregister (should fail)
        response2 = client.delete(
            f"/activities/{activity_name}/signup/{student_email}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400


class TestRootRedirect:
    """Tests for GET / redirect endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static files"""
        # Arrange
        expected_status = 307  # Temporary redirect
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert "static" in response.headers["location"]


class TestIntegrationScenarios:
    """Integration tests for realistic workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        # Arrange
        email = "integration@mergington.edu"
        activity = "Chess Club"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        check_signed_up = client.get("/activities")
        signed_up_participants = check_signed_up.json()[activity]["participants"]
        
        # Assert signup
        assert signup_response.status_code == 200
        assert email in signed_up_participants
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup/{email}"
        )
        check_unregistered = client.get("/activities")
        unregistered_participants = check_unregistered.json()[activity]["participants"]
        
        # Assert unregister
        assert unregister_response.status_code == 200
        assert email not in unregistered_participants
    
    def test_multiple_activities_independent(self, client):
        """Test that registrations in different activities are independent"""
        # Arrange
        email = "student@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act - Sign up for two activities
        client.post(f"/activities/{activity1}/signup?email={email}")
        client.post(f"/activities/{activity2}/signup?email={email}")
        
        # Act - Unregister from first activity
        client.delete(f"/activities/{activity1}/signup/{email}")
        check_response = client.get("/activities")
        activities_data = check_response.json()
        
        # Assert
        assert email not in activities_data[activity1]["participants"]
        assert email in activities_data[activity2]["participants"]
