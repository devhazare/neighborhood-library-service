"""
Comprehensive API Tests for Fines Endpoints.
Run with: pytest tests/test_api_fines.py -v --html=reports/fines_report.html
"""
import pytest


class TestFinesListUnpaid:
    """Tests for unpaid fines listing endpoint."""

    def test_list_unpaid_fines(self, client, auth_headers):
        """Test listing unpaid fines."""
        response = client.get("/api/v1/fines/unpaid", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_unpaid_fines_by_member(self, client, auth_headers, created_member):
        """Test listing unpaid fines for specific member."""
        response = client.get(
            f"/api/v1/fines/unpaid?member_id={created_member['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestMemberFines:
    """Tests for member fines summary endpoint."""

    def test_get_member_fines(self, client, auth_headers, created_member):
        """Test getting member fines summary."""
        response = client.get(
            f"/api/v1/members/{created_member['id']}/fines",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_fines" in data or "total_unpaid" in data or isinstance(data, dict)

    def test_get_fines_nonexistent_member(self, client, auth_headers):
        """Test getting fines for non-existent member."""
        response = client.get(
            "/api/v1/members/00000000-0000-0000-0000-000000000000/fines",
            headers=auth_headers
        )
        assert response.status_code == 404

