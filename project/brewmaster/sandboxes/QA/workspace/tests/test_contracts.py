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
