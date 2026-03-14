import pytest

def test_ai_enrich_book_mock(client):
    book_resp = client.post("/api/v1/books", json={
        "title": "AI Test Book", "author": "AI Author", "isbn": "978-0-000-00200-1",
        "category": "Science"
    })
    assert book_resp.status_code == 201
    book_id = book_resp.json()["id"]
    resp = client.post(f"/api/v1/books/{book_id}/ai-enrich")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "tags" in data

def test_generate_reminder_mock(client):
    book_resp = client.post("/api/v1/books", json={
        "title": "Reminder Book", "author": "Reminder Author", "isbn": "978-0-000-00200-2",
        "category": "Fiction", "total_copies": 2, "available_copies": 2
    })
    member_resp = client.post("/api/v1/members", json={
        "membership_id": "AI-MEM-001", "full_name": "AI Tester",
        "email": "aitester@example.com", "status": "active"
    })
    borrow_resp = client.post("/api/v1/borrow", json={
        "book_id": book_resp.json()["id"], "member_id": member_resp.json()["id"]
    })
    borrow_id = borrow_resp.json()["id"]
    resp = client.post(f"/api/v1/borrow/{borrow_id}/generate-reminder")
    assert resp.status_code == 200
    assert "message" in resp.json()

def test_recommendations_empty_history(client):
    member_resp = client.post("/api/v1/members", json={
        "membership_id": "AI-MEM-002", "full_name": "No History",
        "email": "nohistory@example.com", "status": "active"
    })
    member_id = member_resp.json()["id"]
    resp = client.get(f"/api/v1/members/{member_id}/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
