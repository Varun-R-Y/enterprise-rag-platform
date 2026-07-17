import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.tenant import Tenant

def test_auth_me_workflow(client: TestClient, db_session: Session):
    # 1. Create a dummy tenant in the test database
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    # 2. Register a new user
    user_data = {
        "email": "user@example.com",
        "password": "strongpassword123",
        "full_name": "John Doe",
        "tenant_id": str(tenant_id)
    }
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    registered_user = register_response.json()
    assert registered_user["email"] == "user@example.com"
    assert registered_user["full_name"] == "John Doe"
    assert registered_user["role"] == "employee"

    # 3. Log in with the registered user credentials
    login_data = {
        "username": "user@example.com",
        "password": "strongpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 4. Access the protected GET /auth/me route with token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "user@example.com"
    assert me_data["full_name"] == "John Doe"
    assert me_data["id"] == registered_user["id"]
    assert me_data["tenant_id"] == str(tenant_id)
    assert me_data["is_active"] is True

    # 5. Try to access GET /auth/me with an invalid token
    bad_headers = {"Authorization": "Bearer invalidtokenhere"}
    bad_response = client.get("/auth/me", headers=bad_headers)
    assert bad_response.status_code == 401
    assert "detail" in bad_response.json()

    # 6. Try to access GET /auth/me without an Authorization header
    no_token_response = client.get("/auth/me")
    assert no_token_response.status_code == 401
