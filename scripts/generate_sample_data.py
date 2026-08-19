from __future__ import annotations

import argparse
import random
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd


def generate(rows: int, output: Path, seed: int = 42) -> None:
    rng = random.Random(seed)
    now = datetime.now(UTC)
    records = []
    for _ in range(rows):
        event_type = rng.choices(["view", "click", "purchase", "login"], weights=[45, 30, 10, 15])[0]
        records.append(
            {
                "event_id": str(uuid.UUID(int=rng.getrandbits(128))),
                "user_id": f"user_{rng.randint(1, max(10, rows // 20)):05d}",
                "event_timestamp": (now - timedelta(minutes=rng.randint(0, 60 * 24 * 30))).isoformat(),
                "event_type": event_type,
                "country": rng.choice(["IE", "UK", "MY", "US", "DE", "FR"]),
                "device": rng.choice(["web", "ios", "android"]),
                "value": round(rng.uniform(10, 250), 2) if event_type == "purchase" else 0.0,
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(output, index=False)
    print(f"Generated {rows} rows at {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--output", type=Path, default=Path("data/raw/events.csv"))
    args = parser.parse_args()
    generate(args.rows, args.output)
