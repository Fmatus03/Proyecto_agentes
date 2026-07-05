from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.responses import ok
from app.domain.catalog import ROUTE_CATALOG

app = FastAPI(title="BrewMaster API", version="0.1.0", openapi_url="/api/v1/openapi.json")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "REQ-LOCAL")
    return response


@app.get("/api/v1/health")
def health():
    return ok({"status": "ok", "service": "brewmaster"})


@app.get("/api/v1/catalog/routes")
def catalog_routes():
    return ok(ROUTE_CATALOG)

@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "message": str(exc), "details": []}, "meta": {"request_id": "REQ-LOCAL"}})


ROUTE_CATALOG_SEED = '[\n  {\n    "action_endpoint": true,\n    "description": "iniciar sesi\\u00f3n, retorna token JWT.",\n    "handler": "auth.login",\n    "method": "POST",\n    "path": "/api/v1/auth/login",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "cerrar sesi\\u00f3n.",\n    "handler": "auth.logout",\n    "method": "POST",\n    "path": "/api/v1/auth/logout",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "obtener usuario autenticado.",\n    "handler": "auth.list",\n    "method": "GET",\n    "path": "/api/v1/auth/me",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": true,\n    "description": "cambiar contrase\\u00f1a.",\n    "handler": "auth.change_password",\n    "method": "POST",\n    "path": "/api/v1/auth/change-password",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar usuarios con filtros por rol y estado.",\n    "handler": "users.list",\n    "method": "GET",\n    "path": "/api/v1/users",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "crear usuario (solo admin).",\n    "handler": "users.create",\n    "method": "POST",\n    "path": "/api/v1/users",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "obtener detalle de usuario.",\n    "handler": "users.detail",\n    "method": "GET",\n    "path": "/api/v1/users/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "editar usuario.",\n    "handler": "users.update",\n    "method": "PUT",\n    "path": "/api/v1/users/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "activar o desactivar usuario.",\n    "handler": "users.toggle_status",\n    "method": "PATCH",\n    "path": "/api/v1/users/{id}/toggle-status",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar proveedores.",\n    "handler": "suppliers.list",\n    "method": "GET",\n    "path": "/api/v1/suppliers",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "crear proveedor.",\n    "handler": "suppliers.create",\n    "method": "POST",\n    "path": "/api/v1/suppliers",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "actualizar proveedor.",\n    "handler": "suppliers.update",\n    "method": "PUT",\n    "path": "/api/v1/suppliers/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "activar o desactivar proveedor.",\n    "handler": "suppliers.toggle_status",\n    "method": "PATCH",\n    "path": "/api/v1/suppliers/{id}/toggle-status",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar insumos con filtros.",\n    "handler": "supplies.list",\n    "method": "GET",\n    "path": "/api/v1/supplies",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "crear insumo.",\n    "handler": "supplies.create",\n    "method": "POST",\n    "path": "/api/v1/supplies",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "obtener insumo.",\n    "handler": "supplies.detail",\n    "method": "GET",\n    "path": "/api/v1/supplies/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "actualizar insumo.",\n    "handler": "supplies.update",\n    "method": "PUT",\n    "path": "/api/v1/supplies/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "activar o desactivar insumo.",\n    "handler": "supplies.toggle_status",\n    "method": "PATCH",\n    "path": "/api/v1/supplies/{id}/toggle-status",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "Kardex del insumo.",\n    "handler": "supplies.detail",\n    "method": "GET",\n    "path": "/api/v1/supplies/{id}/kardex",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "insumos bajo stock m\\u00ednimo.",\n    "handler": "supplies.list",\n    "method": "GET",\n    "path": "/api/v1/supplies/low-stock",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "registrar entrada de insumo.",\n    "handler": "supply_entries.create",\n    "method": "POST",\n    "path": "/api/v1/supply-entries",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar entradas de insumos.",\n    "handler": "supply_entries.list",\n    "method": "GET",\n    "path": "/api/v1/supply-entries",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar recetas.",\n    "handler": "recipes.list",\n    "method": "GET",\n    "path": "/api/v1/recipes",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "crear receta.",\n    "handler": "recipes.create",\n    "method": "POST",\n    "path": "/api/v1/recipes",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "obtener receta con ingredientes.",\n    "handler": "recipes.detail",\n    "method": "GET",\n    "path": "/api/v1/recipes/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "actualizar receta.",\n    "handler": "recipes.update",\n    "method": "PUT",\n    "path": "/api/v1/recipes/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "clonar receta.",\n    "handler": "recipes.clone",\n    "method": "POST",\n    "path": "/api/v1/recipes/{id}/clone",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar lotes de producci\\u00f3n.",\n    "handler": "batches.list",\n    "method": "GET",\n    "path": "/api/v1/batches",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "crear lote.",\n    "handler": "batches.create",\n    "method": "POST",\n    "path": "/api/v1/batches",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "obtener lote con detalle de insumos.",\n    "handler": "batches.detail",\n    "method": "GET",\n    "path": "/api/v1/batches/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "editar lote en elaboraci\\u00f3n.",\n    "handler": "batches.update",\n    "method": "PUT",\n    "path": "/api/v1/batches/{id}",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "completar lote.",\n    "handler": "batches.complete",\n    "method": "POST",\n    "path": "/api/v1/batches/{id}/complete",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "cancelar lote.",\n    "handler": "batches.cancel",\n    "method": "POST",\n    "path": "/api/v1/batches/{id}/cancel",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": true,\n    "description": "registrar control de calidad.",\n    "handler": "batches.quality_check",\n    "method": "POST",\n    "path": "/api/v1/batches/{id}/quality-check",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar inventario de productos terminados.",\n    "handler": "products.list",\n    "method": "GET",\n    "path": "/api/v1/products",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": true,\n    "description": "actualizar precio de venta.",\n    "handler": "products.update",\n    "method": "PUT",\n    "path": "/api/v1/products/{id}/price",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "registrar venta.",\n    "handler": "sales.create",\n    "method": "POST",\n    "path": "/api/v1/sales",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar ventas con filtros.",\n    "handler": "sales.list",\n    "method": "GET",\n    "path": "/api/v1/sales",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "listar clientes.",\n    "handler": "customers.list",\n    "method": "GET",\n    "path": "/api/v1/customers",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": false\n  },\n  {\n    "action_endpoint": false,\n    "description": "crear cliente.",\n    "handler": "customers.create",\n    "method": "POST",\n    "path": "/api/v1/customers",\n    "source": "brewmaster_especificacion_completa.md#F.40-endpoints",\n    "transactional": true\n  }\n]'


