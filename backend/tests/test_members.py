import pytest

def test_create_member(client, sample_member_data):
    resp = client.post("/api/v1/members", json=sample_member_data)
    assert resp.status_code == 201
    data = resp.json()
    assert data["full_name"] == sample_member_data["full_name"]
    assert "id" in data

def test_get_member(client, sample_member_data):
    create_resp = client.post("/api/v1/members", json={**sample_member_data, "membership_id": "MEM-101", "email": "m101@example.com"})
    member_id = create_resp.json()["id"]
    resp = client.get(f"/api/v1/members/{member_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == member_id

def test_list_members(client, sample_member_data):
    client.post("/api/v1/members", json={**sample_member_data, "membership_id": "MEM-102", "email": "m102@example.com"})
    resp = client.get("/api/v1/members")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 1

def test_update_member(client, sample_member_data):
    create_resp = client.post("/api/v1/members", json={**sample_member_data, "membership_id": "MEM-103", "email": "m103@example.com"})
    member_id = create_resp.json()["id"]
    resp = client.put(f"/api/v1/members/{member_id}", json={"full_name": "Jane Updated"})
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Jane Updated"

def test_member_duplicate_membership_id(client, sample_member_data):
    client.post("/api/v1/members", json={**sample_member_data, "membership_id": "MEM-DUP", "email": "dup1@example.com"})
    resp = client.post("/api/v1/members", json={**sample_member_data, "membership_id": "MEM-DUP", "email": "dup2@example.com"})
    assert resp.status_code == 422
