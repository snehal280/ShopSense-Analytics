"""
================================================================================
Script  : feature_engineering.py
Project : E-Commerce Customer Analysis
Author  : Your Name

Purpose :
    Load the cleaned transaction data and engineer customer-level features
    used for segmentation, ranking, and business insights.

Features Created:
    ┌─────────────────────────────────────────────────────────────┐
    │  Metric                  │ Business Question Answered        │
    ├─────────────────────────────────────────────────────────────┤
    │  TotalRevenue            │ How much has each customer spent? │
    │  TotalOrders             │ How often do they buy?            │
    │  TotalQuantity           │ How many items do they buy?       │
    │  AvgOrderValue (AOV)     │ What is their typical basket?     │
    │  AvgItemsPerOrder        │ How many items per invoice?       │
    │  CustomerLifetimeValue   │ Long-term profit potential?       │
    │  DaysSinceLastPurchase   │ Are they recent or lapsing?       │
    │  CustomerLifespanDays    │ How long have they been active?   │
    │  PurchaseFrequencyDays   │ How often (in days) do they buy?  │
    │  Recency / Frequency /   │ RFM scores for segmentation       │
    │  Monetary                │                                   │
    └─────────────────────────────────────────────────────────────┘

How to run:
    python scripts/feature_engineering.py
    (Run AFTER data_cleaning.py)
================================================================================
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH  = os.path.join(BASE_DIR, "data", "processed", "cleaned_transactions.csv")
FEAT_PATH   = os.path.join(BASE_DIR, "data", "processed", "customer_features.csv")


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Load cleaned data
# ─────────────────────────────────────────────────────────────────────────────
def load_clean_data(filepath: str) -> pd.DataFrame:
    """Load the cleaned transaction CSV into a DataFrame."""
    print("=" * 65)
    print("  LOADING CLEANED DATA")
    print("=" * 65)

    # parse_dates tells pandas to read InvoiceDate as a datetime, not a string
    df = pd.read_csv(filepath, parse_dates=["InvoiceDate"])
    print(f"✅ Loaded {len(df):,} rows from {filepath}\n")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 1–5: Basic Aggregations per Customer
# ─────────────────────────────────────────────────────────────────────────────
def build_customer_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level data to one row per customer.

    Business intuition:
      - A customer can have hundreds of invoices.
      - We need one summary row per customer for segmentation.

    Aggregation logic:
      - TotalRevenue  = sum of all TotalPrice rows for this customer
      - TotalOrders   = count of unique InvoiceNos (each invoice = 1 order)
      - TotalQuantity = total items purchased
      - FirstPurchase = date of earliest invoice
      - LastPurchase  = date of most recent invoice
    """
    print("=" * 65)
    print("  STEP 1: BUILDING CUSTOMER BASE TABLE")
    print("=" * 65)

    # agg() applies different aggregation functions to different columns
    customer_df = df.groupby("CustomerID").agg(
        TotalRevenue   = ("TotalPrice",   "sum"),       # Total money spent
        TotalOrders    = ("InvoiceNo",    "nunique"),   # Unique orders count
        TotalQuantity  = ("Quantity",     "sum"),       # Total items bought
        FirstPurchase  = ("InvoiceDate",  "min"),       # Earliest purchase date
        LastPurchase   = ("InvoiceDate",  "max"),       # Most recent purchase date
    ).reset_index()  # reset_index() turns CustomerID from an index back into a column

    print(f"✅ Customer base built: {len(customer_df):,} unique customers\n")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 6: Average Order Value (AOV)
