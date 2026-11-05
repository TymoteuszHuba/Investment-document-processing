"""
Transaction and position data models representing closed broker positions.
Uses Decimal precision for accurate financial operations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class PositionType(str, Enum):
    """Position execution direction."""
    BUY = "BUY"
    SELL = "SELL"

class ClosedPosition(BaseModel):
    """
    Represents a closed stock or ETF position extracted from a broker statement.
    Matches the structure observed in XTB and European broker statements.
    """
    position_id: str = Field(..., description="Unique position identifier from broker")
    ticker: str = Field(..., description="Instrument symbol (e.g. AAPL.US, VWCE.DE, PKN.PL)")
    position_type: PositionType = Field(..., description="Order type: BUY or SELL")
    volume: Decimal = Field(..., gt=0, description="Number of shares/units traded")
    open_time: datetime = Field(..., description="Timestamp of position opening")
    open_price: Decimal = Field(..., gt=0, description="Opening price per share")
    close_time: datetime = Field(..., description="Timestamp of position closing")
    close_price: Decimal = Field(..., gt=0, description="Closing price per share")
    currency: str = Field(..., description="Currency of instrument pricing (e.g. USD, EUR, PLN)")
    commission: Decimal = Field(default=Decimal("0.00"), ge=0, description="Transaction fee or commission")
    gross_profit: Decimal = Field(..., description="Gross profit or loss reported on statement")
    calculated_profit: Decimal | None = Field(None, description="Profit calculated by mathematical validation")
    is_valid: bool = Field(default=True, description="Indicates if position passed validation checks")
