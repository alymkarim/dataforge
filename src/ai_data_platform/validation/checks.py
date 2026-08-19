from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    invalid_mask: pd.Series | None = None
    reasons: pd.Series | None = None


def validate_events(
    frame: pd.DataFrame,
    *,
    timestamp_column: str,
    max_null_rate: float,
    min_rows: int,
    required_columns: list[str],
    allowed_event_types: list[str],
    positive_columns: list[str],
    nullable_columns: list[str],
) -> ValidationResult:
    errors: list[str] = []

    invalid = pd.Series(False, index=frame.index)

    reason_lists: dict[int, list[str]] = {
        int(index): []
        for index in frame.index
    }

    def add_reason(mask: pd.Series, reason: str) -> None:
        nonlocal invalid

        mask = mask.fillna(False)
        invalid |= mask

        for index in frame.index[mask]:
            reason_lists[int(index)].append(reason)

    # --------------------------------------------------
    # Row count
    # --------------------------------------------------

    if len(frame) < min_rows:
        errors.append(
            f"Row count {len(frame)} is below minimum {min_rows}"
        )

    # --------------------------------------------------
    # Required columns
    # --------------------------------------------------

    missing_columns = set(required_columns).difference(
        frame.columns
    )

    if missing_columns:
        errors.append(
            f"Missing required columns: {sorted(missing_columns)}"
        )

        all_invalid = pd.Series(
            True,
            index=frame.index,
        )

        reasons = pd.Series(
            "missing_required_columns",
            index=frame.index,
        )

        return ValidationResult(
            passed=False,
            errors=errors,
            invalid_mask=all_invalid,
            reasons=reasons,
        )

    # --------------------------------------------------
    # Duplicate events
    # --------------------------------------------------

    duplicate_columns = [
        "event_time",
        "event_type",
        "product_id",
        "user_id",
        "user_session",
    ]

    duplicate_mask = frame.duplicated(
        subset=duplicate_columns,
        keep="first",
    )

    if duplicate_mask.any():
        errors.append(
            f"Duplicate ecommerce events: {int(duplicate_mask.sum())}"
        )

        add_reason(
            duplicate_mask,
            "duplicate_event",
        )

    # --------------------------------------------------
    # Timestamp
    # --------------------------------------------------

    timestamps = pd.to_datetime(
        frame[timestamp_column],
        errors="coerce",
        utc=True,
    )

    invalid_timestamp = timestamps.isna()

    if invalid_timestamp.any():
        errors.append(
            f"Invalid timestamps: {int(invalid_timestamp.sum())}"
        )

        add_reason(
            invalid_timestamp,
            "invalid_timestamp",
        )

    # --------------------------------------------------
    # Event type
    # --------------------------------------------------

    normalized_events = (
        frame["event_type"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    invalid_event = ~normalized_events.isin(
        allowed_event_types
    )

    if invalid_event.any():
        errors.append(
            f"Unsupported event types: {int(invalid_event.sum())}"
        )

        add_reason(
            invalid_event,
            "unsupported_event_type",
        )

    # --------------------------------------------------
    # Positive numeric fields
    # --------------------------------------------------

    for column in positive_columns:
        numeric = pd.to_numeric(
            frame[column],
            errors="coerce",
        )

        invalid_numeric = (
            numeric.isna()
            | (numeric < 0)
        )

        if invalid_numeric.any():
            errors.append(
                f"Invalid {column} values: {int(invalid_numeric.sum())}"
            )

            add_reason(
                invalid_numeric,
                f"invalid_{column}",
            )

    # --------------------------------------------------
    # Required non-null fields
    # --------------------------------------------------

    required_non_null = [
        column
        for column in required_columns
        if column not in nullable_columns
    ]

    for column in required_non_null:
        null_mask = frame[column].isna()

        if null_mask.any():
            errors.append(
                f"Null required field {column}: {int(null_mask.sum())}"
            )

            add_reason(
                null_mask,
                f"missing_{column}",
            )

    # --------------------------------------------------
    # Null-rate warnings
    # --------------------------------------------------

    null_rates = frame.isna().mean()

    for column, rate in null_rates.items():
        if (
            column not in nullable_columns
            and rate > max_null_rate
        ):
            errors.append(
                f"Null rate for {column} is {rate:.2%}, "
                f"above {max_null_rate:.2%}"
            )

    reasons = pd.Series(
        {
            index: ",".join(reason_lists[int(index)])
            for index in frame.index
        }
    )

    return ValidationResult(
        passed=not invalid.any(),
        errors=errors,
        invalid_mask=invalid,
        reasons=reasons,
    )