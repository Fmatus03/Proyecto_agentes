from fastapi.testclient import TestClient

from app.domain.catalog import ROUTE_CATALOG
from app.main import app


client = TestClient(app)
MASTER_COUNTER = 0
HITO3_ACTIVE = any(route["path"] == "/api/v1/supply-entries" for route in ROUTE_CATALOG)
HITO4_ACTIVE = any(route["path"] == "/api/v1/batches" for route in ROUTE_CATALOG)
HITO5_ACTIVE = any(route["path"] == "/api/v1/sales" for route in ROUTE_CATALOG)


def _admin_headers():
    response = client.post("/api/v1/auth/login", json={"email": "admin@brewmaster.local", "password": "Admin123!"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _create_master_data():
    global MASTER_COUNTER
    MASTER_COUNTER += 1
    suffix = f"{MASTER_COUNTER:03d}"
    headers = _admin_headers()
    supplier = client.post(
        "/api/v1/suppliers",
        json={"codigo": f"SUP-H2-{suffix}", "nombre": f"Malteria Sur {suffix}", "email": f"ventas{suffix}@malteria.local"},
        headers=headers,
    )
    assert supplier.status_code == 200
    warehouse = client.post(
        "/api/v1/warehouses",
        json={"codigo": f"BOD-H2-{suffix}", "nombre": f"Bodega seca {suffix}", "tipo": "insumos", "capacidad": 1200},
        headers=headers,
    )
    assert warehouse.status_code == 200
    supply = client.post(
        "/api/v1/supplies",
        json={
            "codigo": f"INS-H2-{suffix}",
            "nombre": f"Malta Pale {suffix}",
            "tipo": "malta",
            "unidad_medida": "kg",
            "proveedor_id": supplier.json()["data"]["id"],
            "bodega_id": warehouse.json()["data"]["id"],
            "costo_unitario": 750,
            "stock_minimo": 10,
            "stock_actual": 25,
        },
        headers=headers,
    )
    assert supply.status_code == 200
    return headers, supplier.json()["data"], warehouse.json()["data"], supply.json()["data"]


def test_supplier_duplicate_and_invalid_email_are_rejected():
    headers = _admin_headers()
    first = client.post(
        "/api/v1/suppliers",
        json={"codigo": "SUP-H2-DUP", "nombre": "Proveedor Dup", "email": "dup@example.local"},
        headers=headers,
    )
    assert first.status_code == 200
    duplicate = client.post(
        "/api/v1/suppliers",
        json={"codigo": "SUP-H2-DUP", "nombre": "Otro"},
        headers=headers,
    )
    assert duplicate.status_code == 422
    invalid_email = client.post(
        "/api/v1/suppliers",
        json={"codigo": "SUP-H2-BAD", "nombre": "Bad Mail", "email": "bad"},
        headers=headers,
    )
    assert invalid_email.status_code == 422


def test_supply_requires_active_supplier_warehouse_and_valid_numbers():
    headers, supplier, warehouse, _ = _create_master_data()
    negative_cost = client.post(
        "/api/v1/supplies",
        json={
            "codigo": "INS-H2-BAD",
            "nombre": "Costo malo",
            "tipo": "malta",
            "unidad_medida": "kg",
            "proveedor_id": supplier["id"],
            "bodega_id": warehouse["id"],
            "costo_unitario": -1,
            "stock_minimo": 0,
        },
        headers=headers,
    )
    assert negative_cost.status_code == 422
    client.patch(f"/api/v1/suppliers/{supplier['id']}/toggle-status", headers=headers)
    inactive_supplier = client.post(
        "/api/v1/supplies",
        json={
            "codigo": "INS-H2-INACTIVE",
            "nombre": "Proveedor inactivo",
            "tipo": "malta",
            "unidad_medida": "kg",
            "proveedor_id": supplier["id"],
            "bodega_id": warehouse["id"],
            "costo_unitario": 10,
            "stock_minimo": 0,
        },
        headers=headers,
    )
    assert inactive_supplier.status_code == 422


def test_recipe_cost_clone_and_supply_inactivation_guard():
    headers, _, _, supply = _create_master_data()
    presentation = client.post(
        "/api/v1/presentation-types",
        json={"nombre": f"Botella 330 {supply['id']}", "volumen": 330, "unidad": "ml", "costo_presentacion": 120},
        headers=headers,
    )
    assert presentation.status_code == 200
    recipe = client.post(
        "/api/v1/recipes",
        json={
            "nombre": f"Pale Ale H2 {supply['id']}",
            "tipo": "ale",
            "abv_estimado": 5.2,
            "volumen_por_lote": 50,
            "ingredientes": [{"supply_id": supply["id"], "cantidad": 2, "unidad": "kg"}],
        },
        headers=headers,
    )
    assert recipe.status_code == 200
    assert recipe.json()["data"]["costo_estimado"] == 1500
    clone = client.post(
        f"/api/v1/recipes/{recipe.json()['data']['id']}/clone",
        json={"nombre": f"Pale Ale H2 prueba {supply['id']}"},
        headers=headers,
    )
    assert clone.status_code == 200
    assert clone.json()["data"]["estado"] == "en_prueba"
    blocked = client.patch(f"/api/v1/supplies/{supply['id']}/toggle-status", headers=headers)
    assert blocked.status_code == 422


def test_hito3_and_later_operational_routes_follow_milestone_scope():
    headers = _admin_headers()
    if HITO3_ACTIVE:
        assert client.get("/api/v1/supply-entries", headers=headers).status_code == 200
        assert client.get("/api/v1/supplies/low-stock", headers=headers).status_code == 200
    else:
        assert client.get("/api/v1/supply-entries", headers=headers).status_code == 404
        assert client.get("/api/v1/supplies/low-stock", headers=headers).status_code in {404, 422}
    if HITO4_ACTIVE:
        assert client.get("/api/v1/batches", headers=headers).status_code == 200
        assert client.get("/api/v1/products", headers=headers).status_code == 200
        assert client.get("/api/v1/waste-records", headers=headers).status_code == 200
    else:
        assert client.get("/api/v1/batches", headers=headers).status_code == 404
    if HITO5_ACTIVE:
        assert client.get("/api/v1/sales", headers=headers).status_code == 200
        assert client.get("/api/v1/customers", headers=headers).status_code == 200
        assert client.get("/api/v1/purchase-orders", headers=headers).status_code == 200
    else:
        assert client.get("/api/v1/sales", headers=headers).status_code == 404
        assert client.get("/api/v1/customers", headers=headers).status_code == 404
        assert client.get("/api/v1/purchase-orders", headers=headers).status_code == 404
