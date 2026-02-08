import pytest
from fastapi.testclient import TestClient


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 418  # As per the code


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/login",
        data={"username": "nonexistent", "password": "password"},
    )
    assert response.status_code == 418


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/chats")
    assert response.status_code == 401


def test_protected_endpoint_with_token(client, test_user):
    """Test accessing protected endpoint with valid token."""
    # Login first
    login_response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/chats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
