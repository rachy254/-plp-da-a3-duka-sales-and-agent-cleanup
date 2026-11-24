"""Reusable cleaning and enrichment pipeline for mobile money agent transactions."""

from __future__ import annotations

from typing import Any
import pandas as pd


def clean_agent_data(
    txns: pd.DataFrame,
    agents: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean raw mobile money transactions and left-join with the agent register.

    Parameters
    ----------
    txns : pd.DataFrame
        Raw transaction records.
    agents : pd.DataFrame
        Agent register records containing at least ``agent_id`` and ``county``.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, Any]]
        Cleaned, enriched DataFrame and a cleaning log dictionary.
    """
    df = txns.copy()
    agent_ref = agents.copy()

    log: dict[str, Any] = {
        "raw_txn_rows": int(len(df)),
        "agent_register_rows": int(len(agent_ref)),
    }

    # 1. Uniqueness: remove exact duplicate rows
    before_dedup = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log["duplicates_removed"] = int(before_dedup - len(df))
    log["rows_after_dedup"] = int(len(df))

    # 2. Consistency: standardise txn_type into "Deposit" and "Withdrawal"
    raw_txn_type_na = int(df["txn_type"].isna().sum())
    cleaned_type = (
        df["txn_type"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map({"deposit": "Deposit", "withdrawal": "Withdrawal"})
    )
    log["txn_type_na_count"] = raw_txn_type_na
    log["txn_type_invalid_mapped_to_na"] = int(
        (df["txn_type"].notna() & cleaned_type.isna()).sum()
    )
    df["txn_type"] = cleaned_type.astype("object")

    # 3. Validity & completeness: convert amount to numeric, flag missing/invalid
    amount_raw = df["amount"]
    amount_str = amount_raw.astype("string").str.strip()
    na_text_count = int((amount_str.str.upper() == "N/A").fillna(False).sum())
    non_na_input_count = int(
        (amount_raw.notna() & (amount_str.str.upper() != "N/A").fillna(True)).sum()
    )

    cleaned_amount = amount_str.str.replace(",", "", regex=False).str.replace(
        r"[^\d.\-]", "", regex=True
    )
    df["amount"] = pd.to_numeric(cleaned_amount, errors="coerce")
    coerced_invalid_amount = non_na_input_count - int(df["amount"].notna().sum())
    df["is_amount_missing"] = df["amount"].isna()

    log["amount_na_text_rows"] = na_text_count
    log["amount_coerced_invalid_rows"] = int(max(coerced_invalid_amount, 0))
    log["missing_or_invalid_amount_rows"] = int(df["is_amount_missing"].sum())

    # 4. Validity: parse mixed date formats cleanly into datetime64
    raw_na_dates = int(df["txn_date"].isna().sum())
    df["txn_date"] = pd.to_datetime(df["txn_date"], format="mixed", errors="coerce")
    failed_date_parses = int(df["txn_date"].isna().sum()) - raw_na_dates
    log["txn_date_failed_parses"] = int(max(failed_date_parses, 0))

    # 5. Outliers: IQR method on valid amounts + flag KES 250,000 entries
    valid_amounts = df["amount"].dropna()
    q1 = float(valid_amounts.quantile(0.25))
    q3 = float(valid_amounts.quantile(0.75))
    iqr = float(q3 - q1)
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr

    df["is_outlier_iqr"] = (
        df["amount"].notna()
        & ((df["amount"] < lower_fence) | (df["amount"] > upper_fence))
    )
    df["is_250k_flagged"] = df["amount"] == 250000.0

    log["iqr_q1"] = q1
    log["iqr_q3"] = q3
    log["iqr_value"] = iqr
    log["iqr_upper_fence"] = upper_fence
    log["iqr_outlier_count"] = int(df["is_outlier_iqr"].sum())
    log["amount_250k_count"] = int(df["is_250k_flagged"].sum())

    # 6. Merge: left join onto agent register, preserve rows, flag unknown agents
    merged = df.merge(agent_ref, on="agent_id", how="left")
    assert len(merged) == len(df), (
        f"Row count changed during left join: {len(df)} -> {len(merged)}"
    )
    merged["is_unknown_agent"] = merged["county"].isna()
    log["unknown_agent_txns"] = int(merged["is_unknown_agent"].sum())
    merged["county"] = merged["county"].fillna("Unknown")
    log["final_clean_rows"] = int(len(merged))

    return merged, log
