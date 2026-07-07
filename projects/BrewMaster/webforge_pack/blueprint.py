from __future__ import annotations

import copy
from typing import Any

from .spec import load_brewmaster_spec

HITO_001_ENTITY_NAMES = {
    "users",
    "roles",
    "permissions",
    "role_permissions",
    "audit_logs",
    "settings",
    "password_reset_tokens",
}
HITO_001_SCREEN_IDS = {"P-01", "P-02", "P-30"}
HITO_001_VALIDATION_IDS = {f"V{index:03d}" for index in range(1, 25)}
HITO_001_PERMISSION_CODES = {"admin.users", "audit.read"}
HITO_002_ENTITY_NAMES = HITO_001_ENTITY_NAMES | {
    "suppliers",
    "warehouses",
    "supply_categories",
    "supplies",
    "presentation_types",
    "recipes",
    "recipe_ingredients",
}
HITO_002_SCREEN_IDS = HITO_001_SCREEN_IDS | {"P-04", "P-05", "P-08", "P-09", "P-10", "P-11", "P-12", "P-13"}
HITO_002_VALIDATION_IDS = (
    HITO_001_VALIDATION_IDS
    | {f"V{index:03d}" for index in range(25, 34)}
    | {"V035"}
    | {f"V{index:03d}" for index in range(40, 53)}
)
HITO_002_PERMISSION_CODES = HITO_001_PERMISSION_CODES | {
    "suppliers.read",
    "suppliers.create",
    "suppliers.update",
    "supplies.read",
    "supplies.create",
    "supplies.update",
    "supplies.toggle-status",
    "recipes.read",
    "recipes.create",
    "recipes.update",
    "recipes.clone",
}
HITO_003_ENTITY_NAMES = HITO_002_ENTITY_NAMES | {
    "supply_entries",
    "supply_movements",
    "notification_queue",
    "smtp_config",
}
HITO_003_SCREEN_IDS = HITO_002_SCREEN_IDS | {"P-06", "P-07"}
HITO_003_VALIDATION_IDS = HITO_002_VALIDATION_IDS | {"V034", "V036", "V037", "V038", "V039"}
HITO_003_PERMISSION_CODES = HITO_002_PERMISSION_CODES | {
    "supply-entries.create",
    "admin.settings",
}
HITO_004_ENTITY_NAMES = HITO_003_ENTITY_NAMES | {
    "production_batches",
    "batch_quality_checks",
    "waste_records",
    "finished_products",
    "product_movements",
    "batch_supply_snapshots",
}
HITO_004_SCREEN_IDS = HITO_003_SCREEN_IDS | {"P-14", "P-15", "P-16", "P-17", "P-18", "P-19"}
HITO_004_VALIDATION_IDS = HITO_003_VALIDATION_IDS | {f"V{index:03d}" for index in range(53, 79)} | {"V087"}
HITO_004_PERMISSION_CODES = HITO_003_PERMISSION_CODES | {
    "batches.read",
    "batches.create",
    "batches.complete",
    "batches.cancel",
    "batches.quality-check",
    "waste.create",
    "waste.read",
    "products.read",
    "products.update-price",
}
HITO_005_ENTITY_NAMES = HITO_004_ENTITY_NAMES | {
    "customer_types",
    "customers",
    "product_prices",
    "sales",
    "sale_items",
    "stock_reservations",
    "purchase_orders",
    "purchase_order_items",
}
HITO_005_SCREEN_IDS = HITO_004_SCREEN_IDS | {"P-20", "P-21", "P-22", "P-23", "P-24", "P-25", "P-26"}
HITO_005_VALIDATION_IDS = HITO_004_VALIDATION_IDS | {f"V{index:03d}" for index in range(79, 99)}
HITO_005_PERMISSION_CODES = HITO_004_PERMISSION_CODES | {
    "sales.read",
    "sales.create",
    "customers.read",
    "customers.create",
    "customers.update",
    "reservations.create",
    "reservations.manage",
    "purchase-orders.read",
    "purchase-orders.create",
    "purchase-orders.receive",
    "purchase-orders.cancel",
}
HITO_006_ENTITY_NAMES = HITO_005_ENTITY_NAMES | {
    "export_jobs",
}
HITO_006_SCREEN_IDS = HITO_005_SCREEN_IDS | {"P-03", "P-29"}
HITO_006_VALIDATION_IDS = HITO_005_VALIDATION_IDS
HITO_006_PERMISSION_CODES = HITO_005_PERMISSION_CODES | {
    "reports.read",
    "reports.export",
}
HITO_007_ENTITY_NAMES = HITO_006_ENTITY_NAMES | {
    "equipment_types",
    "equipment",
    "equipment_movements",
    "expense_categories",
    "operational_expenses",
    "monthly_goals",
}
HITO_007_SCREEN_IDS = HITO_006_SCREEN_IDS | {"P-27", "P-28"}
HITO_007_VALIDATION_IDS = {f"V{index:03d}" for index in range(1, 101)}
HITO_007_PERMISSION_CODES = HITO_006_PERMISSION_CODES | {
    "equipment.read",
    "equipment.create",
    "equipment.movement",
    "expenses.read",
    "expenses.create",
}
HITO_008_ENTITY_NAMES = HITO_007_ENTITY_NAMES
HITO_008_SCREEN_IDS = HITO_007_SCREEN_IDS
HITO_008_VALIDATION_IDS = HITO_007_VALIDATION_IDS
HITO_008_PERMISSION_CODES = HITO_007_PERMISSION_CODES
HITO_001_ENDPOINTS: list[dict[str, Any]] = [
    {
        "api_id": "API-001",
        "method": "POST",
        "path": "/api/v1/auth/login",
        "handler": "auth.login",
        "description": "iniciar sesion, retorna token JWT.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-002",
        "method": "POST",
        "path": "/api/v1/auth/logout",
        "handler": "auth.logout",
        "description": "cerrar sesion autenticada y auditar salida.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-003",
        "method": "GET",
        "path": "/api/v1/auth/me",
        "handler": "auth.me",
        "description": "obtener usuario autenticado.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": True,
    },
    {
        "api_id": "API-004",
        "method": "POST",
        "path": "/api/v1/auth/change-password",
        "handler": "auth.change_password",
        "description": "cambiar contrasena validando la actual.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-005",
        "method": "GET",
        "path": "/api/v1/users",
        "handler": "users.list",
        "description": "listar usuarios con filtros por rol y estado.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-006",
        "method": "POST",
        "path": "/api/v1/users",
        "handler": "users.create",
        "description": "crear usuario con rol activo, solo admin.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-007",
        "method": "GET",
        "path": "/api/v1/users/{id}",
        "handler": "users.detail",
        "description": "obtener detalle de usuario.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-008",
        "method": "PUT",
        "path": "/api/v1/users/{id}",
        "handler": "users.update",
        "description": "editar usuario y auditar cambio critico.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-009",
        "method": "PATCH",
        "path": "/api/v1/users/{id}/toggle-status",
        "handler": "users.toggle_status",
        "description": "activar o desactivar usuario.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-082",
        "method": "GET",
        "path": "/api/v1/audit-logs",
        "handler": "audit_logs.list",
        "description": "consultar auditoria funcional con permiso audit.read.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-085",
        "method": "POST",
        "path": "/api/v1/auth/password-reset/request",
        "handler": "auth.password_reset_request",
        "description": "solicitar restablecimiento sin filtrar existencia de usuario.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-086",
        "method": "POST",
        "path": "/api/v1/auth/password-reset/confirm",
        "handler": "auth.password_reset_confirm",
        "description": "confirmar token valido y guardar hash nuevo.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
]
HITO_002_ENDPOINTS: list[dict[str, Any]] = HITO_001_ENDPOINTS + [
    {
        "api_id": "API-010",
        "method": "GET",
        "path": "/api/v1/suppliers",
        "handler": "suppliers.list",
        "description": "listar proveedores.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-011",
        "method": "POST",
        "path": "/api/v1/suppliers",
        "handler": "suppliers.create",
        "description": "crear proveedor activo.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-012",
        "method": "PUT",
        "path": "/api/v1/suppliers/{id}",
        "handler": "suppliers.update",
        "description": "actualizar proveedor.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-013",
        "method": "PATCH",
        "path": "/api/v1/suppliers/{id}/toggle-status",
        "handler": "suppliers.toggle_status",
        "description": "activar o desactivar proveedor.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-014",
        "method": "GET",
        "path": "/api/v1/supplies",
        "handler": "supplies.list",
        "description": "listar insumos con filtros.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-015",
        "method": "POST",
        "path": "/api/v1/supplies",
        "handler": "supplies.create",
        "description": "crear insumo maestro.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-016",
        "method": "GET",
        "path": "/api/v1/supplies/{id}",
        "handler": "supplies.detail",
        "description": "obtener insumo.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-017",
        "method": "PUT",
        "path": "/api/v1/supplies/{id}",
        "handler": "supplies.update",
        "description": "actualizar insumo maestro.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-018",
        "method": "PATCH",
        "path": "/api/v1/supplies/{id}/toggle-status",
        "handler": "supplies.toggle_status",
        "description": "activar o desactivar insumo.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-023",
        "method": "GET",
        "path": "/api/v1/recipes",
        "handler": "recipes.list",
        "description": "listar recetas.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-024",
        "method": "POST",
        "path": "/api/v1/recipes",
        "handler": "recipes.create",
        "description": "crear receta con ingredientes.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-025",
        "method": "GET",
        "path": "/api/v1/recipes/{id}",
        "handler": "recipes.detail",
        "description": "obtener receta con ingredientes.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-026",
        "method": "PUT",
        "path": "/api/v1/recipes/{id}",
        "handler": "recipes.update",
        "description": "actualizar receta.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-027",
        "method": "POST",
        "path": "/api/v1/recipes/{id}/clone",
        "handler": "recipes.clone",
        "description": "clonar receta activa o en prueba.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-041",
        "method": "GET",
        "path": "/api/v1/warehouses",
        "handler": "warehouses.list",
        "description": "listar bodegas.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-042",
        "method": "POST",
        "path": "/api/v1/warehouses",
        "handler": "warehouses.create",
        "description": "crear bodega.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-043",
        "method": "PUT",
        "path": "/api/v1/warehouses/{id}",
        "handler": "warehouses.update",
        "description": "actualizar bodega.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-044",
        "method": "GET",
        "path": "/api/v1/presentation-types",
        "handler": "presentation_types.list",
        "description": "listar tipos de presentacion.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-045",
        "method": "POST",
        "path": "/api/v1/presentation-types",
        "handler": "presentation_types.create",
        "description": "crear tipo de presentacion.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-046",
        "method": "PUT",
        "path": "/api/v1/presentation-types/{id}",
        "handler": "presentation_types.update",
        "description": "actualizar tipo de presentacion.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
]
HITO_003_ENDPOINTS: list[dict[str, Any]] = HITO_002_ENDPOINTS + [
    {
        "api_id": "API-019",
        "method": "GET",
        "path": "/api/v1/supplies/{id}/kardex",
        "handler": "supplies.kardex",
        "description": "consultar Kardex de insumo con filtros operativos.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": True,
    },
    {
        "api_id": "API-020",
        "method": "GET",
        "path": "/api/v1/supplies/low-stock",
        "handler": "supplies.low_stock",
        "description": "listar insumos bajo stock minimo.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-021",
        "method": "POST",
        "path": "/api/v1/supply-entries",
        "handler": "supply_entries.create",
        "description": "registrar entrada de insumo, actualizar stock y Kardex.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-022",
        "method": "GET",
        "path": "/api/v1/supply-entries",
        "handler": "supply_entries.list",
        "description": "listar entradas de insumos con filtros.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-077",
        "method": "GET",
        "path": "/api/v1/settings/smtp",
        "handler": "settings.smtp",
        "description": "obtener configuracion SMTP sanitizada.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-078",
        "method": "PUT",
        "path": "/api/v1/settings/smtp",
        "handler": "settings.smtp_update",
        "description": "guardar configuracion SMTP con secreto cifrado localmente.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-079",
        "method": "POST",
        "path": "/api/v1/settings/smtp/test",
        "handler": "settings.smtp_test",
        "description": "registrar prueba SMTP local sin enviar correo real.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-083",
        "method": "GET",
        "path": "/api/v1/notifications",
        "handler": "notifications.list",
        "description": "listar cola de notificaciones de stock bajo y SMTP.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
]
HITO_004_ENDPOINTS: list[dict[str, Any]] = HITO_003_ENDPOINTS + [
    {
        "api_id": "API-028",
        "method": "GET",
        "path": "/api/v1/batches",
        "handler": "batches.list",
        "description": "listar lotes de produccion con filtros.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-029",
        "method": "POST",
        "path": "/api/v1/batches",
        "handler": "batches.create",
        "description": "crear lote en elaboracion desde receta y presentacion activas.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-030",
        "method": "GET",
        "path": "/api/v1/batches/{id}",
        "handler": "batches.detail",
        "description": "obtener lote con detalle de insumos y costos.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-031",
        "method": "PUT",
        "path": "/api/v1/batches/{id}",
        "handler": "batches.update",
        "description": "editar lote solo mientras esta en elaboracion.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-032",
        "method": "POST",
        "path": "/api/v1/batches/{id}/complete",
        "handler": "batches.complete",
        "description": "completar lote descontando insumos, creando producto y calculando costos.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-033",
        "method": "POST",
        "path": "/api/v1/batches/{id}/cancel",
        "handler": "batches.cancel",
        "description": "cancelar lote sin afectar inventario ni Kardex.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-034",
        "method": "POST",
        "path": "/api/v1/batches/{id}/quality-check",
        "handler": "batches.quality_check",
        "description": "registrar control de calidad unico para el lote completado.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-035",
        "method": "GET",
        "path": "/api/v1/products",
        "handler": "products.list",
        "description": "listar inventario de productos terminados.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-036",
        "method": "PUT",
        "path": "/api/v1/products/{id}/price",
        "handler": "products.update_price",
        "description": "actualizar precio de venta base sin permitir valores negativos.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-047",
        "method": "GET",
        "path": "/api/v1/products/{id}/kardex",
        "handler": "products.kardex",
        "description": "consultar Kardex de producto terminado.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": True,
    },
    {
        "api_id": "API-062",
        "method": "GET",
        "path": "/api/v1/waste-records",
        "handler": "waste_records.list",
        "description": "listar mermas registradas.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-063",
        "method": "POST",
        "path": "/api/v1/waste-records",
        "handler": "waste_records.create",
        "description": "registrar merma descontando inventario y escribiendo Kardex.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
]
HITO_005_ENDPOINTS: list[dict[str, Any]] = HITO_004_ENDPOINTS + [
    {
        "api_id": "API-037",
        "method": "POST",
        "path": "/api/v1/sales",
        "handler": "sales.create",
        "description": "registrar venta con stock libre, ganancia y Kardex.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-038",
        "method": "GET",
        "path": "/api/v1/sales",
        "handler": "sales.list",
        "description": "listar ventas con filtros.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-039",
        "method": "GET",
        "path": "/api/v1/customers",
        "handler": "customers.list",
        "description": "listar clientes con filtros comerciales.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-040",
        "method": "POST",
        "path": "/api/v1/customers",
        "handler": "customers.create",
        "description": "crear cliente activo con identificador fiscal unico.",
        "source": "brewmaster_especificacion_completa.md#F.40-endpoints",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-048",
        "method": "GET",
        "path": "/api/v1/customers/{id}",
        "handler": "customers.detail",
        "description": "obtener cliente con historial comercial.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-049",
        "method": "PUT",
        "path": "/api/v1/customers/{id}",
        "handler": "customers.update",
        "description": "editar cliente sin romper historial de ventas.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-050",
        "method": "PATCH",
        "path": "/api/v1/customers/{id}/toggle-status",
        "handler": "customers.toggle_status",
        "description": "activar o inactivar cliente mediante eliminacion logica.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-051",
        "method": "GET",
        "path": "/api/v1/reservations",
        "handler": "reservations.list",
        "description": "listar reservas de stock activas, liberadas o consumidas.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-052",
        "method": "POST",
        "path": "/api/v1/reservations",
        "handler": "reservations.create",
        "description": "crear reserva sobre stock libre de producto terminado.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-053",
        "method": "POST",
        "path": "/api/v1/reservations/{id}/consume",
        "handler": "reservations.consume",
        "description": "convertir reserva activa en venta.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-054",
        "method": "POST",
        "path": "/api/v1/reservations/{id}/release",
        "handler": "reservations.release",
        "description": "liberar reserva activa sin afectar inventario.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-055",
        "method": "GET",
        "path": "/api/v1/purchase-orders",
        "handler": "purchase_orders.list",
        "description": "listar ordenes de compra.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-056",
        "method": "POST",
        "path": "/api/v1/purchase-orders",
        "handler": "purchase_orders.create",
        "description": "crear orden de compra en borrador con proveedor activo.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-057",
        "method": "GET",
        "path": "/api/v1/purchase-orders/{id}",
        "handler": "purchase_orders.detail",
        "description": "obtener orden de compra con lineas.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-058",
        "method": "PUT",
        "path": "/api/v1/purchase-orders/{id}",
        "handler": "purchase_orders.update",
        "description": "editar orden solo en estado borrador.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-059",
        "method": "POST",
        "path": "/api/v1/purchase-orders/{id}/send",
        "handler": "purchase_orders.send",
        "description": "enviar orden de compra borrador.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-060",
        "method": "POST",
        "path": "/api/v1/purchase-orders/{id}/receive",
        "handler": "purchase_orders.receive",
        "description": "recepcionar compra parcial o total y generar Kardex de insumos.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-061",
        "method": "POST",
        "path": "/api/v1/purchase-orders/{id}/cancel",
        "handler": "purchase_orders.cancel",
        "description": "cancelar orden no recibida.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-087",
        "method": "POST",
        "path": "/api/v1/sales/{id}/void",
        "handler": "sales.void",
        "description": "anular venta, revertir stock y registrar Kardex DEVOLUCION.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
]
HITO_006_ENDPOINTS: list[dict[str, Any]] = HITO_005_ENDPOINTS + [
    {
        "api_id": "API-074",
        "method": "GET",
        "path": "/api/v1/dashboard",
        "handler": "dashboard.summary",
        "description": "obtener KPIs reales, graficos y alertas operacionales.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-075",
        "method": "GET",
        "path": "/api/v1/reports",
        "handler": "reports.list",
        "description": "listar reportes operacionales disponibles y exportaciones locales.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-076",
        "method": "POST",
        "path": "/api/v1/reports/export",
        "handler": "reports.export",
        "description": "exportar reporte operacional en CSV, XLSX o PDF y auditar la accion.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
]
HITO_007_ENDPOINTS: list[dict[str, Any]] = HITO_006_ENDPOINTS + [
    {
        "api_id": "API-064",
        "method": "GET",
        "path": "/api/v1/equipment",
        "handler": "equipment.list",
        "description": "listar equipos, estado operativo y proxima revision.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-065",
        "method": "POST",
        "path": "/api/v1/equipment",
        "handler": "equipment.create",
        "description": "crear equipo con codigo unico y calendario de revision.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-066",
        "method": "GET",
        "path": "/api/v1/equipment/{id}",
        "handler": "equipment.detail",
        "description": "obtener equipo con historial de movimientos.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-067",
        "method": "PUT",
        "path": "/api/v1/equipment/{id}",
        "handler": "equipment.update",
        "description": "actualizar datos y estado de equipo sin perder auditoria.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-068",
        "method": "POST",
        "path": "/api/v1/equipment/{id}/movements",
        "handler": "equipment.movements_create",
        "description": "registrar mantencion, traslado o descarte de equipo.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": True,
    },
    {
        "api_id": "API-069",
        "method": "GET",
        "path": "/api/v1/equipment/{id}/movements",
        "handler": "equipment.movements",
        "description": "listar historial de movimientos de equipo.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": True,
    },
    {
        "api_id": "API-070",
        "method": "GET",
        "path": "/api/v1/expenses",
        "handler": "expenses.list",
        "description": "listar gastos operativos con filtros financieros basicos.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-071",
        "method": "POST",
        "path": "/api/v1/expenses",
        "handler": "expenses.create",
        "description": "registrar gasto operativo con monto positivo y auditoria.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-072",
        "method": "PUT",
        "path": "/api/v1/expenses/{id}",
        "handler": "expenses.update",
        "description": "actualizar gasto operativo no bloqueado por documento.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-073",
        "method": "DELETE",
        "path": "/api/v1/expenses/{id}",
        "handler": "expenses.delete",
        "description": "eliminar logicamente gasto operativo sin documento asociado.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-080",
        "method": "GET",
        "path": "/api/v1/monthly-goals",
        "handler": "monthly_goals.list",
        "description": "listar metas mensuales y avance contra dashboard.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-081",
        "method": "PUT",
        "path": "/api/v1/monthly-goals/{month}",
        "handler": "monthly_goals.upsert",
        "description": "crear o actualizar metas mensuales operativas.",
        "source": "brewmaster_especificacion_completa.md#K.6",
        "transactional": True,
        "action_endpoint": False,
    },
    {
        "api_id": "API-088",
        "method": "GET",
        "path": "/api/v1/jobs",
        "handler": "jobs.list",
        "description": "listar politica local de scheduler, incluyendo backup automatico.",
        "source": "brewmaster_especificacion_completa.md#J.16",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-089",
        "method": "GET",
        "path": "/api/v1/backups",
        "handler": "backups.list",
        "description": "listar respaldos automaticos locales simulados.",
        "source": "brewmaster_especificacion_completa.md#J.16",
        "transactional": False,
        "action_endpoint": False,
    },
    {
        "api_id": "API-090",
        "method": "POST",
        "path": "/api/v1/backups",
        "handler": "backups.create",
        "description": "registrar respaldo local simulado sin escribir fuera del sandbox.",
        "source": "brewmaster_especificacion_completa.md#J.16",
        "transactional": True,
        "action_endpoint": False,
    },
]


def _is_hito_001(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-001", "HITO-1", "1"}


def _is_hito_002(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-002", "HITO-2", "2"}


def _is_hito_003(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-003", "HITO-3", "3"}


def _is_hito_004(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-004", "HITO-4", "4"}


def _is_hito_005(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-005", "HITO-5", "5"}


def _is_hito_006(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-006", "HITO-6", "6"}


def _is_hito_007(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-007", "HITO-7", "7"}


def _is_hito_008(milestone_id: str | None) -> bool:
    normalized = (milestone_id or "").strip().upper()
    return normalized in {"HITO-008", "HITO-8", "8"}


def _hito_001_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    screen_overrides = {
        "P-30": {
            "id": "P-30",
            "name": "Configuracion de usuarios, roles y auditoria",
            "module": "Configuracion",
            "route": "/settings/security",
        }
    }
    screens = [
        screen_overrides.get(screen["id"], screen)
        for screen in spec.screens
        if screen["id"] in HITO_001_SCREEN_IDS
    ]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_001_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_001_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_001_PERMISSION_CODES]
    return {
        "blueprint_id": "brewmaster.sdd.hito1.v1",
        "milestone_id": "HITO-001",
        "milestone_name": "Fundamentos",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 1",
            "includes": [
                "Auth JWT",
                "usuarios",
                "roles",
                "permisos",
                "auditoria",
                "estructura base del proyecto",
            ],
            "deferred_milestones": ["HITO-002", "HITO-003", "HITO-004", "HITO-005", "HITO-006", "HITO-007"],
            "deferred_modules": [
                "proveedores",
                "insumos",
                "bodegas",
                "recetas",
                "inventario",
                "produccion",
                "ventas",
                "compras",
                "dashboard",
                "finanzas",
                "alertas SMTP",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 2,
            "business_rule_count": 10,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
        },
        "modules": [
            {
                "id": "MOD-001",
                "name": "Seguridad, usuarios y auditoria",
                "use_cases": ["CU-001", "CU-031"],
                "screens": ["P-01", "P-02", "P-30"],
                "entities": sorted(HITO_001_ENTITY_NAMES),
                "acceptance": "login JWT, recuperacion de contrasena, CRUD usuarios, RBAC y auditoria funcional",
            }
        ],
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_001_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"] in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 60}
        ],
        "transactional_rules": [
            "login_success_returns_expiring_jwt_and_failed_login_is_audited",
            "protected_endpoint_requires_active_user_and_role_permission",
            "user_create_update_toggle_are_admin_only_and_audited",
            "password_change_requires_current_password_and_stores_hash",
            "password_reset_token_is_single_use_expiring_and_audited",
            "audit_log_read_is_limited_to_admin_or_auditor",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1 endpoints"],
            "audit": "critical Hito 1 writes include actor, date, entity, action and IP",
            "observability": ["request_id", "user_id", "module", "structured audit events"],
            "privacy": ["password hashes only", "reset token stored hashed"],
        },
    }


def _hito_002_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    screen_overrides = {
        "P-30": {
            "id": "P-30",
            "name": "Configuracion de usuarios, roles y auditoria",
            "module": "Configuracion",
            "route": "/settings/security",
        }
    }
    screens = [
        screen_overrides.get(screen["id"], screen)
        for screen in spec.screens
        if screen["id"] in HITO_002_SCREEN_IDS
    ]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_002_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_002_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_002_PERMISSION_CODES]
    return {
        "blueprint_id": "brewmaster.sdd.hito2.v1",
        "milestone_id": "HITO-002",
        "milestone_name": "Maestros",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 2",
            "includes": [
                "HITO-001 fundamentos conservados",
                "proveedores",
                "insumos maestros",
                "bodegas",
                "recetas",
                "tipos de presentacion",
            ],
            "deferred_milestones": ["HITO-003", "HITO-004", "HITO-005", "HITO-006", "HITO-007"],
            "deferred_modules": [
                "entradas de insumos",
                "Kardex operativo",
                "alertas email/SMTP",
                "produccion",
                "ventas",
                "compras",
                "dashboard",
                "reportes",
                "equipos",
                "finanzas",
                "jobs",
            ],
            "explicitly_excluded_paths": [
                "/api/v1/supply-entries",
                "/api/v1/supplies/{id}/kardex",
                "/api/v1/supplies/low-stock",
                "/api/v1/batches",
                "/api/v1/products",
                "/api/v1/sales",
                "/api/v1/customers",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 7,
            "business_rule_count": 22,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens from HITO-001",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
        },
        "modules": [
            {
                "id": "MOD-001",
                "name": "Seguridad, usuarios y auditoria",
                "use_cases": ["CU-001", "CU-031"],
                "screens": ["P-01", "P-02", "P-30"],
                "entities": sorted(HITO_001_ENTITY_NAMES),
                "acceptance": "HITO-001 conserva login JWT, usuarios, RBAC y auditoria funcional.",
            },
            {
                "id": "MOD-002",
                "name": "Proveedores",
                "use_cases": ["CU-006"],
                "screens": ["P-08", "P-09"],
                "entities": ["suppliers"],
                "acceptance": "CRUD de proveedor con codigo unico, correo valido, estado y auditoria.",
            },
            {
                "id": "MOD-003",
                "name": "Insumos y bodegas maestros",
                "use_cases": ["CU-002", "CU-005"],
                "screens": ["P-04", "P-05", "P-12"],
                "entities": ["warehouses", "supply_categories", "supplies"],
                "acceptance": "Insumo maestro activo con proveedor/bodega validos, costos y stock no negativos; sin entradas ni Kardex operativo.",
            },
            {
                "id": "MOD-004",
                "name": "Recetas y presentaciones",
                "use_cases": ["CU-007", "CU-008"],
                "screens": ["P-10", "P-11", "P-13"],
                "entities": ["presentation_types", "recipes", "recipe_ingredients"],
                "acceptance": "Receta con ingredientes activos calcula costo estimado y puede clonarse como en_prueba; presentaciones validan volumen y costo.",
            },
        ],
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_002_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"]
            in {
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                25,
                26,
                27,
                28,
                34,
                42,
                60,
            }
        ],
        "transactional_rules": [
            "hito1_auth_user_rbac_audit_regression_remains_active",
            "supplier_code_is_unique_and_status_changes_are_audited",
            "supply_code_is_unique_and_cost_stock_values_are_non_negative",
            "inactive_supply_cannot_be_used_in_new_or_active_recipes",
            "recipe_requires_active_ingredient_and_calculates_estimated_cost",
            "recipe_clone_requires_active_or_test_recipe_and_creates_en_prueba_copy",
            "warehouse_code_is_unique_and_usable_by_active_supplies",
            "presentation_type_requires_positive_volume_and_non_negative_cost",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1 and Hito 2 endpoints"],
            "audit": "critical Hito 2 catalog writes include actor, date, entity, action and IP",
            "observability": ["request_id", "user_id", "module", "structured audit events"],
            "privacy": ["password hashes only", "reset token stored hashed"],
        },
    }


def _hito_003_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    screen_overrides = {
        "P-30": {
            "id": "P-30",
            "name": "Configuracion SMTP, usuarios, roles y auditoria",
            "module": "Configuracion",
            "route": "/settings",
        }
    }
    screens = [
        screen_overrides.get(screen["id"], screen)
        for screen in spec.screens
        if screen["id"] in HITO_003_SCREEN_IDS
    ]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_003_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_003_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_003_PERMISSION_CODES]
    return {
        "blueprint_id": "brewmaster.sdd.hito3.v1",
        "milestone_id": "HITO-003",
        "milestone_name": "Inventario",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 3",
            "includes": [
                "HITO-001 fundamentos conservados",
                "HITO-002 maestros conservados",
                "entradas de insumos",
                "Kardex operativo de insumos",
                "reglas de stock bajo",
                "cola local de notificaciones",
                "configuracion SMTP sanitizada",
                "prueba SMTP local sin envio externo",
            ],
            "deferred_milestones": ["HITO-004", "HITO-005", "HITO-006", "HITO-007"],
            "deferred_modules": [
                "produccion",
                "lotes",
                "control de calidad",
                "mermas productivas",
                "productos terminados",
                "ventas",
                "clientes",
                "compras",
                "dashboard",
                "reportes exportables",
                "equipos",
                "finanzas",
                "metas mensuales",
                "backups",
                "dockerizacion productiva",
                "deploy EC2",
            ],
            "explicitly_excluded_paths": [
                "/api/v1/batches",
                "/api/v1/products",
                "/api/v1/sales",
                "/api/v1/customers",
                "/api/v1/purchase-orders",
                "/api/v1/reports",
                "/api/v1/equipment",
                "/api/v1/expenses",
                "/api/v1/monthly-goals",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 10,
            "business_rule_count": 28,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens from HITO-001",
            "email": "local mocked SMTP adapter, no external delivery",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
            "external_email": "denied; SMTP test uses local queue evidence only",
        },
        "modules": [
            {
                "id": "MOD-001",
                "name": "Seguridad, usuarios y auditoria",
                "use_cases": ["CU-001", "CU-031"],
                "screens": ["P-01", "P-02", "P-30"],
                "entities": sorted(HITO_001_ENTITY_NAMES),
                "acceptance": "HITO-001 conserva login JWT, usuarios, RBAC y auditoria funcional.",
            },
            {
                "id": "MOD-002",
                "name": "Proveedores",
                "use_cases": ["CU-006"],
                "screens": ["P-08", "P-09"],
                "entities": ["suppliers"],
                "acceptance": "HITO-002 conserva proveedores con codigo unico, correo valido, estado y auditoria.",
            },
            {
                "id": "MOD-003",
                "name": "Insumos, bodegas y Kardex",
                "use_cases": ["CU-002", "CU-003", "CU-004", "CU-005"],
                "screens": ["P-04", "P-05", "P-06", "P-07", "P-12"],
                "entities": ["warehouses", "supply_categories", "supplies", "supply_entries", "supply_movements", "notification_queue"],
                "acceptance": "Entrada valida incrementa stock, registra Kardex y encola alerta de stock bajo sin bloquear la operacion.",
            },
            {
                "id": "MOD-004",
                "name": "Recetas y presentaciones",
                "use_cases": ["CU-007", "CU-008"],
                "screens": ["P-10", "P-11", "P-13"],
                "entities": ["presentation_types", "recipes", "recipe_ingredients"],
                "acceptance": "HITO-002 conserva recetas con ingredientes activos, costo estimado y clonado controlado.",
            },
            {
                "id": "MOD-013",
                "name": "Configuracion y alertas",
                "use_cases": ["CU-004", "CU-029"],
                "screens": ["P-30"],
                "entities": ["settings", "smtp_config", "notification_queue"],
                "acceptance": "SMTP se guarda sanitizado, la prueba es local y la cola registra intentos sin enviar correos reales.",
            },
        ],
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_003_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"]
            in {
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                34,
                42,
                60,
            }
        ],
        "transactional_rules": [
            "hito1_auth_user_rbac_audit_regression_remains_active",
            "hito2_master_catalogs_remain_active_and_unchanged",
            "supply_entry_updates_stock_and_kardex_atomically",
            "inactive_supply_cannot_receive_inventory_entries",
            "low_stock_query_uses_current_stock_and_minimum_threshold",
            "stock_alert_queue_respects_enabled_recipients_interval_and_zero_stock_priority",
            "stock_recovery_resets_last_alert_sent_at",
            "smtp_configuration_is_sanitized_and_local_test_never_sends_external_email",
            "email_retry_policy_marks_final_failure_after_five_attempts",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1-3 endpoints"],
            "audit": "critical Hito 3 inventory and SMTP writes include actor, date, entity, action and IP",
            "observability": ["request_id", "user_id", "module", "structured audit events"],
            "privacy": ["password hashes only", "reset token stored hashed", "SMTP secret never returned in API responses"],
            "external_integrations": ["SMTP delivery mocked locally; no real email or network integration"],
        },
    }


def _hito_004_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    base = _hito_003_blueprint()
    screens = [screen for screen in spec.screens if screen["id"] in HITO_004_SCREEN_IDS]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_004_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_004_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_004_PERMISSION_CODES]
    modules = list(base["modules"]) + [
        {
            "id": "MOD-005",
            "name": "Produccion y calidad",
            "use_cases": ["CU-009", "CU-010", "CU-011"],
            "screens": ["P-14", "P-15", "P-16", "P-17"],
            "entities": ["production_batches", "batch_quality_checks", "batch_supply_snapshots"],
            "acceptance": "Lotes se crean en elaboracion, se completan descontando insumos y registran control de calidad unico.",
        },
        {
            "id": "MOD-006",
            "name": "Mermas",
            "use_cases": ["CU-012"],
            "screens": ["P-19"],
            "entities": ["waste_records", "supply_movements", "product_movements"],
            "acceptance": "Merma valida exige motivo, descuenta inventario de insumo o producto y deja Kardex trazable.",
        },
        {
            "id": "MOD-007",
            "name": "Inventario de productos terminados",
            "use_cases": ["CU-013", "CU-014"],
            "screens": ["P-18"],
            "entities": ["finished_products", "product_movements"],
            "acceptance": "Completar lote crea o incrementa producto terminado y permite precio base no negativo.",
        },
    ]
    return {
        "blueprint_id": "brewmaster.sdd.hito4.v1",
        "milestone_id": "HITO-004",
        "milestone_name": "Produccion",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 4",
            "includes": [
                "HITO-001 fundamentos conservados",
                "HITO-002 maestros conservados",
                "HITO-003 inventario y SMTP local conservados",
                "lotes de produccion",
                "completar lote con descuento de insumos",
                "control de calidad unico",
                "mermas de insumos y productos",
                "inventario de productos terminados",
                "Kardex de productos terminados",
            ],
            "deferred_milestones": ["HITO-005", "HITO-006", "HITO-007"],
            "deferred_modules": [
                "ventas",
                "clientes",
                "reservas",
                "compras",
                "ordenes de compra",
                "dashboard",
                "reportes exportables",
                "equipos",
                "finanzas",
                "metas mensuales",
                "backups",
                "dockerizacion productiva",
                "deploy EC2",
            ],
            "explicitly_excluded_paths": [
                "/api/v1/sales",
                "/api/v1/customers",
                "/api/v1/reservations",
                "/api/v1/purchase-orders",
                "/api/v1/reports",
                "/api/v1/equipment",
                "/api/v1/expenses",
                "/api/v1/monthly-goals",
                "/api/v1/dashboard",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 16,
            "business_rule_count": 41,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens from HITO-001",
            "email": "local mocked SMTP adapter from HITO-003, no external delivery",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
            "external_email": "denied; SMTP test uses local queue evidence only",
            "production_deploy": "denied until HITO-007 and explicit approval",
        },
        "modules": modules,
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_004_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"]
            in {
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                42,
                60,
            }
        ],
        "transactional_rules": [
            *base["transactional_rules"],
            "batch_creation_requires_active_recipe_presentation_and_responsible",
            "complete_batch_validates_stock_consumes_supplies_creates_finished_product_and_calculates_cost_atomically",
            "completed_or_cancelled_batch_cannot_be_edited_or_completed_again",
            "cancelled_batch_has_no_inventory_or_kardex_effects",
            "quality_check_is_unique_and_rejection_requires_reason",
            "waste_record_decrements_supply_or_product_inventory_and_writes_kardex_atomically",
            "finished_product_price_update_rejects_negative_values_and_warns_below_cost",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1-4 endpoints"],
            "audit": "critical Hito 4 production, quality, waste and product price writes include actor, date, entity, action and IP",
            "observability": ["request_id", "user_id", "module", "structured audit events"],
            "privacy": ["password hashes only", "reset token stored hashed", "SMTP secret never returned in API responses"],
            "external_integrations": ["SMTP delivery mocked locally; no real email, sales integration or purchasing integration"],
            "deployment": ["no production deploy, dockerization, proxy/TLS or backup automation in HITO-004"],
        },
    }


def _hito_005_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    base = _hito_004_blueprint()
    screens = [screen for screen in spec.screens if screen["id"] in HITO_005_SCREEN_IDS]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_005_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_005_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_005_PERMISSION_CODES]
    modules = list(base["modules"]) + [
        {
            "id": "MOD-008",
            "name": "Ventas, clientes y reservas",
            "use_cases": ["CU-015", "CU-016", "CU-017", "CU-018", "CU-019"],
            "screens": ["P-20", "P-21", "P-22", "P-23"],
            "entities": ["customer_types", "customers", "product_prices", "sales", "sale_items", "stock_reservations"],
            "acceptance": "Clientes, ventas, reservas y precios por tipo de cliente validan stock libre y registran Kardex.",
        },
        {
            "id": "MOD-009",
            "name": "Compras y ordenes de compra",
            "use_cases": ["CU-020", "CU-021"],
            "screens": ["P-24", "P-25", "P-26"],
            "entities": ["purchase_orders", "purchase_order_items", "suppliers", "supplies"],
            "acceptance": "Ordenes con proveedor activo pasan por borrador, enviada, recepcion parcial o total y Kardex de insumos.",
        },
    ]
    return {
        "blueprint_id": "brewmaster.sdd.hito5.v1",
        "milestone_id": "HITO-005",
        "milestone_name": "Ventas",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 5",
            "includes": [
                "HITO-001 fundamentos conservados",
                "HITO-002 maestros conservados",
                "HITO-003 inventario y SMTP local conservados",
                "HITO-004 produccion, calidad, mermas y productos terminados conservados",
                "clientes",
                "ventas",
                "reservas de stock",
                "precios por tipo de cliente",
                "compras",
                "ordenes de compra",
                "recepcion parcial y total de ordenes",
            ],
            "deferred_milestones": ["HITO-006", "HITO-007"],
            "deferred_modules": [
                "dashboard",
                "KPIs graficos",
                "reportes exportables",
                "equipos",
                "finanzas",
                "metas mensuales",
                "respaldos automaticos",
                "dockerizacion productiva",
                "EC2",
                "proxy TLS",
                "deploy productivo",
            ],
            "explicitly_excluded_paths": [
                "/api/v1/reports",
                "/api/v1/reports/export",
                "/api/v1/equipment",
                "/api/v1/expenses",
                "/api/v1/monthly-goals",
                "/api/v1/dashboard",
                "/api/v1/jobs",
                "/api/v1/backups",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 23,
            "business_rule_count": 53,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens from HITO-001",
            "email": "local mocked SMTP adapter from HITO-003, no external delivery",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
            "external_email": "denied; SMTP test uses local queue evidence only",
            "external_sales_or_purchasing_integrations": "denied; all sales and purchasing flows are local MVP logic",
            "production_deploy": "denied until HITO-007 and explicit approval",
        },
        "modules": modules,
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_005_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"]
            in {
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
                49,
                50,
                51,
                52,
                53,
                54,
                60,
            }
        ],
        "transactional_rules": [
            *base["transactional_rules"],
            "customer_fiscal_identifier_is_unique_and_locked_after_sales",
            "sale_validates_customer_active_status_product_stock_and_price_policy",
            "sale_decrements_finished_product_stock_and_writes_product_kardex",
            "sale_void_requires_reason_reverts_stock_and_writes_dev_kardex",
            "reservation_uses_current_stock_minus_active_reservations",
            "reservation_release_or_consume_is_single_transition",
            "purchase_order_requires_active_supplier_and_positive_lines",
            "purchase_order_sent_is_not_editable_without_explicit_permission",
            "purchase_order_receive_generates_supply_entry_kardex_and_updates_state_atomically",
            "cancelled_purchase_order_cannot_receive_inventory",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1-5 endpoints"],
            "audit": "critical Hito 5 customer, sale, reservation and purchase writes include actor, date, entity, action and IP",
            "observability": ["request_id", "user_id", "module", "structured audit events"],
            "privacy": ["password hashes only", "reset token stored hashed", "SMTP secret never returned in API responses"],
            "external_integrations": ["SMTP delivery mocked locally; no real email, sales integration, purchasing integration or payment gateway"],
            "deployment": ["no production deploy, dockerization, proxy/TLS or backup automation in HITO-005"],
        },
    }


def _hito_006_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    base = _hito_005_blueprint()
    screens = [screen for screen in spec.screens if screen["id"] in HITO_006_SCREEN_IDS]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_006_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_006_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_006_PERMISSION_CODES]
    modules = list(base["modules"]) + [
        {
            "id": "MOD-012",
            "name": "Dashboard y reportes operacionales",
            "use_cases": ["CU-027", "CU-028"],
            "screens": ["P-03", "P-29"],
            "entities": ["audit_logs", "export_jobs"],
            "acceptance": "Dashboard con KPIs reales, graficos, alertas operacionales y reportes exportables sin finanzas HITO-007.",
        },
    ]
    return {
        "blueprint_id": "brewmaster.sdd.hito6.v1",
        "milestone_id": "HITO-006",
        "milestone_name": "Dashboard",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 6",
            "includes": [
                "HITO-001 fundamentos conservados",
                "HITO-002 maestros conservados",
                "HITO-003 inventario, Kardex y SMTP local conservados",
                "HITO-004 produccion, calidad, mermas y productos terminados conservados",
                "HITO-005 clientes, ventas, reservas, precios y compras conservados",
                "dashboard general",
                "KPIs reales desde datos operacionales locales",
                "graficos de ventas, stock, produccion y mermas",
                "alertas operacionales de stock, mermas, reservas y compras",
                "reportes operacionales exportables CSV XLSX PDF",
                "trabajos locales de exportacion trazables",
            ],
            "deferred_milestones": ["HITO-007"],
            "deferred_modules": [
                "equipos",
                "finanzas",
                "gastos operativos",
                "metas mensuales",
                "respaldos automaticos",
                "dockerizacion productiva",
                "EC2",
                "proxy TLS",
                "deploy productivo",
            ],
            "explicitly_excluded_paths": [
                "/api/v1/equipment",
                "/api/v1/expenses",
                "/api/v1/monthly-goals",
                "/api/v1/jobs",
                "/api/v1/backups",
            ],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": 25,
            "business_rule_count": 55,
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens from HITO-001",
            "email": "local mocked SMTP adapter from HITO-003, no external delivery",
            "reports": "local in-memory CSV XLSX PDF export payloads with audit evidence",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
            "external_email": "denied; SMTP test uses local queue evidence only",
            "external_sales_or_purchasing_integrations": "denied; all sales and purchasing flows are local MVP logic",
            "production_deploy": "denied until HITO-007 and explicit approval",
            "backups": "denied until HITO-007",
        },
        "modules": modules,
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_006_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": [
            item
            for item in spec.business_rules
            if item["id"]
            in {
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
                49,
                50,
                51,
                52,
                53,
                54,
                60,
            }
        ],
        "transactional_rules": [
            *base["transactional_rules"],
            "dashboard_aggregates_real_operational_stores_without_financial_targets",
            "waste_over_five_percent_creates_dashboard_alert_without_equipment_scope",
            "report_export_validates_type_format_permission_and_records_audit",
            "report_catalog_excludes_financial_monthly_goal_and_equipment_outputs_until_hito7",
            "scheduler_policy_runs_operational_alerts_retries_reservations_and_exports_without_backups",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1-6 endpoints"],
            "performance": ["dashboard aggregations over local stores", "deferred export policy for broad reports"],
            "operations": ["no external integrations", "no production deploy", "no backup jobs before HITO-007"],
        },
    }


