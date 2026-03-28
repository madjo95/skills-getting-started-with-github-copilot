"""
Tests for the unregister endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_success(self, client, activity_name, existing_email):
        """
        Test that an existing student can successfully unregister from an activity.
        
        AAA Pattern:
        - Arrange: Use an email already registered for the activity
        - Act: Make a DELETE request to unregister endpoint
        - Assert: Verify response is successful and participant was removed
        """
        # Arrange
        url = f"/activities/{activity_name}/unregister"
        params = {"email": existing_email}

        # Act
        response = client.delete(url, params=params)

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {existing_email} from {activity_name}"

    def test_unregister_decreases_participant_count(self, client, activity_name, existing_email):
        """
        Test that unregistering decreases the participant count correctly.
        
        AAA Pattern:
        - Arrange: Get initial participant count
        - Act: Unregister a student and retrieve updated activity
        - Assert: Verify participant count decreased by 1
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        unregister_url = f"/activities/{activity_name}/unregister"
        params = {"email": existing_email}

        # Act
        client.delete(unregister_url, params=params)
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])

        # Assert
        assert updated_count == initial_count - 1
        assert existing_email not in updated_response.json()[activity_name]["participants"]

    def test_unregister_nonexistent_student_fails(self, client, activity_name, sample_email):
        """
        Test that unregistering a student not enrolled in activity fails with 400.
        
        AAA Pattern:
        - Arrange: Use an email not registered for the activity
        - Act: Make a DELETE request to unregister endpoint
        - Assert: Verify response is 400 and error message indicates not registered
        """
        # Arrange
        url = f"/activities/{activity_name}/unregister"
        params = {"email": sample_email}

        # Act
        response = client.delete(url, params=params)

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, client, existing_email):
        """
        Test that unregistering from a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Use an invalid activity name
        - Act: Make a DELETE request to unregister endpoint
        - Assert: Verify response is 404 and error message is shown
        """
        # Arrange
        non_existent_activity = "Non Existent Club"
        url = f"/activities/{non_existent_activity}/unregister"
        params = {"email": existing_email}

        # Act
        response = client.delete(url, params=params)

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_then_signup_again_succeeds(self, client, activity_name, sample_email):
        """
        Test that a student can sign up after unregistering.
        
        AAA Pattern:
        - Arrange: Register a new student
        - Act: Unregister the student, then register again
        - Assert: Verify both operations succeed
        """
        # Arrange
        signup_url = f"/activities/{activity_name}/signup"
        unregister_url = f"/activities/{activity_name}/unregister"
        params = {"email": sample_email}

        # Act - First signup
        response1 = client.post(signup_url, params=params)
        assert response1.status_code == 200

        # Act - Unregister
        response2 = client.delete(unregister_url, params=params)
        assert response2.status_code == 200

        # Act - Sign up again
        response3 = client.post(signup_url, params=params)

        # Assert
        assert response3.status_code == 200
        assert sample_email in response3.json()["message"]

    def test_unregister_multiple_students(self, client, activity_name):
        """
        Test that multiple students can be independently unregistered.
        
        AAA Pattern:
        - Arrange: Get initial participants for an activity
        - Act: Unregister two different students
        - Assert: Verify both were removed successfully
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        unregister_url = f"/activities/{activity_name}/unregister"

        # Act - Unregister first student
        response1 = client.delete(unregister_url, params={"email": initial_participants[0]})
        
        # Act - Unregister second student
        response2 = client.delete(unregister_url, params={"email": initial_participants[1]})

        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(final_participants) == len(initial_participants) - 2
        assert initial_participants[0] not in final_participants
        assert initial_participants[1] not in final_participants
