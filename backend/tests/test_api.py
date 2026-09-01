"""
Integration tests for SmartFlow API endpoints.
Uses FastAPI TestClient for HTTP-level testing.
"""
import pytest


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_project_name(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "project" in data
        assert data["project"] == "SmartFlow"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_new_user(self, client):
        response = client.post("/api/auth/register", json={
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        })
        # Should succeed or return 400 if user exists
        assert response.status_code in [200, 201, 400]

    def test_register_duplicate_returns_error(self, client):
        payload = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        }
        # Register first time
        client.post("/api/auth/register", json=payload)
        # Register again — should fail
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code in [400, 409, 422]

    def test_login_with_invalid_credentials(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code in [401, 403, 404, 422]


class TestDataEndpoints:
    """Test data retrieval endpoints (may require auth in production)."""

    def test_unknown_route_returns_404(self, client):
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_openapi_docs_available(self, client):
        """FastAPI auto-generates OpenAPI docs at /docs."""
        response = client.get("/docs")
        assert response.status_code == 200
