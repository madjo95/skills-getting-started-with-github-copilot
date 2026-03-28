"""
Tests for the signup endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupForActivity:
    """Test suite for the /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client, activity_name, sample_email):
        """
        Test that a new student can successfully sign up for an activity.
        
        AAA Pattern:
        - Arrange: Prepare a valid activity name and new email
        - Act: Make a POST request to signup endpoint
        - Assert: Verify response is successful and participant was added
        """
        # Arrange
        url = f"/activities/{activity_name}/signup"
        params = {"email": sample_email}

        # Act
        response = client.post(url, params=params)

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {sample_email} for {activity_name}"

    def test_signup_duplicate_student_fails(self, client, activity_name, existing_email):
        """
        Test that a student cannot sign up twice for the same activity.
        
        AAA Pattern:
        - Arrange: Use an email already registered for the activity
        - Act: Attempt to sign up the same student again
        - Assert: Verify request fails with 400 status code
        """
        # Arrange
        url = f"/activities/{activity_name}/signup"
        params = {"email": existing_email}

        # Act
        response = client.post(url, params=params)

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client, sample_email):
        """
        Test that signing up for a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Use an invalid activity name
        - Act: Make a POST request to signup endpoint
        - Assert: Verify response is 404 and error message is shown
        """
        # Arrange
        non_existent_activity = "Non Existent Club"
        url = f"/activities/{non_existent_activity}/signup"
        params = {"email": sample_email}

        # Act
        response = client.post(url, params=params)

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_updates_participant_count(self, client, activity_name, sample_email):
        """
        Test that signing up increments the participant count correctly.
        
        AAA Pattern:
        - Arrange: Get initial participant count
        - Act: Sign up a new student and retrieve updated activity
        - Assert: Verify participant count increased by 1
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        signup_url = f"/activities/{activity_name}/signup"
        params = {"email": sample_email}

        # Act
        client.post(signup_url, params=params)
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])

        # Assert
        assert updated_count == initial_count + 1
        assert sample_email in updated_response.json()[activity_name]["participants"]

    def test_signup_with_special_characters_in_email(self, client, activity_name):
        """
        Test that signup works with emails containing special characters.
        
        AAA Pattern:
        - Arrange: Prepare an email with special characters
        - Act: Sign up with special character email
        - Assert: Verify successful signup
        """
        # Arrange
        special_email = "student+test@mergington.edu"
        url = f"/activities/{activity_name}/signup"
        params = {"email": special_email}

        # Act
        response = client.post(url, params=params)

        # Assert
        assert response.status_code == 200
        assert special_email in response.json()["message"]
