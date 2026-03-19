"""
Comprehensive API Tests for Borrow/Return Endpoints.
Run with: pytest tests/test_api_borrow.py -v --html=reports/borrow_report.html
"""
import pytest


class TestBorrowBook:
    """Tests for book borrowing endpoint."""

    def test_borrow_book_success(self, client, auth_headers, created_book, created_member):
        """Test successful book borrowing."""
        response = client.post("/api/v1/borrow", json={
            "book_id": created_book["id"],
            "member_id": created_member["id"]
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["book_id"] == created_book["id"]
        assert data["member_id"] == created_member["id"]
        assert data["status"] == "borrowed"
        assert "due_date" in data

    def test_borrow_book_unauthenticated(self, client, created_book, created_member):
        """Test borrowing without auth fails."""
        response = client.post("/api/v1/borrow", json={
            "book_id": created_book["id"],
            "member_id": created_member["id"]
        })
        assert response.status_code == 401

    def test_borrow_nonexistent_book(self, client, auth_headers, created_member):
        """Test borrowing non-existent book fails."""
        response = client.post("/api/v1/borrow", json={
            "book_id": "00000000-0000-0000-0000-000000000000",
            "member_id": created_member["id"]
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_borrow_nonexistent_member(self, client, auth_headers, created_book):
        """Test borrowing for non-existent member fails."""
        response = client.post("/api/v1/borrow", json={
            "book_id": created_book["id"],
            "member_id": "00000000-0000-0000-0000-000000000000"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestReturnBook:
    """Tests for book return endpoint."""

    def test_return_book_success(self, client, auth_headers, created_book, created_member):
        """Test successful book return."""
        # First borrow the book
        borrow_response = client.post("/api/v1/borrow", json={
            "book_id": created_book["id"],
            "member_id": created_member["id"]
        }, headers=auth_headers)
        borrow_id = borrow_response.json()["id"]

        # Then return it
        response = client.post("/api/v1/return", json={
            "borrow_id": borrow_id
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "returned"
        assert "return_date" in data

    def test_return_nonexistent_borrow(self, client, auth_headers):
        """Test returning non-existent borrow fails."""
        response = client.post("/api/v1/return", json={
            "borrow_id": "00000000-0000-0000-0000-000000000000"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestActiveBorrowings:
    """Tests for active borrowings endpoint."""

    def test_list_active_borrowings(self, client, auth_headers):
        """Test listing active borrowings."""
        response = client.get("/api/v1/borrow/active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_active_borrowings_pagination(self, client, auth_headers):
        """Test active borrowings pagination."""
        response = client.get("/api/v1/borrow/active?skip=0&limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10


class TestOverdueBorrowings:
    """Tests for overdue borrowings endpoint."""

    def test_list_overdue_borrowings(self, client, auth_headers):
        """Test listing overdue borrowings."""
        response = client.get("/api/v1/borrow/overdue", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestDuplicateBorrowPrevention:
    """Tests for duplicate borrow prevention."""

    def test_cannot_borrow_same_book_twice(self, client, auth_headers, created_book, created_member):
        """Test that member cannot borrow same book twice."""
        # First borrow
        response1 = client.post("/api/v1/borrow", json={
            "book_id": created_book["id"],
            "member_id": created_member["id"]
        }, headers=auth_headers)
        assert response1.status_code == 201

        # Second borrow attempt should fail
        response2 = client.post("/api/v1/borrow", json={
            "book_id": created_book["id"],
            "member_id": created_member["id"]
        }, headers=auth_headers)
        assert response2.status_code in [400, 409, 422]
        assert "already" in response2.json()["detail"].lower()

