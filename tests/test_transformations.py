import pandas as pd

from ai_data_platform.transformation.events import build_daily_features, clean_events


def test_clean_and_build_features() -> None:
    frame = pd.DataFrame(
        [
            {"event_id": "1", "user_id": "u1", "event_timestamp": "2026-01-01T10:00:00Z", "event_type": " Click ", "country": "ie", "device": "Web", "value": 0},
            {"event_id": "2", "user_id": "u1", "event_timestamp": "2026-01-01T10:05:00Z", "event_type": "purchase", "country": "IE", "device": "ios", "value": 25},
        ]
    )
    clean = clean_events(frame)
    features = build_daily_features(clean)
    assert clean.loc[0, "event_type"] == "click"
    assert features.loc[0, "event_count"] == 2
    assert features.loc[0, "purchase_count"] == 1
    assert features.loc[0, "total_value"] == 25
