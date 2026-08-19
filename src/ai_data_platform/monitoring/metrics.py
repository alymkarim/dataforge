from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class StageMetric:
    run_id: str
    stage: str
    status: str

    rows_in: int
    rows_out: int

    duration_seconds: float

    rejected_rows: int = 0

    started_at: str | None = None
    finished_at: str | None = None


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def append_metric(
    path: Path,
    metric: StageMetric,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                asdict(metric),
                default=str,
            )
            + "\n"
        )