from __future__ import annotations

import json
from textwrap import dedent
from typing import Any

from .brewmaster_spec import BREWMASTER_MODULES, load_brewmaster_spec

def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True)

def _readme() -> str:
    return dedent(
        """
        # BrewMaster MVP

        Implementacion base generada por WEBFORGE para el sistema web de gestion de cervecerias artesanales.

        El alcance cubre autenticacion JWT, RBAC, auditoria, insumos, proveedores, recetas, produccion,
        calidad, mermas, inventario de productos terminados, ventas, reservas, compras, equipos, finanzas,
        dashboard, reportes y alertas por correo.

        Todas las rutas de API viven bajo `/api/v1`, las eliminaciones son logicas y las acciones de cambio
        de estado usan endpoints explicitos como `POST /api/v1/batches/{id}/complete`.
        """
    ).strip()

def _architecture_md() -> str:
    return dedent(
        """
        # Arquitectura BrewMaster

        Capas:

        - Frontend React + Bootstrap con rutas protegidas por rol, formularios validados, tablas paginadas y estados de carga, vacio y error.
        - API REST FastAPI bajo `/api/v1`, respuestas JSON uniformes, RBAC por accion y `request_id` en cada respuesta.
        - Dominio con servicios puros para stock, costo, ventas, compras, mermas y alertas.
        - Persistencia SQLAlchemy/Alembic orientada a MySQL o MariaDB con indices y soft delete.
        - Jobs APScheduler para alertas de stock, reintentos de correo, reservas vencidas, exportaciones y backups.
        - Observabilidad con logs estructurados, auditoria funcional y metricas por modulo.

        Controles de fabrica:

        - Workflow antes que agentes: los archivos se producen como bundle cerrado y verificable.
        - Arnes como frontera: la escritura ocurre solo por el materializador DEV.
        - Permiso minimo: no hay deploy, secretos ni datos reales.
        - Trazabilidad: `contracts/coverage.json` mapea modulos, pantallas, endpoints y reglas transaccionales.
        """
    ).strip()

def _api_contract_md(blueprint: dict[str, Any]) -> str:
    rows = ["# API contract", "", "Respuesta exitosa: `{\"data\": {}, \"meta\": {\"request_id\": \"REQ-TBD\"}}`.", "", "| method | path | handler |", "|---|---|---|"]
    for endpoint in blueprint["endpoints"]:
        rows.append(f"| {endpoint['method']} | `{endpoint['path']}` | `{endpoint['handler']}` |")
    return "\n".join(rows)

def _traceability_md() -> str:
    rows = ["# Trazabilidad macro", "", "| requisito | evidencia generada | prueba |", "|---|---|---|"]
    for module in BREWMASTER_MODULES:
        rows.append(f"| {module['id']} {module['name']} | contracts/coverage.json, app/domain/catalog.py | unit + integration + E2E |")
    return "\n".join(rows)

def _test_strategy_md() -> str:
    return dedent(
        """
        # Estrategia de pruebas

        Unitarias:

        - Validaciones V001 a V100 como reglas puras por servicio.
        - Costo de lote, costo por litro, costo por unidad y costo de presentacion.
        - Stock disponible como stock actual menos reservas activas.
        - Alertas de stock bajo con intervalo de 24 horas y prioridad de stock cero.
        - Transiciones de estado en lotes, ordenes de compra y reservas.

        Integracion:

        - Entrada de insumo actualiza stock y Kardex en la misma transaccion.
        - Completar lote consume insumos, crea producto terminado y calcula costo.
        - Venta descuenta inventario de productos y registra Kardex.
        - Recepcion de compra genera entrada de inventario y actualiza estado.
        - Worker de correo reintenta y marca error definitivo tras 5 intentos.

        E2E:

        - Login, crear insumo, registrar entrada y verificar Kardex.
        - Crear receta, crear lote, completar lote y verificar producto terminado.
        - Registrar venta y verificar stock y Kardex.
        - Crear orden de compra, recepcionar y verificar stock.
        - Exportar reporte de produccion a XLSX con filtro de fechas.
        """
    ).strip()

def _permissions() -> dict[str, Any]:
    declared_permissions = load_brewmaster_spec().permissions
    return {
        "declared_permissions": declared_permissions,
        "roles": {
            "admin": ["*"],
            "compras": ["supplies:*", "suppliers:*", "purchase-orders:*", "reports:inventory"],
            "produccion": ["recipes:*", "batches:*", "quality:*", "waste:*", "equipment:*"],
            "ventas": ["customers:*", "sales:*", "reservations:*", "finished-products:read"],
            "finanzas": ["expenses:*", "reports:financial", "monthly-goals:read"],
            "auditor": ["audit:read", "reports:audit"],
        },
        "sensitive_permissions": ["costs:read", "financial:read", "smtp:update", "users:write"],
    }
