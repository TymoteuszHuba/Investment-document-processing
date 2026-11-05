"""
Unit tests for domain models (ClosedPosition, StatementMetadata, StatementExtractionResponse).
"""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.statement import StatementExtractionResponse, StatementMetadata
from app.models.transaction import ClosedPosition, PositionType


def test_closed_position_valid():
    pos = ClosedPosition(
        position_id="4829104",
        ticker="AAPL.US",
        position_type=PositionType.BUY,
        volume=Decimal("10.00"),
        open_time=datetime(2024, 1, 8, 15, 45, 10),
        open_price=Decimal("185.50"),
        close_time=datetime(2024, 1, 22, 17, 10, 0),
        close_price=Decimal("195.00"),
        currency="USD",
        commission=Decimal("0.00"),
        gross_profit=Decimal("95.00"),
    )
    assert pos.ticker == "AAPL.US"
    assert pos.volume == Decimal("10.00")
    assert pos.is_valid is True

def test_closed_position_invalid_volume():
    with pytest.raises(ValidationError):
        ClosedPosition(
            position_id="1",
            ticker="AAPL.US",
            position_type=PositionType.BUY,
            volume=Decimal("-5.00"),  # Must be gt 0
            open_time=datetime(2024, 1, 8, 15, 0),
            open_price=Decimal(100),
            close_time=datetime(2024, 1, 9, 15, 0),
            close_price=Decimal(110),
            currency="USD",
            gross_profit=Decimal(50),
        )

def test_closed_position_invalid_price():
    with pytest.raises(ValidationError):
        ClosedPosition(
            position_id="1",
            ticker="AAPL.US",
            position_type=PositionType.BUY,
            volume=Decimal("5.00"),
            open_time=datetime(2024, 1, 8, 15, 0),
            open_price=Decimal("0.00"),  # Must be gt 0
            close_time=datetime(2024, 1, 9, 15, 0),
            close_price=Decimal(110),
            currency="USD",
            gross_profit=Decimal(50),
        )

def test_statement_extraction_response_defaults():
    resp = StatementExtractionResponse()
    assert resp.total_positions == 0
    assert resp.is_valid is True
    assert resp.positions == []
    assert resp.validation_warnings == []
    assert isinstance(resp.metadata, StatementMetadata)
