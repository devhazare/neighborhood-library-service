"""Test for duplicate borrow protection."""

import pytest
from sqlalchemy.orm import Session
from app.services import borrow_service
from app.core.exceptions import BusinessRuleError
from app.repositories import book_repository, member_repository


class TestDuplicateBorrowProtection:
    """Test that members cannot borrow the same book twice simultaneously."""

    @pytest.fixture
    def sample_member(self, db_session: Session):
        """Create a test member."""
        member_data = {
            "membership_id": "TEST001",
            "full_name": "Test Member",
            "email": "test@example.com",
            "status": "active"
        }
        return member_repository.create(db_session, member_data)

    @pytest.fixture
    def sample_book(self, db_session: Session):
        """Create a test book."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "total_copies": 2,
            "available_copies": 2
        }
        return book_repository.create(db_session, book_data)

    def test_cannot_borrow_same_book_twice(self, db_session: Session, sample_member, sample_book):
        """Test that a member cannot borrow the same book twice while it's active."""

        # First borrow should succeed
        first_borrow = borrow_service.borrow_book(
            db_session,
            sample_book.id,
            sample_member.id
        )
        assert first_borrow is not None
        assert first_borrow.status == "borrowed"

        # Second borrow attempt should fail with clear error
        with pytest.raises(BusinessRuleError) as exc_info:
            borrow_service.borrow_book(
                db_session,
                sample_book.id,
                sample_member.id
            )

        assert "already has this book borrowed" in str(exc_info.value)
        assert "return it before borrowing again" in str(exc_info.value)

    def test_can_borrow_after_return(self, db_session: Session, sample_member, sample_book):
        """Test that a member CAN borrow the same book again after returning it."""

        # Borrow the book
        first_borrow = borrow_service.borrow_book(
            db_session,
            sample_book.id,
            sample_member.id
        )

        # Return the book
        borrow_service.return_book(db_session, first_borrow.id)

        # Should be able to borrow again
        second_borrow = borrow_service.borrow_book(
            db_session,
            sample_book.id,
            sample_member.id
        )

        assert second_borrow is not None
        assert second_borrow.id != first_borrow.id  # Different transaction
        assert second_borrow.status == "borrowed"

    def test_different_members_can_borrow_same_book(self, db_session: Session, sample_book):
        """Test that different members can borrow copies of the same book."""

        # Create two members
        member1_data = {
            "membership_id": "TEST002",
            "full_name": "Member One",
            "email": "member1@example.com",
            "status": "active"
        }
        member1 = member_repository.create(db_session, member1_data)

        member2_data = {
            "membership_id": "TEST003",
            "full_name": "Member Two",
            "email": "member2@example.com",
            "status": "active"
        }
        member2 = member_repository.create(db_session, member2_data)

        # Both should be able to borrow the same book (different copies)
        borrow1 = borrow_service.borrow_book(db_session, sample_book.id, member1.id)
        borrow2 = borrow_service.borrow_book(db_session, sample_book.id, member2.id)

        assert borrow1.book_id == borrow2.book_id  # Same book
        assert borrow1.member_id != borrow2.member_id  # Different members
        assert borrow1.status == "borrowed"
        assert borrow2.status == "borrowed"

    def test_overdue_book_still_blocks_duplicate(self, db_session: Session, sample_member, sample_book):
        """Test that an overdue book still prevents duplicate borrowing."""

        # Borrow the book
        borrow = borrow_service.borrow_book(
            db_session,
            sample_book.id,
            sample_member.id
        )

        # Manually set to overdue (simulating time passing)
        borrow.status = "overdue"
        db_session.commit()

        # Should still not be able to borrow again while overdue
        with pytest.raises(BusinessRuleError) as exc_info:
            borrow_service.borrow_book(
                db_session,
                sample_book.id,
                sample_member.id
            )

        assert "already has this book borrowed" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

