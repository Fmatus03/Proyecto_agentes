from __future__ import annotations

from textwrap import dedent

def _test_domain_rules_py() -> str:
    return dedent(
        """
        from app.domain.rules import CostInput, available_stock, batch_cost, line_profit, should_send_stock_alert


        def test_available_stock_subtracts_active_reservations():
            assert available_stock(100, 35) == 65


        def test_stock_alert_interval_and_zero_stock():
            assert should_send_stock_alert(0, 10, 1) is True
            assert should_send_stock_alert(8, 10, 23) is False
            assert should_send_stock_alert(8, 10, 24) is True


        def test_line_profit_and_batch_cost():
            assert line_profit(1200, 700, 3) == 1500
            result = batch_cost(CostInput(1000, 2, 500, 4, 100, 20, 5, 50, 200, 30, 10, 20))
            assert result["total"] == 3350
            assert result["cost_per_liter"] == 335
            assert result["cost_per_unit"] == 167.5
        """
    ).strip()


def _test_contracts_py(blueprint: dict | None = None) -> str:
    if blueprint and blueprint.get("milestone_id") == "HITO-001":
        return dedent(
            """
            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito1_catalog_is_limited_to_foundations():
                paths = {route["path"] for route in ROUTE_CATALOG}
                assert len(ROUTE_CATALOG) == 12
                assert all(path.startswith("/api/v1") for path in paths)
                assert {
                    "/api/v1/auth/login",
                    "/api/v1/auth/logout",
                    "/api/v1/auth/me",
                    "/api/v1/auth/change-password",
                    "/api/v1/users",
                    "/api/v1/users/{id}",
                    "/api/v1/users/{id}/toggle-status",
                    "/api/v1/audit-logs",
                    "/api/v1/auth/password-reset/request",
                    "/api/v1/auth/password-reset/confirm",
                } <= paths
                assert not any(path.startswith("/api/v1/supplies") for path in paths)
                assert not any(path.startswith("/api/v1/batches") for path in paths)
                assert not any(path.startswith("/api/v1/sales") for path in paths)
                assert not any("{resource}" in path for path in paths)


            def test_hito1_screens_are_foundational():
                assert {screen["id"] for screen in SCREEN_CATALOG} == {"P-01", "P-02", "P-30"}
            """
        ).strip()
    return dedent(
        """
        from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


        def test_api_uses_api_v1_and_has_action_endpoints():
            assert all(route["path"].startswith("/api/v1") for route in ROUTE_CATALOG)
            assert len(ROUTE_CATALOG) == 40
            assert any(route["path"] == "/api/v1/batches/{id}/complete" for route in ROUTE_CATALOG)
            assert not any("{resource}" in route["path"] for route in ROUTE_CATALOG)
            assert {route["path"] for route in ROUTE_CATALOG} >= {"/api/v1/auth/login", "/api/v1/supplies/{id}/kardex", "/api/v1/customers"}


        def test_thirty_screens_are_declared():
            assert len(SCREEN_CATALOG) == 30
            assert {screen["id"] for screen in SCREEN_CATALOG} >= {"P-01", "P-15", "P-22", "P-30"}
        """
    ).strip()


def _test_auth_foundation_py() -> str:
    return dedent(
        """
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
        """
    ).strip()
