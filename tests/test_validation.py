import pandas as pd

from ai_data_platform.validation.checks import validate_events


def test_invalid_event_is_quarantined() -> None:
    frame = pd.DataFrame(
        [{"event_id": "1", "user_id": "u1", "event_timestamp": "bad", "event_type": "unknown", "country": "XX", "device": "web", "value": 0}]
    )
    result = validate_events(
        frame,
        primary_key="event_id",
        timestamp_column="event_timestamp",
        max_null_rate=0.1,
        min_rows=1,
        allowed_event_types=["view"],
        accepted_countries=["IE"],
    )
    assert not result.passed
    assert result.invalid_mask is not None
    assert bool(result.invalid_mask.iloc[0])
