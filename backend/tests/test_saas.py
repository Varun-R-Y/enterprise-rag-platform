import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def get_auth_headers(client: TestClient, email: str, password: str) -> dict:
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_saas_workflow(client: TestClient, db_session: Session):
    # 1. Super Admin authentication
    super_admin_headers = get_auth_headers(client, "superadmin@saas.com", "superadminpass123")

    # 2. Super Admin creates Company "Google"
    google_payload = {
        "name": "Google",
        "slug": "google",
        "description": "Alphabet Inc. search engine company",
        "logo_url": "http://logo.com/google.png",
        "timezone": "PST"
    }
    res_google = client.post("/tenants", json=google_payload, headers=super_admin_headers)
    assert res_google.status_code == 201
    google_data = res_google.json()
    google_id = google_data["id"]
    assert google_data["name"] == "Google"
    assert google_data["slug"] == "google"
    assert google_data["is_active"] is True

    # 3. Super Admin creates Company Admin for "Google"
    g_admin_payload = {
        "full_name": "Google Admin",
        "email": "g_admin@google.com",
        "password": "adminpassgoogle",
        "tenant_id": google_id
    }
    res_admin = client.post("/users/company-admin", json=g_admin_payload, headers=super_admin_headers)
    assert res_admin.status_code == 201
    g_admin_data = res_admin.json()
    assert g_admin_data["role"] == "ADMIN"
    assert g_admin_data["tenant_id"] == google_id

    # 4. Super Admin creates Company "Microsoft"
    ms_payload = {
        "name": "Microsoft",
        "slug": "microsoft",
        "description": "Software giant",
        "logo_url": "http://logo.com/ms.png",
        "timezone": "EST"
    }
    res_ms = client.post("/tenants", json=ms_payload, headers=super_admin_headers)
    assert res_ms.status_code == 201
    ms_id = res_ms.json()["id"]

    # 5. Super Admin creates Company Admin for "Microsoft"
    ms_admin_payload = {
        "full_name": "MS Admin",
        "email": "ms_admin@microsoft.com",
        "password": "adminpassmicrosoft",
        "tenant_id": ms_id
    }
    client.post("/users/company-admin", json=ms_admin_payload, headers=super_admin_headers)

    # 6. Verify role protection: Company Admin cannot list other companies
    g_admin_headers = get_auth_headers(client, "g_admin@google.com", "adminpassgoogle")
    res_list_comp = client.get("/tenants", headers=g_admin_headers)
    assert res_list_comp.status_code == 403

    # 7. Company Admin creates employee
    g_emp_payload = {
        "full_name": "Google Employee",
        "email": "g_emp@google.com",
        "password": "emppassgoogle"
    }
    res_create_emp = client.post("/users", json=g_emp_payload, headers=g_admin_headers)
    assert res_create_emp.status_code == 201
    g_emp_data = res_create_emp.json()
    assert g_emp_data["role"] == "EMPLOYEE"
    assert g_emp_data["tenant_id"] == google_id

    # 8. Employee login and list users blocked
    g_emp_headers = get_auth_headers(client, "g_emp@google.com", "emppassgoogle")
    res_users = client.get("/users", headers=g_emp_headers)
    assert res_users.status_code == 403

    # 9. Super Admin lists all companies and validates stats
    res_tenants = client.get("/tenants", headers=super_admin_headers)
    assert res_tenants.status_code == 200
    tenants_list = res_tenants.json()
    google_item = next(t for t in tenants_list if t["tenant"]["id"] == google_id)
    assert google_item["stats"]["admins_count"] == 1
    assert google_item["stats"]["employees_count"] == 1

    # 10. Test Deactivation
    # Super Admin deactivates Google
    deactivate_res = client.patch(f"/tenants/{google_id}", json={"is_active": False}, headers=super_admin_headers)
    assert deactivate_res.status_code == 200
    assert deactivate_res.json()["is_active"] is False

    # 11. Locked out: Google Admin attempt to call `/users` lists results in 403 Forbidden because tenant is deactivated
    res_deactivated_call = client.get("/users", headers=g_admin_headers)
    assert res_deactivated_call.status_code == 403
    assert "Tenant is deactivated" in res_deactivated_call.json()["detail"]
