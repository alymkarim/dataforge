from __future__ import annotations

import pandas as pd


def clean_events(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    output = frame.copy()

    # Timestamp
    output["event_time"] = pd.to_datetime(
        output["event_time"],
        errors="coerce",
        utc=True,
    )

    # Normalise strings
    output["event_type"] = (
        output["event_type"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    output["brand"] = (
        output["brand"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    output["category_code"] = (
        output["category_code"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Numeric columns
    output["price"] = pd.to_numeric(
        output["price"],
        errors="coerce",
    )

    # Date derived column
    output["event_date"] = (
        output["event_time"]
        .dt.date
    )

    # Composite duplicate handling
    output = output.drop_duplicates(
        subset=[
            "event_time",
            "event_type",
            "product_id",
            "user_id",
            "user_session",
        ],
        keep="first",
    )

    output = output.sort_values(
        "event_time"
    )

    return output.reset_index(
        drop=True
    )


def build_daily_metrics(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    enriched = frame.assign(
        is_view=(
            frame["event_type"] == "view"
        ).astype(int),
        is_cart=(
            frame["event_type"] == "cart"
        ).astype(int),
        is_purchase=(
            frame["event_type"] == "purchase"
        ).astype(int),
        purchase_value=frame["price"].where(
            frame["event_type"] == "purchase",
            0.0,
        ),
    )

    daily = (
        enriched
        .groupby(
            "event_date",
            as_index=False,
        )
        .agg(
            views=("is_view", "sum"),
            cart_events=("is_cart", "sum"),
            purchases=("is_purchase", "sum"),
            revenue=("purchase_value", "sum"),
            active_users=("user_id", "nunique"),
        )
    )

    daily["conversion_rate"] = (
        daily["purchases"]
        / daily["views"].clip(lower=1)
        * 100
    ).round(4)

    daily["average_order_value"] = (
        daily["revenue"]
        / daily["purchases"].clip(lower=1)
    ).round(2)

    return daily


def build_product_metrics(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    enriched = frame.assign(
        is_view=(
            frame["event_type"] == "view"
        ).astype(int),
        is_cart=(
            frame["event_type"] == "cart"
        ).astype(int),
        is_purchase=(
            frame["event_type"] == "purchase"
        ).astype(int),
        purchase_value=frame["price"].where(
            frame["event_type"] == "purchase",
            0.0,
        ),
    )

    product = (
        enriched
        .groupby(
            [
                "product_id",
                "brand",
                "category_code",
            ],
            dropna=False,
            as_index=False,
        )
        .agg(
            views=("is_view", "sum"),
            cart_events=("is_cart", "sum"),
            purchases=("is_purchase", "sum"),
            revenue=("purchase_value", "sum"),
            unique_users=("user_id", "nunique"),
        )
    )

    product["conversion_rate"] = (
        product["purchases"]
        / product["views"].clip(lower=1)
        * 100
    ).round(4)

    return product.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


def build_customer_features(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    enriched = frame.assign(
        is_view=(
            frame["event_type"] == "view"
        ).astype(int),
        is_cart=(
            frame["event_type"] == "cart"
        ).astype(int),
        is_purchase=(
            frame["event_type"] == "purchase"
        ).astype(int),
        purchase_value=frame["price"].where(
            frame["event_type"] == "purchase",
            0.0,
        ),
    )

    customers = (
        enriched
        .groupby(
            "user_id",
            as_index=False,
        )
        .agg(
            sessions=("user_session", "nunique"),
            views=("is_view", "sum"),
            cart_events=("is_cart", "sum"),
            purchases=("is_purchase", "sum"),
            total_spend=("purchase_value", "sum"),
            average_event_price=("price", "mean"),
            last_activity=("event_time", "max"),
        )
    )

    customers["average_order_value"] = (
        customers["total_spend"]
        / customers["purchases"].clip(lower=1)
    ).round(2)

    return customers