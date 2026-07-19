import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.core.config import settings

def test_public_registration_disabled(client: TestClient):
    """Verify public registration route is completely disabled."""
    user_data = {
        "email": "user@example.com",
        "password": "strongpassword123",
        "full_name": "John Doe",
        "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code in (404, 405)

def test_admin_seeding_and_auth_workflow(client: TestClient, db_session: Session):
    """Verify default seeded admin can login, call /auth/me, create employees, and manage roles."""
    # 1. Verify default admin can log in
    admin_email = settings.DEFAULT_ADMIN_EMAIL
    admin_pwd = settings.DEFAULT_ADMIN_PASSWORD
    
    login_data = {
        "username": admin_email,
        "password": admin_pwd
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    admin_token = token_data["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Access /auth/me as admin
    me_response = client.get("/auth/me", headers=admin_headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == admin_email
    assert me_data["role"] == "ADMIN"
    admin_id = me_data["id"]

    # 3. Create employee via POST /users (Admin only)
    emp_payload = {
        "full_name": "Jane Employee",
        "email": "employee@enterprise.com",
        "password": "employeepass123"
    }
    create_response = client.post("/users", json=emp_payload, headers=admin_headers)
    assert create_response.status_code == 201
    emp_data = create_response.json()
    assert emp_data["email"] == "employee@enterprise.com"
    assert emp_data["role"] == "EMPLOYEE"
    assert emp_data["created_by"] == admin_id
    emp_id = emp_data["id"]

    # 4. Log in as employee
    emp_login = {
        "username": "employee@enterprise.com",
        "password": "employeepass123"
    }
    emp_login_response = client.post("/auth/login", data=emp_login)
    assert emp_login_response.status_code == 200
    emp_token = emp_login_response.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # 5. Access /auth/me as employee
    emp_me = client.get("/auth/me", headers=emp_headers)
    assert emp_me.status_code == 200
    assert emp_me.json()["role"] == "EMPLOYEE"

    # 6. Verify role protection: employee cannot create users
    bad_create = client.post("/users", json=emp_payload, headers=emp_headers)
    assert bad_create.status_code == 403

    # 7. Verify role protection: employee cannot list users
    bad_list = client.get("/users", headers=emp_headers)
    assert bad_list.status_code == 403

    # 8. Verify role protection: employee cannot delete users
    bad_delete = client.delete(f"/users/{emp_id}", headers=emp_headers)
    assert bad_delete.status_code == 403

    # 9. Verify admin can list users
    users_list = client.get("/users", headers=admin_headers)
    assert users_list.status_code == 200
    users_data = users_list.json()
    assert len(users_data) >= 2 # default admin + employee

    # 10. Verify admin cannot delete themselves
    self_delete = client.delete(f"/users/{admin_id}", headers=admin_headers)
    assert self_delete.status_code == 400
    assert "delete themselves" in self_delete.json()["detail"]

    # 11. Verify duplicate email creation block
    duplicate_payload = {
        "full_name": "Jane Copy",
        "email": "employee@enterprise.com",
        "password": "employeepass123"
    }
    dup_response = client.post("/users", json=duplicate_payload, headers=admin_headers)
    assert dup_response.status_code == 400
    assert "exists" in dup_response.json()["detail"]

    # 12. Verify admin can delete employee
    del_response = client.delete(f"/users/{emp_id}", headers=admin_headers)
    assert del_response.status_code == 204
