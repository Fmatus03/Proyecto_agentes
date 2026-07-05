from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password, require_permission, verify_password, verify_token
from app.main import app


client = TestClient(app)


def _admin_headers():
    response = client.post("/api/v1/auth/login", json={"email": "admin@brewmaster.local", "password": "Admin123!"})
    assert response.status_code == 200
    jwt_value = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {jwt_value}"}


def test_password_hash_and_jwt_are_verifiable():
    stored = hash_password("Valid123!")
    assert "Valid123!" not in stored
    assert verify_password("Valid123!", stored)
    jwt_value = create_access_token("7", ["audit.read"], {"role": "auditor"})
    payload = verify_token(jwt_value)
    assert payload["sub"] == "7"
    assert payload["role"] == "auditor"


def test_permission_helper_allows_admin_and_blocks_missing_permission():
    require_permission({"*"}, "admin.users")
    try:
        require_permission({"audit.read"}, "admin.users")
    except PermissionError:
        return
    raise AssertionError("missing permission must raise")


def test_login_me_and_audit_log_flow():
    headers = _admin_headers()
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "admin@brewmaster.local"
    audit = client.get("/api/v1/audit-logs", headers=headers)
    assert audit.status_code == 200
    assert any(item["action"] == "login_success" for item in audit.json()["data"])


def test_invalid_login_is_401_and_audited():
    bad = client.post("/api/v1/auth/login", json={"email": "admin@brewmaster.local", "password": "wrong"})
    assert bad.status_code == 401
    audit = client.get("/api/v1/audit-logs", headers=_admin_headers())
    assert any(item["action"] == "login_failed" for item in audit.json()["data"])


def test_admin_creates_user_duplicate_is_rejected_and_operator_gets_403():
    headers = _admin_headers()
    created = client.post(
        "/api/v1/users",
        json={"nombre": "Operador", "email": "operador@brewmaster.local", "password": "Operador123", "role": "operador"},
        headers=headers,
    )
    assert created.status_code == 200
    duplicate = client.post(
        "/api/v1/users",
        json={"nombre": "Otro", "email": "operador@brewmaster.local", "password": "Operador123", "role": "operador"},
        headers=headers,
    )
    assert duplicate.status_code == 422
    login = client.post("/api/v1/auth/login", json={"email": "operador@brewmaster.local", "password": "Operador123"})
    operator_headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    forbidden = client.get("/api/v1/users", headers=operator_headers)
    assert forbidden.status_code == 403


def test_password_change_and_reset_confirm_update_credentials():
    headers = _admin_headers()
    changed = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "Admin123!", "new_password": "Admin456!"},
        headers=headers,
    )
    assert changed.status_code == 200
    old_login = client.post("/api/v1/auth/login", json={"email": "admin@brewmaster.local", "password": "Admin123!"})
    assert old_login.status_code == 401
    request_reset = client.post("/api/v1/auth/password-reset/request", json={"email": "admin@brewmaster.local"})
    reset_value = request_reset.json()["data"]["local_delivery"]
    confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_value, "new_password": "Admin123!"},
    )
    assert confirm.status_code == 200
    reused = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_value, "new_password": "Admin789!"},
    )
    assert reused.status_code == 401