@app.post('/api/v1/auth/login')
def route_1_post_auth_login():
    return ok({'handler': 'auth.login', 'method': 'POST', 'path': '/api/v1/auth/login', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/auth/logout')
def route_2_post_auth_logout():
    return ok({'handler': 'auth.logout', 'method': 'POST', 'path': '/api/v1/auth/logout', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/auth/me')
def route_3_get_auth_me():
    return ok({'handler': 'auth.list', 'method': 'GET', 'path': '/api/v1/auth/me', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/auth/change-password')
def route_4_post_auth_change_password():
    return ok({'handler': 'auth.change_password', 'method': 'POST', 'path': '/api/v1/auth/change-password', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/users')
def route_5_get_users():
    return ok({'handler': 'users.list', 'method': 'GET', 'path': '/api/v1/users', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/users')
def route_6_post_users():
    return ok({'handler': 'users.create', 'method': 'POST', 'path': '/api/v1/users', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/suppliers')
def route_10_get_suppliers():
    return ok({'handler': 'suppliers.list', 'method': 'GET', 'path': '/api/v1/suppliers', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/suppliers')
def route_11_post_suppliers():
    return ok({'handler': 'suppliers.create', 'method': 'POST', 'path': '/api/v1/suppliers', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/supplies')
def route_14_get_supplies():
    return ok({'handler': 'supplies.list', 'method': 'GET', 'path': '/api/v1/supplies', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/supplies')
def route_15_post_supplies():
    return ok({'handler': 'supplies.create', 'method': 'POST', 'path': '/api/v1/supplies', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/supplies/low-stock')
def route_20_get_supplies_low_stock():
    return ok({'handler': 'supplies.list', 'method': 'GET', 'path': '/api/v1/supplies/low-stock', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/supply-entries')
def route_21_post_supply_entries():
    return ok({'handler': 'supply_entries.create', 'method': 'POST', 'path': '/api/v1/supply-entries', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/supply-entries')
def route_22_get_supply_entries():
    return ok({'handler': 'supply_entries.list', 'method': 'GET', 'path': '/api/v1/supply-entries', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/recipes')
def route_23_get_recipes():
    return ok({'handler': 'recipes.list', 'method': 'GET', 'path': '/api/v1/recipes', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/recipes')
def route_24_post_recipes():
    return ok({'handler': 'recipes.create', 'method': 'POST', 'path': '/api/v1/recipes', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/batches')
def route_28_get_batches():
    return ok({'handler': 'batches.list', 'method': 'GET', 'path': '/api/v1/batches', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/batches')
def route_29_post_batches():
    return ok({'handler': 'batches.create', 'method': 'POST', 'path': '/api/v1/batches', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/products')
def route_35_get_products():
    return ok({'handler': 'products.list', 'method': 'GET', 'path': '/api/v1/products', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/sales')
def route_37_post_sales():
    return ok({'handler': 'sales.create', 'method': 'POST', 'path': '/api/v1/sales', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/sales')
def route_38_get_sales():
    return ok({'handler': 'sales.list', 'method': 'GET', 'path': '/api/v1/sales', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/customers')
def route_39_get_customers():
    return ok({'handler': 'customers.list', 'method': 'GET', 'path': '/api/v1/customers', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.post('/api/v1/customers')
def route_40_post_customers():
    return ok({'handler': 'customers.create', 'method': 'POST', 'path': '/api/v1/customers', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints'})


@app.get('/api/v1/users/{id}')
def route_7_get_users_id(id: int):
    return ok({'handler': 'users.detail', 'method': 'GET', 'path': '/api/v1/users/{id}', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.put('/api/v1/users/{id}')
def route_8_put_users_id(id: int):
    return ok({'handler': 'users.update', 'method': 'PUT', 'path': '/api/v1/users/{id}', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.patch('/api/v1/users/{id}/toggle-status')
def route_9_patch_users_id_toggle_status(id: int):
    return ok({'handler': 'users.toggle_status', 'method': 'PATCH', 'path': '/api/v1/users/{id}/toggle-status', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.put('/api/v1/suppliers/{id}')
def route_12_put_suppliers_id(id: int):
    return ok({'handler': 'suppliers.update', 'method': 'PUT', 'path': '/api/v1/suppliers/{id}', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.patch('/api/v1/suppliers/{id}/toggle-status')
def route_13_patch_suppliers_id_toggle_status(id: int):
    return ok({'handler': 'suppliers.toggle_status', 'method': 'PATCH', 'path': '/api/v1/suppliers/{id}/toggle-status', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.get('/api/v1/supplies/{id}')
def route_16_get_supplies_id(id: int):
    return ok({'handler': 'supplies.detail', 'method': 'GET', 'path': '/api/v1/supplies/{id}', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.put('/api/v1/supplies/{id}')
def route_17_put_supplies_id(id: int):
    return ok({'handler': 'supplies.update', 'method': 'PUT', 'path': '/api/v1/supplies/{id}', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.patch('/api/v1/supplies/{id}/toggle-status')
def route_18_patch_supplies_id_toggle_status(id: int):
    return ok({'handler': 'supplies.toggle_status', 'method': 'PATCH', 'path': '/api/v1/supplies/{id}/toggle-status', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.get('/api/v1/supplies/{id}/kardex')
def route_19_get_supplies_id_kardex(id: int):
    return ok({'handler': 'supplies.detail', 'method': 'GET', 'path': '/api/v1/supplies/{id}/kardex', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.get('/api/v1/recipes/{id}')
def route_25_get_recipes_id(id: int):
    return ok({'handler': 'recipes.detail', 'method': 'GET', 'path': '/api/v1/recipes/{id}', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.put('/api/v1/recipes/{id}')
def route_26_put_recipes_id(id: int):
    return ok({'handler': 'recipes.update', 'method': 'PUT', 'path': '/api/v1/recipes/{id}', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.post('/api/v1/recipes/{id}/clone')
def route_27_post_recipes_id_clone(id: int):
    return ok({'handler': 'recipes.clone', 'method': 'POST', 'path': '/api/v1/recipes/{id}/clone', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.get('/api/v1/batches/{id}')
def route_30_get_batches_id(id: int):
    return ok({'handler': 'batches.detail', 'method': 'GET', 'path': '/api/v1/batches/{id}', 'transactional': False, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.put('/api/v1/batches/{id}')
def route_31_put_batches_id(id: int):
    return ok({'handler': 'batches.update', 'method': 'PUT', 'path': '/api/v1/batches/{id}', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.post('/api/v1/batches/{id}/complete')
def route_32_post_batches_id_complete(id: int):
    return ok({'handler': 'batches.complete', 'method': 'POST', 'path': '/api/v1/batches/{id}/complete', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.post('/api/v1/batches/{id}/cancel')
def route_33_post_batches_id_cancel(id: int):
    return ok({'handler': 'batches.cancel', 'method': 'POST', 'path': '/api/v1/batches/{id}/cancel', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.post('/api/v1/batches/{id}/quality-check')
def route_34_post_batches_id_quality_check(id: int):
    return ok({'handler': 'batches.quality_check', 'method': 'POST', 'path': '/api/v1/batches/{id}/quality-check', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})


@app.put('/api/v1/products/{id}/price')
def route_36_put_products_id_price(id: int):
    return ok({'handler': 'products.update', 'method': 'PUT', 'path': '/api/v1/products/{id}/price', 'transactional': True, 'source': 'brewmaster_especificacion_completa.md#F.40-endpoints', 'path_params': {'id': '{id}'}})
