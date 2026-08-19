from __future__ import annotations

import os

import pandas as pd


def load_to_snowflake(
    frame: pd.DataFrame,
    *,
    database: str,
    schema: str,
    table: str,
    warehouse: str,
) -> None:
    try:
        import snowflake.connector
        from snowflake.connector.pandas_tools import write_pandas
    except ImportError as exc:
        raise RuntimeError("Install the 'snowflake' optional dependency") from exc

    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing Snowflake environment variables: {missing}")

    connection = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=warehouse,
        database=database,
        schema=schema,
    )
    try:
        success, _, rows, _ = write_pandas(connection, frame, table_name=table)
        if not success:
            raise RuntimeError(f"Snowflake write failed after processing {rows} rows")
    finally:
        connection.close()
