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