def _hito_007_blueprint() -> dict[str, Any]:
    spec = load_brewmaster_spec()
    base = _hito_006_blueprint()
    screens = [screen for screen in spec.screens if screen["id"] in HITO_007_SCREEN_IDS]
    entities = [entity for entity in spec.entities if entity["name"] in HITO_007_ENTITY_NAMES]
    validations = [item for item in spec.validations if item["id"] in HITO_007_VALIDATION_IDS]
    permissions = [permission for permission in spec.permissions if permission in HITO_007_PERMISSION_CODES]
    modules = list(base["modules"]) + [
        {
            "id": "MOD-010",
            "name": "Equipos",
            "use_cases": ["CU-022", "CU-023"],
            "screens": ["P-27"],
            "entities": ["equipment_types", "equipment", "equipment_movements"],
            "acceptance": "Equipos con codigo unico, historial de movimientos y alerta de revision vencida.",
        },
        {
            "id": "MOD-011",
            "name": "Finanzas operativas",
            "use_cases": ["CU-024", "CU-025", "CU-026"],
            "screens": ["P-28", "P-29", "P-30"],
            "entities": ["expense_categories", "operational_expenses", "monthly_goals"],
            "acceptance": "Gastos operativos, reportes financieros basicos y metas mensuales.",
        },
        {
            "id": "MOD-013",
            "name": "Cierre operacional y despliegue preparado",
            "use_cases": ["CU-029", "CU-030"],
            "screens": ["P-30"],
            "entities": ["monthly_goals", "export_jobs"],
            "acceptance": "Backups automaticos locales, Docker Compose, proxy/TLS documentado y runbook EC2 sin deploy real.",
        },
    ]
    return {
        "blueprint_id": "brewmaster.sdd.hito7.v1",
        "milestone_id": "HITO-007",
        "milestone_name": "Cierre",
        "source_spec": spec.source_path,
        "scope": {
            "source": "J.12 Hito 7",
            "includes": [
                "HITO-001 fundamentos conservados",
                "HITO-002 maestros conservados",
                "HITO-003 inventario, Kardex y SMTP local seguro conservados",
                "HITO-004 produccion, calidad, mermas y productos terminados conservados",
                "HITO-005 clientes, ventas, reservas, precios y compras conservados",
                "HITO-006 dashboard, KPIs, alertas operacionales, reportes y scheduler conservados",
                "equipos con historial y alertas de revision",
                "gastos operativos y reportes financieros basicos",
                "metas mensuales visibles en dashboard",
                "respaldos automaticos locales simulados sin escritura externa",
                "dockerizacion productiva preparada",
                "documentacion EC2, proxy y TLS preparada sin deploy real",
            ],
            "deferred_milestones": [],
            "explicitly_excluded_paths": [],
        },
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": len(spec.use_cases),
            "business_rule_count": len(spec.business_rules),
            "validation_count": len(validations),
            "permission_count": len(permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic contract",
            "database": "MySQL or MariaDB",
            "auth": "JWT with expiring local HS256 tokens from HITO-001",
            "email": "local mocked SMTP adapter from HITO-003, no external delivery",
            "reports": "local in-memory CSV XLSX PDF export payloads with audit evidence",
            "scheduler": "APScheduler policy with low_activity_backup job",
            "deployment": "Docker Compose, Nginx proxy, EC2 runbook and TLS placeholders only",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
            "external_email": "denied; SMTP test uses local queue evidence only",
            "external_sales_or_purchasing_integrations": "denied; all sales and purchasing flows are local MVP logic",
            "production_deploy": "denied; HITO-007 prepares EC2/proxy/TLS only",
            "external_backups": "denied; backup artifacts are local sandbox metadata only",
        },
        "modules": modules,
        "screens": screens,
        "entities": [entity["name"] for entity in entities],
        "entity_models": entities,
        "endpoints": HITO_007_ENDPOINTS,
        "validations": validations,
        "permissions": permissions,
        "business_rules": spec.business_rules,
        "transactional_rules": [
            *base["transactional_rules"],
            "equipment_code_is_unique_and_discarded_equipment_rejects_movements",
            "equipment_next_revision_overdue_creates_dashboard_alert",
            "operational_expense_requires_positive_amount_and_blocks_delete_with_document",
            "monthly_goals_are_upserted_by_month_and_compared_with_dashboard_actuals",
            "low_activity_backup_is_registered_locally_without_external_writes",
            "docker_ec2_proxy_tls_assets_are_prepared_but_not_deployed",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["password hash", "expiring JWT", "RBAC on protected Hito 1-7 endpoints"],
            "performance": ["dashboard aggregations over local stores", "deferred export policy for broad reports"],
            "operations": ["no external integrations", "no production deploy", "local backup evidence only"],
            "deployment": ["docker compose", "aws ec2 runbook", "nginx reverse proxy", "tls placeholders", "backup restore", "rollback"],
        },
    }


