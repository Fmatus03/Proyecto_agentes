from __future__ import annotations

from textwrap import dedent

def _test_domain_rules_py(milestone_id: str | None = None) -> str:
    if (milestone_id or "").strip().upper() == "HITO-008":
        return _test_domain_rules_py("HITO-007")
    if (milestone_id or "").strip().upper() == "HITO-007":
        base = _test_domain_rules_py("HITO-006")
        base = base.replace(
            "def test_dashboard_uses_real_operational_data_and_alerts_without_hito7_scope():",
            "def test_dashboard_uses_real_operational_data_and_alerts_with_hito7_scope():",
        )
        base = base.replace(
            'assert "equipment" in payload["hito7_scope_excluded"]',
            'assert payload["hito7_scope_excluded"] == []',
        )
        base = base.replace(
            'assert client.get("/api/v1/equipment", headers=headers).status_code == 404',
            'assert client.get("/api/v1/equipment", headers=headers).status_code == 200',
        )
        base = base.replace(
            'assert client.get("/api/v1/expenses", headers=headers).status_code == 404',
            'assert client.get("/api/v1/expenses", headers=headers).status_code == 200',
        )
        base = base.replace(
            'assert client.get("/api/v1/monthly-goals", headers=headers).status_code == 404',
            'assert client.get("/api/v1/monthly-goals", headers=headers).status_code == 200',
        )
        base = base.replace(
            'assert "financiero" not in report_types',
            'assert "financiero" in report_types',
        )
        base = base.replace(
            'assert client.get("/api/v1/jobs", headers=headers).status_code == 404',
            'assert client.get("/api/v1/jobs", headers=headers).status_code == 200',
        )
        base = base.replace(
            'assert client.get("/api/v1/backups", headers=headers).status_code == 404',
            'assert client.get("/api/v1/backups", headers=headers).status_code == 200',
        )
        base = base.replace(
            "def test_scheduler_policy_is_operational_only_for_hito6():",
            "def test_scheduler_policy_includes_local_backups_only_for_hito7():",
        )
        base = base.replace(
            'assert policy["backup_jobs"] is False',
            'assert policy["backup_jobs"] is True',
        )
        base = base.replace(
            '        "deferred_exports",\n    }',
            '        "deferred_exports",\n        "low_activity_backup",\n    }',
        )
        base = base.replace(
            'assert should_run("low_activity_backup") is False',
            'assert should_run("low_activity_backup") is True',
        )
        return (
            base
            + "\n\n"
            + dedent(
                """

                def test_hito7_equipment_lifecycle_alerts_and_discard_guard():
                    headers = _admin_headers()
                    equipment = client.post(
                        "/api/v1/equipment",
                        json={
                            "codigo": "EQ-H7-001",
                            "nombre": "Fermentador piloto",
                            "tipo_id": 1,
                            "marca": "BrewLocal",
                            "modelo": "F-100",
                            "serie": "SER-H7-001",
                            "fecha_compra": "2026-01-01",
                            "costo_adquisicion": 1250000,
                            "ultima_mantencion": "2026-01-15",
                            "proxima_revision": "2026-02-15",
                        },
                        headers=headers,
                    )
                    assert equipment.status_code == 200
                    payload = equipment.json()["data"]
                    assert payload["revision_vencida"] is True
                    listing = client.get("/api/v1/equipment", headers=headers)
                    assert listing.status_code == 200
                    assert listing.json()["data"]["equipment"][0]["codigo"] == "EQ-H7-001"
                    movement = client.post(
                        f"/api/v1/equipment/{payload['id']}/movements",
                        json={"tipo_movimiento": "mantencion", "descripcion": "Cambio de sello", "costo": 45000, "fecha": "2026-07-01"},
                        headers=headers,
                    )
                    assert movement.status_code == 200
                    assert movement.json()["data"]["equipment"]["estado"] == "operativo"
                    discard = client.post(
                        f"/api/v1/equipment/{payload['id']}/movements",
                        json={"tipo_movimiento": "descarte", "descripcion": "Fin de vida util", "costo": 0},
                        headers=headers,
                    )
                    assert discard.status_code == 200
                    blocked = client.post(
                        f"/api/v1/equipment/{payload['id']}/movements",
                        json={"tipo_movimiento": "revision", "descripcion": "No aplica", "costo": 0},
                        headers=headers,
                    )
                    assert blocked.status_code == 422


                def test_hito7_expenses_goals_financial_report_and_dashboard_progress():
                    headers = _admin_headers()
                    expense = client.post(
                        "/api/v1/expenses",
                        json={
                            "concepto": "Mantencion bomba",
                            "categoria_id": 2,
                            "monto": 55000,
                            "fecha": "2026-07-03",
                            "proveedor": "Servicio local",
                            "documento_referencia": "FAC-H7-001",
                        },
                        headers=headers,
                    )
                    assert expense.status_code == 200
                    assert expense.json()["data"]["monto"] == 55000
                    delete_blocked = client.delete(f"/api/v1/expenses/{expense.json()['data']['id']}", headers=headers)
                    assert delete_blocked.status_code == 422
                    invalid_expense = client.post(
                        "/api/v1/expenses",
                        json={"concepto": "Gasto invalido", "categoria_id": 1, "monto": 0},
                        headers=headers,
                    )
                    assert invalid_expense.status_code == 422
                    goal = client.put(
                        "/api/v1/monthly-goals/2026-07",
                        json={"litros_produccion": 100, "monto_ventas": 100000, "num_clientes": 2, "margen_promedio_pct": 20},
                        headers=headers,
                    )
                    assert goal.status_code == 200
                    assert goal.json()["data"]["goal"]["month"] == "2026-07"
                    dashboard = client.get("/api/v1/dashboard", headers=headers)
                    assert dashboard.status_code == 200
                    payload = dashboard.json()["data"]
                    assert payload["kpis"]["gastos_operativos"] >= 55000
                    assert payload["deployment_status"]["deploy_executed"] is False
                    assert payload["monthly_goal"]["month"] == "2026-07"
                    export = client.post(
                        "/api/v1/reports/export",
                        json={"tipo_reporte": "financiero", "formato": "csv"},
                        headers=headers,
                    )
                    assert export.status_code == 200
                    assert "Mantencion bomba" in export.json()["data"]["content"]


                def test_hito7_backup_endpoints_are_local_metadata_without_deploy_or_secrets():
                    headers = _admin_headers()
                    jobs = client.get("/api/v1/jobs", headers=headers)
                    assert jobs.status_code == 200
                    assert jobs.json()["data"]["policy"]["backup_jobs"] is True
                    backup = client.post("/api/v1/backups", json={"retention_days": 7}, headers=headers)
                    assert backup.status_code == 200
                    payload = backup.json()["data"]
                    assert payload["archivo_url"].startswith("local://sandbox/backups/")
                    assert payload["external_write"] is False
                    assert payload["deploy_executed"] is False
                    backups = client.get("/api/v1/backups", headers=headers)
                    assert backups.status_code == 200
                    assert backups.json()["data"]["backups"][0]["id"] == payload["id"]
                """
            ).strip()
        )
    if (milestone_id or "").strip().upper() == "HITO-006":
        base = _test_domain_rules_py("HITO-005")
        base = base.replace(
            "from app.services.sales import confirm_sale, consume_reservation as consume_reserved_line, price_for_customer_type, release_reservation as release_reserved_line",
            "\n".join(
                [
                    "from app.services.sales import confirm_sale, consume_reservation as consume_reserved_line, price_for_customer_type, release_reservation as release_reserved_line",
                    "from app.jobs.scheduler import job_policy, should_run",
                ]
            ),
        )
        return (
            base
            + "\n\n"
            + dedent(
                """

                def test_dashboard_uses_real_operational_data_and_alerts_without_hito7_scope():
                    headers, _, _, presentation, recipe = _create_production_stack(stock_actual=10, ingredient_quantity=10)
                    batch = _create_batch(headers, recipe, presentation)
                    completed = _complete_batch(headers, batch["id"], units=100)
                    product = completed["product"]
                    client.put(f"/api/v1/products/{product['id']}/price", json={"precio_venta": 950}, headers=headers)
                    customer = _create_customer(headers, "H6DASH001", "minorista")
                    sale = client.post(
                        "/api/v1/sales",
                        json={"cliente_id": customer["id"], "items": [{"product_id": product["id"], "cantidad": 12}]},
                        headers=headers,
                    )
                    assert sale.status_code == 200
                    waste = client.post(
                        "/api/v1/waste-records",
                        json={
                            "tipo_entidad": "producto",
                            "entidad_id": product["id"],
                            "cantidad_perdida": 6,
                            "tipo_merma": "calidad",
                            "motivo": "desviacion sensorial",
                            "batch_id": batch["id"],
                        },
                        headers=headers,
                    )
                    assert waste.status_code == 200
                    dashboard = client.get("/api/v1/dashboard", headers=headers)
                    assert dashboard.status_code == 200
                    payload = dashboard.json()["data"]
                    assert payload["kpis"]["litros_producidos"] >= 50
                    assert payload["kpis"]["monto_ventas"] > 0
                    assert payload["kpis"]["alertas_operacionales"] >= 2
                    assert payload["charts"]["ventas_por_mes"]
                    assert payload["charts"]["stock_por_producto"]
                    assert {alert["type"] for alert in payload["alerts"]} >= {"stock", "merma"}
                    assert "equipment" in payload["hito7_scope_excluded"]
                    assert client.get("/api/v1/equipment", headers=headers).status_code == 404
                    assert client.get("/api/v1/expenses", headers=headers).status_code == 404
                    assert client.get("/api/v1/monthly-goals", headers=headers).status_code == 404


                def test_reports_export_csv_xlsx_pdf_and_audit_without_external_integrations():
                    headers = _admin_headers()
                    catalog = client.get("/api/v1/reports", headers=headers)
                    assert catalog.status_code == 200
                    report_types = {item["type"] for item in catalog.json()["data"]["reports"]}
                    assert {"produccion", "ventas", "inventario", "kardex", "mermas", "compras", "auditoria"} <= report_types
                    assert "financiero" not in report_types
                    csv_export = client.post(
                        "/api/v1/reports/export",
                        json={"tipo_reporte": "ventas", "formato": "csv"},
                        headers=headers,
                    )
                    assert csv_export.status_code == 200
                    csv_payload = csv_export.json()["data"]
                    assert csv_payload["job"]["estado"] == "completado"
                    assert csv_payload["filename"].endswith(".csv")
                    assert csv_payload["mime_type"] == "text/csv"
                    xlsx_export = client.post(
                        "/api/v1/reports/export",
                        json={"tipo_reporte": "inventario", "formato": "xlsx"},
                        headers=headers,
                    )
                    assert xlsx_export.status_code == 200
                    assert "local-xlsx-workbook" in xlsx_export.json()["data"]["content"]
                    pdf_export = client.post(
                        "/api/v1/reports/export",
                        json={"tipo_reporte": "auditoria", "formato": "pdf"},
                        headers=headers,
                    )
                    assert pdf_export.status_code == 200
                    assert "local-pdf-report" in pdf_export.json()["data"]["content"]
                    audit = client.get("/api/v1/audit-logs", headers=headers)
                    assert any(item["action"] == "report_exported" for item in audit.json()["data"])
                    assert client.get("/api/v1/jobs", headers=headers).status_code == 404
                    assert client.get("/api/v1/backups", headers=headers).status_code == 404


                def test_scheduler_policy_is_operational_only_for_hito6():
                    policy = job_policy()
                    assert policy["scheduler"] == "APScheduler"
                    assert policy["idempotent"] is True
                    assert policy["blocking_main_flow"] is False
                    assert policy["external_integrations"] is False
                    assert policy["backup_jobs"] is False
                    assert set(policy["jobs"]) == {
                        "stock_alerts",
                        "email_retries",
                        "reservation_expiration",
                        "deferred_exports",
                    }
                    assert should_run("deferred_exports") is True
                    assert should_run("low_activity_backup") is False
                """
            ).strip()
        )
    if (milestone_id or "").strip().upper() == "HITO-005":
        base = _test_domain_rules_py("HITO-004")
        base = base.replace(
            "from app.services.production import planned_consumption, quality_payload, stock_failures, waste_payload",
            "\n".join(
                [
                    "from app.services.production import planned_consumption, quality_payload, stock_failures, waste_payload",
                    "from app.services.purchasing import editable_order_state, order_line_total, receive_order, receipt_state",
                    "from app.services.sales import confirm_sale, consume_reservation as consume_reserved_line, price_for_customer_type, release_reservation as release_reserved_line",
                ]
            ),
        )
        base = base.replace(
            "def test_product_price_and_waste_update_inventory_without_hito5_scope():",
            "def test_product_price_and_waste_update_inventory_with_hito5_scope():",
        )
        base = base.replace(
            'assert client.get("/api/v1/sales", headers=headers).status_code == 404',
            'assert client.get("/api/v1/sales", headers=headers).status_code == 200',
        )
        base = base.replace(
            'assert client.get("/api/v1/customers", headers=headers).status_code == 404',
            'assert client.get("/api/v1/customers", headers=headers).status_code == 200',
        )
        base = base.replace(
            'assert client.get("/api/v1/purchase-orders", headers=headers).status_code == 404',
            'assert client.get("/api/v1/purchase-orders", headers=headers).status_code == 200',
        )
        return (
            base
            + "\n\n"
            + dedent(
                """

                def _create_customer(headers, suffix, tipo_cliente="minorista"):
                    created = client.post(
                        "/api/v1/customers",
                        json={
                            "nombre": f"Cliente {suffix}",
                            "identificador_fiscal": f"CL-{suffix}",
                            "email": f"cliente{suffix.lower()}@brewmaster.local",
                            "tipo_cliente": tipo_cliente,
                            "limite_credito": 0,
                        },
                        headers=headers,
                    )
                    assert created.status_code == 200
                    return created.json()["data"]


                def _product_by_id(headers, product_id):
                    products = client.get("/api/v1/products", headers=headers)
                    assert products.status_code == 200
                    return next(item for item in products.json()["data"] if item["id"] == product_id)


                def test_sales_services_price_policy_and_customer_sale_void_flow():
                    assert price_for_customer_type(1200, 10, 12, 10800)["precio_unitario"] == 900
                    confirmed = confirm_sale(100, 20, 12, 900, 620)
                    assert confirmed["remaining_stock"] == 88
                    assert confirmed["profit"] == 3360
                    headers, _, _, presentation, recipe = _create_production_stack(stock_actual=100)
                    batch = _create_batch(headers, recipe, presentation)
                    product = _complete_batch(headers, batch["id"], units=80)["product"]
                    priced = client.put(f"/api/v1/products/{product['id']}/price", json={"precio_venta": 1000}, headers=headers)
                    assert priced.status_code == 200
                    customer = _create_customer(headers, "H5SALE001", "mayorista")
                    duplicate = client.post(
                        "/api/v1/customers",
                        json={"nombre": "Duplicado", "identificador_fiscal": customer["identificador_fiscal"], "tipo_cliente": "minorista"},
                        headers=headers,
                    )
                    assert duplicate.status_code == 422
                    sale = client.post(
                        "/api/v1/sales",
                        json={"cliente_id": customer["id"], "items": [{"product_id": product["id"], "cantidad": 12}]},
                        headers=headers,
                    )
                    assert sale.status_code == 200
                    sale_data = sale.json()["data"]
                    assert sale_data["estado"] == "confirmada"
                    assert sale_data["items"][0]["precio_unitario"] == 920
                    assert _product_by_id(headers, product["id"])["cantidad_stock"] == 68
                    fiscal_edit = client.put(
                        f"/api/v1/customers/{customer['id']}",
                        json={"identificador_fiscal": "CL-H5SALE001-NEW"},
                        headers=headers,
                    )
                    assert fiscal_edit.status_code == 422
                    product_kardex = client.get(f"/api/v1/products/{product['id']}/kardex", headers=headers)
                    assert any(item["tipo_movimiento"] == "VENTA" for item in product_kardex.json()["data"])
                    voided = client.post(f"/api/v1/sales/{sale_data['id']}/void", json={"motivo": "error de digitacion"}, headers=headers)
                    assert voided.status_code == 200
                    assert voided.json()["data"]["estado"] == "anulada"
                    assert _product_by_id(headers, product["id"])["cantidad_stock"] == 80
                    product_kardex = client.get(f"/api/v1/products/{product['id']}/kardex", headers=headers)
                    assert any(item["tipo_movimiento"] == "DEVOLUCION" for item in product_kardex.json()["data"])
                    client.patch(f"/api/v1/customers/{customer['id']}/toggle-status", headers=headers)
                    blocked = client.post(
                        "/api/v1/sales",
                        json={"cliente_id": customer["id"], "items": [{"product_id": product["id"], "cantidad": 1, "precio_unitario": 1000}]},
                        headers=headers,
                    )
                    assert blocked.status_code == 422


                def test_reservations_block_free_stock_release_and_consume_once():
                    assert release_reserved_line(5)["status"] == "liberada"
                    assert consume_reserved_line(5, 900, 620)["profit"] == 1400
                    headers, _, _, presentation, recipe = _create_production_stack(stock_actual=100)
                    batch = _create_batch(headers, recipe, presentation)
                    product = _complete_batch(headers, batch["id"], units=60)["product"]
                    priced = client.put(f"/api/v1/products/{product['id']}/price", json={"precio_venta": 900}, headers=headers)
                    assert priced.status_code == 200
                    customer = _create_customer(headers, "H5RES001", "minorista")
                    reservation = client.post(
                        "/api/v1/reservations",
                        json={
                            "cliente_id": customer["id"],
                            "product_id": product["id"],
                            "cantidad_reservada": 30,
                            "fecha_entrega_prometida": "2026-07-10",
                        },
                        headers=headers,
                    )
                    assert reservation.status_code == 200
                    blocked_sale = client.post(
                        "/api/v1/sales",
                        json={"cliente_id": customer["id"], "items": [{"product_id": product["id"], "cantidad": 60, "precio_unitario": 900}]},
                        headers=headers,
                    )
                    assert blocked_sale.status_code == 422
                    consumed = client.post(f"/api/v1/reservations/{reservation.json()['data']['id']}/consume", headers=headers)
                    assert consumed.status_code == 200
                    payload = consumed.json()["data"]
                    assert payload["reservation"]["estado"] == "consumida"
                    assert payload["sale"]["estado"] == "confirmada"
                    assert _product_by_id(headers, product["id"])["cantidad_stock"] == 30
                    release_again = client.post(f"/api/v1/reservations/{reservation.json()['data']['id']}/release", headers=headers)
                    assert release_again.status_code == 422
                    second_reservation = client.post(
                        "/api/v1/reservations",
                        json={
                            "cliente_id": customer["id"],
                            "product_id": product["id"],
                            "cantidad_reservada": 10,
                            "fecha_entrega_prometida": "2026-07-12",
                        },
                        headers=headers,
                    )
                    assert second_reservation.status_code == 200
                    released = client.post(f"/api/v1/reservations/{second_reservation.json()['data']['id']}/release", headers=headers)
                    assert released.status_code == 200
                    assert released.json()["data"]["estado"] == "liberada"


                def test_purchase_orders_send_receive_supply_kardex_and_block_over_receive():
                    assert order_line_total(10, 700) == 7000
                    assert editable_order_state("borrador") is True
                    assert receive_order(10, 4, 6)["estado"] == "recibida"
                    assert receipt_state(10, 4) == "parcialmente_recibida"
                    headers, supplier, supply, _, _ = _create_production_stack(stock_actual=2, ingredient_quantity=1)
                    order = client.post(
                        "/api/v1/purchase-orders",
                        json={
                            "proveedor_id": supplier["id"],
                            "items": [{"supply_id": supply["id"], "cantidad_solicitada": 10, "precio_unitario": 700}],
                        },
                        headers=headers,
                    )
                    assert order.status_code == 200
                    order_id = order.json()["data"]["id"]
                    assert order.json()["data"]["estado"] == "borrador"
                    sent = client.post(f"/api/v1/purchase-orders/{order_id}/send", headers=headers)
                    assert sent.status_code == 200
                    assert sent.json()["data"]["estado"] == "enviada"
                    edit_after_send = client.put(
                        f"/api/v1/purchase-orders/{order_id}",
                        json={"observacion": "no editable"},
                        headers=headers,
                    )
                    assert edit_after_send.status_code == 422
                    partial = client.post(
                        f"/api/v1/purchase-orders/{order_id}/receive",
                        json={"items": [{"supply_id": supply["id"], "cantidad_recibida": 4, "precio_unitario": 710}]},
                        headers=headers,
                    )
                    assert partial.status_code == 200
                    assert partial.json()["data"]["order"]["estado"] == "parcialmente_recibida"
                    supply_detail = client.get(f"/api/v1/supplies/{supply['id']}", headers=headers)
                    assert supply_detail.json()["data"]["stock_actual"] == 6
                    kardex = client.get(f"/api/v1/supplies/{supply['id']}/kardex", headers=headers)
                    assert any(item["tipo_movimiento"] == "ENTRADA" and item["referencia"] == f"purchase_order:{order_id}" for item in kardex.json()["data"])
                    over_receive = client.post(
                        f"/api/v1/purchase-orders/{order_id}/receive",
                        json={"items": [{"supply_id": supply["id"], "cantidad_recibida": 7, "precio_unitario": 710}]},
                        headers=headers,
                    )
                    assert over_receive.status_code == 422
                    completed = client.post(
                        f"/api/v1/purchase-orders/{order_id}/receive",
                        json={"items": [{"supply_id": supply["id"], "cantidad_recibida": 6, "precio_unitario": 710}]},
                        headers=headers,
                    )
                    assert completed.status_code == 200
                    assert completed.json()["data"]["order"]["estado"] == "recibida"
                    cancel_received = client.post(f"/api/v1/purchase-orders/{order_id}/cancel", headers=headers)
                    assert cancel_received.status_code == 422
                    client.patch(f"/api/v1/suppliers/{supplier['id']}/toggle-status", headers=headers)
                    blocked_supplier = client.post(
                        "/api/v1/purchase-orders",
                        json={
                            "proveedor_id": supplier["id"],
                            "items": [{"supply_id": supply["id"], "cantidad_solicitada": 1, "precio_unitario": 700}],
                        },
                        headers=headers,
                    )
                    assert blocked_supplier.status_code == 422
                """
            ).strip()
        )
    if (milestone_id or "").strip().upper() == "HITO-004":
        return dedent(
            """
            from fastapi.testclient import TestClient

            from app.domain.rules import (
                CostInput,
                batch_cost,
                batch_supply_consumption,
                email_status_after_attempt,
                local_secret_marker,
                normalize_email_list,
                should_send_stock_alert,
                validate_quality_result,
                waste_total,
            )
            from app.main import app
            from app.services.inventory import low_stock_items, register_supply_entry
            from app.services.notifications import MockEmailSender, process_notification
            from app.services.production import planned_consumption, quality_payload, stock_failures, waste_payload


            client = TestClient(app)
            HITO4_COUNTER = 0


            def _admin_headers():
                response = client.post("/api/v1/auth/login", json={"email": "admin@brewmaster.local", "password": "Admin123!"})
                assert response.status_code == 200
                return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


            def _create_production_stack(stock_actual=100, recipe_volume=50, ingredient_quantity=10):
                global HITO4_COUNTER
                HITO4_COUNTER += 1
                suffix = f"H4-{HITO4_COUNTER:03d}"
                headers = _admin_headers()
                supplier = client.post(
                    "/api/v1/suppliers",
                    json={"codigo": f"SUP-{suffix}", "nombre": f"Proveedor {suffix}", "email": f"proveedor{HITO4_COUNTER}@mail.local"},
                    headers=headers,
                )
                assert supplier.status_code == 200
                warehouse = client.post(
                    "/api/v1/warehouses",
                    json={"codigo": f"BOD-{suffix}", "nombre": f"Bodega {suffix}", "tipo": "insumos", "capacidad": 500},
                    headers=headers,
                )
                assert warehouse.status_code == 200
                supply = client.post(
                    "/api/v1/supplies",
                    json={
                        "codigo": f"INS-{suffix}",
                        "nombre": f"Malta {suffix}",
                        "tipo": "malta",
                        "unidad_medida": "kg",
                        "proveedor_id": supplier.json()["data"]["id"],
                        "bodega_id": warehouse.json()["data"]["id"],
                        "costo_unitario": 700,
                        "stock_minimo": 10,
                        "stock_actual": stock_actual,
                        "enable_email_alerts": True,
                        "alert_emails": [f"stock{HITO4_COUNTER}@brewmaster.local"],
                    },
                    headers=headers,
                )
                assert supply.status_code == 200
                presentation = client.post(
                    "/api/v1/presentation-types",
                    json={"nombre": f"Botella 330 {suffix}", "volumen": 330, "unidad": "ml", "costo_presentacion": 120},
                    headers=headers,
                )
                assert presentation.status_code == 200
                recipe = client.post(
                    "/api/v1/recipes",
                    json={
                        "nombre": f"Pale Ale {suffix}",
                        "tipo": "ale",
                        "abv_estimado": 5.2,
                        "volumen_por_lote": recipe_volume,
                        "ingredientes": [{"supply_id": supply.json()["data"]["id"], "cantidad": ingredient_quantity, "unidad": "kg"}],
                    },
                    headers=headers,
                )
                assert recipe.status_code == 200
                return headers, supplier.json()["data"], supply.json()["data"], presentation.json()["data"], recipe.json()["data"]


            def _create_batch(headers, recipe, presentation, liters=50):
                batch = client.post(
                    "/api/v1/batches",
                    json={
                        "recipe_id": recipe["id"],
                        "presentation_type_id": presentation["id"],
                        "cantidad_producida": liters,
                        "fecha_produccion": "2026-07-06",
                        "responsable_id": 1,
                        "horas_mano_obra": 2,
                        "kwh_consumidos": 3,
                        "litros_agua": 40,
                        "porcentaje_merma": 2,
                    },
                    headers=headers,
                )
                assert batch.status_code == 200
                return batch.json()["data"]


            def _complete_batch(headers, batch_id, liters=50, units=100):
                completed = client.post(
                    f"/api/v1/batches/{batch_id}/complete",
                    json={
                        "cantidad_producida": liters,
                        "unidades_producidas": units,
                        "horas_mano_obra": 2,
                        "tarifa_mano_obra": 500,
                        "kwh_consumidos": 3,
                        "tarifa_kwh": 100,
                        "litros_agua": 40,
                        "tarifa_litro_agua": 2,
                        "porcentaje_merma": 2,
                        "costo_indirecto": 250,
                    },
                    headers=headers,
                )
                assert completed.status_code == 200
                return completed.json()["data"]


            def test_hito3_inventory_and_smtp_regression_still_passes():
                assert normalize_email_list("Ops@Example.local, ops@example.local") == ["ops@example.local"]
                assert should_send_stock_alert(0, 10, 1) is True
                assert should_send_stock_alert(8, 10, 23) is False
                assert email_status_after_attempt(4, False) == {"status": "failed", "attempts": 5, "final_error": True}
                marker = local_secret_marker("local-only", "smtp-user")
                assert marker.startswith("local-encrypted:")
                assert "local-only" not in marker
                result = register_supply_entry(2, 3, 750, 10, None)
                assert result["movement"] == "ENTRADA"
                assert low_stock_items([{"estado": "activo", "stock_actual": 5, "stock_minimo": 10}])
                notification = {
                    "recipients": ["stock@brewmaster.local"],
                    "subject": "Stock bajo",
                    "body_html": "<p>stock</p>",
                    "status": "queued",
                    "attempts": 0,
                    "final_error": False,
                }
                sender = MockEmailSender(failures_before_success=10)
                for _ in range(5):
                    notification = process_notification(notification, sender)
                assert notification["status"] == "failed"


            def test_production_services_calculate_cost_quality_and_waste():
                recipe = {
                    "volumen_por_lote": 50,
                    "ingredientes": [{"supply_id": 7, "nombre_insumo": "Malta", "cantidad": 10, "costo_unitario": 700}],
                }
                consumption = planned_consumption(recipe, 25)
                assert consumption[0]["cantidad_usada"] == 5
                assert batch_supply_consumption(10, 50, 25) == 5
                assert not stock_failures(consumption, {7: 5})
                assert stock_failures(consumption, {7: 4})
                cost = batch_cost(CostInput(3500, 2, 500, 3, 100, 40, 2, 70, 250, 120, 50, 100))
                assert cost["total"] == 17200
                assert validate_quality_result("rechazado", "acidez") == "rechazado"
                assert quality_payload("aprobado")["resultado"] == "aprobado"
                assert waste_total(3, 700) == 2100
                assert waste_payload("insumo", 2, 700, "rotura")["movement"] == "MERMA"


            def test_complete_batch_discounts_supplies_creates_product_and_kardex():
                headers, _, supply, presentation, recipe = _create_production_stack(stock_actual=100)
                batch = _create_batch(headers, recipe, presentation)
                assert batch["estado"] == "en_elaboracion"
                blocked_recipe_update = client.put(
                    f"/api/v1/recipes/{recipe['id']}",
                    json={"nombre": f"{recipe['nombre']} editada"},
                    headers=headers,
                )
                assert blocked_recipe_update.status_code == 422
                completed = _complete_batch(headers, batch["id"])
                assert completed["batch"]["estado"] == "completado"
                assert completed["batch"]["costo_total"] > 0
                supply_detail = client.get(f"/api/v1/supplies/{supply['id']}", headers=headers)
                assert supply_detail.json()["data"]["stock_actual"] == 90
                supply_kardex = client.get(f"/api/v1/supplies/{supply['id']}/kardex", headers=headers)
                assert any(item["tipo_movimiento"] == "SALIDA_PRODUCCION" for item in supply_kardex.json()["data"])
                products = client.get("/api/v1/products", headers=headers)
                assert products.status_code == 200
                product = products.json()["data"][0]
                assert product["cantidad_stock"] == 100
                product_kardex = client.get(f"/api/v1/products/{product['id']}/kardex", headers=headers)
                assert product_kardex.status_code == 200
                assert product_kardex.json()["data"][0]["tipo_movimiento"] == "ENTRADA_PRODUCCION"
                repeated = client.post(f"/api/v1/batches/{batch['id']}/complete", json={}, headers=headers)
                assert repeated.status_code == 422


            def test_stock_shortage_blocks_completion_and_cancel_has_no_inventory_effect():
                headers, _, supply, presentation, recipe = _create_production_stack(stock_actual=4, ingredient_quantity=10)
                batch = _create_batch(headers, recipe, presentation)
                blocked = client.post(f"/api/v1/batches/{batch['id']}/complete", json={"unidades_producidas": 100}, headers=headers)
                assert blocked.status_code == 422
                cancelled = client.post(f"/api/v1/batches/{batch['id']}/cancel", headers=headers)
                assert cancelled.status_code == 200
                after_cancel = client.get(f"/api/v1/supplies/{supply['id']}", headers=headers)
                assert after_cancel.json()["data"]["stock_actual"] == 4
                after = client.post(f"/api/v1/batches/{batch['id']}/complete", json={}, headers=headers)
                assert after.status_code == 422


            def test_quality_check_is_unique_and_rejection_requires_reason():
                headers, _, _, presentation, recipe = _create_production_stack(stock_actual=100)
                batch = _create_batch(headers, recipe, presentation)
                _complete_batch(headers, batch["id"])
                rejected_without_reason = client.post(
                    f"/api/v1/batches/{batch['id']}/quality-check",
                    json={"resultado": "rechazado", "og": 1.05, "fg": 1.01, "ph": 4.2},
                    headers=headers,
                )
                assert rejected_without_reason.status_code == 422
                quality = client.post(
                    f"/api/v1/batches/{batch['id']}/quality-check",
                    json={"resultado": "aprobado", "og": 1.05, "fg": 1.01, "ph": 4.2, "nota_aroma": 8, "nota_sabor": 8},
                    headers=headers,
                )
                assert quality.status_code == 200
                duplicate = client.post(
                    f"/api/v1/batches/{batch['id']}/quality-check",
                    json={"resultado": "aprobado", "og": 1.05, "fg": 1.01, "ph": 4.2},
                    headers=headers,
                )
                assert duplicate.status_code == 422


            def test_product_price_and_waste_update_inventory_without_hito5_scope():
                headers, _, _, presentation, recipe = _create_production_stack(stock_actual=100)
                batch = _create_batch(headers, recipe, presentation)
                completed = _complete_batch(headers, batch["id"], units=80)
                product = completed["product"]
                negative_price = client.put(f"/api/v1/products/{product['id']}/price", json={"precio_venta": -1}, headers=headers)
                assert negative_price.status_code == 422
                low_price = client.put(f"/api/v1/products/{product['id']}/price", json={"precio_venta": 1}, headers=headers)
                assert low_price.status_code == 200
                assert low_price.json()["data"]["warning"] == "price_below_cost"
                missing_reason = client.post(
                    "/api/v1/waste-records",
                    json={"tipo_entidad": "producto", "entidad_id": product["id"], "cantidad_perdida": 5, "tipo_merma": "calidad"},
                    headers=headers,
                )
                assert missing_reason.status_code == 422
                waste = client.post(
                    "/api/v1/waste-records",
                    json={
                        "tipo_entidad": "producto",
                        "entidad_id": product["id"],
                        "cantidad_perdida": 5,
                        "tipo_merma": "calidad",
                        "motivo": "lote rechazado parcialmente",
                        "batch_id": batch["id"],
                    },
                    headers=headers,
                )
                assert waste.status_code == 200
                products = client.get("/api/v1/products", headers=headers)
                updated = next(item for item in products.json()["data"] if item["id"] == product["id"])
                assert updated["cantidad_stock"] == 75
                product_kardex = client.get(f"/api/v1/products/{product['id']}/kardex", headers=headers)
                assert any(item["tipo_movimiento"] == "MERMA" for item in product_kardex.json()["data"])
                assert client.get("/api/v1/sales", headers=headers).status_code == 404
                assert client.get("/api/v1/customers", headers=headers).status_code == 404
                assert client.get("/api/v1/purchase-orders", headers=headers).status_code == 404
            """
        ).strip()
    if (milestone_id or "").strip().upper() == "HITO-003":
        return dedent(
            """
            from fastapi.testclient import TestClient

            from app.domain.rules import (
                email_status_after_attempt,
                local_secret_marker,
                normalize_email_list,
                should_send_stock_alert,
            )
            from app.main import app
            from app.services.inventory import low_stock_items, register_supply_entry
            from app.services.notifications import MockEmailSender, process_notification


            client = TestClient(app)
            INVENTORY_COUNTER = 0


            def _admin_headers():
                response = client.post("/api/v1/auth/login", json={"email": "admin@brewmaster.local", "password": "Admin123!"})
                assert response.status_code == 200
                return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


            def _create_supply(stock_actual=2, stock_minimo=10, enable_email_alerts=True):
                global INVENTORY_COUNTER
                INVENTORY_COUNTER += 1
                suffix = f"H3-{INVENTORY_COUNTER:03d}"
                headers = _admin_headers()
                supplier = client.post(
                    "/api/v1/suppliers",
                    json={"codigo": f"SUP-{suffix}", "nombre": f"Proveedor {suffix}", "email": f"proveedor{INVENTORY_COUNTER}@mail.local"},
                    headers=headers,
                )
                assert supplier.status_code == 200
                warehouse = client.post(
                    "/api/v1/warehouses",
                    json={"codigo": f"BOD-{suffix}", "nombre": f"Bodega {suffix}", "tipo": "insumos", "capacidad": 500},
                    headers=headers,
                )
                assert warehouse.status_code == 200
                supply = client.post(
                    "/api/v1/supplies",
                    json={
                        "codigo": f"INS-{suffix}",
                        "nombre": f"Malta {suffix}",
                        "tipo": "malta",
                        "unidad_medida": "kg",
                        "proveedor_id": supplier.json()["data"]["id"],
                        "bodega_id": warehouse.json()["data"]["id"],
                        "costo_unitario": 700,
                        "stock_minimo": stock_minimo,
                        "stock_actual": stock_actual,
                        "enable_email_alerts": enable_email_alerts,
                        "alert_emails": [f"stock{INVENTORY_COUNTER}@brewmaster.local"],
                    },
                    headers=headers,
                )
                assert supply.status_code == 200
                return headers, supplier.json()["data"], supply.json()["data"]


            def test_inventory_rules_cover_stock_alert_and_retry_policy():
                assert normalize_email_list("Ops@Example.local, ops@example.local") == ["ops@example.local"]
                assert should_send_stock_alert(0, 10, 1) is True
                assert should_send_stock_alert(8, 10, 23) is False
                assert should_send_stock_alert(8, 10, 24) is True
                assert email_status_after_attempt(4, False) == {"status": "failed", "attempts": 5, "final_error": True}
                marker = local_secret_marker("local-only", "smtp-user")
                assert marker.startswith("local-encrypted:")
                assert "local-only" not in marker


            def test_inventory_service_registers_entry_and_low_stock():
                result = register_supply_entry(2, 3, 750, 10, None)
                assert result["stock_actual"] == 5
                assert result["movement"] == "ENTRADA"
                assert result["alert_needed"] is True
                assert low_stock_items([{"estado": "activo", "stock_actual": 5, "stock_minimo": 10}])


            def test_notification_service_retries_until_final_failure():
                notification = {
                    "recipients": ["stock@brewmaster.local"],
                    "subject": "Stock bajo",
                    "body_html": "<p>stock</p>",
                    "status": "queued",
                    "attempts": 0,
                    "final_error": False,
                }
                sender = MockEmailSender(failures_before_success=10)
                for _ in range(5):
                    notification = process_notification(notification, sender)
                assert notification["status"] == "failed"
                assert notification["attempts"] == 5
                assert notification["final_error"] is True


            def test_supply_entry_updates_stock_writes_kardex_and_queues_alert():
                headers, supplier, supply = _create_supply()
                created = client.post(
                    "/api/v1/supply-entries",
                    json={"supply_id": supply["id"], "cantidad": 3, "costo_unitario": 720, "proveedor_id": supplier["id"], "referencia": "FAC-LOCAL"},
                    headers=headers,
                )
                assert created.status_code == 200
                assert created.json()["data"]["stock_actual"] == 5
                assert created.json()["data"]["movement"]["tipo_movimiento"] == "ENTRADA"
                kardex = client.get(f"/api/v1/supplies/{supply['id']}/kardex", headers=headers)
                assert kardex.status_code == 200
                assert kardex.json()["data"][0]["saldo_resultante"] == 5
                low_stock = client.get("/api/v1/supplies/low-stock", headers=headers)
                assert low_stock.status_code == 200
                assert any(item["id"] == supply["id"] for item in low_stock.json()["data"])
                notifications = client.get("/api/v1/notifications", headers=headers)
                assert notifications.status_code == 200
                assert any(item["supply_id"] == supply["id"] and item["status"] == "queued" for item in notifications.json()["data"])


            def test_stock_recovery_resets_alert_and_inactive_supply_blocks_entry():
                headers, supplier, supply = _create_supply(stock_actual=1, stock_minimo=5)
                recovered = client.post(
                    "/api/v1/supply-entries",
                    json={"supply_id": supply["id"], "cantidad": 10, "costo_unitario": 710, "proveedor_id": supplier["id"]},
                    headers=headers,
                )
                assert recovered.status_code == 200
                detail = client.get(f"/api/v1/supplies/{supply['id']}", headers=headers)
                assert detail.json()["data"]["stock_actual"] == 11
                assert detail.json()["data"].get("last_alert_sent_at") is None
                client.patch(f"/api/v1/supplies/{supply['id']}/toggle-status", headers=headers)
                blocked = client.post(
                    "/api/v1/supply-entries",
                    json={"supply_id": supply["id"], "cantidad": 1, "costo_unitario": 700, "proveedor_id": supplier["id"]},
                    headers=headers,
                )
                assert blocked.status_code == 422


            def test_smtp_configuration_is_sanitized_and_test_is_local_only():
                headers = _admin_headers()
                saved = client.put(
                    "/api/v1/settings/smtp",
                    json={
                        "host": "smtp.local",
                        "port": 2525,
                        "username": "alerts",
                        "password": "local-only",
                        "from_email": "alerts@brewmaster.local",
                        "use_tls": True,
                    },
                    headers=headers,
                )
                assert saved.status_code == 200
                assert saved.json()["data"]["configured"] is True
                assert "password" not in saved.json()["data"]
                fetched = client.get("/api/v1/settings/smtp", headers=headers)
                assert fetched.status_code == 200
                assert fetched.json()["data"]["secret_configured"] is True
                test = client.post(
                    "/api/v1/settings/smtp/test",
                    json={"recipient": "qa@brewmaster.local"},
                    headers=headers,
                )
                assert test.status_code == 200
                payload = test.json()["data"]
                assert payload["mocked"] is True
                assert payload["delivered"] is False
                assert payload["notification"]["transport"] == "mock_local"
            """
        ).strip()
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
    if blueprint and blueprint.get("milestone_id") == "HITO-002":
        return dedent(
            """
            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito2_catalog_preserves_foundations_and_adds_only_masters():
                paths = {route["path"] for route in ROUTE_CATALOG}
                assert len(ROUTE_CATALOG) == 32
                assert all(path.startswith("/api/v1") for path in paths)
                assert {
                    "/api/v1/auth/login",
                    "/api/v1/auth/me",
                    "/api/v1/users",
                    "/api/v1/audit-logs",
                    "/api/v1/suppliers",
                    "/api/v1/supplies",
                    "/api/v1/supplies/{id}",
                    "/api/v1/warehouses",
                    "/api/v1/recipes",
                    "/api/v1/recipes/{id}/clone",
                    "/api/v1/presentation-types",
                } <= paths
                assert not any(path.startswith("/api/v1/supply-entries") for path in paths)
                assert "/api/v1/supplies/{id}/kardex" not in paths
                assert "/api/v1/supplies/low-stock" not in paths
                assert not any(path.startswith("/api/v1/batches") for path in paths)
                assert not any(path.startswith("/api/v1/products") for path in paths)
                assert not any(path.startswith("/api/v1/sales") for path in paths)
                assert not any(path.startswith("/api/v1/customers") for path in paths)
                assert not any(path.startswith("/api/v1/purchase-orders") for path in paths)
                assert not any("{resource}" in path for path in paths)


            def test_hito2_screens_are_foundation_plus_masters():
                assert {screen["id"] for screen in SCREEN_CATALOG} == {
                    "P-01",
                    "P-02",
                    "P-04",
                    "P-05",
                    "P-08",
                    "P-09",
                    "P-10",
                    "P-11",
                    "P-12",
                    "P-13",
                    "P-30",
                }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-003":
        return dedent(
            """
            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito3_catalog_preserves_hito1_hito2_and_adds_inventory_only():
                paths = {route["path"] for route in ROUTE_CATALOG}
                assert len(ROUTE_CATALOG) == 40
                assert all(path.startswith("/api/v1") for path in paths)
                assert {
                    "/api/v1/auth/login",
                    "/api/v1/auth/me",
                    "/api/v1/users",
                    "/api/v1/suppliers",
                    "/api/v1/supplies",
                    "/api/v1/supplies/{id}",
                    "/api/v1/warehouses",
                    "/api/v1/recipes",
                    "/api/v1/presentation-types",
                    "/api/v1/supplies/{id}/kardex",
                    "/api/v1/supplies/low-stock",
                    "/api/v1/supply-entries",
                    "/api/v1/settings/smtp",
                    "/api/v1/settings/smtp/test",
                    "/api/v1/notifications",
                } <= paths
                assert not any(path.startswith("/api/v1/batches") for path in paths)
                assert not any(path.startswith("/api/v1/products") for path in paths)
                assert not any(path.startswith("/api/v1/sales") for path in paths)
                assert not any(path.startswith("/api/v1/customers") for path in paths)
                assert not any(path.startswith("/api/v1/purchase-orders") for path in paths)
                assert not any(path.startswith("/api/v1/reports") for path in paths)
                assert not any(path.startswith("/api/v1/equipment") for path in paths)
                assert not any(path.startswith("/api/v1/expenses") for path in paths)
                assert not any(path.startswith("/api/v1/monthly-goals") for path in paths)
                assert not any("{resource}" in path for path in paths)


            def test_hito3_screens_are_foundation_masters_and_inventory():
                assert {screen["id"] for screen in SCREEN_CATALOG} == {
                    "P-01",
                    "P-02",
                    "P-04",
                    "P-05",
                    "P-06",
                    "P-07",
                    "P-08",
                    "P-09",
                    "P-10",
                    "P-11",
                    "P-12",
                    "P-13",
                    "P-30",
                }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-004":
        return dedent(
            """
            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito4_catalog_preserves_hito1_hito2_hito3_and_adds_production_only():
                paths = {route["path"] for route in ROUTE_CATALOG}
                assert len(ROUTE_CATALOG) == 52
                assert all(path.startswith("/api/v1") for path in paths)
                assert {
                    "/api/v1/auth/login",
                    "/api/v1/auth/me",
                    "/api/v1/users",
                    "/api/v1/suppliers",
                    "/api/v1/supplies",
                    "/api/v1/supplies/{id}",
                    "/api/v1/warehouses",
                    "/api/v1/recipes",
                    "/api/v1/presentation-types",
                    "/api/v1/supplies/{id}/kardex",
                    "/api/v1/supplies/low-stock",
                    "/api/v1/supply-entries",
                    "/api/v1/settings/smtp",
                    "/api/v1/settings/smtp/test",
                    "/api/v1/notifications",
                    "/api/v1/batches",
                    "/api/v1/batches/{id}",
                    "/api/v1/batches/{id}/complete",
                    "/api/v1/batches/{id}/cancel",
                    "/api/v1/batches/{id}/quality-check",
                    "/api/v1/products",
                    "/api/v1/products/{id}/price",
                    "/api/v1/products/{id}/kardex",
                    "/api/v1/waste-records",
                } <= paths
                assert not any(path.startswith("/api/v1/sales") for path in paths)
                assert not any(path.startswith("/api/v1/customers") for path in paths)
                assert not any(path.startswith("/api/v1/reservations") for path in paths)
                assert not any(path.startswith("/api/v1/purchase-orders") for path in paths)
                assert not any(path.startswith("/api/v1/reports") for path in paths)
                assert not any(path.startswith("/api/v1/equipment") for path in paths)
                assert not any(path.startswith("/api/v1/expenses") for path in paths)
                assert not any(path.startswith("/api/v1/monthly-goals") for path in paths)
                assert not any(path.startswith("/api/v1/dashboard") for path in paths)
                assert not any("{resource}" in path for path in paths)


            def test_hito4_screens_are_accumulated_without_hito5_or_later():
                assert {screen["id"] for screen in SCREEN_CATALOG} == {
                    "P-01",
                    "P-02",
                    "P-04",
                    "P-05",
                    "P-06",
                    "P-07",
                    "P-08",
                    "P-09",
                    "P-10",
                    "P-11",
                    "P-12",
                    "P-13",
                    "P-14",
                    "P-15",
                    "P-16",
                    "P-17",
                    "P-18",
                    "P-19",
                    "P-30",
                }
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-005":
        return dedent(
            """
            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito5_catalog_preserves_hito1_to_hito4_and_adds_sales_purchases_only():
                paths = {route["path"] for route in ROUTE_CATALOG}
                assert len(ROUTE_CATALOG) == 71
                assert all(path.startswith("/api/v1") for path in paths)
                assert {
                    "/api/v1/auth/login",
                    "/api/v1/auth/me",
                    "/api/v1/users",
                    "/api/v1/suppliers",
                    "/api/v1/supplies",
                    "/api/v1/supplies/{id}",
                    "/api/v1/warehouses",
                    "/api/v1/recipes",
                    "/api/v1/presentation-types",
                    "/api/v1/supplies/{id}/kardex",
                    "/api/v1/supplies/low-stock",
                    "/api/v1/supply-entries",
                    "/api/v1/settings/smtp",
                    "/api/v1/settings/smtp/test",
                    "/api/v1/notifications",
                    "/api/v1/batches",
                    "/api/v1/batches/{id}",
                    "/api/v1/batches/{id}/complete",
                    "/api/v1/batches/{id}/cancel",
                    "/api/v1/batches/{id}/quality-check",
                    "/api/v1/products",
                    "/api/v1/products/{id}/price",
                    "/api/v1/products/{id}/kardex",
                    "/api/v1/waste-records",
                    "/api/v1/customers",
                    "/api/v1/customers/{id}",
                    "/api/v1/customers/{id}/toggle-status",
                    "/api/v1/sales",
                    "/api/v1/sales/{id}/void",
                    "/api/v1/reservations",
                    "/api/v1/reservations/{id}/consume",
                    "/api/v1/reservations/{id}/release",
                    "/api/v1/purchase-orders",
                    "/api/v1/purchase-orders/{id}",
                    "/api/v1/purchase-orders/{id}/send",
                    "/api/v1/purchase-orders/{id}/receive",
                    "/api/v1/purchase-orders/{id}/cancel",
                } <= paths
                assert not any(path.startswith("/api/v1/reports") for path in paths)
                assert not any(path.startswith("/api/v1/equipment") for path in paths)
                assert not any(path.startswith("/api/v1/expenses") for path in paths)
                assert not any(path.startswith("/api/v1/monthly-goals") for path in paths)
                assert not any(path.startswith("/api/v1/dashboard") for path in paths)
                assert not any(path.startswith("/api/v1/jobs") for path in paths)
                assert not any(path.startswith("/api/v1/backups") for path in paths)
                assert not any("{resource}" in path for path in paths)


            def test_hito5_screens_are_accumulated_without_hito6_or_hito7():
                assert {screen["id"] for screen in SCREEN_CATALOG} == {
                    "P-01",
                    "P-02",
                    "P-04",
                    "P-05",
                    "P-06",
                    "P-07",
                    "P-08",
                    "P-09",
                    "P-10",
                    "P-11",
                    "P-12",
                    "P-13",
                    "P-14",
                    "P-15",
                    "P-16",
                    "P-17",
                    "P-18",
                    "P-19",
                    "P-20",
                    "P-21",
                    "P-22",
                    "P-23",
                    "P-24",
                    "P-25",
                    "P-26",
                    "P-30",
                }
                screens_by_id = {screen["id"]: screen for screen in SCREEN_CATALOG}
                assert screens_by_id["P-26"]["module"] == "Compras"
                assert "equipo" not in screens_by_id["P-26"]["name"].lower()
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-006":
        return dedent(
            """
            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito6_catalog_preserves_hito1_to_hito5_and_adds_dashboard_reports_only():
                paths = {route["path"] for route in ROUTE_CATALOG}
                assert len(ROUTE_CATALOG) == 74
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
                } <= paths
                assert not any(path.startswith("/api/v1/equipment") for path in paths)
                assert not any(path.startswith("/api/v1/expenses") for path in paths)
                assert not any(path.startswith("/api/v1/monthly-goals") for path in paths)
                assert not any(path.startswith("/api/v1/jobs") for path in paths)
                assert not any(path.startswith("/api/v1/backups") for path in paths)
                assert not any("{resource}" in path for path in paths)


            def test_hito6_screens_add_dashboard_and_reports_without_hito7_screens():
                screen_ids = {screen["id"] for screen in SCREEN_CATALOG}
                assert len(SCREEN_CATALOG) == 28
                assert {"P-03", "P-29"}.issubset(screen_ids)
                assert {"P-27", "P-28"}.isdisjoint(screen_ids)
                assert {"P-01", "P-14", "P-20", "P-26", "P-30"}.issubset(screen_ids)
                screens_by_id = {screen["id"]: screen for screen in SCREEN_CATALOG}
                assert screens_by_id["P-03"]["module"] == "Dashboard"
                assert screens_by_id["P-29"]["module"] == "Reportes"
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-007":
        return dedent(
            """
            from pathlib import Path

            from app.domain.catalog import ROUTE_CATALOG, SCREEN_CATALOG


            def test_hito7_catalog_preserves_hito1_to_hito6_and_adds_close_scope():
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


            def test_hito7_screens_are_complete_and_navigation_keeps_react_bootstrap_contract():
                screen_ids = {screen["id"] for screen in SCREEN_CATALOG}
                assert len(SCREEN_CATALOG) == 30
                assert {"P-01", "P-03", "P-14", "P-20", "P-26", "P-27", "P-28", "P-29", "P-30"}.issubset(screen_ids)
                screens_by_id = {screen["id"]: screen for screen in SCREEN_CATALOG}
                assert screens_by_id["P-27"]["module"] == "Equipos"
                assert screens_by_id["P-28"]["module"] == "Finanzas"


            def test_hito7_deployment_artifacts_are_present_without_real_secrets():
                assert Path("docker-compose.yml").exists()
                assert Path("deploy/nginx.conf").exists()
                assert Path("docs/deployment.md").exists()
                assert Path("backend/Dockerfile").exists()
                assert Path("frontend/Dockerfile").exists()
                env_example = Path(".env.example").read_text(encoding="utf-8")
                assert "setme" in env_example
                assert "AWS_SECRET_ACCESS_KEY" not in env_example
            """
        ).strip()
    if blueprint and blueprint.get("milestone_id") == "HITO-008":
        return dedent(
            """
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
                assert "replace(/\\\\:id/g" not in routes
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


def _test_master_catalog_py() -> str:
    return dedent(
        """
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
