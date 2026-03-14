import pytest

def test_create_book(client, sample_book_data):
    resp = client.post("/api/v1/books", json=sample_book_data)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == sample_book_data["title"]
    assert data["author"] == sample_book_data["author"]
    assert "id" in data

def test_get_book(client, sample_book_data):
    create_resp = client.post("/api/v1/books", json={**sample_book_data, "isbn": "978-0-000-00000-2"})
    book_id = create_resp.json()["id"]
    resp = client.get(f"/api/v1/books/{book_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == book_id

def test_list_books(client, sample_book_data):
    client.post("/api/v1/books", json={**sample_book_data, "isbn": "978-0-000-00000-3"})
    resp = client.get("/api/v1/books")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1

def test_update_book(client, sample_book_data):
    create_resp = client.post("/api/v1/books", json={**sample_book_data, "isbn": "978-0-000-00000-4"})
    book_id = create_resp.json()["id"]
    resp = client.put(f"/api/v1/books/{book_id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"

def test_create_book_duplicate_isbn(client, sample_book_data):
    client.post("/api/v1/books", json={**sample_book_data, "isbn": "978-0-000-00000-5"})
    resp = client.post("/api/v1/books", json={**sample_book_data, "isbn": "978-0-000-00000-5"})
    assert resp.status_code == 422
