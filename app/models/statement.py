"""
Statement-level metadata and response models.
Includes validation reporting models.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.transaction import ClosedPosition


class ValidationWarning(BaseModel):
    """
    Detailed warning describing numerical or chronological inconsistencies.
    """
    position_id: str | None = Field(None, description="Position ID associated with the warning")
    field: str = Field(..., description="Field name where discrepancy was detected")
    message: str = Field(..., description="Human-readable explanation of the issue")
    expected_value: str | None = Field(None, description="Expected calculated value")
    actual_value: str | None = Field(None, description="Reported value from statement")

class StatementMetadata(BaseModel):
    """
    Header metadata from the broker statement.
    """
    broker_name: str | None = Field(default="XTB", description="Identified broker name")
    account_currency: str | None = Field(default="PLN", description="Base currency of the broker account")
    period_start: date | None = Field(None, description="Start date of statement period")
    period_end: date | None = Field(None, description="End date of statement period")
    generation_date: datetime | None = Field(None, description="Report generation timestamp")

class StatementExtractionResponse(BaseModel):
    """
    Final standardized API response returned by the IDP service.
    """
    metadata: StatementMetadata = Field(default_factory=StatementMetadata)
    positions: list[ClosedPosition] = Field(default_factory=list, description="Extracted closed positions")
    total_positions: int = Field(default=0, description="Total number of extracted positions")
    is_valid: bool = Field(default=True, description="True if all positions passed mathematical validation")
    validation_warnings: list[ValidationWarning] = Field(
        default_factory=list,
        description="List of detected anomalies or mathematical discrepancies",
    )
