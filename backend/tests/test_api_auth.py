"""
Comprehensive API Tests for Authentication Endpoints.
Run with: pytest tests/test_api_auth.py -v --html=reports/auth_report.html
"""
import pytest
import time
from jose import jwt


class TestAuthRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "full_name": "New User"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        # Ensure password is not returned
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_weak_password(self, client):
        """Test registration with weak password fails."""
        response = client.post("/api/v1/auth/register", json={
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak",  # Too short, no uppercase, no digit
        })
        assert response.status_code == 422

    def test_register_password_no_uppercase(self, client):
        """Test registration without uppercase letter fails."""
        response = client.post("/api/v1/auth/register", json={
            "username": "noupperuser",
            "email": "noupper@example.com",
            "password": "password123",  # No uppercase
        })
        assert response.status_code == 422

    def test_register_password_no_digit(self, client):
        """Test registration without digit fails."""
        response = client.post("/api/v1/auth/register", json={
            "username": "nodigituser",
            "email": "nodigit@example.com",
            "password": "PasswordNoDigit",  # No digit
        })
        assert response.status_code == 422

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username fails."""
        response = client.post("/api/v1/auth/register", json={
            "username": test_user["user"].username,
            "email": "another@example.com",
            "password": "SecurePass123",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post("/api/v1/auth/register", json={
            "username": "differentuser",
            "email": test_user["user"].email,
            "password": "SecurePass123",
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post("/api/v1/auth/register", json={
            "username": "invalidemailuser",
            "email": "not-an-email",
            "password": "SecurePass123",
        })
        assert response.status_code == 422


class TestAuthLogin:
    """Tests for user login endpoints."""

    def test_login_json_success(self, client, test_user):
        """Test successful login with JSON endpoint."""
        response = client.post("/api/v1/auth/login/json", json={
            "username": test_user["user"].username,
            "password": test_user["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # Token should be a valid JWT string
        assert len(data["access_token"]) > 50

    def test_login_returns_valid_jwt(self, client, test_user):
        """Test that login returns a properly formatted JWT."""
        response = client.post("/api/v1/auth/login/json", json={
            "username": test_user["user"].username,
            "password": test_user["password"]
        })
        token = response.json()["access_token"]
        # JWT has 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post("/api/v1/auth/login/json", json={
            "username": test_user["user"].username,
            "password": "WrongPassword123"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post("/api/v1/auth/login/json", json={
            "username": "nonexistent",
            "password": "SomePassword123"
        })
        assert response.status_code == 401

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials fails."""
        response = client.post("/api/v1/auth/login/json", json={
            "username": "",
            "password": ""
        })
        assert response.status_code in [401, 422]

    def test_login_sql_injection_attempt(self, client):
        """Test login is protected against SQL injection."""
        response = client.post("/api/v1/auth/login/json", json={
            "username": "admin' OR '1'='1",
            "password": "anything"
        })
        assert response.status_code == 401


class TestAuthMe:
    """Tests for current user endpoint."""

    def test_me_authenticated(self, client, auth_headers):
        """Test getting current user when authenticated."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        # Ensure sensitive data is not exposed
        assert "password" not in data
        assert "hashed_password" not in data

    def test_me_unauthenticated(self, client):
        """Test getting current user without auth fails."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        """Test getting current user with invalid token fails."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        assert response.status_code == 401


class TestTokenSecurity:
    """Tests for JWT token security."""

    def test_token_required_for_protected_routes(self, client):
        """Test that protected routes require authentication."""
        protected_routes = [
            ("GET", "/api/v1/books"),
            ("GET", "/api/v1/members"),
            ("GET", "/api/v1/borrow/active"),
            ("POST", "/api/v1/books"),
            ("POST", "/api/v1/members"),
        ]
        for method, route in protected_routes:
            if method == "GET":
                response = client.get(route)
            else:
                response = client.post(route, json={})
            assert response.status_code == 401, f"Route {method} {route} should require auth"

    def test_malformed_token_rejected(self, client):
        """Test that malformed tokens are rejected."""
        malformed_tokens = [
            "Bearer ",
            "Bearer invalid",
            "Bearer abc.def",
            "Bearer abc.def.ghi.jkl",
            "NotBearer validtoken",
            "bearer lowercase",
        ]
        for token in malformed_tokens:
            response = client.get("/api/v1/auth/me", headers={
                "Authorization": token
            })
            assert response.status_code == 401, f"Token '{token}' should be rejected"

    def test_empty_authorization_header(self, client):
        """Test empty authorization header is rejected."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": ""
        })
        assert response.status_code in [401, 422]

    def test_token_without_bearer_prefix(self, client, auth_headers):
        """Test token without Bearer prefix is rejected."""
        token = auth_headers["Authorization"].replace("Bearer ", "")
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": token
        })
        assert response.status_code == 401

    def test_tampered_token_rejected(self, client, auth_headers):
        """Test that tampered tokens are rejected."""
        token = auth_headers["Authorization"]
        # Modify last character of token
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": tampered
        })
        assert response.status_code == 401

    def test_token_with_wrong_signature(self, client, test_user):
        """Test token signed with wrong secret is rejected."""
        # Create a token with wrong secret
        payload = {"sub": test_user["user"].username, "exp": time.time() + 3600}
        fake_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {fake_token}"
        })
        assert response.status_code == 401

    def test_token_can_access_multiple_endpoints(self, client, auth_headers):
        """Test that a valid token works across multiple endpoints."""
        endpoints = [
            "/api/v1/auth/me",
            "/api/v1/books",
            "/api/v1/members",
        ]
        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == 200, f"Token should work for {endpoint}"

    def test_different_users_get_different_tokens(self, client, db):
        """Test that different users receive different tokens."""
        from app.core.auth import get_password_hash
        from app.models.user import User

        # Create two users
        user1 = User(
            username="tokenuser1",
            email="token1@example.com",
            hashed_password=get_password_hash("TestPass123"),
            is_active=True
        )
        user2 = User(
            username="tokenuser2",
            email="token2@example.com",
            hashed_password=get_password_hash("TestPass123"),
            is_active=True
        )
        db.add(user1)
        db.add(user2)
        db.commit()

        # Get tokens
        resp1 = client.post("/api/v1/auth/login/json", json={
            "username": "tokenuser1", "password": "TestPass123"
        })
        resp2 = client.post("/api/v1/auth/login/json", json={
            "username": "tokenuser2", "password": "TestPass123"
        })

        token1 = resp1.json()["access_token"]
        token2 = resp2.json()["access_token"]

        # Tokens should be different
        assert token1 != token2


class TestInactiveUser:
    """Tests for inactive user handling."""

    def test_inactive_user_cannot_access_protected_routes(self, client, db):
        """Test that inactive users cannot access protected routes."""
        from app.core.auth import get_password_hash
        from app.models.user import User

        # Create inactive user
        inactive_user = User(
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password=get_password_hash("TestPass123"),
            is_active=False
        )
        db.add(inactive_user)
        db.commit()

        # Login
        login_resp = client.post("/api/v1/auth/login/json", json={
            "username": "inactiveuser",
            "password": "TestPass123"
        })

        # Should be able to login but...
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
            # Should not be able to access protected routes
            response = client.get("/api/v1/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 400  # Inactive user
        """Test getting current user with invalid token fails."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        assert response.status_code == 401


