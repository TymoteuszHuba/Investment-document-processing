"""
Financial Validator Service.
Performs hard mathematical and chronological consistency checks on extracted positions
using Decimal precision, detecting LLM numerical hallucinations or statement anomalies.
"""

from decimal import Decimal

from app.models.statement import StatementExtractionResponse, ValidationWarning
from app.models.transaction import ClosedPosition, PositionType


class FinancialValidator:
    """
    Validates extracted financial transactions for mathematical correctness,
    chronological validity, and logical consistency.
    """

    DEFAULT_TOLERANCE = Decimal("0.05")

    @classmethod
    def validate_position(
        cls,
        position: ClosedPosition,
        tolerance: Decimal = DEFAULT_TOLERANCE,
    ) -> tuple[ClosedPosition, list[ValidationWarning]]:
        """
        Validates an individual closed position.
        
        Args:
            position: The ClosedPosition to validate.
            tolerance: Permissible rounding deviation in currency units (default: 0.05).
            
        Returns:
            Tuple of (updated ClosedPosition with calculated fields, list of warnings).
        """
        warnings: list[ValidationWarning] = []
        is_valid = True

        # 1. Chronological check: close_time must be >= open_time
        if position.close_time < position.open_time:
            warnings.append(
                ValidationWarning(
                    position_id=position.position_id,
                    field="close_time",
                    message="Position close time precedes open time.",
                    expected_value=f">= {position.open_time.isoformat()}",
                    actual_value=position.close_time.isoformat(),
                )
            )
            is_valid = False

        # 2. Mathematical check: Profit calculation based on direction
        if position.position_type == PositionType.BUY:
            expected_profit = (position.close_price - position.open_price) * position.volume
        else:
            expected_profit = (position.open_price - position.close_price) * position.volume

        # Round calculated profit to 2 decimal places for comparison
        expected_profit = round(expected_profit, 2)
        diff = abs(expected_profit - position.gross_profit)

        if diff > tolerance:
            warnings.append(
                ValidationWarning(
                    position_id=position.position_id,
                    field="gross_profit",
                    message=(
                        f"Gross profit mismatch for {position.ticker}: reported {position.gross_profit} {position.currency}, "
                        f"calculated {expected_profit} {position.currency} (discrepancy: {diff})."
                    ),
                    expected_value=str(expected_profit),
                    actual_value=str(position.gross_profit),
                )
            )
            is_valid = False

        # Attach calculated profit and validation state
        position.calculated_profit = expected_profit
        position.is_valid = is_valid

        return position, warnings

    @classmethod
    def validate_statement(
        cls,
        statement: StatementExtractionResponse,
        tolerance: Decimal = DEFAULT_TOLERANCE,
    ) -> StatementExtractionResponse:
        """
        Validates all positions within a statement response and updates statement-level validity.
        
        Args:
            statement: StatementExtractionResponse containing extracted positions.
            tolerance: Permissible rounding deviation.
            
        Returns:
            Validated StatementExtractionResponse with aggregated warnings and status.
        """
        all_warnings: list[ValidationWarning] = list(statement.validation_warnings)
        validated_positions: list[ClosedPosition] = []

        for pos in statement.positions:
            validated_pos, pos_warnings = cls.validate_position(pos, tolerance=tolerance)
            validated_positions.append(validated_pos)
            all_warnings.extend(pos_warnings)

        statement.positions = validated_positions
        statement.total_positions = len(validated_positions)
        statement.validation_warnings = all_warnings
        statement.is_valid = (
            all(p.is_valid for p in validated_positions) and len(all_warnings) == 0
        )

        return statement
