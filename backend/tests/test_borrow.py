import pytest

@pytest.fixture()
def book_and_member(client):
    book_resp = client.post("/api/v1/books", json={
        "title": "Borrow Test Book", "author": "Author X", "isbn": "978-0-000-00100-1",
        "category": "Fiction", "total_copies": 2, "available_copies": 2
    })
    member_resp = client.post("/api/v1/members", json={
        "membership_id": "BOR-MEM-001", "full_name": "Borrower One",
        "email": "borrow1@example.com", "status": "active"
    })
    return book_resp.json()["id"], member_resp.json()["id"]

def test_borrow_book_success(client, book_and_member):
    book_id, member_id = book_and_member
    resp = client.post("/api/v1/borrow", json={"book_id": book_id, "member_id": member_id})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "borrowed"
    assert data["book_id"] == book_id

def test_borrow_book_unavailable(client):
    book_resp = client.post("/api/v1/books", json={
        "title": "No Copy Book", "author": "Author Y", "isbn": "978-0-000-00100-2",
        "category": "Fiction", "total_copies": 0, "available_copies": 0
    })
    member_resp = client.post("/api/v1/members", json={
        "membership_id": "BOR-MEM-002", "full_name": "Borrower Two",
        "email": "borrow2@example.com", "status": "active"
    })
    resp = client.post("/api/v1/borrow", json={
        "book_id": book_resp.json()["id"], "member_id": member_resp.json()["id"]
    })
    assert resp.status_code == 409

def test_borrow_inactive_member(client):
    book_resp = client.post("/api/v1/books", json={
        "title": "Inactive Test Book", "author": "Author Z", "isbn": "978-0-000-00100-3",
        "category": "Fiction", "total_copies": 2, "available_copies": 2
    })
    member_resp = client.post("/api/v1/members", json={
        "membership_id": "BOR-MEM-003", "full_name": "Borrower Three",
        "email": "borrow3@example.com", "status": "inactive"
    })
    resp = client.post("/api/v1/borrow", json={
        "book_id": book_resp.json()["id"], "member_id": member_resp.json()["id"]
    })
    assert resp.status_code == 409

def test_return_book_success(client, book_and_member):
    book_id, member_id = book_and_member
    borrow_resp = client.post("/api/v1/borrow", json={"book_id": book_id, "member_id": member_id})
    borrow_id = borrow_resp.json()["id"]
    resp = client.post("/api/v1/return", json={"borrow_id": borrow_id})
    assert resp.status_code == 200
    assert resp.json()["status"] == "returned"

def test_list_active_borrowings(client, book_and_member):
    book_id, member_id = book_and_member
    client.post("/api/v1/borrow", json={"book_id": book_id, "member_id": member_id})
    resp = client.get("/api/v1/borrow/active")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data

def test_list_overdue(client):
    resp = client.get("/api/v1/borrow/overdue")
    assert resp.status_code == 200
    assert "items" in resp.json()
