from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ai_data_platform.config import load_settings
from ai_data_platform.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "data" / "raw" / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="DataForge API",
    description="Backend API for the AI Data Platform.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def safe_name(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    return value.strip("-")


def find_dataset(dataset_id: str) -> Path:
    matches = list(
        UPLOAD_DIR.glob(f"{dataset_id}.*")
    )

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    return matches[0]


def load_sample(
    path: Path,
    limit: int = 10_000,
) -> pd.DataFrame:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(
            path,
            nrows=limit,
            low_memory=False,
        )

    if suffix == ".parquet":
        return pd.read_parquet(
            path,
        ).head(limit)

    if suffix == ".json":
        return pd.read_json(
            path,
        ).head(limit)

    raise HTTPException(
        status_code=400,
        detail="Unsupported dataset format.",
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "dataforge-api",
    }


@app.get("/api/datasets")
def datasets() -> list[dict[str, Any]]:
    result = []

    for path in sorted(
        UPLOAD_DIR.glob("*")
    ):
        if not path.is_file():
            continue

        result.append(
            {
                "id": path.stem,
                "filename": path.name,
                "format": (
                    path.suffix
                    .replace(".", "")
                    .upper()
                ),
                "sizeBytes": (
                    path.stat().st_size
                ),
                "status": "Uploaded",
            }
        )

    return result


@app.post("/api/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing filename.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in {
        ".csv",
        ".parquet",
        ".json",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only CSV, Parquet and "
                "JSON datasets are supported."
            ),
        )

    base = safe_name(
        Path(file.filename).stem
    )

    dataset_id = (
        f"{base}-"
        f"{uuid.uuid4().hex[:8]}"
    )

    destination = (
        UPLOAD_DIR
        / f"{dataset_id}{extension}"
    )

    try:
        with destination.open("wb") as target:
            shutil.copyfileobj(
                file.file,
                target,
            )
    finally:
        await file.close()

    return {
        "id": dataset_id,
        "filename": file.filename,
        "storedAs": destination.name,
        "sizeBytes": destination.stat().st_size,
        "status": "uploaded",
    }


@app.get("/api/datasets/{dataset_id}/profile")
def profile_dataset(
    dataset_id: str,
) -> dict[str, Any]:
    path = find_dataset(dataset_id)

    try:
        frame = load_sample(path)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Profiling failed: {exc}",
        ) from exc

    schema = []

    for column in frame.columns:
        series = frame[column]

        non_null = series.dropna()

        schema.append(
            {
                "name": column,
                "type": str(series.dtype),
                "missingPercent": round(
                    float(
                        series.isna().mean()
                        * 100
                    ),
                    2,
                ),
                "uniqueValues": int(
                    series.nunique(
                        dropna=True
                    )
                ),
                "sample": (
                    str(non_null.iloc[0])
                    if not non_null.empty
                    else None
                ),
            }
        )

    return {
        "datasetId": dataset_id,
        "filename": path.name,
        "sampleRows": len(frame),
        "columnCount": len(frame.columns),
        "schema": schema,
    }


@app.post("/api/datasets/{dataset_id}/validate")
def validate_dataset(
    dataset_id: str,
) -> dict[str, Any]:
    path = find_dataset(dataset_id)
    frame = load_sample(path)

    issues = []

    for column in frame.columns:
        null_count = int(
            frame[column].isna().sum()
        )

        if null_count:
            issues.append(
                {
                    "type": "missing_values",
                    "column": column,
                    "affectedRows": null_count,
                }
            )

    duplicate_count = int(
        frame.duplicated().sum()
    )

    if duplicate_count:
        issues.append(
            {
                "type": "duplicate_rows",
                "column": "dataset",
                "affectedRows": duplicate_count,
            }
        )

    return {
        "datasetId": dataset_id,
        "rowsChecked": len(frame),
        "columnsChecked": len(frame.columns),
        "issueCount": len(issues),
        "issues": issues,
        "status": (
            "warning"
            if issues
            else "passed"
        ),
    }

@app.post("/api/datasets/{dataset_id}/run")
def run_uploaded_dataset(
    dataset_id: str,
    domain: str = "Generic",
) -> dict[str, Any]:
    path = find_dataset(dataset_id)

    if domain.lower() == "retail":
        settings = load_settings(
            PROJECT_ROOT / "configs" / "pipeline.yml"
        )

        # Point the ecommerce pipeline at this uploaded file
        settings.paths.raw = path

        try:
            result = run_pipeline(settings)

            return {
                "status": "completed",
                "datasetId": dataset_id,
                "domain": domain,
                "result": result,
            }

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc

    # Generic fallback
    frame = load_sample(
        path,
        limit=100_000,
    )

    return {
        "status": "completed",
        "datasetId": dataset_id,
        "domain": domain,
        "mode": "generic",
        "rowsProfiled": len(frame),
        "columns": len(frame.columns),
        "message": (
            "Generic dataset processing completed. "
            "Gold and ML outputs are only available "
            "for supported domain pipelines."
        ),
    }

@app.post("/api/pipeline/run")
def run_configured_pipeline() -> dict[str, Any]:
    try:
        settings = load_settings(
            PROJECT_ROOT
            / "configs"
            / "pipeline.yml"
        )

        result = run_pipeline(settings)

        return {
            "status": "completed",
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc