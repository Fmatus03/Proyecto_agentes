from __future__ import annotations

from textwrap import dedent

def _test_domain_rules_py() -> str:
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


def _test_contracts_py() -> str:
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
