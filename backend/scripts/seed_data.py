import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.book import Book
from app.models.member import Member
from app.models.borrow_transaction import BorrowTransaction
import uuid
from datetime import date, datetime, timedelta, timezone


def seed():
    db = SessionLocal()
    try:
        today = date.today()

        # Clear existing data (in reverse order due to foreign keys)
        db.query(BorrowTransaction).delete()
        db.query(Member).delete()
        db.query(Book).delete()
        db.commit()
        print("Cleared existing seed data.")

        # ------------------------------------------------------------------
        # Books
        # ------------------------------------------------------------------
        books_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Atomic Habits",
                "author": "James Clear",
                "isbn": "9780735211292",
                "category": "Self-Help",
                "total_copies": 3,
                "available_copies": 2,
                "tags": ["habits", "productivity", "self-improvement"],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "9780743273565",
                "category": "Fiction",
                "total_copies": 2,
                "available_copies": 2,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Sapiens: A Brief History of Humankind",
                "author": "Yuval Noah Harari",
                "isbn": "9780062316097",
                "category": "History",
                "total_copies": 2,
                "available_copies": 1,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "The Pragmatic Programmer",
                "author": "David Thomas",
                "isbn": "9780135957059",
                "category": "Technology",
                "total_copies": 2,
                "available_copies": 2,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "isbn": "9780061935466",
                "category": "Fiction",
                "total_copies": 3,
                "available_copies": 3,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "A Brief History of Time",
                "author": "Stephen Hawking",
                "isbn": "9780553380163",
                "category": "Science",
                "total_copies": 1,
                "available_copies": 0,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "The Alchemist",
                "author": "Paulo Coelho",
                "isbn": "9780062315007",
                "category": "Fiction",
                "total_copies": 2,
                "available_copies": 2,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "isbn": "9780132350884",
                "category": "Technology",
                "total_copies": 1,
                "available_copies": 1,
            },
        ]

        books = []
        for data in books_data:
            book = Book(**data)
            db.add(book)
            books.append(book)
        db.flush()

        book_by_title = {b.title: b for b in books}
        print(f"Created {len(books)} books:")
        for b in books:
            print(f"  - [{b.category}] {b.title} by {b.author}")

        # ------------------------------------------------------------------
        # Members
        # ------------------------------------------------------------------
        members_data = [
            {
                "id": str(uuid.uuid4()),
                "membership_id": "MEM001",
                "full_name": "Alice Johnson",
                "email": "alice@email.com",
                "status": "active",
                "joined_date": today - timedelta(days=365),
            },
            {
                "id": str(uuid.uuid4()),
                "membership_id": "MEM002",
                "full_name": "Bob Smith",
                "email": "bob@email.com",
                "status": "active",
                "joined_date": today - timedelta(days=300),
            },
            {
                "id": str(uuid.uuid4()),
                "membership_id": "MEM003",
                "full_name": "Carol White",
                "email": "carol@email.com",
                "status": "active",
                "joined_date": today - timedelta(days=200),
            },
            {
                "id": str(uuid.uuid4()),
                "membership_id": "MEM004",
                "full_name": "David Brown",
                "email": "david@email.com",
                "status": "inactive",
                "joined_date": today - timedelta(days=500),
            },
            {
                "id": str(uuid.uuid4()),
                "membership_id": "MEM005",
                "full_name": "Emma Davis",
                "email": "emma@email.com",
                "status": "active",
                "joined_date": today - timedelta(days=90),
            },
        ]

        members = []
        for data in members_data:
            member = Member(**data)
            db.add(member)
            members.append(member)
        db.flush()

        member_by_name = {m.full_name: m for m in members}
        print(f"\nCreated {len(members)} members:")
        for m in members:
            print(f"  - [{m.status}] {m.full_name} ({m.membership_id})")

        # ------------------------------------------------------------------
        # Borrow Transactions
        # ------------------------------------------------------------------
        alice = member_by_name["Alice Johnson"]
        bob = member_by_name["Bob Smith"]
        carol = member_by_name["Carol White"]

        sapiens = book_by_title["Sapiens: A Brief History of Humankind"]
        brief_history = book_by_title["A Brief History of Time"]
        atomic_habits = book_by_title["Atomic Habits"]

        transactions_data = [
            # Alice borrowed Sapiens — active, due in 4 days
            BorrowTransaction(
                id=str(uuid.uuid4()),
                book_id=sapiens.id,
                member_id=alice.id,
                borrow_date=today - timedelta(days=10),
                due_date=today + timedelta(days=4),
                status="borrowed",
                overdue_days=0,
            ),
            # Bob borrowed A Brief History of Time — overdue by 6 days
            BorrowTransaction(
                id=str(uuid.uuid4()),
                book_id=brief_history.id,
                member_id=bob.id,
                borrow_date=today - timedelta(days=20),
                due_date=today - timedelta(days=6),
                status="overdue",
                overdue_days=6,
            ),
            # Carol borrowed Atomic Habits — returned 3 days ago
            BorrowTransaction(
                id=str(uuid.uuid4()),
                book_id=atomic_habits.id,
                member_id=carol.id,
                borrow_date=today - timedelta(days=17),
                due_date=today - timedelta(days=3),
                return_date=today - timedelta(days=3),
                status="returned",
                overdue_days=0,
            ),
        ]

        for txn in transactions_data:
            db.add(txn)

        db.commit()

        print(f"\nCreated {len(transactions_data)} borrow transactions:")
        print(f"  - Alice Johnson borrowed 'Sapiens' (due {today + timedelta(days=4)}) — active")
        print(f"  - Bob Smith borrowed 'A Brief History of Time' (overdue by 6 days) — OVERDUE")
        print(f"  - Carol White borrowed 'Atomic Habits' (returned {today - timedelta(days=3)}) — returned")

        print("\nSeed data created successfully.")

    except Exception as exc:
        db.rollback()
        print(f"Error seeding data: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
