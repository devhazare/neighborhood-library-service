"""
API Health Check Tests.
Run with: pytest tests/test_api_health.py -v --html=reports/health_report.html
"""
import pytest


class TestHealthCheck:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "ok"]

    def test_root_redirect_or_response(self, client):
        """Test root endpoint returns something."""
        response = client.get("/", follow_redirects=False)
        # Should either return 200 or redirect
        assert response.status_code in [200, 307, 404]


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""

    def test_openapi_schema(self, client):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_swagger_docs(self, client):
        """Test Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc(self, client):
        """Test ReDoc is available."""
        response = client.get("/redoc")
        assert response.status_code == 200

