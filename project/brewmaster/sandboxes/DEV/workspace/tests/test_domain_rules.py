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
