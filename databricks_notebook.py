# Databricks notebook source
# MAGIC %md
# MAGIC # AI Data Platform — Spark reference pipeline

from pyspark.sql import functions as F

raw_path = dbutils.widgets.get("raw_path") or "/mnt/ai-platform/raw/events.csv"
silver_path = dbutils.widgets.get("silver_path") or "/mnt/ai-platform/silver/events"
gold_path = dbutils.widgets.get("gold_path") or "/mnt/ai-platform/gold/daily_features"

bronze = (
    spark.read.option("header", True).option("inferSchema", True).csv(raw_path)
    .withColumn("ingested_at", F.current_timestamp())
)

valid = (
    bronze.filter(F.col("event_id").isNotNull())
    .filter(F.col("event_timestamp").isNotNull())
    .filter(F.col("event_type").isin("view", "click", "purchase", "login"))
)

silver = (
    valid.withColumn("event_timestamp", F.to_timestamp("event_timestamp"))
    .withColumn("event_type", F.lower(F.trim("event_type")))
    .withColumn("country", F.upper(F.trim("country")))
    .withColumn("event_date", F.to_date("event_timestamp"))
    .dropDuplicates(["event_id"])
)
silver.write.format("delta").mode("overwrite").save(silver_path)

gold = (
    silver.groupBy("event_date", "user_id", "country")
    .agg(
        F.count("event_id").alias("event_count"),
        F.sum(F.when(F.col("event_type") == "purchase", 1).otherwise(0)).alias("purchase_count"),
        F.sum("value").alias("total_value"),
        F.max("event_timestamp").alias("last_event_at"),
    )
)
gold.write.format("delta").mode("overwrite").save(gold_path)
