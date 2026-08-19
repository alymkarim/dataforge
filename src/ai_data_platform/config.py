from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: str
    environment: str = "local"
    run_id_prefix: str = "run"


class DatasetConfig(BaseModel):
    id: str = "ecommerce"
    name: str = "Ecommerce Behaviour Events"
    source: str = "Kaggle"
    domain: str = "Retail"


class PathsConfig(BaseModel):
    raw: Path
    bronze: Path
    silver: Path

    gold_daily: Path
    gold_products: Path
    gold_customers: Path

    metrics: Path
    quarantine: Path


class PipelineConfig(BaseModel):
    engine: str = "pandas"
    timestamp_column: str = "event_time"
    chunk_size: int = Field(default=100_000, ge=1)
    partitions: int = Field(default=4, ge=1)


class QualityConfig(BaseModel):
    max_null_rate: float = Field(default=0.10, ge=0, le=1)
    min_rows: int = Field(default=1, ge=0)

    required_columns: list[str]

    allowed_event_types: list[str]

    positive_columns: list[str] = Field(default_factory=list)

    nullable_columns: list[str] = Field(default_factory=list)


class GoldConfig(BaseModel):
    daily_metrics: bool = True
    product_metrics: bool = True
    customer_features: bool = True


class SnowflakeConfig(BaseModel):
    enabled: bool = False

    database: str
    schema: str
    warehouse: str

    daily_table: str
    product_table: str
    customer_table: str


class Settings(BaseModel):
    project: ProjectConfig
    dataset: DatasetConfig
    paths: PathsConfig
    pipeline: PipelineConfig
    quality: QualityConfig
    gold: GoldConfig
    snowflake: SnowflakeConfig


def load_settings(
    path: str | Path = "configs/pipeline.yml",
) -> Settings:
    config_path = Path(path)

    with config_path.open("r", encoding="utf-8") as file:
        raw: dict[str, Any] = yaml.safe_load(file)

    return Settings.model_validate(raw)