def _hito_008_blueprint() -> dict[str, Any]:
    base = copy.deepcopy(_hito_007_blueprint())
    base["blueprint_id"] = "brewmaster.sdd.hito8.v1"
    base["milestone_id"] = "HITO-008"
    base["milestone_name"] = "Pantallas interactivas"
    base["scope"] = {
        "source": "J.12 Hito 8",
        "includes": [
            "HITO-001 a HITO-007 conservados sin degradacion",
            "30 pantallas React + Bootstrap separadas y navegables",
            "estados de carga, error y vacio por pantalla",
            "validacion cliente en formularios operativos",
            "navegacion entre pantallas relacionadas",
            "cliente frontend local conectado a endpoints /api/v1 aprobados",
            "sin endpoints backend nuevos",
            "sin deploy real",
            "sin secretos reales ni integraciones externas nuevas",
        ],
        "deferred_milestones": [],
        "explicitly_excluded_paths": [],
    }
    base["factory_controls"] = {
        **base["factory_controls"],
        "hito8_backend_changes": "denied; frontend consumes approved HITO-007 /api/v1 contract only",
        "frontend_contract": "React + Bootstrap with Vite entrypoints frontend/index.html and frontend/src/main.jsx",
    }
    base["transactional_rules"] = [
        *base["transactional_rules"],
        "frontend_actions_use_existing_api_v1_endpoints_only",
        "all_declared_screens_render_loading_error_empty_and_data_states",
    ]
    base["non_functional"] = {
        **base["non_functional"],
        "frontend": [
            "Vite build required",
            "responsive Bootstrap layout",
            "hash navigation for all P-01..P-30 routes",
            "no generic placeholder screens",
        ],
    }
    return base


