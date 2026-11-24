"""Generate reproducible datasets for Duka Electronics and Mobile Money Agent Network."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_duka_sales(output_path: str = "duka_sales.csv", seed: int = 2026) -> pd.DataFrame:
    """Generate 1,000 Duka Electronics orders for H1 2026."""
    rng = np.random.default_rng(seed)
    n = 1000

    branches = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"]
    channels = ["Online", "In-Store"]
    products = {
        "Laptop": (55000, 75000),
        "Smartphone": (24000, 48000),
        "Smart TV": (32000, 65000),
        "Headphones": (2500, 8500),
    }
    product_names = list(products.keys())

    chosen_products = rng.choice(product_names, size=n, p=[0.22, 0.36, 0.20, 0.22])
    unit_prices = np.array([
        rng.integers(products[p][0], products[p][1] + 1) for p in chosen_products
    ])
    quantities = rng.integers(1, 5, size=n)
    order_dates = pd.to_datetime("2026-01-01") + pd.to_timedelta(
        rng.integers(0, 181, size=n), unit="D"
    )

    df = pd.DataFrame({
        "order_id": [f"ORD{i:04d}" for i in range(1, n + 1)],
        "order_date": order_dates.strftime("%Y-%m-%d"),
        "branch": rng.choice(branches, size=n, p=[0.35, 0.20, 0.15, 0.16, 0.14]),
        "channel": rng.choice(channels, size=n, p=[0.42, 0.58]),
        "product": chosen_products,
        "unit_price": unit_prices,
        "quantity": quantities,
    })

    df.to_csv(output_path, index=False)
    return df


def generate_agent_network(
    agents_path: str = "agents.csv",
    txns_path: str = "agent_transactions.csv",
    seed: int = 44,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate 20 agents and 600 raw mobile money transactions with realistic dirty data."""
    rng = np.random.default_rng(seed)
    n = 600

    agents = pd.DataFrame({
        "agent_id": [f"AG{i:03d}" for i in range(1, 21)],
        "county": rng.choice(["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"], 20),
        "onboarded": pd.date_range("2024-01-01", periods=20, freq="MS").strftime("%Y-%m-%d"),
    })

    txns = pd.DataFrame({
        "txn_id": [f"TX{i:05d}" for i in range(1, n + 1)],
        "agent_id": rng.choice(agents["agent_id"], n),
        "txn_type": rng.choice(["Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"], n),
        "amount": rng.lognormal(7.5, 0.8, n).round(0).astype(str),
        "txn_date": (
            pd.to_datetime("2026-03-01")
            + pd.to_timedelta(rng.integers(0, 60, n), unit="D")
        ).strftime("%Y-%m-%d"),
    })

    idx = rng.choice(n, 30, replace=False)
    txns.loc[idx[:15], "amount"] = np.nan
    txns.loc[idx[15:20], "amount"] = "N/A"
    txns.loc[idx[20:25], "amount"] = "250000"
    txns.loc[idx[25:], "txn_date"] = txns.loc[idx[25:], "txn_date"].str.replace("-", "/")

    txns = pd.concat([txns, txns.sample(12, random_state=1)], ignore_index=True)
    txns.loc[rng.choice(len(txns), 8, replace=False), "agent_id"] = "AG099"

    agents.to_csv(agents_path, index=False)
    txns.to_csv(txns_path, index=False)
    return agents, txns


if __name__ == "__main__":
    duka_df = generate_duka_sales()
    agents_df, txns_df = generate_agent_network()
    print("Wrote duka_sales.csv:", duka_df.shape)
    print("Wrote agents.csv:", agents_df.shape)
    print("Wrote agent_transactions.csv:", txns_df.shape)
