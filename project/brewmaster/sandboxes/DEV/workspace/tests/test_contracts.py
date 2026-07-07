from pathlib import Path

from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


def test_hito8_preserves_hito7_backend_contract_without_new_endpoints():
    paths = {route["path"] for route in ROUTE_CATALOG}
    assert len(ROUTE_CATALOG) == 89
    assert all(path.startswith("/api/v1") for path in paths)
    assert {
        "/api/v1/auth/login",
        "/api/v1/suppliers",
        "/api/v1/supplies/{id}/kardex",
        "/api/v1/settings/smtp",
        "/api/v1/batches/{id}/complete",
        "/api/v1/products/{id}/kardex",
        "/api/v1/customers",
        "/api/v1/sales",
        "/api/v1/reservations/{id}/consume",
        "/api/v1/purchase-orders/{id}/receive",
        "/api/v1/dashboard",
        "/api/v1/reports",
        "/api/v1/reports/export",
        "/api/v1/equipment",
        "/api/v1/equipment/{id}/movements",
        "/api/v1/expenses",
        "/api/v1/expenses/{id}",
        "/api/v1/monthly-goals",
        "/api/v1/monthly-goals/{month}",
        "/api/v1/jobs",
        "/api/v1/backups",
    } <= paths
    assert not any("{resource}" in path for path in paths)


def test_hito8_declares_30_screens_and_specific_frontend_components():
    screen_ids = {screen["id"] for screen in SCREEN_CATALOG}
    assert screen_ids == {f"P-{index:02d}" for index in range(1, 31)}
    screen_views = Path("frontend/src/screens/ScreenViews.jsx").read_text(encoding="utf-8")
    assert "GenericScreen" not in screen_views
    for screen_id in sorted(screen_ids):
        assert f"'{screen_id}'" in screen_views
    assert screen_views.count("export function ") >= 31
    assert "useResources(" in screen_views
    assert "ScreenFrame" in screen_views
    assert "EmptyState" in screen_views


def test_hito8_vite_entrypoints_routes_and_api_client_are_local_api_v1_only():
    assert Path("frontend/index.html").exists()
    assert Path("frontend/src/main.jsx").exists()
    app = Path("frontend/src/App.jsx").read_text(encoding="utf-8")
    routes = Path("frontend/src/routes.js").read_text(encoding="utf-8")
    client = Path("frontend/src/api/client.js").read_text(encoding="utf-8")
    package = Path("frontend/package.json").read_text(encoding="utf-8")
    assert "createRoot" in Path("frontend/src/main.jsx").read_text(encoding="utf-8")
    assert "screenForPath" in app
    assert "hashchange" in app
    assert "SCREENS.map" in routes
    assert "replace(/:id/g, '[^/]+')" in routes
    assert "replace(/\\:id/g" not in routes
    assert "VITE_API_BASE_URL" in client
    assert "'/api/v1'" in client
    assert "fetch(`${API_BASE}${path}`" in client
    assert "vite build" in package


def test_hito8_preserves_deployment_preparation_without_real_secrets():
    assert Path("docker-compose.yml").exists()
    assert Path("deploy/nginx.conf").exists()
    assert Path("docs/deployment.md").exists()
    assert Path("backend/Dockerfile").exists()
    assert Path("frontend/Dockerfile").exists()
    env_example = Path(".env.example").read_text(encoding="utf-8")
    assert "setme" in env_example
    assert "AWS_SECRET_ACCESS_KEY" not in env_example
