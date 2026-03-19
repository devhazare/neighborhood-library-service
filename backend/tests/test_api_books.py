"""
Comprehensive API Tests for Books Endpoints.
Run with: pytest tests/test_api_books.py -v --html=reports/books_report.html
"""
import pytest


class TestBooksCreate:
    """Tests for book creation endpoint."""

    def test_create_book_success(self, client, auth_headers, sample_book_data):
        """Test successful book creation."""
        response = client.post("/api/v1/books", json=sample_book_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_book_data["title"]
        assert data["author"] == sample_book_data["author"]
        assert "id" in data

    def test_create_book_unauthenticated(self, client, sample_book_data):
        """Test book creation without auth fails."""
        response = client.post("/api/v1/books", json=sample_book_data)
        assert response.status_code == 401

    def test_create_book_missing_required_fields(self, client, auth_headers):
        """Test book creation with missing fields fails."""
        response = client.post("/api/v1/books", json={
            "title": "Incomplete Book"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_book_duplicate_isbn(self, client, auth_headers, created_book, sample_book_data):
        """Test creating book with duplicate ISBN fails."""
        sample_book_data["isbn"] = created_book["isbn"]
        sample_book_data["title"] = "Different Book"
        response = client.post("/api/v1/books", json=sample_book_data, headers=auth_headers)
        assert response.status_code == 422


class TestBooksList:
    """Tests for books listing endpoint."""

    def test_list_books(self, client, auth_headers, created_book):
        """Test listing books."""
        response = client.get("/api/v1/books", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_list_books_pagination(self, client, auth_headers):
        """Test books pagination."""
        response = client.get("/api/v1/books?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5


class TestBooksSearch:
    """Tests for books search endpoint."""

    def test_search_books_by_title(self, client, auth_headers, created_book):
        """Test searching books by title."""
        response = client.get(
            f"/api/v1/books/search?q={created_book['title'][:4]}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_search_books_by_category(self, client, auth_headers, created_book):
        """Test filtering books by category."""
        response = client.get(
            f"/api/v1/books/search?category={created_book['category']}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_search_books_available_only(self, client, auth_headers, created_book):
        """Test filtering available books only."""
        response = client.get(
            "/api/v1/books/search?available_only=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for book in data["items"]:
            assert book["available_copies"] > 0


class TestBooksGetById:
    """Tests for getting book by ID."""

    def test_get_book_by_id(self, client, auth_headers, created_book):
        """Test getting book by ID."""
        response = client.get(f"/api/v1/books/{created_book['id']}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_book["id"]
        assert data["title"] == created_book["title"]

    def test_get_book_not_found(self, client, auth_headers):
        """Test getting non-existent book returns 404."""
        response = client.get(
            "/api/v1/books/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestBooksUpdate:
    """Tests for book update endpoint."""

    def test_update_book(self, client, auth_headers, created_book):
        """Test updating a book."""
        response = client.put(
            f"/api/v1/books/{created_book['id']}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_book_not_found(self, client, auth_headers):
        """Test updating non-existent book returns 404."""
        response = client.put(
            "/api/v1/books/00000000-0000-0000-0000-000000000000",
            json={"title": "Updated"},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestBooksDelete:
    """Tests for book deletion endpoint."""

    def test_delete_book(self, client, auth_headers, created_book):
        """Test deleting a book."""
        response = client.delete(
            f"/api/v1/books/{created_book['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/v1/books/{created_book['id']}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_book_not_found(self, client, auth_headers):
        """Test deleting non-existent book returns 404."""
        response = client.delete(
            "/api/v1/books/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404

