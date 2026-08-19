# Architecture

```mermaid
flowchart LR
    A[CSV / Azure Data Lake] --> B[Bronze ingestion]
    B --> C{Data quality checks}
    C -->|Valid| D[Silver cleaned events]
    C -->|Invalid| Q[Quarantine]
    D --> E[Gold daily AI features]
    E --> F[Snowflake analytics table]
    B --> M[JSON metrics + structured logs]
    C --> M
    D --> M
    E --> M
```

## Design decisions

- **Medallion architecture:** raw source data is retained, cleaned records are isolated from aggregates, and model-ready features are published separately.
- **Boundary validation:** schema, identity, timestamp, domain and null checks run before transformation.
- **Quarantine instead of silent deletion:** rejected records are persisted by run ID for investigation and replay.
- **Idempotent file outputs:** each layer is replaced deterministically for the local reference implementation.
- **Portable compute:** pandas provides a lightweight local execution path; the same transformation boundaries can be mapped to Spark DataFrames in Databricks.
- **Cloud-ready loading:** Snowflake integration is disabled by default and activated through configuration plus environment variables.
