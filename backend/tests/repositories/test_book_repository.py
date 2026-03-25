"""Tests for BookRepository."""

import pytest
from sqlalchemy.orm import Session
from app.repositories.book_repository import BookRepository
from app.models.book import Book


class TestBookRepository:
    """Test suite for BookRepository."""

    @pytest.fixture
    def book_repo(self, db_session: Session):
        """Create a BookRepository instance."""
        return BookRepository(db_session)

    @pytest.fixture
    def sample_book_data(self):
        """Sample book data for testing."""
        return {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-0-123456-78-9",
            "publisher": "Test Publisher",
            "published_year": 2024,
            "category": "Technology",
            "total_copies": 5,
            "available_copies": 5,
            "shelf_location": "A1"
        }

    def test_create_book(self, book_repo: BookRepository, sample_book_data):
        """Test creating a new book."""
        book = book_repo.create(sample_book_data)

        assert book.id is not None
        assert book.title == sample_book_data["title"]
        assert book.author == sample_book_data["author"]
        assert book.available_copies == 5

    def test_get_by_id(self, book_repo: BookRepository, sample_book_data):
        """Test retrieving a book by ID."""
        created_book = book_repo.create(sample_book_data)
        retrieved_book = book_repo.get_by_id(created_book.id)

        assert retrieved_book is not None
        assert retrieved_book.id == created_book.id
        assert retrieved_book.title == created_book.title

    def test_get_by_id_not_found(self, book_repo: BookRepository):
        """Test retrieving a non-existent book."""
        book = book_repo.get_by_id("non-existent-id")
        assert book is None

    def test_list_all(self, book_repo: BookRepository, sample_book_data):
        """Test listing all books."""
        # Create multiple books
        book_repo.create(sample_book_data)
        book_repo.create({**sample_book_data, "title": "Another Book", "isbn": "978-1-234567-89-0"})

        books = book_repo.list_all()
        assert len(books) >= 2

    def test_search_by_title(self, book_repo: BookRepository, sample_book_data):
        """Test searching books by title."""
        book_repo.create({**sample_book_data, "title": "Python Programming"})
        book_repo.create({**sample_book_data, "title": "JavaScript Basics", "isbn": "978-1-234567-89-0"})

        results = book_repo.search(query="Python")
        assert len(results) >= 1
        assert any("Python" in book.title for book in results)

    def test_search_by_author(self, book_repo: BookRepository, sample_book_data):
        """Test searching books by author."""
        book_repo.create({**sample_book_data, "author": "John Smith"})
        book_repo.create({**sample_book_data, "author": "Jane Doe", "isbn": "978-1-234567-89-0"})

        results = book_repo.search(query="Smith")
        assert len(results) >= 1
        assert any("Smith" in book.author for book in results)

    def test_filter_by_category(self, book_repo: BookRepository, sample_book_data):
        """Test filtering books by category."""
        book_repo.create({**sample_book_data, "category": "Technology"})
        book_repo.create({**sample_book_data, "title": "Fiction Book", "category": "Fiction", "isbn": "978-1-234567-89-0"})

        results = book_repo.search(category="Technology")
        assert len(results) >= 1
        assert all(book.category == "Technology" for book in results)

    def test_filter_available_only(self, book_repo: BookRepository, sample_book_data):
        """Test filtering only available books."""
        book_repo.create({**sample_book_data, "available_copies": 5})
        book_repo.create({**sample_book_data, "title": "Unavailable Book", "available_copies": 0, "isbn": "978-1-234567-89-0"})

        results = book_repo.search(available_only=True)
        assert all(book.available_copies > 0 for book in results)

    def test_update_book(self, book_repo: BookRepository, sample_book_data):
        """Test updating a book."""
        book = book_repo.create(sample_book_data)

        updated_data = {"title": "Updated Title", "available_copies": 3}
        updated_book = book_repo.update(book.id, updated_data)

        assert updated_book.title == "Updated Title"
        assert updated_book.available_copies == 3

    def test_delete_book(self, book_repo: BookRepository, sample_book_data):
        """Test deleting a book."""
        book = book_repo.create(sample_book_data)
        book_id = book.id

        result = book_repo.delete(book_id)
        assert result is True

        deleted_book = book_repo.get_by_id(book_id)
        assert deleted_book is None

    def test_get_by_isbn(self, book_repo: BookRepository, sample_book_data):
        """Test retrieving a book by ISBN."""
        created_book = book_repo.create(sample_book_data)
        retrieved_book = book_repo.get_by_isbn(sample_book_data["isbn"])

        assert retrieved_book is not None
        assert retrieved_book.isbn == sample_book_data["isbn"]

    def test_decrease_available_copies(self, book_repo: BookRepository, sample_book_data):
        """Test decreasing available copies when book is borrowed."""
        book = book_repo.create(sample_book_data)
        original_copies = book.available_copies

        book_repo.update(book.id, {"available_copies": original_copies - 1})
        updated_book = book_repo.get_by_id(book.id)

        assert updated_book.available_copies == original_copies - 1

    def test_increase_available_copies(self, book_repo: BookRepository, sample_book_data):
        """Test increasing available copies when book is returned."""
        book = book_repo.create({**sample_book_data, "available_copies": 3})

        book_repo.update(book.id, {"available_copies": 4})
        updated_book = book_repo.get_by_id(book.id)

        assert updated_book.available_copies == 4

    def test_pagination(self, book_repo: BookRepository, sample_book_data):
        """Test pagination of book listings."""
        # Create multiple books
        for i in range(5):
            book_repo.create({
                **sample_book_data,
                "title": f"Book {i}",
                "isbn": f"978-0-12345{i}-78-9"
            })

        # Test first page
        page1 = book_repo.list_all(skip=0, limit=2)
        assert len(page1) == 2

        # Test second page
        page2 = book_repo.list_all(skip=2, limit=2)
        assert len(page2) == 2

        # Ensure different results
        assert page1[0].id != page2[0].id

