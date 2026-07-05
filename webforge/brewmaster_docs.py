from __future__ import annotations

import json
from textwrap import dedent
from typing import Any

from .brewmaster_spec import BREWMASTER_MODULES, load_brewmaster_spec

def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True)

def _is_hito_001(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-001")


def _readme(blueprint: dict[str, Any] | None = None) -> str:
    if _is_hito_001(blueprint):
        return dedent(
            """
            # BrewMaster HITO-001 Fundamentos

            Implementacion incremental generada por WEBFORGE para el primer hito de BrewMaster.

            Alcance implementado: autenticacion JWT local, usuarios, roles, permisos, recuperacion/cambio de
            contrasena, auditoria funcional y estructura base React + Bootstrap / FastAPI bajo `/api/v1`.

            Alcance diferido: proveedores, insumos, bodegas, recetas, inventario, produccion, ventas, compras,
            dashboard, finanzas, reportes exportables, SMTP y jobs operativos.
            """
        ).strip()
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

def _architecture_md(blueprint: dict[str, Any] | None = None) -> str:
    if _is_hito_001(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-001

            Capas:

            - Frontend React + Bootstrap limitado a login, recuperacion de contrasena y panel de usuarios/auditoria.
            - API REST FastAPI bajo `/api/v1` con respuesta JSON uniforme y `request_id`.
            - Seguridad local con hash PBKDF2, JWT HS256 expirable y RBAC por rol.
            - Persistencia contractual SQLAlchemy/Alembic acotada a usuarios, roles, permisos, auditoria y tokens de restablecimiento.
            - Auditoria funcional en memoria para el MVP local del hito, sin datos reales ni escrituras externas.

            Controles de fabrica:

            - El bundle se materializa solo por el arnes P12/INV en el sandbox DEV.
            - La promocion a QA ocurre despues de validadores y gate incremental.
            - Los modulos de hitos posteriores quedan explicitamente diferidos y no exponen endpoints ejecutables.
            """
        ).strip()
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

def _traceability_md(blueprint: dict[str, Any] | None = None) -> str:
    if _is_hito_001(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-001",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| J.12 Hito 1 Fundamentos | backend/app/main.py, backend/app/core/security.py, contracts/permissions.json | tests/test_auth_foundation.py |",
                "| FUN-001 Autenticar usuario | /api/v1/auth/login, /api/v1/auth/me | login valido, invalido e inactivo |",
                "| FUN-002 Recuperar contrasena | /api/v1/auth/password-reset/request, /api/v1/auth/password-reset/confirm | token local de un uso |",
                "| FUN-003 Gestionar usuarios roles permisos | /api/v1/users* | admin requerido, correo unico, rol activo |",
                "| FUN-004 Registrar auditoria funcional | /api/v1/audit-logs | eventos de login, usuarios y contrasena |",
                "| FUN-038 RBAC por endpoint | core/security.py | 401/403 sin datos parciales |",
            ]
        )
    rows = ["# Trazabilidad macro", "", "| requisito | evidencia generada | prueba |", "|---|---|---|"]
    for module in BREWMASTER_MODULES:
        rows.append(f"| {module['id']} {module['name']} | contracts/coverage.json, app/domain/catalog.py | unit + integration + E2E |")
    return "\n".join(rows)

def _test_strategy_md(blueprint: dict[str, Any] | None = None) -> str:
    if _is_hito_001(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-001

            Unitarias:

            - Hash de contrasena PBKDF2 no almacena texto plano.
            - JWT HS256 expirable rechaza firma alterada o vencida.
            - `require_permission` acepta comodin admin y bloquea permiso ausente.

            Integracion local:

            - Login exitoso retorna JWT y `auth/me` responde con usuario activo.
            - Credenciales invalidas o usuario inactivo retornan HTTP 401 y generan auditoria.
            - Usuario no admin recibe HTTP 403 al listar usuarios.
            - Admin crea usuario con correo unico y rol activo; duplicado se rechaza.
            - Cambio y restablecimiento de contrasena actualizan hash y auditan.
            - Auditor o admin consulta `/api/v1/audit-logs`; otros roles no reciben datos parciales.
            """
        ).strip()
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

def _permissions(blueprint: dict[str, Any] | None = None) -> dict[str, Any]:
    declared_permissions = blueprint.get("permissions", []) if blueprint else load_brewmaster_spec().permissions
    if _is_hito_001(blueprint):
        return {
            "milestone_id": "HITO-001",
            "declared_permissions": declared_permissions,
            "roles": {
                "admin": ["*"],
                "auditor": ["audit.read"],
                "operador": [],
            },
            "sensitive_permissions": ["admin.users", "audit.read"],
            "deferred_permissions": [
                permission
                for permission in load_brewmaster_spec().permissions
                if permission not in set(declared_permissions)
            ],
        }
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