# ─────────────────────────────────────────────────────────────────────────────
def add_aov(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    Average Order Value (AOV) = TotalRevenue / TotalOrders

    Business meaning:
      A customer with TotalRevenue=£500 and TotalOrders=5 has an AOV of £100.
      High AOV customers are "big-basket" shoppers — valuable per visit.

    Note: We use np.where to avoid division by zero for any edge cases.
    """
    customer_df["AvgOrderValue"] = np.where(
        customer_df["TotalOrders"] > 0,
        customer_df["TotalRevenue"] / customer_df["TotalOrders"],
        0   # If somehow TotalOrders is 0, AOV is 0
    )
    print("✅ Feature added: AvgOrderValue (AOV)")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 7: Average Items per Order
# ─────────────────────────────────────────────────────────────────────────────
def add_avg_items(df: pd.DataFrame, customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    AvgItemsPerOrder = average number of items (quantity) in each order.

    Method:
      1. For each invoice, sum the quantities (items in that basket).
      2. Then average those basket sizes per customer.

    This distinguishes bulk buyers (large baskets) from frequent small-buyers.
    """
    # Step 1: Total items per invoice (basket size)
    basket_sizes = df.groupby(["CustomerID", "InvoiceNo"])["Quantity"].sum().reset_index()
    basket_sizes.rename(columns={"Quantity": "BasketSize"}, inplace=True)

    # Step 2: Average basket size per customer
    avg_basket = basket_sizes.groupby("CustomerID")["BasketSize"].mean().reset_index()
    avg_basket.rename(columns={"BasketSize": "AvgItemsPerOrder"}, inplace=True)

    # Step 3: Merge into customer_df using a LEFT JOIN
    customer_df = customer_df.merge(avg_basket, on="CustomerID", how="left")
    print("✅ Feature added: AvgItemsPerOrder")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 8: Customer Lifespan & Days Since Last Purchase (Recency)
# ─────────────────────────────────────────────────────────────────────────────
def add_time_features(customer_df: pd.DataFrame, snapshot_date: pd.Timestamp) -> pd.DataFrame:
    """
    Add time-based customer metrics.

    snapshot_date: The reference "today" for recency calculations.
                   We use the day AFTER the last transaction in the dataset.
                   This simulates the business analyst running reports on that date.

    CustomerLifespanDays:
        = LastPurchase - FirstPurchase
        = How many days the customer has been active.
        A long lifespan is a sign of a loyal, retained customer.

    DaysSinceLastPurchase (Recency):
        = snapshot_date - LastPurchase
        = How many days ago did they last buy?
        Small number = very recent = healthy sign.
        Large number = dormant / at-risk customer.
    """
    # timedelta.dt.days converts the result to an integer number of days
    customer_df["CustomerLifespanDays"] = (
        customer_df["LastPurchase"] - customer_df["FirstPurchase"]
    ).dt.days

    customer_df["DaysSinceLastPurchase"] = (
        snapshot_date - customer_df["LastPurchase"]
    ).dt.days

    print(f"✅ Feature added: CustomerLifespanDays (reference date: {snapshot_date.date()})")
    print(f"✅ Feature added: DaysSinceLastPurchase (Recency)")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 9: Purchase Frequency (in days)
# ─────────────────────────────────────────────────────────────────────────────
def add_frequency_days(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    PurchaseFrequencyDays = CustomerLifespanDays / TotalOrders

    Business meaning:
        If a customer has been active for 300 days and made 10 orders,
        they buy approximately every 30 days — very loyal!

    Customers with a low frequency (buy every few days) are your VIPs.
    Customers with a high frequency (buy once every 200+ days) may churn.
    """
    customer_df["PurchaseFrequencyDays"] = np.where(
        customer_df["TotalOrders"] > 1,
        customer_df["CustomerLifespanDays"] / customer_df["TotalOrders"],
        customer_df["CustomerLifespanDays"]  # Only 1 order → lifespan = frequency
    )
    print("✅ Feature added: PurchaseFrequencyDays")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 10: Customer Lifetime Value (CLV)
# ─────────────────────────────────────────────────────────────────────────────
def add_clv(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    Customer Lifetime Value (CLV) estimates how much a customer is worth
    over their entire relationship with the business.

    Formula used (simplified):
        CLV = (Average Order Value) × (Purchase Frequency per Year) × (Lifespan in Years)

    Where:
        PurchaseFrequencyPerYear = TotalOrders / (CustomerLifespanDays / 365)
        LifespanYears            = CustomerLifespanDays / 365

    Simplified → CLV = TotalRevenue × (365 / max(CustomerLifespanDays, 1))
        This is the annual revenue rate — "how much would this customer spend per year?"

    Note: This is a basic historic CLV, not a predictive model.
    In a more advanced project, you'd use probabilistic models (BG/NBD + Gamma-Gamma).
    """
    # Lifespan in years (minimum 1 day to avoid division by zero)
    lifespan_years = np.maximum(customer_df["CustomerLifespanDays"], 1) / 365

    # Annual purchase frequency rate
    purchase_freq_per_year = customer_df["TotalOrders"] / lifespan_years

    # CLV = AOV × annual frequency × 1 year
    customer_df["CustomerLifetimeValue"] = (
        customer_df["AvgOrderValue"] * purchase_freq_per_year
    ).round(2)

    print("✅ Feature added: CustomerLifetimeValue (CLV)")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 11: Country — Most Common Country per Customer
# ─────────────────────────────────────────────────────────────────────────────
def add_country(df: pd.DataFrame, customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign each customer their most frequently used country.
    Most customers shop from one country; this handles edge cases.
    """
    # mode()[0] returns the most common value; groupby + apply runs it per group
    country_map = (
        df.groupby("CustomerID")["Country"]
        .agg(lambda x: x.mode()[0])
        .reset_index()
        .rename(columns={"Country": "PrimaryCountry"})
    )
    customer_df = customer_df.merge(country_map, on="CustomerID", how="left")
    print("✅ Feature added: PrimaryCountry")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 12: Customer Tier (based on TotalRevenue percentiles)
# ─────────────────────────────────────────────────────────────────────────────
def add_customer_tier(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify customers into revenue tiers using percentiles.

    Tiers:
        Platinum : Top 5%  revenue customers   → Your absolute best
        Gold     : 75–95th percentile           → High value
        Silver   : 25–75th percentile           → Mid value
        Bronze   : Bottom 25%                   → Low value / new

    pd.qcut() divides data into equal-frequency buckets.
    We use pd.cut() with our own percentile-based thresholds instead,
    so the labels are meaningful business segments.
    """
    p25  = customer_df["TotalRevenue"].quantile(0.25)
    p75  = customer_df["TotalRevenue"].quantile(0.75)
    p95  = customer_df["TotalRevenue"].quantile(0.95)

    # np.select applies conditions in order; the first match wins
    conditions = [
        customer_df["TotalRevenue"] >= p95,
        customer_df["TotalRevenue"] >= p75,
        customer_df["TotalRevenue"] >= p25,
    ]
    choices = ["Platinum", "Gold", "Silver"]
    customer_df["CustomerTier"] = np.select(conditions, choices, default="Bronze")

    print("✅ Feature added: CustomerTier (Bronze / Silver / Gold / Platinum)")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 13: Repeat Customer Flag
# ─────────────────────────────────────────────────────────────────────────────
def add_repeat_flag(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    IsRepeatCustomer = 1 if the customer made more than 1 order, else 0.

    Business meaning:
        Repeat customers are far more valuable than one-time buyers.
        Industry stat: Acquiring a new customer costs 5–7× more than retaining one.
    """
    customer_df["IsRepeatCustomer"] = (customer_df["TotalOrders"] > 1).astype(int)
    repeat_pct = customer_df["IsRepeatCustomer"].mean() * 100
    print(f"✅ Feature added: IsRepeatCustomer | {repeat_pct:.1f}% of customers are repeat buyers")
    return customer_df


# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
def save_features(customer_df: pd.DataFrame, filepath: str) -> None:
    """Save the engineered customer features to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    customer_df.to_csv(filepath, index=False)
    print(f"\n💾 Customer features saved to: {filepath}")
    print(f"   {len(customer_df):,} customers  |  {customer_df.shape[1]} features\n")

    # Print final feature summary
    print("📊 Feature Summary:")
    print(customer_df.describe(include="all").T[
        ["count", "mean", "min", "max"]
    ].to_string())


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load cleaned transactions
    df = load_clean_data(CLEAN_PATH)

    # Snapshot date = 1 day after the last transaction in the dataset
    # This is the standard industry approach for recency calculations
    SNAPSHOT_DATE = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    print(f"\n📅 Snapshot date set to: {SNAPSHOT_DATE.date()}\n")

    # Build features step by step
    print("=" * 65)
    print("  STEP 2: ENGINEERING CUSTOMER FEATURES")
    print("=" * 65)

    customer_df = build_customer_base(df)
    customer_df = add_aov(customer_df)
    customer_df = add_avg_items(df, customer_df)
    customer_df = add_time_features(customer_df, SNAPSHOT_DATE)
    customer_df = add_frequency_days(customer_df)
    customer_df = add_clv(customer_df)
    customer_df = add_country(df, customer_df)
    customer_df = add_customer_tier(customer_df)
    customer_df = add_repeat_flag(customer_df)

    # Save
    save_features(customer_df, FEAT_PATH)

    print("=" * 65)
    print("  ✅ FEATURE ENGINEERING COMPLETE")
    print("=" * 65)
    print(f"\n  Next step → Run: python scripts/rfm_analysis.py\n")
