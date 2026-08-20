# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

SOURCE = "/Volumes/workspace/default/dataforge/sample-multiday.csv"

bronze = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(SOURCE)
)

display(bronze.limit(10))

# COMMAND ----------

print("Rows:", bronze.count())
bronze.printSchema()

# COMMAND ----------

(
    bronze.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_bronze")
)

# COMMAND ----------

spark.table("dataforge_bronze").count()

# COMMAND ----------

VALID_EVENT_TYPES = [
    "view",
    "cart",
    "remove_from_cart",
    "purchase",
]

validated = (
    bronze
    .withColumn(
        "parsed_event_time",
        F.to_timestamp("event_time"),
    )
    .withColumn(
        "validation_reason",
        F.when(
            F.col("event_time").isNull(),
            "missing_event_time",
        )
        .when(
            F.to_timestamp("event_time").isNull(),
            "invalid_event_time",
        )
        .when(
            F.col("user_id").isNull(),
            "missing_user_id",
        )
        .when(
            F.col("product_id").isNull(),
            "missing_product_id",
        )
        .when(
            ~F.lower(F.trim("event_type")).isin(
                VALID_EVENT_TYPES
            ),
            "unsupported_event_type",
        )
        .when(
            F.col("price").cast("double") < 0,
            "negative_price",
        )
    )
)

# COMMAND ----------

valid_rows = validated.filter(
    F.col("validation_reason").isNull()
)

quarantine = validated.filter(
    F.col("validation_reason").isNotNull()
)

print("Bronze:", bronze.count())
print("Valid:", valid_rows.count())
print("Quarantine:", quarantine.count())

# COMMAND ----------

(
    quarantine.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_quarantine")
)

# COMMAND ----------

silver = (
    valid_rows
    .withColumn(
        "event_time",
        F.to_timestamp("event_time"),
    )
    .withColumn(
        "event_type",
        F.lower(
            F.trim(
                F.col("event_type")
            )
        ),
    )
    .withColumn(
        "brand",
        F.lower(
            F.trim(
                F.col("brand")
            )
        ),
    )
    .withColumn(
        "category_code",
        F.lower(
            F.trim(
                F.col("category_code")
            )
        ),
    )
    .withColumn(
        "price",
        F.col("price").cast("double"),
    )
    .dropDuplicates(
        [
            "event_time",
            "event_type",
            "product_id",
            "user_id",
            "user_session",
        ]
    )
    .drop(
        "parsed_event_time",
        "validation_reason",
    )
)

print("Silver rows:", silver.count())

display(
    silver.limit(20)
)

# COMMAND ----------

(
    silver.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_silver")
)

print("Silver saved:", silver.count())

# COMMAND ----------

print("Bronze rows:", bronze.count())
print("Silver rows:", silver.count())

# COMMAND ----------

(
    silver.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_silver")
)

# COMMAND ----------

spark.table("dataforge_silver").count()

# COMMAND ----------

display(
    spark.table("dataforge_silver").limit(20)
)

# COMMAND ----------

gold_daily = (
    silver
    .withColumn(
        "event_date",
        F.to_date("event_time"),
    )
    .groupBy("event_date")
    .agg(
        F.sum(
            F.when(
                F.col("event_type") == "view",
                1,
            ).otherwise(0)
        ).alias("views"),

        F.sum(
            F.when(
                F.col("event_type") == "cart",
                1,
            ).otherwise(0)
        ).alias("cart_events"),

        F.sum(
            F.when(
                F.col("event_type") == "purchase",
                1,
            ).otherwise(0)
        ).alias("purchases"),

        F.sum(
            F.when(
                F.col("event_type") == "purchase",
                F.col("price"),
            ).otherwise(0)
        ).alias("revenue"),

        F.countDistinct(
            "user_id"
        ).alias("active_users"),
    )
)

# COMMAND ----------

gold_daily = (
    gold_daily
    .withColumn(
        "conversion_rate",
        F.when(
            F.col("views") > 0,
            (
                F.col("purchases")
                / F.col("views")
                * 100
            ),
        ).otherwise(0),
    )
    .withColumn(
        "average_order_value",
        F.when(
            F.col("purchases") > 0,
            (
                F.col("revenue")
                / F.col("purchases")
            ),
        ).otherwise(0),
    )
)

# COMMAND ----------

display(gold_daily.orderBy("event_date"))

# COMMAND ----------

(
    gold_daily.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_gold_daily")
)

# COMMAND ----------

gold_products = (
    silver
    .groupBy(
        "product_id",
        "brand",
        "category_code",
    )
    .agg(
        F.sum(
            F.when(
                F.col("event_type") == "view",
                1,
            ).otherwise(0)
        ).alias("views"),

        F.sum(
            F.when(
                F.col("event_type") == "cart",
                1,
            ).otherwise(0)
        ).alias("cart_events"),

        F.sum(
            F.when(
                F.col("event_type") == "purchase",
                1,
            ).otherwise(0)
        ).alias("purchases"),

        F.sum(
            F.when(
                F.col("event_type") == "purchase",
                F.col("price"),
            ).otherwise(0)
        ).alias("revenue"),

        F.countDistinct(
            "user_id"
        ).alias("unique_users"),
    )
)

# COMMAND ----------

gold_products = gold_products.withColumn(
    "conversion_rate",
    F.when(
        F.col("views") > 0,
        (
            F.col("purchases")
            / F.col("views")
            * 100
        ),
    ).otherwise(0),
)

# COMMAND ----------

display(
    gold_products
    .orderBy(
        F.col("revenue").desc()
    )
    .limit(20)
)

# COMMAND ----------

(
    gold_products.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_gold_products")
)

# COMMAND ----------

gold_customers = (
    silver
    .groupBy("user_id")
    .agg(
        F.countDistinct(
            "user_session"
        ).alias("sessions"),

        F.sum(
            F.when(
                F.col("event_type") == "view",
                1,
            ).otherwise(0)
        ).alias("views"),

        F.sum(
            F.when(
                F.col("event_type") == "cart",
                1,
            ).otherwise(0)
        ).alias("cart_events"),

        F.sum(
            F.when(
                F.col("event_type") == "purchase",
                1,
            ).otherwise(0)
        ).alias("purchases"),

        F.sum(
            F.when(
                F.col("event_type") == "purchase",
                F.col("price"),
            ).otherwise(0)
        ).alias("total_spend"),

        F.avg("price").alias(
            "average_event_price"
        ),

        F.max(
            "event_time"
        ).alias("last_activity"),
    )
)

# COMMAND ----------

gold_customers = gold_customers.withColumn(
    "average_order_value",
    F.when(
        F.col("purchases") > 0,
        (
            F.col("total_spend")
            / F.col("purchases")
        ),
    ).otherwise(0),
)

# COMMAND ----------

display(
    gold_customers
    .orderBy(
        F.col("total_spend").desc()
    )
    .limit(20)
)

# COMMAND ----------

(
    gold_customers.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dataforge_gold_customers")
)

# COMMAND ----------

tables = [
    "dataforge_bronze",
    "dataforge_silver",
    "dataforge_gold_daily",
    "dataforge_gold_products",
    "dataforge_gold_customers",
]

for table in tables:
    print(
        table,
        spark.table(table).count(),
    )

# COMMAND ----------

tables = [
    "dataforge_bronze",
    "dataforge_quarantine",
    "dataforge_silver",
    "dataforge_gold_daily",
    "dataforge_gold_products",
    "dataforge_gold_customers",
]

for table in tables:
    print(
        f"{table}: "
        f"{spark.table(table).count():,} rows"
    )