def brewmaster_blueprint(milestone_id: str | None = None) -> dict[str, Any]:
    if _is_hito_001(milestone_id):
        return _hito_001_blueprint()
    if _is_hito_002(milestone_id):
        return _hito_002_blueprint()
    if _is_hito_003(milestone_id):
        return _hito_003_blueprint()
    if _is_hito_004(milestone_id):
        return _hito_004_blueprint()
    if _is_hito_005(milestone_id):
        return _hito_005_blueprint()
    if _is_hito_006(milestone_id):
        return _hito_006_blueprint()
    if _is_hito_007(milestone_id):
        return _hito_007_blueprint()
    if _is_hito_008(milestone_id):
        return _hito_008_blueprint()
    spec = load_brewmaster_spec()
    endpoints = spec.endpoints
    entity_models = spec.entities
    entities = [entity["name"] for entity in entity_models]
    return {
        "blueprint_id": "brewmaster.sdd.mvp.v1",
        "source_spec": spec.source_path,
        "spec_model": {
            "parsed": spec.parsed,
            "use_case_count": len(spec.use_cases),
            "business_rule_count": len(spec.business_rules),
            "validation_count": len(spec.validations),
            "permission_count": len(spec.permissions),
            "non_functional_count": len(spec.non_functional),
        },
        "architecture_source": "fabricas_agentes_ia.md",
        "stack": {
            "frontend": "React + Bootstrap",
            "backend": "Python 3 + FastAPI",
            "orm": "SQLAlchemy + Alembic",
            "database": "MySQL or MariaDB",
            "jobs": "APScheduler",
            "auth": "JWT with refresh token",
            "reports": ["CSV", "XLSX", "PDF"],
            "deployment": "Docker Compose on AWS EC2 single VM",
        },
        "factory_controls": {
            "entrypoint": "harness.run_agent(agent_id, state)",
            "side_effects": "all generated implementation files pass through DEV sandbox materializer",
            "production_deploy": "allowed only with approved_deploy WorkOrder, human approval, rollback and evidence",
            "context": "authorized specification and architecture sources only",
            "memory": "project scoped propose-only memory",
            "gates": ["schema", "budget", "project_isolation", "frontend_template", "sandbox", "tests", "security", "coverage"],
            "determinism": "local deterministic generation, no external cost",
        },
        "modules": spec.modules,
        "screens": spec.screens,
        "entities": entities,
        "entity_models": entity_models,
        "endpoints": endpoints,
        "validations": spec.validations,
        "permissions": spec.permissions,
        "business_rules": spec.business_rules,
        "transactional_rules": [
            "complete_batch_validates_stock_consumes_supplies_creates_finished_product_and_calculates_cost_atomically",
            "supply_entry_updates_stock_and_kardex_atomically",
            "sale_validates_available_stock_decrements_inventory_and_writes_kardex_atomically",
            "purchase_order_receive_generates_supply_entry_and_updates_order_atomically",
            "reservation_uses_current_stock_minus_active_reservations",
            "waste_record_decrements_inventory_and_writes_kardex_atomically",
            "email_alerts_are_enqueued_and_retried_asynchronously",
            "state_change_actions_are_idempotent_or_reject_current_state_conflict",
        ],
        "non_functional": {
            "source_requirements": spec.non_functional,
            "security": ["bcrypt", "expiring JWT", "RBAC on every endpoint"],
            "audit": "100 percent critical writes include actor, date, entity, action and IP",
            "performance": ["paginated listings", "SQL aggregations for dashboard", "background heavy exports"],
            "observability": ["request_id", "user_id", "module", "latency", "structured logs"],
            "privacy": ["financial data hidden without permission", "SMTP credential encrypted at rest"],
            "deployment": ["docker compose", "aws ec2", "reverse proxy", "healthchecks", "backup restore", "rollback"],
        },
    }

