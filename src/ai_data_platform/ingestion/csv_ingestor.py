from __future__ import annotations

from pathlib import Path

import pandas as pd


def ingest_csv(
    source: Path,
    destination: Path,
    *,
    required_columns: list[str],
    chunk_size: int = 100_000,
) -> pd.DataFrame:
    if not source.exists():
        raise FileNotFoundError(
            f"Raw source not found: {source}"
        )

    chunks: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        source,
        chunksize=chunk_size,
        low_memory=False,
    ):
        missing = set(required_columns).difference(
            chunk.columns
        )

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        chunks.append(chunk)

    if not chunks:
        raise ValueError("Source dataset is empty.")

    frame = pd.concat(
        chunks,
        ignore_index=True,
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_parquet(
        destination,
        index=False,
    )

    return frame