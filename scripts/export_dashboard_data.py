from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
OUTPUT_ROOT = FRONTEND_DIR / "public" / "demo-data"


def write_json(
    path: Path,
    data: Any,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"✓ {path.relative_to(PROJECT_ROOT)}")


def read_parquet(
    path: Path,
) -> pd.DataFrame:
    if not path.exists():
        print(f"⚠ Missing: {path}")
        return pd.DataFrame()

    return pd.read_parquet(path)


def read_metrics(
    path: Path,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    for line in path.read_text(
        encoding="utf-8",
    ).splitlines():
        line = line.strip()

        if not line:
            continue

        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return rows


def get_latest_run_id(
    metrics: list[dict[str, Any]],
) -> str | None:
    if not metrics:
        return None

    return metrics[-1].get("run_id")


def get_latest_run_metrics(
    metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_run = get_latest_run_id(metrics)

    if latest_run is None:
        return []

    return [
        row
        for row in metrics
        if row.get("run_id") == latest_run
    ]


def export_pipeline_summary(
    *,
    bronze: pd.DataFrame,
    silver: pd.DataFrame,
    daily: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
    metrics: list[dict[str, Any]],
    quarantine: pd.DataFrame,
    output_dir: Path,
) -> None:
    latest_metrics = get_latest_run_metrics(metrics)

    duration = sum(
        float(row.get("duration_seconds", 0))
        for row in latest_metrics
    )

    rejected_rows = len(quarantine)

    bronze_rows = len(bronze)
    silver_rows = len(silver)

    quality_score = (
        (silver_rows / bronze_rows * 100)
        if bronze_rows
        else 100.0
    )

    summary = {
        "pipelineStatus": "Completed",
        "lastRun": datetime.now().isoformat(),
        "durationSeconds": round(duration, 3),
        "bronzeRows": bronze_rows,
        "silverRows": silver_rows,
        "goldRows": (
            len(daily)
            + len(products)
            + len(customers)
        ),
        "rejectedRows": rejected_rows,
        "qualityScore": round(
            quality_score,
            2,
        ),
    }

    write_json(
        output_dir / "pipeline-summary.json",
        summary,
    )


def export_daily_metrics(
    daily: pd.DataFrame,
    output_dir: Path,
) -> None:
    if daily.empty:
        write_json(
            output_dir / "daily-metrics.json",
            [],
        )
        return

    frame = daily.copy()

    frame["event_date"] = (
        frame["event_date"]
        .astype(str)
    )

    rows = []

    for _, row in frame.iterrows():
        rows.append(
            {
                "date": row["event_date"],
                "revenue": round(
                    float(row["revenue"]),
                    2,
                ),
                "purchases": int(
                    row["purchases"]
                ),
                "activeUsers": int(
                    row["active_users"]
                ),
                "conversionRate": float(
                    row["conversion_rate"]
                ),
                "views": int(
                    row["views"]
                ),
                "carts": int(
                    row["cart_events"]
                ),
            }
        )

    write_json(
        output_dir / "daily-metrics.json",
        rows,
    )


def export_product_metrics(
    products: pd.DataFrame,
    output_dir: Path,
) -> None:
    if products.empty:
        write_json(
            output_dir / "product-metrics.json",
            [],
        )
        return

    rows = []

    for _, row in (
        products
        .sort_values(
            "revenue",
            ascending=False,
        )
        .head(100)
        .iterrows()
    ):
        brand = (
            None
            if pd.isna(row["brand"])
            else str(row["brand"])
        )

        category = (
            None
            if pd.isna(row["category_code"])
            else str(row["category_code"])
        )

        rows.append(
            {
                "productId": int(
                    row["product_id"]
                ),
                "brand": brand or "Unknown",
                "category": (
                    category
                    or "Uncategorised"
                ),
                "views": int(
                    row["views"]
                ),
                "carts": int(
                    row["cart_events"]
                ),
                "purchases": int(
                    row["purchases"]
                ),
                "revenue": round(
                    float(row["revenue"]),
                    2,
                ),
                "conversionRate": float(
                    row["conversion_rate"]
                ),
            }
        )

    write_json(
        output_dir / "product-metrics.json",
        rows,
    )


def export_sample_events(
    silver: pd.DataFrame,
    output_dir: Path,
) -> None:
    if silver.empty:
        write_json(
            output_dir / "sample-events.json",
            [],
        )
        return

    sample = silver.head(100).copy()

    sample["event_time"] = (
        sample["event_time"]
        .astype(str)
    )

    rows = []

    for _, row in sample.iterrows():
        category = (
            None
            if pd.isna(row["category_code"])
            else str(row["category_code"])
        )

        brand = (
            None
            if pd.isna(row["brand"])
            else str(row["brand"])
        )

        session = (
            ""
            if pd.isna(row["user_session"])
            else str(row["user_session"])
        )

        rows.append(
            {
                "event_time": str(
                    row["event_time"]
                ),
                "event_type": str(
                    row["event_type"]
                ),
                "product_id": int(
                    row["product_id"]
                ),
                "category_code": category,
                "brand": brand,
                "price": float(
                    row["price"]
                ),
                "user_id": int(
                    row["user_id"]
                ),
                "user_session": session,
            }
        )

    write_json(
        output_dir / "sample-events.json",
        rows,
    )


def export_quality_results(
    *,
    bronze: pd.DataFrame,
    silver: pd.DataFrame,
    quarantine: pd.DataFrame,
    output_dir: Path,
) -> None:
    duplicate_count = 0
    invalid_price_count = 0
    invalid_timestamp_count = 0
    invalid_event_count = 0

    if not bronze.empty:
        duplicate_count = int(
            bronze.duplicated(
                subset=[
                    "event_time",
                    "event_type",
                    "product_id",
                    "user_id",
                    "user_session",
                ]
            ).sum()
        )

        price = pd.to_numeric(
            bronze["price"],
            errors="coerce",
        )

        invalid_price_count = int(
            (
                price.isna()
                | (price < 0)
            ).sum()
        )

        timestamps = pd.to_datetime(
            bronze["event_time"],
            errors="coerce",
            utc=True,
        )

        invalid_timestamp_count = int(
            timestamps.isna().sum()
        )

        invalid_event_count = int(
            (
                ~bronze["event_type"].isin(
                    [
                        "view",
                        "cart",
                        "remove_from_cart",
                        "purchase",
                    ]
                )
            ).sum()
        )

    quality = [
        {
            "check": "Required columns",
            "column": "dataset",
            "status": "passed",
            "affectedRows": 0,
            "description": (
                "All required ecommerce "
                "fields are present."
            ),
        },
        {
            "check": "Duplicate events",
            "column": "composite key",
            "status": (
                "warning"
                if duplicate_count
                else "passed"
            ),
            "affectedRows": duplicate_count,
            "description": (
                "Duplicate ecommerce "
                "events are quarantined."
            ),
        },
        {
            "check": "Valid timestamp",
            "column": "event_time",
            "status": (
                "warning"
                if invalid_timestamp_count
                else "passed"
            ),
            "affectedRows": (
                invalid_timestamp_count
            ),
            "description": (
                "Event timestamps must "
                "parse as UTC dates."
            ),
        },
        {
            "check": "Positive price",
            "column": "price",
            "status": (
                "warning"
                if invalid_price_count
                else "passed"
            ),
            "affectedRows": (
                invalid_price_count
            ),
            "description": (
                "Price values must be "
                "numeric and non-negative."
            ),
        },
        {
            "check": "Known event type",
            "column": "event_type",
            "status": (
                "warning"
                if invalid_event_count
                else "passed"
            ),
            "affectedRows": (
                invalid_event_count
            ),
            "description": (
                "Only supported ecommerce "
                "event types are accepted."
            ),
        },
        {
            "check": "Silver retention",
            "column": "dataset",
            "status": "passed",
            "affectedRows": (
                len(bronze) - len(silver)
            ),
            "description": (
                f"{len(silver):,} trusted "
                "records remained after "
                "validation."
            ),
        },
    ]

    write_json(
        output_dir / "quality-results.json",
        quality,
    )


def export_quarantine(
    quarantine: pd.DataFrame,
    output_dir: Path,
) -> None:
    if quarantine.empty:
        write_json(
            output_dir
            / "quarantine-records.json",
            [],
        )
        return

    rows = []

    for index, (_, row) in enumerate(
        quarantine.head(100).iterrows(),
        start=1,
    ):
        raw_reason = row.get(
            "validation_reason",
            "validation_failed",
        )

        reason = (
            str(raw_reason)
            .replace("_", " ")
            .title()
        )

        details = [
            item.replace("_", " ").title()
            for item in str(raw_reason).split(",")
            if item
        ]

        rows.append(
            {
                "id": f"q-{index:04d}",
                "reason": reason,
                "event_time": (
                    None
                    if pd.isna(
                        row.get("event_time")
                    )
                    else str(
                        row.get("event_time")
                    )
                ),
                "event_type": (
                    None
                    if pd.isna(
                        row.get("event_type")
                    )
                    else str(
                        row.get("event_type")
                    )
                ),
                "product_id": (
                    None
                    if pd.isna(
                        row.get("product_id")
                    )
                    else int(
                        row.get("product_id")
                    )
                ),
                "price": (
                    None
                    if pd.isna(
                        row.get("price")
                    )
                    else float(
                        row.get("price")
                    )
                ),
                "user_id": (
                    None
                    if pd.isna(
                        row.get("user_id")
                    )
                    else int(
                        row.get("user_id")
                    )
                ),
                "details": details,
            }
        )

    write_json(
        output_dir
        / "quarantine-records.json",
        rows,
    )


def export_pipeline_runs(
    metrics: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    grouped: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for metric in metrics:
        run_id = metric.get("run_id")

        if run_id:
            grouped[run_id].append(
                metric
            )

    runs = []

    for run_id, stages in reversed(
        list(grouped.items())
    ):
        if not stages:
            continue

        duration = sum(
            float(
                stage.get(
                    "duration_seconds",
                    0,
                )
            )
            for stage in stages
        )

        rows = max(
            (
                int(
                    stage.get(
                        "rows_in",
                        0,
                    )
                )
                for stage in stages
            ),
            default=0,
        )

        started_at = next(
            (
                stage.get(
                    "started_at"
                )
                for stage in stages
                if stage.get(
                    "started_at"
                )
            ),
            None,
        )

        finished_at = next(
            (
                stage.get(
                    "finished_at"
                )
                for stage in reversed(
                    stages
                )
                if stage.get(
                    "finished_at"
                )
            ),
            None,
        )

        has_failure = any(
            stage.get("status")
            == "failed"
            for stage in stages
        )

        has_warning = any(
            stage.get("status")
            == "warning"
            for stage in stages
        )

        status = (
            "Failed"
            if has_failure
            else "Completed"
        )

        rejected_rows = sum(
            int(
                stage.get(
                    "rejected_rows",
                    0,
                )
            )
            for stage in stages
        )

        runs.append(
            {
                "id": run_id,
                "startedAt": (
                    started_at
                    or "Unknown"
                ),
                "finishedAt": (
                    finished_at
                    or "Unknown"
                ),
                "duration": (
                    f"{duration:.2f}s"
                ),
                "rows": rows,
                "rejectedRows": (
                    rejected_rows
                ),
                "status": status,
                "warning": has_warning,
            }
        )

    write_json(
        output_dir
        / "pipeline-runs.json",
        runs[:20],
    )


def export_run_details(
    metrics: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    stages = get_latest_run_metrics(
        metrics
    )

    if not stages:
        write_json(
            output_dir
            / "run-details.json",
            {},
        )
        return

    run_id = str(
        stages[0]["run_id"]
    )

    total_duration = sum(
        float(
            stage.get(
                "duration_seconds",
                0,
            )
        )
        for stage in stages
    )

    max_rows = max(
        (
            int(
                stage.get(
                    "rows_in",
                    0,
                )
            )
            for stage in stages
        ),
        default=0,
    )

    throughput = (
        int(
            max_rows
            / total_duration
        )
        if total_duration > 0
        else 0
    )

    started_at = next(
        (
            stage.get(
                "started_at"
            )
            for stage in stages
            if stage.get(
                "started_at"
            )
        ),
        None,
    )

    finished_at = next(
        (
            stage.get(
                "finished_at"
            )
            for stage in reversed(
                stages
            )
            if stage.get(
                "finished_at"
            )
        ),
        None,
    )

    rejected_rows = sum(
        int(
            stage.get(
                "rejected_rows",
                0,
            )
        )
        for stage in stages
    )

    run_stages = []

    for stage in stages:
        raw_status = (
            stage.get("status")
        )

        status = (
            "Failed"
            if raw_status == "failed"
            else "Completed"
        )

        run_stages.append(
            {
                "name": (
                    str(
                        stage.get(
                            "stage",
                            "unknown",
                        )
                    )
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                ),
                "durationSeconds": round(
                    float(
                        stage.get(
                            "duration_seconds",
                            0,
                        )
                    ),
                    3,
                ),
                "status": status,
                "inputRows": int(
                    stage.get(
                        "rows_in",
                        0,
                    )
                ),
                "outputRows": int(
                    stage.get(
                        "rows_out",
                        0,
                    )
                ),
                "rejectedRows": int(
                    stage.get(
                        "rejected_rows",
                        0,
                    )
                ),
                "startedAt": (
                    stage.get(
                        "started_at"
                    )
                ),
                "finishedAt": (
                    stage.get(
                        "finished_at"
                    )
                ),
            }
        )

    details = {
        "id": run_id,
        "startedAt": (
            started_at
            or "Unknown"
        ),
        "finishedAt": (
            finished_at
            or "Unknown"
        ),
        "durationSeconds": round(
            total_duration,
            3,
        ),
        "rowsPerSecond": (
            throughput
        ),
        "rejectedRows": (
            rejected_rows
        ),
        "status": (
            "Failed"
            if any(
                stage.get("status")
                == "failed"
                for stage in stages
            )
            else "Completed"
        ),
        "stages": run_stages,
    }

    write_json(
        output_dir
        / "run-details.json",
        details,
    )


def export_dataset_info(
    *,
    bronze: pd.DataFrame,
    dataset_name: str,
    output_dir: Path,
) -> None:
    schema = []

    descriptions = {
        "event_time": (
            "UTC event occurrence time"
        ),
        "event_type": (
            "view, cart, remove_from_cart "
            "or purchase"
        ),
        "product_id": (
            "Product identifier"
        ),
        "category_id": (
            "Hierarchical category identifier"
        ),
        "category_code": (
            "Readable product category path"
        ),
        "brand": (
            "Product brand"
        ),
        "price": (
            "Product/event price"
        ),
        "user_id": (
            "Anonymous customer identifier"
        ),
        "user_session": (
            "Customer session identifier"
        ),
    }

    for column in bronze.columns:
        schema.append(
            {
                "name": column,
                "type": str(
                    bronze[column].dtype
                ),
                "nullable": bool(
                    bronze[column]
                    .isna()
                    .any()
                ),
                "description": (
                    descriptions.get(
                        column,
                        "Dataset field",
                    )
                ),
            }
        )

    info = {
        "name": (
            "eCommerce Behavior Data "
            "from Multi-Category Store"
        ),
        "source": "Kaggle",
        "sourceType": "Public dataset",
        "records": len(bronze),
        "period": "October 2019 sample",
        "format": "CSV → Parquet",
        "estimatedSize": (
            f"{len(bronze):,} processed rows"
        ),
        "columns": len(
            bronze.columns
        ),
        "description": (
            "High-volume ecommerce "
            "behaviour events used to "
            "simulate a production "
            "data-engineering pipeline."
        ),
        "schema": schema,
    }

    write_json(
        output_dir / "dataset-info.json",
        info,
    )


def export_lineage(
    *,
    bronze: pd.DataFrame,
    silver: pd.DataFrame,
    daily: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
    output_dir: Path,
) -> None:
    lineage = [
        {
            "id": "raw",
            "label": (
                "Kaggle ecommerce CSV"
            ),
            "layer": "Source",
            "path": (
                "data/raw/ecommerce/"
                "sample-multiday.csv"
            ),
            "rows": len(bronze),
            "description": (
                "External ecommerce "
                "behaviour source."
            ),
            "transformations": [],
        },
        {
            "id": "bronze",
            "label": (
                "Bronze events"
            ),
            "layer": "Bronze",
            "path": (
                "data/bronze/ecommerce/"
                "events.parquet"
            ),
            "rows": len(bronze),
            "description": (
                "Immutable source-preserving "
                "Parquet layer."
            ),
            "transformations": [
                "CSV ingestion",
                "Parquet conversion",
                "Source schema verification",
            ],
        },
        {
            "id": "silver",
            "label": (
                "Silver events"
            ),
            "layer": "Silver",
            "path": (
                "data/silver/ecommerce/"
                "events_clean.parquet"
            ),
            "rows": len(silver),
            "description": (
                "Validated and normalized "
                "event dataset."
            ),
            "transformations": [
                "Duplicate removal",
                "Timestamp parsing",
                "Event type validation",
                "Price validation",
                "String normalization",
            ],
        },
        {
            "id": "gold",
            "label": (
                "Gold analytics "
                "and features"
            ),
            "layer": "Gold",
            "path": (
                "data/gold/ecommerce/"
            ),
            "rows": (
                len(daily)
                + len(products)
                + len(customers)
            ),
            "description": (
                "Analytics and "
                "ML-ready outputs."
            ),
            "transformations": [
                "Daily KPI aggregation",
                "Product metrics",
                "Customer features",
            ],
        },
    ]

    write_json(
        output_dir / "lineage.json",
        lineage,
    )


def export_ml_readiness(
    *,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    output_dir: Path,
) -> None:
    groups = [
        {
            "name": "Customer Features",
            "description": (
                "Behavioural features for "
                "recommendation, propensity "
                "and customer modelling."
            ),
            "entity": "user_id",
            "rows": len(customers),
            "features": [
                "sessions",
                "views",
                "cart_events",
                "purchases",
                "total_spend",
                "average_order_value",
                "last_activity",
            ],
            "checks": [
                {
                    "label": (
                        "Unique entity key"
                    ),
                    "status": "passed",
                },
                {
                    "label": (
                        "Feature timestamp "
                        "available"
                    ),
                    "status": "passed",
                },
                {
                    "label": (
                        "Model-ready numeric "
                        "features"
                    ),
                    "status": "passed",
                },
            ],
        },
        {
            "name": "Product Features",
            "description": (
                "Product engagement and "
                "conversion features."
            ),
            "entity": "product_id",
            "rows": len(products),
            "features": [
                "views",
                "cart_events",
                "purchases",
                "revenue",
                "unique_users",
                "conversion_rate",
            ],
            "checks": [
                {
                    "label": (
                        "Product identifiers "
                        "available"
                    ),
                    "status": "passed",
                },
                {
                    "label": (
                        "Non-negative "
                        "aggregates"
                    ),
                    "status": "passed",
                },
                {
                    "label": (
                        "Conversion features "
                        "generated"
                    ),
                    "status": "passed",
                },
            ],
        },
    ]

    write_json(
        output_dir / "ml-readiness.json",
        groups,
    )


def get_latest_quarantine(
    quarantine_dir: Path,
) -> pd.DataFrame:
    if not quarantine_dir.exists():
        return pd.DataFrame()

    files = sorted(
        quarantine_dir.glob("*.parquet"),
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    )

    if not files:
        return pd.DataFrame()

    return pd.read_parquet(
        files[0]
    )


def export_dataset_registry(
    *,
    bronze: pd.DataFrame,
    output_dir: Path,
) -> None:
    datasets = [
        {
            "id": "ecommerce",
            "name": (
                "Ecommerce Behaviour Events"
            ),
            "domain": "Retail",
            "filename": (
                "sample-multiday.csv"
            ),
            "format": "CSV",
            "rows": len(bronze),
            "columns": len(bronze.columns),
            "size": (
                "Multi-day development sample"
            ),
            "status": "Ready",
            "lastProcessed": (
                "Latest run"
            ),
            "description": (
                "Real Kaggle ecommerce "
                "behaviour dataset processed "
                "through the data platform."
            ),
            "supportsGold": True,
            "supportsML": True,
        }
    ]

    write_json(
        output_dir / "datasets.json",
        datasets,
    )


def export_dataset(
    dataset: str,
) -> None:
    if dataset != "ecommerce":
        raise ValueError(
            "Currently supported dataset: "
            "ecommerce"
        )

    output_dir = OUTPUT_ROOT

    bronze_path = (
        DATA_DIR
        / "bronze"
        / "ecommerce"
        / "events.parquet"
    )

    silver_path = (
        DATA_DIR
        / "silver"
        / "ecommerce"
        / "events_clean.parquet"
    )

    daily_path = (
        DATA_DIR
        / "gold"
        / "ecommerce"
        / "daily_metrics.parquet"
    )

    product_path = (
        DATA_DIR
        / "gold"
        / "ecommerce"
        / "product_metrics.parquet"
    )

    customer_path = (
        DATA_DIR
        / "gold"
        / "ecommerce"
        / "customer_features.parquet"
    )

    metrics_path = (
        DATA_DIR
        / "pipeline_metrics.jsonl"
    )

    quarantine_dir = (
        DATA_DIR
        / "quarantine"
        / "ecommerce"
    )

    print()
    print(
        "Exporting ecommerce "
        "dashboard data..."
    )
    print()

    bronze = read_parquet(
        bronze_path
    )

    silver = read_parquet(
        silver_path
    )

    daily = read_parquet(
        daily_path
    )

    products = read_parquet(
        product_path
    )

    customers = read_parquet(
        customer_path
    )

    quarantine = (
        get_latest_quarantine(
            quarantine_dir
        )
    )

    metrics = read_metrics(
        metrics_path
    )

    export_pipeline_summary(
        bronze=bronze,
        silver=silver,
        daily=daily,
        products=products,
        customers=customers,
        metrics=metrics,
        quarantine=quarantine,
        output_dir=output_dir,
    )

    export_daily_metrics(
        daily,
        output_dir,
    )

    export_product_metrics(
        products,
        output_dir,
    )

    export_sample_events(
        silver,
        output_dir,
    )

    export_quality_results(
        bronze=bronze,
        silver=silver,
        quarantine=quarantine,
        output_dir=output_dir,
    )

    export_quarantine(
        quarantine,
        output_dir,
    )

    export_pipeline_runs(
        metrics,
        output_dir,
    )

    export_run_details(
        metrics,
        output_dir,
    )

    export_dataset_info(
        bronze=bronze,
        dataset_name=dataset,
        output_dir=output_dir,
    )

    export_lineage(
        bronze=bronze,
        silver=silver,
        daily=daily,
        products=products,
        customers=customers,
        output_dir=output_dir,
    )

    export_ml_readiness(
        customers=customers,
        products=products,
        output_dir=output_dir,
    )

    export_dataset_registry(
        bronze=bronze,
        output_dir=output_dir,
    )

    print()
    print(
        "✓ Dashboard export complete."
    )

    print(
        f"Output: {output_dir}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Export processed pipeline "
            "outputs for the React dashboard."
        )
    )

    parser.add_argument(
        "--dataset",
        default="ecommerce",
        choices=[
            "ecommerce",
        ],
    )

    args = parser.parse_args()

    export_dataset(
        args.dataset
    )


if __name__ == "__main__":
    main()