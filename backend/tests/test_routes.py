import pytest


def test_get_chats_empty(client, test_user):
    """Test getting chats for a user with no chats."""
    # Login first
    login_response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = login_response.json()["access_token"]
    
    # Get chats
    response = client.get(
        "/api/chats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_create_chat(client, test_user):
    """Test creating a new chat."""
    # Login first
    login_response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = login_response.json()["access_token"]
    
    # Create chat
    response = client.post(
        "/api/chats",
        json={"title": "Test Chat"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Chat"


def test_admin_endpoints_require_admin(client, test_user):
    """Test that admin endpoints require admin privileges."""
    # Login as regular user
    login_response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = login_response.json()["access_token"]
    
    # Try to access admin endpoint
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_admin_endpoints_with_admin(client, test_admin):
    """Test that admin can access admin endpoints."""
    # Login as admin
    login_response = client.post(
        "/api/login",
        data={"username": "admin", "password": "adminpassword"},
    )
    token = login_response.json()["access_token"]
    
    # Access admin endpoint
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
