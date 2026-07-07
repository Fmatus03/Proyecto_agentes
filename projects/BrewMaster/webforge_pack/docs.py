from __future__ import annotations

import json
from textwrap import dedent
from typing import Any

from .spec import BREWMASTER_MODULES, load_brewmaster_spec

def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True)

def _is_hito_001(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-001")


def _is_hito_002(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-002")


def _is_hito_003(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-003")


def _is_hito_004(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-004")


def _is_hito_005(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-005")


def _is_hito_006(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-006")


def _is_hito_007(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-007")


def _is_hito_008(blueprint: dict[str, Any] | None = None) -> bool:
    return bool(blueprint and blueprint.get("milestone_id") == "HITO-008")


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
    if _is_hito_002(blueprint):
        return dedent(
            """
            # BrewMaster HITO-002 Maestros

            Implementacion incremental generada por WEBFORGE sobre HITO-001.

            Alcance conservado: autenticacion JWT local, usuarios, roles, permisos, recuperacion/cambio de
            contrasena, auditoria funcional y estructura base React + Bootstrap / FastAPI bajo `/api/v1`.

            Alcance nuevo: proveedores, insumos maestros, bodegas, recetas con ingredientes activos y tipos de
            presentacion. Los cambios criticos quedan auditados y los contratos permanecen derivados de la
            especificacion oficial.

            Alcance diferido: entradas de insumos, Kardex operativo, alertas email/SMTP, produccion, ventas,
            compras, dashboard, reportes, equipos, finanzas y jobs.
            """
        ).strip()
    if _is_hito_003(blueprint):
        return dedent(
            """
            # BrewMaster HITO-003 Inventario

            Implementacion incremental generada por WEBFORGE sobre HITO-002.

            Alcance conservado: autenticacion JWT local, usuarios, roles, permisos, auditoria, proveedores,
            insumos maestros, bodegas, recetas y tipos de presentacion.

            Alcance nuevo: entradas de insumos, Kardex operativo de insumos, listado de bajo stock,
            cola local de notificaciones, reglas de intervalo de alerta y configuracion SMTP sanitizada.

            Seguridad SMTP: no se envian correos reales, no se usan credenciales reales y la prueba SMTP queda
            registrada como entrega mock local. Produccion, ventas, compras, dashboard, reportes, backups y
            deploy EC2 quedan diferidos.
            """
        ).strip()
    if _is_hito_004(blueprint):
        return dedent(
            """
            # BrewMaster HITO-004 Produccion

            Implementacion incremental generada por WEBFORGE sobre HITO-003.

            Alcance conservado: autenticacion JWT local, usuarios, roles, permisos, auditoria, proveedores,
            insumos, bodegas, recetas, tipos de presentacion, entradas, Kardex, alertas, cola local y SMTP
            sanitizado sin envio externo.

            Alcance nuevo: lotes de produccion, completar lote con descuento de insumos, costo calculado,
            control de calidad unico, mermas de insumos/productos e inventario de productos terminados.

            Alcance diferido: ventas, clientes, reservas, compras, dashboard, reportes exportables, equipos,
            finanzas, metas mensuales, respaldos automaticos, dockerizacion productiva y deploy EC2.
            """
        ).strip()
    if _is_hito_005(blueprint):
        return dedent(
            """
            # BrewMaster HITO-005 Ventas y compras

            Implementacion incremental generada por WEBFORGE sobre HITO-004.

            Alcance conservado: fundamentos, maestros, inventario, Kardex, alertas/SMTP local seguro,
            produccion, lotes, calidad, mermas e inventario de productos terminados.

            Alcance nuevo: clientes, tipos de cliente, precios por tipo, ventas, anulacion de ventas,
            reservas de stock, ordenes de compra y recepcion parcial o total con entrada de insumos.

            Alcance diferido: dashboard, reportes exportables, equipos, finanzas, metas mensuales,
            respaldos automaticos, dockerizacion productiva, EC2, proxy/TLS y deploy productivo.
            """
        ).strip()
    if _is_hito_006(blueprint):
        return dedent(
            """
            # BrewMaster HITO-006 Dashboard y reportes

            Implementacion incremental generada por WEBFORGE sobre HITO-005.

            Alcance conservado: fundamentos, maestros, inventario, Kardex, SMTP local seguro, produccion,
            calidad, mermas, productos terminados, clientes, ventas, reservas, precios por tipo de cliente,
            compras y ordenes de compra.

            Alcance nuevo: dashboard general, KPIs reales desde stores operacionales, graficos, alertas
            operacionales, reportes operacionales exportables en CSV/XLSX/PDF y jobs locales de alertas,
            reintentos, vencimiento de reservas y exportaciones diferidas.

            Alcance diferido: equipos, finanzas, metas mensuales, respaldos automaticos, dockerizacion
            productiva, EC2, proxy/TLS y deploy productivo.
            """
        ).strip()
    if _is_hito_007(blueprint):
        return dedent(
            """
            # BrewMaster HITO-007 Cierre

            Implementacion incremental generada por WEBFORGE sobre HITO-006.

            Alcance conservado: fundamentos, maestros, inventario, Kardex, SMTP local seguro, produccion,
            calidad, mermas, productos terminados, clientes, ventas, reservas, precios por tipo de cliente,
            compras, dashboard, KPIs, alertas operacionales, reportes exportables y scheduler HITO-006.

            Alcance nuevo: equipos con historial y alertas de revision, gastos operativos, reportes financieros,
            metas mensuales, respaldos automaticos locales, Docker Compose productivo, proxy Nginx y documentacion
            de despliegue EC2/TLS. No se ejecuta deploy real ni se usan secretos reales.
            """
        ).strip()
    if _is_hito_008(blueprint):
        return dedent(
            """
            # BrewMaster HITO-008 Pantallas interactivas

            Implementacion incremental generada por WEBFORGE sobre HITO-007.

            Alcance conservado: fundamentos, maestros, inventario, Kardex, SMTP local seguro, produccion,
            lotes, calidad, mermas, productos terminados, clientes, ventas, reservas, precios por tipo de
            cliente, compras, dashboard, reportes, scheduler, equipos, finanzas, metas, respaldos locales,
            Docker Compose, proxy Nginx y documentacion EC2/TLS.

            Alcance nuevo: las 30 pantallas P-01..P-30 quedan como vistas React + Bootstrap separadas,
            navegables, responsivas y conectadas a endpoints `/api/v1` ya aprobados. No se crean endpoints
            backend nuevos, no se ejecuta deploy real, no se usan secretos reales ni integraciones externas.
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
    if _is_hito_002(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-002

            Capas:

            - Frontend React + Bootstrap con vistas de seguridad HITO-001 y maestros HITO-002.
            - API REST FastAPI bajo `/api/v1` con respuesta JSON uniforme y `request_id`.
            - Seguridad local acumulativa con hash PBKDF2, JWT HS256 expirable y RBAC por rol.
            - Persistencia contractual SQLAlchemy/Alembic acotada a fundamentos y maestros.
            - Dominio de maestros en memoria para el MVP local: proveedores, bodegas, insumos, recetas e ingredientes.

            Limites del hito:

            - `supply_entries`, Kardex operativo, colas de notificacion, SMTP y jobs quedan diferidos.
            - Produccion, ventas, compras, dashboard, reportes, equipos y finanzas no exponen endpoints ejecutables.
            - El bundle se materializa solo por el arnes P12/INV en DEV y se promueve a QA despues de validadores.
            """
        ).strip()
    if _is_hito_003(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-003

            Capas:

            - Frontend React + Bootstrap con vistas acumuladas de seguridad, maestros e inventario.
            - API REST FastAPI bajo `/api/v1` con respuesta JSON uniforme y `request_id`.
            - Seguridad local acumulativa con hash PBKDF2, JWT HS256 expirable y RBAC por rol.
            - Persistencia contractual SQLAlchemy/Alembic acotada a fundamentos, maestros, Kardex, cola y SMTP.
            - Dominio de inventario en memoria para el MVP local: entradas, movimientos, bajo stock y cola.
            - SMTP local mock: configuracion sanitizada, secreto no expuesto y prueba sin red ni correo real.

            Limites del hito:

            - Produccion, lotes, calidad, mermas, productos terminados, ventas, clientes, compras, dashboard,
              reportes, equipos, finanzas, backups y dockerizacion/deploy productivo no exponen endpoints ejecutables.
            - No hay scheduler operativo; la cola y reintentos se prueban con servicios puros y mocks locales.
            - El bundle se materializa solo por el arnes P12/INV en DEV y se promueve a QA despues de validadores.
            """
        ).strip()
    if _is_hito_004(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-004

            Capas:

            - Frontend React + Bootstrap con vistas acumuladas de seguridad, maestros, inventario y produccion.
            - API REST FastAPI bajo `/api/v1` con respuesta JSON uniforme y `request_id`.
            - Seguridad local acumulativa con hash PBKDF2, JWT HS256 expirable y RBAC por rol.
            - Persistencia contractual SQLAlchemy/Alembic acotada a fundamentos, maestros, inventario, SMTP,
              lotes, calidad, mermas y productos terminados.
            - Dominio de produccion en memoria para el MVP local: completar lote descuenta insumos,
              registra snapshots/Kardex y crea o incrementa producto terminado.

            Limites del hito:

            - Ventas, clientes, reservas, compras, dashboard, reportes exportables, equipos, finanzas,
              metas mensuales, respaldos automaticos y deploy productivo no exponen endpoints ejecutables.
            - SMTP sigue siendo mock local de HITO-003; no hay envio real ni integracion externa.
            - El bundle se materializa solo por el arnes P12/INV en DEV y se promueve a QA despues de validadores.
            """
        ).strip()
    if _is_hito_005(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-005

            Capas:

            - Frontend React + Bootstrap con vistas acumuladas hasta produccion mas clientes, ventas, reservas y compras.
            - API REST FastAPI bajo `/api/v1` con respuesta JSON uniforme y `request_id`.
            - Seguridad local acumulativa con hash PBKDF2, JWT HS256 expirable y RBAC por rol.
            - Persistencia contractual SQLAlchemy/Alembic acotada a fundamentos, maestros, inventario, SMTP,
              produccion, productos terminados, clientes, ventas, reservas y ordenes de compra.
            - Dominio comercial local en memoria: ventas descuentan producto terminado y reservas bloquean stock libre.
            - Dominio de compras local en memoria: recepcion de orden genera entrada de insumo y Kardex ENTRADA.

            Limites del hito:

            - Dashboard, reportes exportables, equipos, finanzas, metas mensuales, respaldos automaticos,
              dockerizacion productiva, proxy/TLS y deploy EC2 no exponen endpoints ejecutables.
            - SMTP sigue siendo mock local de HITO-003; no hay correo real, pasarela de pago ni integracion externa.
            - El bundle se materializa solo por el arnes P12/INV en DEV y se promueve a QA despues de validadores.
            """
        ).strip()
    if _is_hito_006(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-006

            Capas:

            - FastAPI conserva los stores locales acumulados HITO-001..HITO-005 y agrega agregaciones de dashboard.
            - Reportes operacionales leen datos reales de produccion, inventario, Kardex, ventas, compras, mermas y auditoria.
            - Exportaciones CSV/XLSX/PDF son payloads locales auditados, sin escritura externa ni integraciones externas.
            - Scheduler local declara jobs operacionales idempotentes para alertas, reintentos, reservas y exportaciones.
            - React + Bootstrap presenta KPIs, graficos, alertas y reportes sin cambiar el contrato frontend.

            Limites del hito:

            - Equipos, gastos operativos, finanzas, metas mensuales, backups, dockerizacion productiva y deploy EC2 quedan diferidos.
            - No se exponen endpoints `/api/v1/equipment`, `/api/v1/expenses`, `/api/v1/monthly-goals`, `/api/v1/jobs` ni `/api/v1/backups`.
            - SMTP sigue siendo mock local de HITO-003; no hay correo real ni integracion externa.
            - El bundle se materializa solo por el arnes P12/INV en DEV y se promueve a QA despues de validadores.
            """
        ).strip()
    if _is_hito_007(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-007

            Capas:

            - FastAPI conserva los stores locales acumulados HITO-001..HITO-006 y agrega equipos, gastos, metas y backups locales.
            - Dashboard incorpora gastos operativos, flujo de caja, metas mensuales y alertas de revision de equipos.
            - Reportes agregan vista financiera basica sin integraciones externas ni escritura fuera del sandbox.
            - Scheduler local agrega `low_activity_backup` como job idempotente; el respaldo se registra como metadata local.
            - React + Bootstrap mantiene Vite con `frontend/index.html` y `frontend/src/main.jsx`, ahora con P-27 y P-28 navegables.
            - Docker Compose, Dockerfiles y Nginx quedan preparados para EC2/proxy/TLS, sin ejecutar deploy real.

            Controles:

            - No hay secretos reales: `.env.example` usa placeholders.
            - No hay integraciones externas nuevas.
            - El deploy productivo permanece bloqueado por politica y requiere aprobacion externa futura.
            - DEV se promueve a QA solo despues de validadores, gate y regresion HITO-001..HITO-006.
            """
        ).strip()
    if _is_hito_008(blueprint):
        return dedent(
            """
            # Arquitectura BrewMaster HITO-008

            Capas:

            - FastAPI conserva exactamente el contrato acumulado HITO-007: rutas `/api/v1`, stores locales, reglas y pruebas.
            - React + Bootstrap usa Vite (`frontend/index.html`, `frontend/src/main.jsx`) y un shell con navegacion hash para P-01..P-30.
            - `frontend/src/api/client.js` encapsula fetch local, token JWT de sesion y errores normalizados sin inventar endpoints.
            - `frontend/src/screens/ScreenViews.jsx` declara un componente por pantalla, con loading, error, vacio, datos y formularios validados.
            - `frontend/src/routes.js` resuelve rutas estaticas y dinamicas declaradas en `frontend/src/screens/catalog.js`.

            Controles:

            - HITO-008 no cambia reglas de negocio ni entidades backend.
            - Acciones de UI consumen solamente endpoints aprobados bajo `/api/v1`.
            - Las pantallas mantienen datos de respaldo visual para no quedar vacias cuando el backend local no esta levantado, mostrando el error observado.
            - DEV se promueve a QA solo despues de validadores, gate, build frontend y regresion HITO-001..HITO-007.
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
        - Deploy productivo: permitido solo con WorkOrder `approved_deploy`, aprobacion humana, rollback y secretos fuera de git.
        - Destino productivo BrewMaster: AWS EC2 con Docker Compose y todos los servicios contenidos en la VM.
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
    if _is_hito_002(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-002",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| FUN-005/FUN-006 Proveedores | /api/v1/suppliers* | tests/test_master_catalog.py |",
                "| FUN-007/FUN-008 Insumos maestros | /api/v1/supplies* sin Kardex ni entradas | tests/test_master_catalog.py |",
                "| FUN-012 Bodegas | /api/v1/warehouses* | tests/test_master_catalog.py |",
                "| FUN-013 Tipos de presentacion | /api/v1/presentation-types* | tests/test_master_catalog.py |",
                "| FUN-014/FUN-015 Recetas | /api/v1/recipes* | tests/test_master_catalog.py |",
                "| Frontera HITO-003+ | supply-entries, Kardex, low-stock, batches, sales no declarados | tests/test_contracts.py |",
            ]
        )
    if _is_hito_003(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-003",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |",
                "| FUN-009 Entrada de insumo | POST /api/v1/supply-entries | tests/test_domain_rules.py |",
                "| FUN-010 Kardex de insumo | GET /api/v1/supplies/{id}/kardex | tests/test_domain_rules.py |",
                "| FUN-011 Bajo stock y cola | GET /api/v1/supplies/low-stock, GET /api/v1/notifications | tests/test_domain_rules.py |",
                "| FUN-035 SMTP local seguro | GET/PUT/POST /api/v1/settings/smtp* | tests/test_domain_rules.py |",
                "| Frontera HITO-004+ | batches, products, sales, customers, purchase-orders, reports, jobs no declarados | tests/test_contracts.py |",
            ]
        )
    if _is_hito_004(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-004",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |",
                "| HITO-003 Inventario y SMTP conservados | supply-entries, Kardex, low-stock, settings/smtp, notifications | tests/test_domain_rules.py |",
                "| FUN-016 Crear lote | GET/POST/PUT /api/v1/batches* | tests/test_domain_rules.py |",
                "| FUN-017 Completar lote | POST /api/v1/batches/{id}/complete | tests/test_domain_rules.py |",
                "| FUN-018 Control de calidad | POST /api/v1/batches/{id}/quality-check | tests/test_domain_rules.py |",
                "| FUN-019 Mermas | GET/POST /api/v1/waste-records | tests/test_domain_rules.py |",
                "| FUN-020/FUN-021 Productos terminados | GET /api/v1/products, PUT /api/v1/products/{id}/price, GET /api/v1/products/{id}/kardex | tests/test_domain_rules.py |",
                "| Frontera HITO-005+ | sales, customers, reservations, purchase-orders, reports, equipment, expenses, monthly-goals, dashboard no declarados | tests/test_contracts.py |",
            ]
        )
    if _is_hito_005(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-005",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |",
                "| HITO-003 Inventario y SMTP conservados | supply-entries, Kardex, low-stock, settings/smtp, notifications | tests/test_domain_rules.py |",
                "| HITO-004 Produccion conservada | batches, quality-check, waste-records, products, product Kardex | tests/test_domain_rules.py |",
                "| FUN-022/FUN-023 Clientes | GET/POST/PUT/PATCH /api/v1/customers* | tests/test_domain_rules.py |",
                "| FUN-024/FUN-026 Ventas y anulacion | POST/GET /api/v1/sales, POST /api/v1/sales/{id}/void | tests/test_domain_rules.py |",
                "| FUN-025 Reservas de stock | GET/POST/consume/release /api/v1/reservations* | tests/test_domain_rules.py |",
                "| FUN-027 Ordenes de compra | GET/POST/PUT/send/cancel /api/v1/purchase-orders* | tests/test_domain_rules.py |",
                "| FUN-028 Recepcionar compra | POST /api/v1/purchase-orders/{id}/receive | tests/test_domain_rules.py |",
                "| Frontera HITO-006/HITO-007 | dashboard, reports, equipment, expenses, monthly-goals, jobs, backups y deploy no declarados | tests/test_contracts.py |",
            ]
        )
    if _is_hito_006(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-006",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |",
                "| HITO-003 Inventario y SMTP conservados | supply-entries, Kardex, low-stock, settings/smtp, notifications | tests/test_domain_rules.py |",
                "| HITO-004 Produccion conservada | batches, quality-check, waste-records, products, product Kardex | tests/test_domain_rules.py |",
                "| HITO-005 Ventas y compras conservadas | customers, sales, reservations, purchase-orders | tests/test_domain_rules.py |",
                "| FUN-033 Dashboard general | GET /api/v1/dashboard | tests/test_domain_rules.py |",
                "| FUN-034 Reportes exportables | GET /api/v1/reports, POST /api/v1/reports/export | tests/test_domain_rules.py |",
                "| Alertas operacionales | stock, merma >5%, compras pendientes y reservas vencidas | tests/test_domain_rules.py |",
                "| Scheduler operacional | backend/app/jobs/scheduler.py sin backups | tests/test_domain_rules.py |",
                "| Frontera HITO-007 | equipment, expenses, monthly-goals, jobs API, backups y deploy no declarados | tests/test_contracts.py |",
            ]
        )
    if _is_hito_007(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-007",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |",
                "| HITO-003 Inventario y SMTP conservados | supply-entries, Kardex, low-stock, settings/smtp, notifications | tests/test_domain_rules.py |",
                "| HITO-004 Produccion conservada | batches, quality-check, waste-records, products, product Kardex | tests/test_domain_rules.py |",
                "| HITO-005 Ventas y compras conservadas | customers, sales, reservations, purchase-orders | tests/test_domain_rules.py |",
                "| HITO-006 Dashboard/reportes/scheduler conservados | dashboard, reports/export, jobs operacionales | tests/test_domain_rules.py |",
                "| FUN-029/FUN-030 Equipos | GET/POST/PUT /api/v1/equipment y movements | tests/test_domain_rules.py |",
                "| FUN-031 Finanzas | GET/POST/PUT/DELETE /api/v1/expenses | tests/test_domain_rules.py |",
                "| FUN-036 Metas mensuales | GET/PUT /api/v1/monthly-goals* | tests/test_domain_rules.py |",
                "| Respaldos automaticos locales | GET /api/v1/jobs, GET/POST /api/v1/backups | tests/test_domain_rules.py |",
                "| Despliegue preparado | docker-compose.yml, Dockerfiles, deploy/nginx.conf, docs/deployment.md | tests/test_contracts.py |",
            ]
        )
    if _is_hito_008(blueprint):
        return "\n".join(
            [
                "# Trazabilidad HITO-008",
                "",
                "| requisito | evidencia generada | prueba |",
                "|---|---|---|",
                "| HITO-001 Fundamentos conservados | backend/app/main.py, backend/app/core/security.py | tests/test_auth_foundation.py |",
                "| HITO-002 Maestros conservados | proveedores, insumos, bodegas, recetas, presentaciones | tests/test_master_catalog.py |",
                "| HITO-003 Inventario y SMTP conservados | supply-entries, Kardex, low-stock, settings/smtp, notifications | tests/test_domain_rules.py |",
                "| HITO-004 Produccion conservada | batches, quality-check, waste-records, products, product Kardex | tests/test_domain_rules.py |",
                "| HITO-005 Ventas y compras conservadas | customers, sales, reservations, purchase-orders | tests/test_domain_rules.py |",
                "| HITO-006 Dashboard/reportes/scheduler conservados | dashboard, reports/export, jobs operacionales | tests/test_domain_rules.py |",
                "| HITO-007 Cierre conservado | equipment, expenses, monthly-goals, jobs, backups, deploy docs | tests/test_domain_rules.py, tests/test_contracts.py |",
                "| SCR-001..SCR-030 pantallas separadas | frontend/src/screens/catalog.js, frontend/src/screens/ScreenViews.jsx | tests/test_contracts.py, pnpm build |",
                "| Navegacion frontend | frontend/src/App.jsx, frontend/src/routes.js | tests/test_contracts.py, pnpm build |",
                "| Cliente API local | frontend/src/api/client.js consume solo `/api/v1` | tests/test_contracts.py |",
                "| Estados loading/error/vacio | ScreenViews.jsx helpers `useResources`, `ScreenFrame`, `EmptyState` | tests/test_contracts.py |",
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
    if _is_hito_002(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-002

            Regresion HITO-001:

            - Hash de contrasena, JWT, RBAC, login, cambio y recuperacion de contrasena.
            - Usuarios, roles, permisos y auditoria siguen activos.

            Contratos HITO-002:

            - ROUTE_CATALOG conserva HITO-001 y agrega solo rutas de maestros.
            - SCREEN_CATALOG conserva seguridad y agrega P-04, P-05, P-08, P-09, P-10, P-11, P-12 y P-13.
            - Rutas de entradas, Kardex, stock bajo, lotes, productos, ventas, compras y jobs quedan fuera.

            Integracion local:

            - Proveedor rechaza codigo duplicado y correo invalido.
            - Insumo exige proveedor y bodega activos, tipo valido, costos y stock no negativos.
            - Receta exige ingredientes activos, calcula costo estimado y clona como `en_prueba`.
            - Insumo usado por receta activa no puede inactivarse.
            - Presentacion exige volumen positivo y costo no negativo.
            """
        ).strip()
    if _is_hito_003(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-003

            Regresion HITO-001/HITO-002:

            - Hash de contrasena, JWT, RBAC, login, usuarios, permisos y auditoria siguen activos.
            - Proveedores, insumos maestros, bodegas, recetas, presentaciones y bloqueo de insumos usados por receta siguen activos.

            Contratos HITO-003:

            - ROUTE_CATALOG conserva HITO-001/HITO-002 y agrega solo entradas, Kardex, bajo stock, SMTP y notificaciones.
            - SCREEN_CATALOG agrega P-06 y P-07 al acumulado, manteniendo P-30 para SMTP/seguridad.
            - Rutas de produccion, productos, ventas, clientes, compras, reportes, equipos, finanzas, metas y jobs quedan fuera.

            Unitarias e integracion local:

            - Entrada valida incrementa stock, crea movimiento Kardex y audita.
            - Insumo inactivo bloquea entradas.
            - Bajo stock encola notificacion si alertas estan habilitadas y respeta intervalo de 24 horas.
            - Stock en cero fuerza alerta y stock recuperado resetea `last_alert_sent_at`.
            - Configuracion SMTP se devuelve sanitizada y la prueba se registra como mock local sin envio real.
            - Cola de correo reintenta con mock y marca error definitivo tras cinco fallos.
            """
        ).strip()
    if _is_hito_004(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-004

            Regresion HITO-001/HITO-002/HITO-003:

            - Hash de contrasena, JWT, RBAC, login, usuarios, permisos y auditoria siguen activos.
            - Proveedores, insumos, bodegas, recetas, presentaciones y bloqueo de insumos usados por receta siguen activos.
            - Entradas, Kardex, bajo stock, cola local de notificaciones y SMTP sanitizado siguen activos sin envio real.

            Contratos HITO-004:

            - ROUTE_CATALOG conserva el acumulado HITO-001..HITO-003 y agrega lotes, productos y mermas.
            - SCREEN_CATALOG agrega P-14 a P-19 al acumulado, manteniendo fuera P-03 y P-20 en adelante.
            - Rutas de ventas, clientes, reservas, compras, reportes, equipos, finanzas, metas y dashboard quedan fuera.

            Unitarias e integracion local:

            - Crear lote requiere receta y presentacion activas, responsable y cantidad positiva.
            - Completar lote valida stock, descuenta insumos, escribe Kardex, calcula costos y crea producto terminado.
            - Lote cancelado no afecta inventario ni puede completarse.
            - Control de calidad es unico por lote; rechazo exige motivo.
            - Merma exige motivo, no permite stock negativo y registra Kardex.
            - Precio de producto terminado rechaza negativo y advierte si queda bajo costo.
            """
        ).strip()
    if _is_hito_005(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-005

            Regresion HITO-001/HITO-002/HITO-003/HITO-004:

            - Hash de contrasena, JWT, RBAC, login, usuarios, permisos y auditoria siguen activos.
            - Proveedores, insumos, bodegas, recetas, presentaciones, entradas, Kardex, bajo stock y SMTP local siguen activos.
            - Lotes, calidad, mermas, precios de producto y productos terminados conservan reglas de HITO-004.

            Contratos HITO-005:

            - ROUTE_CATALOG conserva el acumulado HITO-001..HITO-004 y agrega solo clientes, ventas, reservas y ordenes de compra.
            - SCREEN_CATALOG agrega P-20 a P-26 al acumulado, manteniendo fuera P-03 y P-27 en adelante.
            - Rutas de dashboard, reportes, equipos, finanzas, metas, jobs, backups y deploy quedan fuera.

            Unitarias e integracion local:

            - Cliente exige identificador fiscal unico, email valido y bloquea cambio fiscal despues de ventas.
            - Venta valida cliente activo, stock libre, precios por tipo de cliente y escribe Kardex VENTA.
            - Anulacion de venta exige motivo, restaura stock y escribe Kardex DEVOLUCION.
            - Reserva usa stock actual menos reservas activas, puede liberarse o consumirse una sola vez.
            - Orden de compra exige proveedor activo, lineas positivas y se bloquea al enviarse.
            - Recepcion parcial o total genera entrada de insumo, Kardex ENTRADA y evita sobre-recepcion sin tolerancia.
            """
        ).strip()
    if _is_hito_006(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-006

            Regresion HITO-001/HITO-002/HITO-003/HITO-004/HITO-005:

            - Hash de contrasena, JWT, RBAC, login, usuarios, permisos y auditoria siguen activos.
            - Proveedores, insumos, bodegas, recetas, presentaciones, entradas, Kardex, bajo stock y SMTP local siguen activos.
            - Produccion, lotes, calidad, mermas, precios de producto y productos terminados conservan reglas de HITO-004.
            - Clientes, ventas, anulaciones, reservas, precios por tipo de cliente y ordenes de compra conservan reglas de HITO-005.

            Contratos HITO-006:

            - ROUTE_CATALOG conserva el acumulado HITO-001..HITO-005 y agrega solo `/api/v1/dashboard`, `/api/v1/reports` y `/api/v1/reports/export`.
            - SCREEN_CATALOG agrega P-03 y P-29, manteniendo fuera P-27 y P-28.
            - Rutas de equipos, gastos operativos, metas mensuales, jobs API, backups y deploy quedan fuera.

            Unitarias e integracion local:

            - Dashboard calcula KPIs reales sobre stores operacionales: produccion, stock libre, ventas, compras, mermas y alertas.
            - Alertas operacionales cubren stock bajo, merma sobre 5%, compras pendientes y reservas vencidas.
            - Reportes disponibles cubren produccion, ventas, inventario, Kardex, mermas, compras y auditoria operacional.
            - Exportacion CSV/XLSX/PDF valida tipo, formato, permisos y registra auditoria local sin integraciones externas.
            - Scheduler HITO-006 declara solo alertas, reintentos, vencimiento de reservas y exportaciones diferidas; backups quedan bloqueados hasta HITO-007.
            """
        ).strip()
    if _is_hito_007(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-007

            Regresion HITO-001..HITO-006:

            - Hash de contrasena, JWT, RBAC, usuarios, permisos y auditoria siguen activos.
            - Maestros, inventario, Kardex, SMTP local, produccion, calidad, mermas y productos terminados siguen activos.
            - Clientes, ventas, reservas, precios por tipo, compras, dashboard, reportes exportables y scheduler HITO-006 siguen activos.

            Contratos HITO-007:

            - ROUTE_CATALOG conserva el acumulado HITO-001..HITO-006 y agrega equipos, gastos, metas, jobs y backups.
            - SCREEN_CATALOG declara las 30 pantallas, incluyendo P-27 equipos y P-28 finanzas.
            - Artefactos de despliegue preparado: `docker-compose.yml`, Dockerfiles, Nginx y runbook EC2/TLS.

            Unitarias e integracion local:

            - Equipo exige codigo unico, historial de movimientos y bloquea movimientos si esta descartado.
            - Equipo con proxima revision vencida aparece como alerta de dashboard.
            - Gasto operativo exige monto positivo y bloquea eliminacion si tiene documento de respaldo.
            - Metas mensuales se actualizan por mes y dashboard devuelve progreso meta vs real.
            - Reporte financiero exporta gastos/metas sin integraciones externas.
            - Scheduler activa `low_activity_backup` y backups quedan como metadata local sin deploy ni secretos reales.
            """
        ).strip()
    if _is_hito_008(blueprint):
        return dedent(
            """
            # Estrategia de pruebas HITO-008

            Regresion HITO-001..HITO-007:

            - Hash de contrasena, JWT, RBAC, usuarios, permisos y auditoria siguen activos.
            - Maestros, inventario, Kardex, SMTP local, produccion, calidad, mermas y productos terminados siguen activos.
            - Clientes, ventas, anulaciones, reservas, precios por tipo, compras, dashboard, reportes, scheduler, equipos y finanzas siguen activos.
            - Respaldos automaticos locales y artefactos Docker/proxy/TLS siguen presentes sin deploy real.

            Contratos HITO-008:

            - ROUTE_CATALOG conserva el acumulado HITO-007 sin endpoints backend nuevos.
            - SCREEN_CATALOG declara P-01..P-30 y cada pantalla tiene componente especifico en `ScreenViews.jsx`.
            - `App.jsx` usa navegacion hash sobre `routes.js`; rutas dinamicas se materializan con IDs locales de ejemplo.
            - `api/client.js` usa exclusivamente `/api/v1`, token local y errores normalizados.
            - No existe `GenericScreen` ni fallback placeholder para pantallas declaradas.

            Frontend:

            - `pnpm build` debe compilar Vite.
            - Las 30 pantallas renderizan cabecera, estado de endpoint, datos o vacio profesional y acciones relacionadas.
            - Formularios validan campos requeridos y numeros positivos antes de llamar a endpoints aprobados.
            - Los errores de backend se muestran sin dejar la pantalla vacia.
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

        Infraestructura:

        - Build de imagen backend y frontend.
        - `docker compose config` valido para EC2.
        - Smoke test de `/api/v1/health`, frontend, proxy reverso y base de datos.
        - Backup, restore y rollback ensayados antes de aprobar deploy.
        """
    ).strip()


def _deployment_md() -> str:
    return dedent(
        """
        # Despliegue BrewMaster en AWS EC2

        Objetivo:

        - Ejecutar BrewMaster completo en una VM EC2 mediante Docker Compose.
        - Mantener frontend, backend, base de datos, proxy reverso y jobs dentro de la VM.
        - Bloquear deploy productivo hasta contar con aprobacion humana, rollback y evidencia de pruebas.

        Servicios esperados:

        - `frontend`: React compilado y servido por Nginx.
        - `backend`: FastAPI bajo `/api/v1`.
        - `db`: MariaDB/MySQL con volumen persistente.
        - `proxy`: Nginx como entrada HTTP/HTTPS.

        Reglas operativas:

        - No versionar secretos reales.
        - Usar `.env` local protegido en la VM y `.env.example` en git.
        - Ejecutar migraciones Alembic antes de habilitar trafico.
        - Validar healthchecks antes de cerrar el deploy.
        - Probar backup/restore y rollback en cada cierre mayor.

        Puertos:

        - Exponer publicamente solo 80/443 en el security group.
        - Mantener base de datos y backend en red interna Docker.

        Evidencia requerida:

        - `docker compose config` sin errores.
        - Build de imagenes exitoso.
        - Smoke test HTTP de frontend y API.
        - Log de migraciones.
        - Backup restaurable.
        - Plan de rollback firmado/aprobado.
        """
    ).strip()


def _env_example() -> str:
    return dedent(
        """
        APP_ENV=production
        APP_PUBLIC_URL=https://brewmaster.example.com
        API_BASE_URL=/api/v1

        DB_HOST=db
        DB_PORT=3306
        DB_NAME=brewmaster
        DB_USER=brewmaster
        DB_PASSWORD=setme
        DB_ROOT_PASSWORD=setme

        JWT_SECRET_KEY=setme
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

        SMTP_HOST=smtp.example.com
        SMTP_PORT=587
        SMTP_USER=alerts@example.com
        SMTP_PASSWORD=setme
        SMTP_FROM=alerts@example.com

        BACKUP_RETENTION_DAYS=14
        """
    ).strip() + "\n"


def _docker_compose_yml() -> str:
    return dedent(
        """
        services:
          db:
            image: mariadb:11
            restart: unless-stopped
            environment:
              MARIADB_DATABASE: ${DB_NAME}
              MARIADB_USER: ${DB_USER}
              MARIADB_PASSWORD: ${DB_PASSWORD}
              MARIADB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
            volumes:
              - brewmaster-db:/var/lib/mysql
            healthcheck:
              test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
              interval: 10s
              timeout: 5s
              retries: 10

          backend:
            build:
              context: ./backend
            restart: unless-stopped
            env_file:
              - .env
            depends_on:
              db:
                condition: service_healthy
            expose:
              - "8000"
            healthcheck:
              test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
              interval: 30s
              timeout: 5s
              retries: 5

          frontend:
            build:
              context: ./frontend
            restart: unless-stopped
            expose:
              - "80"

          proxy:
            image: nginx:1.27-alpine
            restart: unless-stopped
            depends_on:
              - backend
              - frontend
            ports:
              - "80:80"
              - "443:443"
            volumes:
              - ./deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro
              - ./deploy/certs:/etc/nginx/certs:ro

        volumes:
          brewmaster-db:
        """
    ).strip() + "\n"


def _backend_dockerfile() -> str:
    return dedent(
        """
        FROM python:3.12-slim

        ENV PYTHONDONTWRITEBYTECODE=1
        ENV PYTHONUNBUFFERED=1

        WORKDIR /app
        COPY pyproject.toml /app/pyproject.toml
        RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy alembic pymysql python-jose passlib[bcrypt]
        COPY . /app

        EXPOSE 8000
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
        """
    ).strip() + "\n"


def _frontend_dockerfile() -> str:
    return dedent(
        """
        FROM node:22-alpine AS build
        WORKDIR /app
        RUN corepack enable
        COPY . .
        RUN pnpm install --no-frozen-lockfile
        RUN pnpm run build

        FROM nginx:1.27-alpine
        COPY --from=build /app/dist /usr/share/nginx/html
        EXPOSE 80
        """
    ).strip() + "\n"


def _nginx_conf() -> str:
    return dedent(
        """
        server {
          listen 80;
          server_name _;

          location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
          }

          location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
          }
        }
        """
    ).strip() + "\n"

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
    if _is_hito_002(blueprint):
        return {
            "milestone_id": "HITO-002",
            "declared_permissions": declared_permissions,
            "roles": {
                "admin": ["*"],
                "auditor": ["audit.read"],
                "compras": [
                    "suppliers.read",
                    "suppliers.create",
                    "suppliers.update",
                    "supplies.read",
                    "supplies.create",
                    "supplies.update",
                    "supplies.toggle-status",
                ],
                "produccion": ["supplies.read", "recipes.read", "recipes.create", "recipes.update", "recipes.clone"],
                "operador": [],
            },
            "sensitive_permissions": ["admin.users", "audit.read"],
            "permission_mapping_notes": {
                "warehouses": "gestionado con supplies.read/supplies.update durante HITO-002",
                "presentation_types": "gestionado con recipes.read/recipes.update durante HITO-002",
            },
            "deferred_permission_count": len(
                [permission for permission in load_brewmaster_spec().permissions if permission not in set(declared_permissions)]
            ),
            "deferred_permission_policy": "no declarados como permisos activos hasta sus hitos posteriores",
        }
    if _is_hito_003(blueprint):
        return {
            "milestone_id": "HITO-003",
            "declared_permissions": declared_permissions,
            "roles": {
                "admin": ["*"],
                "auditor": ["audit.read"],
                "compras": [
                    "suppliers.read",
                    "suppliers.create",
                    "suppliers.update",
                    "supplies.read",
                    "supplies.create",
                    "supplies.update",
                    "supplies.toggle-status",
                    "supply-entries.create",
                ],
                "inventario": ["supplies.read", "supply-entries.create"],
                "produccion": ["supplies.read", "recipes.read", "recipes.create", "recipes.update", "recipes.clone"],
                "operador": [],
            },
            "sensitive_permissions": ["admin.users", "admin.settings", "audit.read"],
            "permission_mapping_notes": {
                "smtp": "admin.settings requerido; la prueba SMTP es mock local",
                "notifications": "lectura permitida a admin.settings o supplies.read durante HITO-003",
                "warehouses": "gestionado con supplies.read/supplies.update",
                "presentation_types": "gestionado con recipes.read/recipes.update",
            },
            "deferred_permission_count": len(
                [permission for permission in load_brewmaster_spec().permissions if permission not in set(declared_permissions)]
            ),
            "deferred_permission_policy": "permisos de produccion, ventas, compras, reportes, equipos y finanzas quedan diferidos",
        }
    if _is_hito_004(blueprint):
        return {
            "milestone_id": "HITO-004",
            "declared_permissions": declared_permissions,
            "roles": {
                "admin": ["*"],
                "auditor": ["audit.read"],
                "compras": [
                    "suppliers.read",
                    "suppliers.create",
                    "suppliers.update",
                    "supplies.read",
                    "supplies.create",
                    "supplies.update",
                    "supplies.toggle-status",
                    "supply-entries.create",
                ],
                "inventario": ["supplies.read", "supply-entries.create", "products.read"],
                "produccion": [
                    "supplies.read",
                    "recipes.read",
                    "recipes.create",
                    "recipes.update",
                    "recipes.clone",
                    "batches.read",
                    "batches.create",
                    "batches.complete",
                    "batches.cancel",
                    "batches.quality-check",
                    "waste.create",
                    "waste.read",
                    "products.read",
                ],
                "productos": ["products.read", "products.update-price"],
                "operador": [],
            },
            "sensitive_permissions": ["admin.users", "admin.settings", "audit.read", "products.update-price"],
            "permission_mapping_notes": {
                "production": "batches.* y waste.* activos solo desde HITO-004",
                "products": "products.read/update-price activo sin ventas ni clientes",
                "smtp": "admin.settings se conserva de HITO-003; prueba mock local",
            },
            "deferred_permission_count": len(
                [permission for permission in load_brewmaster_spec().permissions if permission not in set(declared_permissions)]
            ),
            "deferred_permission_policy": "permisos de ventas, compras, reportes, equipos, finanzas, metas y deploy quedan diferidos",
        }
    if _is_hito_005(blueprint):
        return {
            "milestone_id": "HITO-005",
            "declared_permissions": declared_permissions,
            "roles": {
                "admin": ["*"],
                "auditor": ["audit.read"],
                "compras": [
                    "suppliers.read",
                    "suppliers.create",
                    "suppliers.update",
                    "supplies.read",
                    "supplies.create",
                    "supplies.update",
                    "supplies.toggle-status",
                    "supply-entries.create",
                    "purchase-orders.read",
                    "purchase-orders.create",
                    "purchase-orders.receive",
                    "purchase-orders.cancel",
                ],
                "inventario": ["supplies.read", "supply-entries.create", "products.read"],
                "produccion": [
                    "supplies.read",
                    "recipes.read",
                    "recipes.create",
                    "recipes.update",
                    "recipes.clone",
                    "batches.read",
                    "batches.create",
                    "batches.complete",
                    "batches.cancel",
                    "batches.quality-check",
                    "waste.create",
                    "waste.read",
                    "products.read",
                ],
                "productos": ["products.read", "products.update-price"],
                "ventas": [
                    "products.read",
                    "sales.read",
                    "sales.create",
                    "customers.read",
                    "customers.create",
                    "customers.update",
                    "reservations.create",
                    "reservations.manage",
                ],
                "operador": [],
            },
            "sensitive_permissions": [
                "admin.users",
                "admin.settings",
                "audit.read",
                "products.update-price",
                "sales.create",
                "purchase-orders.receive",
            ],
            "permission_mapping_notes": {
                "sales": "ventas y reservas activas desde HITO-005, sin pasarela ni integracion externa",
                "purchasing": "ordenes y recepcion activas desde HITO-005, sin envio externo a proveedores",
                "smtp": "admin.settings se conserva de HITO-003; prueba mock local",
            },
            "deferred_permission_count": len(
                [permission for permission in load_brewmaster_spec().permissions if permission not in set(declared_permissions)]
            ),
            "deferred_permission_policy": "permisos de reportes, equipos, finanzas, metas, jobs, backups y deploy quedan diferidos",
        }
    if _is_hito_006(blueprint):
        return {
            "milestone_id": "HITO-006",
            "declared_permissions": declared_permissions,
            "roles": {
                "admin": ["*"],
                "auditor": ["audit.read", "reports.read", "reports.export"],
                "compras": [
                    "suppliers.read",
                    "suppliers.create",
                    "suppliers.update",
                    "supplies.read",
                    "supplies.create",
                    "supplies.update",
                    "supplies.toggle-status",
                    "supply-entries.create",
                    "purchase-orders.read",
                    "purchase-orders.create",
                    "purchase-orders.receive",
                    "purchase-orders.cancel",
                    "reports.read",
                ],
                "inventario": ["supplies.read", "supply-entries.create", "products.read", "reports.read"],
                "produccion": [
                    "supplies.read",
                    "recipes.read",
                    "recipes.create",
                    "recipes.update",
                    "recipes.clone",
                    "batches.read",
                    "batches.create",
                    "batches.complete",
                    "batches.cancel",
                    "batches.quality-check",
                    "waste.create",
                    "waste.read",
                    "products.read",
                    "reports.read",
                ],
                "productos": ["products.read", "products.update-price", "reports.read"],
                "ventas": [
                    "products.read",
                    "sales.read",
                    "sales.create",
                    "customers.read",
                    "customers.create",
                    "customers.update",
                    "reservations.create",
                    "reservations.manage",
                    "reports.read",
                ],
                "reportes": ["reports.read", "reports.export"],
                "operador": [],
            },
            "sensitive_permissions": [
                "admin.users",
                "admin.settings",
                "audit.read",
                "products.update-price",
                "sales.create",
                "purchase-orders.receive",
                "reports.export",
            ],
            "permission_mapping_notes": {
                "reports": "dashboard y reportes operacionales activos desde HITO-006",
                "audit_report": "reporte de auditoria requiere audit.read ademas de reports.export",
                "scheduler": "jobs operacionales declarados en scheduler.py sin exponer API /jobs",
                "hito7": "equipment.*, expenses.*, monthly-goals.*, backups y deploy siguen diferidos",
            },
            "deferred_permission_count": len(
                [permission for permission in load_brewmaster_spec().permissions if permission not in set(declared_permissions)]
            ),
            "deferred_permission_policy": "permisos de equipos, finanzas, metas, backups y deploy quedan diferidos para HITO-007",
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
