from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

import pandas as pd
import structlog

from ai_data_platform.config import Settings
from ai_data_platform.ingestion.csv_ingestor import (
    ingest_csv,
)
from ai_data_platform.loaders.snowflake_loader import (
    load_to_snowflake,
)
from ai_data_platform.monitoring.metrics import (
    StageMetric,
    append_metric,
)
from ai_data_platform.transformation.events import (
    build_customer_features,
    build_daily_metrics,
    build_product_metrics,
    clean_events,
)
from ai_data_platform.validation.checks import (
    validate_events,
)


logger = structlog.get_logger()


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _record(
    settings: Settings,
    metric: StageMetric,
) -> None:
    append_metric(
        settings.paths.metrics,
        metric,
    )

    logger.info(
        "pipeline_stage",
        run_id=metric.run_id,
        stage=metric.stage,
        status=metric.status,
        rows_in=metric.rows_in,
        rows_out=metric.rows_out,
        duration_seconds=metric.duration_seconds,
        rejected_rows=metric.rejected_rows,
        started_at=metric.started_at,
        finished_at=metric.finished_at,
    )


def run_pipeline(
    settings: Settings,
) -> dict[str, int | str]:
    run_id = (
        f"{settings.project.run_id_prefix}-"
        f"{uuid.uuid4().hex[:10]}"
    )

    pipeline_started_at = utc_now()

    logger.info(
        "pipeline_started",
        run_id=run_id,
        environment=settings.project.environment,
        dataset=settings.dataset.id,
        started_at=pipeline_started_at,
    )

    # ==================================================
    # BRONZE INGESTION
    # ==================================================

    stage_started_at = utc_now()
    started = time.perf_counter()

    bronze = ingest_csv(
        settings.paths.raw,
        settings.paths.bronze,
        required_columns=(
            settings.quality.required_columns
        ),
        chunk_size=(
            settings.pipeline.chunk_size
        ),
    )

    duration = (
        time.perf_counter()
        - started
    )

    stage_finished_at = utc_now()

    _record(
        settings,
        StageMetric(
            run_id=run_id,
            stage="ingestion",
            status="success",
            rows_in=len(bronze),
            rows_out=len(bronze),
            duration_seconds=duration,
            rejected_rows=0,
            started_at=stage_started_at,
            finished_at=stage_finished_at,
        ),
    )

    # ==================================================
    # VALIDATION
    # ==================================================

    stage_started_at = utc_now()
    started = time.perf_counter()

    result = validate_events(
        bronze,
        timestamp_column=(
            settings.pipeline.timestamp_column
        ),
        max_null_rate=(
            settings.quality.max_null_rate
        ),
        min_rows=(
            settings.quality.min_rows
        ),
        required_columns=(
            settings.quality.required_columns
        ),
        allowed_event_types=(
            settings.quality.allowed_event_types
        ),
        positive_columns=(
            settings.quality.positive_columns
        ),
        nullable_columns=(
            settings.quality.nullable_columns
        ),
    )

    invalid_mask = (
        result.invalid_mask
        if result.invalid_mask is not None
        else pd.Series(
            False,
            index=bronze.index,
        )
    )

    rejected = bronze.loc[
        invalid_mask
    ].copy()

    accepted = bronze.loc[
        ~invalid_mask
    ].copy()

    if (
        result.reasons is not None
        and not rejected.empty
    ):
        rejected[
            "validation_reason"
        ] = result.reasons.loc[
            rejected.index
        ]

    if not rejected.empty:
        settings.paths.quarantine.mkdir(
            parents=True,
            exist_ok=True,
        )

        rejected.to_parquet(
            settings.paths.quarantine
            / f"{run_id}.parquet",
            index=False,
        )

    duration = (
        time.perf_counter()
        - started
    )

    stage_finished_at = utc_now()

    _record(
        settings,
        StageMetric(
            run_id=run_id,
            stage="validation",
            status=(
                "success"
                if result.passed
                else "warning"
            ),
            rows_in=len(bronze),
            rows_out=len(accepted),
            duration_seconds=duration,
            rejected_rows=len(rejected),
            started_at=stage_started_at,
            finished_at=stage_finished_at,
        ),
    )

    for error in result.errors:
        logger.warning(
            "quality_issue",
            run_id=run_id,
            detail=error,
        )

    if accepted.empty:
        raise RuntimeError(
            "No valid rows remain after validation."
        )

    # ==================================================
    # SILVER
    # ==================================================

    stage_started_at = utc_now()
    started = time.perf_counter()

    silver = clean_events(
        accepted
    )

    settings.paths.silver.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    silver.to_parquet(
        settings.paths.silver,
        index=False,
    )

    duration = (
        time.perf_counter()
        - started
    )

    stage_finished_at = utc_now()

    _record(
        settings,
        StageMetric(
            run_id=run_id,
            stage="silver_transform",
            status="success",
            rows_in=len(accepted),
            rows_out=len(silver),
            duration_seconds=duration,
            rejected_rows=0,
            started_at=stage_started_at,
            finished_at=stage_finished_at,
        ),
    )

    # ==================================================
    # GOLD DAILY
    # ==================================================

    stage_started_at = utc_now()
    started = time.perf_counter()

    daily = build_daily_metrics(
        silver
    )

    settings.paths.gold_daily.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily.to_parquet(
        settings.paths.gold_daily,
        index=False,
    )

    duration = (
        time.perf_counter()
        - started
    )

    stage_finished_at = utc_now()

    _record(
        settings,
        StageMetric(
            run_id=run_id,
            stage="gold_daily",
            status="success",
            rows_in=len(silver),
            rows_out=len(daily),
            duration_seconds=duration,
            rejected_rows=0,
            started_at=stage_started_at,
            finished_at=stage_finished_at,
        ),
    )

    # ==================================================
    # GOLD PRODUCTS
    # ==================================================

    stage_started_at = utc_now()
    started = time.perf_counter()

    products = build_product_metrics(
        silver
    )

    products.to_parquet(
        settings.paths.gold_products,
        index=False,
    )

    duration = (
        time.perf_counter()
        - started
    )

    stage_finished_at = utc_now()

    _record(
        settings,
        StageMetric(
            run_id=run_id,
            stage="gold_products",
            status="success",
            rows_in=len(silver),
            rows_out=len(products),
            duration_seconds=duration,
            rejected_rows=0,
            started_at=stage_started_at,
            finished_at=stage_finished_at,
        ),
    )

    # ==================================================
    # GOLD CUSTOMERS
    # ==================================================

    stage_started_at = utc_now()
    started = time.perf_counter()

    customers = build_customer_features(
        silver
    )

    customers.to_parquet(
        settings.paths.gold_customers,
        index=False,
    )

    duration = (
        time.perf_counter()
        - started
    )

    stage_finished_at = utc_now()

    _record(
        settings,
        StageMetric(
            run_id=run_id,
            stage="gold_customers",
            status="success",
            rows_in=len(silver),
            rows_out=len(customers),
            duration_seconds=duration,
            rejected_rows=0,
            started_at=stage_started_at,
            finished_at=stage_finished_at,
        ),
    )

    # ==================================================
    # SNOWFLAKE
    # ==================================================

    if settings.snowflake.enabled:
        stage_started_at = utc_now()
        started = time.perf_counter()

        load_to_snowflake(
            daily,
            database=(
                settings.snowflake.database
            ),
            schema=(
                settings.snowflake.schema
            ),
            table=(
                settings.snowflake.daily_table
            ),
            warehouse=(
                settings.snowflake.warehouse
            ),
        )

        duration = (
            time.perf_counter()
            - started
        )

        stage_finished_at = utc_now()

        _record(
            settings,
            StageMetric(
                run_id=run_id,
                stage="snowflake_load",
                status="success",
                rows_in=len(daily),
                rows_out=len(daily),
                duration_seconds=duration,
                rejected_rows=0,
                started_at=stage_started_at,
                finished_at=stage_finished_at,
            ),
        )

    pipeline_finished_at = utc_now()

    logger.info(
        "pipeline_completed",
        run_id=run_id,
        started_at=pipeline_started_at,
        finished_at=pipeline_finished_at,
        daily_rows=len(daily),
        product_rows=len(products),
        customer_rows=len(customers),
    )

    return {
        "run_id": run_id,
        "bronze_rows": len(bronze),
        "silver_rows": len(silver),
        "daily_rows": len(daily),
        "product_rows": len(products),
        "customer_rows": len(customers),
        "rejected_rows": len(rejected),
        "started_at": pipeline_started_at,
        "finished_at": pipeline_finished_at,
    }