def brewmaster_coverage(milestone_id: str | None = None) -> dict[str, Any]:
    blueprint = brewmaster_blueprint(milestone_id)
    modules = blueprint["modules"]
    screens = blueprint["screens"]
    endpoints = blueprint["endpoints"]
    entities = blueprint["entities"]
    validations = blueprint.get("validations", [])
    if blueprint.get("milestone_id") == "HITO-001":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        acceptance_gate = {
            "is_hito_001_scope": blueprint.get("milestone_id") == "HITO-001",
            "has_only_foundation_module": {module["id"] for module in modules} == {"MOD-001"},
            "has_foundation_screens": {screen["id"] for screen in screens} == HITO_001_SCREEN_IDS,
            "has_hito1_endpoints": endpoint_paths
            == {endpoint["path"] for endpoint in HITO_001_ENDPOINTS},
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_security_entities": set(entities) == HITO_001_ENTITY_NAMES,
            "has_v001_v024": {item["id"] for item in validations} == HITO_001_VALIDATION_IDS,
            "has_hito1_permissions": set(blueprint.get("permissions", [])) == HITO_001_PERMISSION_CODES,
            "defers_future_modules": bool(blueprint.get("scope", {}).get("deferred_milestones")),
            "no_future_endpoint_paths": not any(
                fragment in path
                for path in endpoint_paths
                for fragment in [
                    "/suppliers",
                    "/supplies",
                    "/recipes",
                    "/batches",
                    "/products",
                    "/sales",
                    "/customers",
                    "/purchase-orders",
                    "/equipment",
                    "/expenses",
                    "/reports/export",
                    "/settings/smtp",
                    "/monthly-goals",
                ]
            ),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-001",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-002":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        excluded_fragments = {
            "/api/v1/supply-entries",
            "/api/v1/supplies/{id}/kardex",
            "/api/v1/supplies/low-stock",
            "/api/v1/batches",
            "/api/v1/products",
            "/api/v1/sales",
            "/api/v1/customers",
            "/api/v1/purchase-orders",
            "/api/v1/reports",
            "/api/v1/settings/smtp",
            "/api/v1/equipment",
            "/api/v1/expenses",
            "/api/v1/monthly-goals",
        }
        required_paths = {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}
        acceptance_gate = {
            "is_hito_002_scope": blueprint.get("milestone_id") == "HITO-002",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "has_hito2_master_endpoints": required_paths.issubset(endpoint_paths),
            "has_exact_hito2_endpoint_count": len(endpoints) == len(HITO_002_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito2_screens_only": {screen["id"] for screen in screens} == HITO_002_SCREEN_IDS,
            "has_hito2_entities_only": set(entities) == HITO_002_ENTITY_NAMES,
            "has_hito2_validations": {item["id"] for item in validations} == HITO_002_VALIDATION_IDS,
            "has_hito2_permissions": set(blueprint.get("permissions", [])) == HITO_002_PERMISSION_CODES,
            "defers_future_modules": bool(blueprint.get("scope", {}).get("deferred_milestones")),
            "no_hito3_or_later_endpoint_paths": not endpoint_paths.intersection(excluded_fragments),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-002",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-003":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        excluded_fragments = {
            "/api/v1/batches",
            "/api/v1/products",
            "/api/v1/sales",
            "/api/v1/customers",
            "/api/v1/purchase-orders",
            "/api/v1/reports",
            "/api/v1/equipment",
            "/api/v1/expenses",
            "/api/v1/monthly-goals",
            "/api/v1/dashboard",
        }
        required_paths = {endpoint["path"] for endpoint in HITO_003_ENDPOINTS}
        acceptance_gate = {
            "is_hito_003_scope": blueprint.get("milestone_id") == "HITO-003",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_002_master_endpoints": {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}.issubset(endpoint_paths),
            "has_hito3_inventory_and_smtp_endpoints": required_paths.issubset(endpoint_paths),
            "has_exact_hito3_endpoint_count": len(endpoints) == len(HITO_003_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito3_screens_only": {screen["id"] for screen in screens} == HITO_003_SCREEN_IDS,
            "has_hito3_entities_only": set(entities) == HITO_003_ENTITY_NAMES,
            "has_hito3_validations": {item["id"] for item in validations} == HITO_003_VALIDATION_IDS,
            "has_hito3_permissions": set(blueprint.get("permissions", [])) == HITO_003_PERMISSION_CODES,
            "defers_future_modules": bool(blueprint.get("scope", {}).get("deferred_milestones")),
            "no_hito4_or_later_endpoint_paths": not endpoint_paths.intersection(excluded_fragments),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-003",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-004":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        excluded_fragments = {
            "/api/v1/sales",
            "/api/v1/customers",
            "/api/v1/reservations",
            "/api/v1/purchase-orders",
            "/api/v1/reports",
            "/api/v1/equipment",
            "/api/v1/expenses",
            "/api/v1/monthly-goals",
            "/api/v1/dashboard",
        }
        required_paths = {endpoint["path"] for endpoint in HITO_004_ENDPOINTS}
        acceptance_gate = {
            "is_hito_004_scope": blueprint.get("milestone_id") == "HITO-004",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_002_master_endpoints": {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_003_inventory_smtp_endpoints": {endpoint["path"] for endpoint in HITO_003_ENDPOINTS}.issubset(endpoint_paths),
            "has_hito4_production_product_waste_endpoints": required_paths.issubset(endpoint_paths),
            "has_exact_hito4_endpoint_count": len(endpoints) == len(HITO_004_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito4_screens_only": {screen["id"] for screen in screens} == HITO_004_SCREEN_IDS,
            "has_hito4_entities_only": set(entities) == HITO_004_ENTITY_NAMES,
            "has_hito4_validations": {item["id"] for item in validations} == HITO_004_VALIDATION_IDS,
            "has_hito4_permissions": set(blueprint.get("permissions", [])) == HITO_004_PERMISSION_CODES,
            "defers_future_modules": bool(blueprint.get("scope", {}).get("deferred_milestones")),
            "no_hito5_or_later_endpoint_paths": not endpoint_paths.intersection(excluded_fragments),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-004",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-005":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        excluded_fragments = {
            "/api/v1/reports",
            "/api/v1/reports/export",
            "/api/v1/equipment",
            "/api/v1/expenses",
            "/api/v1/monthly-goals",
            "/api/v1/dashboard",
            "/api/v1/jobs",
            "/api/v1/backups",
        }
        required_paths = {endpoint["path"] for endpoint in HITO_005_ENDPOINTS}
        acceptance_gate = {
            "is_hito_005_scope": blueprint.get("milestone_id") == "HITO-005",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_002_master_endpoints": {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_003_inventory_smtp_endpoints": {endpoint["path"] for endpoint in HITO_003_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_004_production_endpoints": {endpoint["path"] for endpoint in HITO_004_ENDPOINTS}.issubset(endpoint_paths),
            "has_hito5_sales_purchase_endpoints": required_paths.issubset(endpoint_paths),
            "has_exact_hito5_endpoint_count": len(endpoints) == len(HITO_005_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito5_screens_only": {screen["id"] for screen in screens} == HITO_005_SCREEN_IDS,
            "has_hito5_entities_only": set(entities) == HITO_005_ENTITY_NAMES,
            "has_hito5_validations": {item["id"] for item in validations} == HITO_005_VALIDATION_IDS,
            "has_hito5_permissions": set(blueprint.get("permissions", [])) == HITO_005_PERMISSION_CODES,
            "defers_future_modules": bool(blueprint.get("scope", {}).get("deferred_milestones")),
            "no_hito6_or_hito7_endpoint_paths": not endpoint_paths.intersection(excluded_fragments),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-005",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-006":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        excluded_fragments = {
            "/api/v1/equipment",
            "/api/v1/expenses",
            "/api/v1/monthly-goals",
            "/api/v1/jobs",
            "/api/v1/backups",
        }
        required_paths = {endpoint["path"] for endpoint in HITO_006_ENDPOINTS}
        acceptance_gate = {
            "is_hito_006_scope": blueprint.get("milestone_id") == "HITO-006",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_002_master_endpoints": {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_003_inventory_smtp_endpoints": {endpoint["path"] for endpoint in HITO_003_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_004_production_endpoints": {endpoint["path"] for endpoint in HITO_004_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_005_sales_purchase_endpoints": {endpoint["path"] for endpoint in HITO_005_ENDPOINTS}.issubset(endpoint_paths),
            "has_hito6_dashboard_report_endpoints": required_paths.issubset(endpoint_paths),
            "has_exact_hito6_endpoint_count": len(endpoints) == len(HITO_006_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito6_screens_only": {screen["id"] for screen in screens} == HITO_006_SCREEN_IDS,
            "has_hito6_entities_only": set(entities) == HITO_006_ENTITY_NAMES,
            "has_hito6_validations": {item["id"] for item in validations} == HITO_006_VALIDATION_IDS,
            "has_hito6_permissions": set(blueprint.get("permissions", [])) == HITO_006_PERMISSION_CODES,
            "defers_hito7_modules": blueprint.get("scope", {}).get("deferred_milestones") == ["HITO-007"],
            "no_hito7_endpoint_paths": not endpoint_paths.intersection(excluded_fragments),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-006",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-007":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        required_paths = {endpoint["path"] for endpoint in HITO_007_ENDPOINTS}
        acceptance_gate = {
            "is_hito_007_scope": blueprint.get("milestone_id") == "HITO-007",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_002_master_endpoints": {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_003_inventory_smtp_endpoints": {endpoint["path"] for endpoint in HITO_003_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_004_production_endpoints": {endpoint["path"] for endpoint in HITO_004_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_005_sales_purchase_endpoints": {endpoint["path"] for endpoint in HITO_005_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_006_dashboard_report_endpoints": {endpoint["path"] for endpoint in HITO_006_ENDPOINTS}.issubset(endpoint_paths),
            "has_hito7_equipment_finance_goals_backup_endpoints": required_paths.issubset(endpoint_paths),
            "has_exact_hito7_endpoint_count": len(endpoints) == len(HITO_007_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito7_all_screens": {screen["id"] for screen in screens} == HITO_007_SCREEN_IDS,
            "has_hito7_entities": set(entities) == HITO_007_ENTITY_NAMES,
            "has_v001_v100": {item["id"] for item in validations} == HITO_007_VALIDATION_IDS,
            "has_hito7_permissions": set(blueprint.get("permissions", [])) == HITO_007_PERMISSION_CODES,
            "has_no_deferred_scope": not blueprint.get("scope", {}).get("deferred_milestones"),
            "no_catch_all_endpoint_paths": not any("{resource}" in path for path in endpoint_paths),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-007",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    if blueprint.get("milestone_id") == "HITO-008":
        endpoint_paths = {endpoint["path"] for endpoint in endpoints}
        required_paths = {endpoint["path"] for endpoint in HITO_007_ENDPOINTS}
        acceptance_gate = {
            "is_hito_008_scope": blueprint.get("milestone_id") == "HITO-008",
            "preserves_hito_001_endpoints": {endpoint["path"] for endpoint in HITO_001_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_002_master_endpoints": {endpoint["path"] for endpoint in HITO_002_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_003_inventory_smtp_endpoints": {endpoint["path"] for endpoint in HITO_003_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_004_production_endpoints": {endpoint["path"] for endpoint in HITO_004_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_005_sales_purchase_endpoints": {endpoint["path"] for endpoint in HITO_005_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_006_dashboard_report_endpoints": {endpoint["path"] for endpoint in HITO_006_ENDPOINTS}.issubset(endpoint_paths),
            "preserves_hito_007_close_endpoints": required_paths.issubset(endpoint_paths),
            "has_hito8_no_new_backend_endpoint_count": len(endpoints) == len(HITO_007_ENDPOINTS),
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_hito8_all_screens": {screen["id"] for screen in screens} == HITO_008_SCREEN_IDS,
            "has_hito8_entities": set(entities) == HITO_008_ENTITY_NAMES,
            "has_v001_v100": {item["id"] for item in validations} == HITO_008_VALIDATION_IDS,
            "has_hito8_permissions": set(blueprint.get("permissions", [])) == HITO_008_PERMISSION_CODES,
            "has_no_deferred_scope": not blueprint.get("scope", {}).get("deferred_milestones"),
            "no_catch_all_endpoint_paths": not any("{resource}" in path for path in endpoint_paths),
        }
        return {
            "status": "pass" if all(acceptance_gate.values()) else "partial",
            "milestone_id": "HITO-008",
            "module_count": len(modules),
            "screen_count": len(screens),
            "endpoint_count": len(endpoints),
            "entity_count": len(entities),
            "validation_count": len(validations),
            "permission_count": len(blueprint.get("permissions", [])),
            "critical_transaction_count": len(blueprint["transactional_rules"]),
            "module_coverage": {module["id"]: module["acceptance"] for module in modules},
            "screen_ids": [screen["id"] for screen in screens],
            "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
            "acceptance_gate": acceptance_gate,
        }
    return {
        "status": "pass"
        if len(screens) == 30 and len(endpoints) == 40 and len(validations) == 100
        else "partial",
        "module_count": len(modules),
        "screen_count": len(screens),
        "endpoint_count": len(endpoints),
        "entity_count": len(entities),
        "validation_count": len(validations),
        "permission_count": len(blueprint.get("permissions", [])),
        "critical_transaction_count": len(blueprint["transactional_rules"]),
        "module_coverage": {module["id"]: module["acceptance"] for module in modules},
        "screen_ids": [screen["id"] for screen in screens],
        "action_endpoints": [endpoint for endpoint in endpoints if endpoint.get("action_endpoint")],
        "acceptance_gate": {
            "has_30_screens": len(screens) == 30,
            "has_40_spec_endpoints": len(endpoints) == 40,
            "has_v001_v100": len(validations) == 100 and {item["id"] for item in validations} == {f"V{index:03d}" for index in range(1, 101)},
            "has_all_macro_requirements": {module["id"] for module in modules}
            >= {"REQ-INS", "REQ-REC", "REQ-PROD", "REQ-PRO", "REQ-VTA", "REQ-COM", "REQ-EQU", "REQ-FIN", "REQ-REP", "REQ-ALT"},
            "has_api_v1": all(endpoint["path"].startswith("/api/v1") for endpoint in endpoints),
            "has_transactional_rules": len(blueprint["transactional_rules"]) >= 8,
        },
    }
