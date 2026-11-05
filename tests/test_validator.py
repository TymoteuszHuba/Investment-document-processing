"""
Unit tests for FinancialValidator service.
"""

from datetime import datetime
from decimal import Decimal

from app.models.statement import StatementExtractionResponse
from app.models.transaction import ClosedPosition, PositionType
from app.services.validator import FinancialValidator


def test_validate_position_valid_buy():
    # 10 shares * (195.00 - 185.50) = 95.00
    pos = ClosedPosition(
        position_id="4829104",
        ticker="AAPL.US",
        position_type=PositionType.BUY,
        volume=Decimal("10.00"),
        open_time=datetime(2024, 1, 8, 15, 0),
        open_price=Decimal("185.50"),
        close_time=datetime(2024, 1, 22, 17, 0),
        close_price=Decimal("195.00"),
        currency="USD",
        gross_profit=Decimal("95.00"),
    )
    validated_pos, warnings = FinancialValidator.validate_position(pos)
    assert validated_pos.is_valid is True
    assert validated_pos.calculated_profit == Decimal("95.00")
    assert len(warnings) == 0

def test_validate_position_valid_sell():
    # Short sell: 15 shares * (215.00 - 198.00) = +255.00, or loss if closed higher
    # In XTB sample: SELL 15 shares, open 215.00, close 198.00 -> gross +255.00
    pos = ClosedPosition(
        position_id="4841209",
        ticker="TSLA.US",
        position_type=PositionType.SELL,
        volume=Decimal("15.00"),
        open_time=datetime(2024, 1, 18, 16, 0),
        open_price=Decimal("215.00"),
        close_time=datetime(2024, 1, 25, 18, 0),
        close_price=Decimal("198.00"),
        currency="USD",
        gross_profit=Decimal("255.00"),
    )
    validated_pos, warnings = FinancialValidator.validate_position(pos)
    assert validated_pos.is_valid is True
    assert validated_pos.calculated_profit == Decimal("255.00")
    assert len(warnings) == 0

def test_validate_position_hallucination_detected():
    # LLM hallucinates profit 150.00 instead of 95.00
    pos = ClosedPosition(
        position_id="4829104",
        ticker="AAPL.US",
        position_type=PositionType.BUY,
        volume=Decimal("10.00"),
        open_time=datetime(2024, 1, 8, 15, 0),
        open_price=Decimal("185.50"),
        close_time=datetime(2024, 1, 22, 17, 0),
        close_price=Decimal("195.00"),
        currency="USD",
        gross_profit=Decimal("150.00"),  # INCORRECT
    )
    validated_pos, warnings = FinancialValidator.validate_position(pos)
    assert validated_pos.is_valid is False
    assert validated_pos.calculated_profit == Decimal("95.00")
    assert len(warnings) == 1
    assert warnings[0].field == "gross_profit"
    assert warnings[0].expected_value == "95.00"
    assert warnings[0].actual_value == "150.00"

def test_validate_position_within_tolerance():
    # Difference of 0.02 (broker penny rounding) should be accepted under 0.05 default tolerance
    pos = ClosedPosition(
        position_id="1",
        ticker="VWCE.DE",
        position_type=PositionType.BUY,
        volume=Decimal("25.00"),
        open_time=datetime(2024, 1, 10, 10, 0),
        open_price=Decimal("108.20"),
        close_time=datetime(2024, 1, 29, 16, 0),
        close_price=Decimal("112.40"),
        currency="EUR",
        gross_profit=Decimal("105.02"),  # Exact is 105.00
    )
    validated_pos, warnings = FinancialValidator.validate_position(pos)
    assert validated_pos.is_valid is True
    assert len(warnings) == 0

def test_validate_position_chronology_error():
    # Close time before open time
    pos = ClosedPosition(
        position_id="1",
        ticker="PKN.PL",
        position_type=PositionType.BUY,
        volume=Decimal("100.00"),
        open_time=datetime(2024, 1, 20, 10, 0),
        open_price=Decimal("62.50"),
        close_time=datetime(2024, 1, 15, 10, 0),  # Prior to open
        close_price=Decimal("65.80"),
        currency="PLN",
        gross_profit=Decimal("330.00"),
    )
    validated_pos, warnings = FinancialValidator.validate_position(pos)
    assert validated_pos.is_valid is False
    assert any(w.field == "close_time" for w in warnings)

def test_validate_statement_aggregated():
    # Statement with 1 valid position and 1 flawed position
    pos_valid = ClosedPosition(
        position_id="1",
        ticker="AAPL.US",
        position_type=PositionType.BUY,
        volume=Decimal("10.00"),
        open_time=datetime(2024, 1, 8, 15, 0),
        open_price=Decimal("185.50"),
        close_time=datetime(2024, 1, 22, 17, 0),
        close_price=Decimal("195.00"),
        currency="USD",
        gross_profit=Decimal("95.00"),
    )
    pos_flawed = ClosedPosition(
        position_id="2",
        ticker="TSLA.US",
        position_type=PositionType.BUY,
        volume=Decimal("10.00"),
        open_time=datetime(2024, 1, 8, 15, 0),
        open_price=Decimal("200.00"),
        close_time=datetime(2024, 1, 22, 17, 0),
        close_price=Decimal("210.00"),
        currency="USD",
        gross_profit=Decimal("999.00"),  # Halucination
    )

    statement = StatementExtractionResponse(positions=[pos_valid, pos_flawed])
    validated_stmt = FinancialValidator.validate_statement(statement)

    assert validated_stmt.total_positions == 2
    assert validated_stmt.is_valid is False
    assert len(validated_stmt.validation_warnings) == 1
    assert validated_stmt.validation_warnings[0].position_id == "2"
