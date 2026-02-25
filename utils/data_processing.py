"""Data loading, filtering, and KPI calculation utilities."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).parent.parent / "data" / "synthetic_spend_data.csv"

EXPECTED_COLUMNS = [
    "transaction_id",
    "transaction_date",
    "facility_name",
    "department",
    "spend_category",
    "vendor_name",
    "product_description",
    "unit_price",
    "quantity",
    "total_amount",
    "contract_type",
    "ppi_flag",
]


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and validate the synthetic spend data CSV.

    Returns:
        DataFrame with parsed dates and validated schema.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required columns are missing.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH, parse_dates=["transaction_date"])

    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["ppi_flag"] = df["ppi_flag"].astype(bool)
    df["total_amount"] = df["total_amount"].astype(float)
    df["unit_price"] = df["unit_price"].astype(float)
    df["quantity"] = df["quantity"].astype(int)

    return df


def apply_filters(
    df: pd.DataFrame,
    date_range: Optional[tuple[date, date]] = None,
    facilities: Optional[list[str]] = None,
    categories: Optional[list[str]] = None,
    vendors: Optional[list[str]] = None,
    contract_types: Optional[list[str]] = None,
    ppi_only: bool = False,
) -> pd.DataFrame:
    """Apply sidebar filter selections to the DataFrame.

    Args:
        df: Full unfiltered DataFrame.
        date_range: Tuple of (start_date, end_date).
        facilities: Selected facility names.
        categories: Selected spend categories.
        vendors: Selected vendor names.
        contract_types: Selected contract types.
        ppi_only: If True, filter to PPI items only.

    Returns:
        Filtered DataFrame.
    """
    filtered = df.copy()

    if date_range is not None:
        start, end = date_range
        filtered = filtered[
            (filtered["transaction_date"].dt.date >= start)
            & (filtered["transaction_date"].dt.date <= end)
        ]

    if facilities:
        filtered = filtered[
            filtered["facility_name"].isin(facilities)
        ]

    if categories:
        filtered = filtered[
            filtered["spend_category"].isin(categories)
        ]

    if vendors:
        filtered = filtered[
            filtered["vendor_name"].isin(vendors)
        ]

    if contract_types:
        filtered = filtered[
            filtered["contract_type"].isin(contract_types)
        ]

    if ppi_only:
        filtered = filtered[filtered["ppi_flag"]]

    return filtered


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate all KPI values from filtered data.

    Args:
        df: Filtered DataFrame.

    Returns:
        Dictionary with KPI keys: total_spend, transaction_count,
        unique_vendors, ppi_spend_pct, avg_transaction.
    """
    total_spend = df["total_amount"].sum()
    transaction_count = len(df)
    unique_vendors = df["vendor_name"].nunique()

    ppi_spend = df.loc[df["ppi_flag"], "total_amount"].sum()
    ppi_spend_pct = (
        (ppi_spend / total_spend * 100) if total_spend > 0 else 0.0
    )

    avg_transaction = (
        total_spend / transaction_count
        if transaction_count > 0
        else 0.0
    )

    return {
        "total_spend": total_spend,
        "transaction_count": transaction_count,
        "unique_vendors": unique_vendors,
        "ppi_spend_pct": ppi_spend_pct,
        "avg_transaction": avg_transaction,
    }


def calculate_prior_period(
    df_full: pd.DataFrame,
    current_start: date,
    current_end: date,
) -> dict:
    """Calculate prior period KPIs for delta comparison.

    The prior period is the same duration immediately preceding
    the current date range.

    Args:
        df_full: Full unfiltered DataFrame.
        current_start: Start of the current period.
        current_end: End of the current period.

    Returns:
        Dictionary with the same keys as calculate_kpis.
    """
    current_start_ts = pd.Timestamp(current_start)
    current_end_ts = pd.Timestamp(current_end)
    duration = current_end_ts - current_start_ts

    prior_end = current_start_ts - pd.Timedelta(days=1)
    prior_start = prior_end - duration

    prior_df = df_full[
        (df_full["transaction_date"] >= prior_start)
        & (df_full["transaction_date"] <= prior_end)
    ]

    return calculate_kpis(prior_df)
