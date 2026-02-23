import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User, ActivityLog

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@test.com",
        password="password123",
        first_name="Admin",
        last_name="User",
        role=User.ADMIN
    )

@pytest.fixture
def manager_user(db):
    return User.objects.create_user(
        email="manager@test.com",
        password="password123",
        first_name="Manager",
        last_name="User",
        role=User.RESIDENTIAL_MANAGER
    )

@pytest.mark.django_db
class TestAccountViews:
    def test_login(self, api_client, manager_user):
        url = "/api/managers/login/"
        data = {
            "email": "manager@test.com",
            "password": "password123"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self, api_client, manager_user):
        url = "/api/managers/login/"
        data = {
            "email": "manager@test.com",
            "password": "wrongpassword"
        }
        response = api_client.post(url, data)
        # In this project's configuration, AuthenticationFailed returns 403
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == "Invalid email or password"

    def test_manager_list_as_admin(self, api_client, admin_user, manager_user):
        api_client.force_authenticate(user=admin_user)
        url = "/api/managers/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Should return both admin and manager
        assert len(response.data) >= 2

    def test_manager_list_as_manager_denied(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        url = "/api/managers/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_manager_as_admin(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = "/api/managers/"
        data = {
            "email": "newmanager@test.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "Manager",
            "role": "RESIDENTIAL_MANAGER",
            "phone": "+250780000000"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newmanager@test.com").exists()

    def test_change_password(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        url = "/api/managers/change-password/"
        data = {
            "old_password": "password123",
            "new_password": "newpassword123",
            "password_confirm": "newpassword123"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify can login with new password
        api_client.logout()
        login_url = "/api/managers/login/"
        login_data = {
            "email": "manager@test.com",
            "password": "newpassword123"
        }
        login_response = api_client.post(login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK

    def test_activity_logs_as_admin(self, api_client, admin_user, manager_user):
        # Create an activity log
        ActivityLog.objects.create(
            user=manager_user,
            action="LOGIN",
            resource="User",
            resource_id=str(manager_user.id)
        )
        
        api_client.force_authenticate(user=admin_user)
        url = "/api/activity-logs/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_logout(self, api_client, manager_user):
        api_client.force_authenticate(user=manager_user)
        # First login to get tokens
        login_url = "/api/managers/login/"
        login_data = {
            "email": "manager@test.com",
            "password": "password123"
        }
        login_response = api_client.post(login_url, login_data)
        assert login_response.status_code == 200, f"Inner login failed: {login_response.content}"
        refresh_token = login_response.data["refresh"]
        
        # Now logout
        logout_url = "/api/managers/logout/"
        response = api_client.post(logout_url, {"refresh": refresh_token})
        assert response.status_code == status.HTTP_204_NO_CONTENT
