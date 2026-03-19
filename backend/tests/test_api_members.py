"""
Comprehensive API Tests for Members Endpoints.
Run with: pytest tests/test_api_members.py -v --html=reports/members_report.html
"""
import pytest


class TestMembersCreate:
    """Tests for member creation endpoint."""

    def test_create_member_success(self, client, auth_headers, sample_member_data):
        """Test successful member creation."""
        response = client.post("/api/v1/members", json=sample_member_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == sample_member_data["full_name"]
        assert data["membership_id"] == sample_member_data["membership_id"]
        assert "id" in data

    def test_create_member_unauthenticated(self, client, sample_member_data):
        """Test member creation without auth fails."""
        response = client.post("/api/v1/members", json=sample_member_data)
        assert response.status_code == 401

    def test_create_member_missing_required_fields(self, client, auth_headers):
        """Test member creation with missing fields fails."""
        response = client.post("/api/v1/members", json={
            "full_name": "Incomplete Member"
            # Missing membership_id
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_member_duplicate_membership_id(self, client, auth_headers, created_member, sample_member_data):
        """Test creating member with duplicate membership_id fails."""
        sample_member_data["membership_id"] = created_member["membership_id"]
        sample_member_data["email"] = "different@example.com"
        response = client.post("/api/v1/members", json=sample_member_data, headers=auth_headers)
        assert response.status_code == 422


class TestMembersList:
    """Tests for members listing endpoint."""

    def test_list_members(self, client, auth_headers, created_member):
        """Test listing members."""
        response = client.get("/api/v1/members", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_list_members_pagination(self, client, auth_headers):
        """Test members pagination."""
        response = client.get("/api/v1/members?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5


class TestMembersSearch:
    """Tests for members search endpoint."""

    def test_search_members_by_name(self, client, auth_headers, created_member):
        """Test searching members by name."""
        response = client.get(
            f"/api/v1/members/search?q={created_member['full_name'][:4]}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_search_members_by_status(self, client, auth_headers, created_member):
        """Test filtering members by status."""
        response = client.get(
            "/api/v1/members/search?status=active",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for member in data["items"]:
            assert member["status"] == "active"

    def test_search_inactive_members(self, client, auth_headers):
        """Test filtering inactive members."""
        response = client.get(
            "/api/v1/members/search?status=inactive",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestMembersGetById:
    """Tests for getting member by ID."""

    def test_get_member_by_id(self, client, auth_headers, created_member):
        """Test getting member by ID."""
        response = client.get(f"/api/v1/members/{created_member['id']}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_member["id"]
        assert data["full_name"] == created_member["full_name"]

    def test_get_member_not_found(self, client, auth_headers):
        """Test getting non-existent member returns 404."""
        response = client.get(
            "/api/v1/members/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestMembersUpdate:
    """Tests for member update endpoint."""

    def test_update_member(self, client, auth_headers, created_member):
        """Test updating a member."""
        response = client.put(
            f"/api/v1/members/{created_member['id']}",
            json={"full_name": "Updated Name"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    def test_update_member_status(self, client, auth_headers, created_member):
        """Test updating member status."""
        response = client.put(
            f"/api/v1/members/{created_member['id']}",
            json={"status": "inactive"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"

    def test_update_member_not_found(self, client, auth_headers):
        """Test updating non-existent member returns 404."""
        response = client.put(
            "/api/v1/members/00000000-0000-0000-0000-000000000000",
            json={"full_name": "Updated"},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestMembersDelete:
    """Tests for member deletion endpoint."""

    def test_delete_member(self, client, auth_headers, created_member):
        """Test deleting a member."""
        response = client.delete(
            f"/api/v1/members/{created_member['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/v1/members/{created_member['id']}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_member_not_found(self, client, auth_headers):
        """Test deleting non-existent member returns 404."""
        response = client.delete(
            "/api/v1/members/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestMemberBorrowedBooks:
    """Tests for member borrowed books endpoint."""

    def test_get_member_borrowed_books(self, client, auth_headers, created_member):
        """Test getting member's borrowed books."""
        response = client.get(
            f"/api/v1/members/{created_member['id']}/borrowed-books",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

