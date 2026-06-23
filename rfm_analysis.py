"""
================================================================================
Script  : rfm_analysis.py
Project : E-Commerce Customer Analysis
Author  : Your Name

Purpose :
    Perform full RFM (Recency, Frequency, Monetary) Analysis to segment
    customers into actionable business groups.

What is RFM?
    RFM is a proven marketing framework used by companies like Amazon, Netflix,
    and Starbucks to identify and target the right customers with the right offer.

    R = Recency   → How recently did the customer buy?
                    (Lower days = Better. Recent buyers are more likely to buy again.)

    F = Frequency → How often do they buy?
                    (More orders = Better. Frequent buyers are loyal.)

    M = Monetary  → How much have they spent in total?
                    (Higher spend = Better. High spenders drive revenue.)

Scoring Method:
    Each dimension is scored 1–5 using quintiles (equal-sized groups).
    Score 5 = Best, Score 1 = Worst.

    For Recency: LOW days → HIGH score (1 = most recent is BEST)
    For Frequency & Monetary: HIGH value → HIGH score

Combined RFM Score:
    RFM_Score = R_Score + F_Score + M_Score (range: 3–15)

Customer Segments (based on score thresholds):
    Champion         → Bought recently, buy often, spend the most
    Loyal Customer   → Frequent buyers, good spenders
    Potential Loyal  → Recent, some frequency
    At Risk          → Used to be loyal, haven't bought recently
    Hibernating      → Long inactive, low engagement
    New Customer     → Bought recently for the first time
    Lost             → Very old purchases, very low engagement

How to run:
    python scripts/rfm_analysis.py
    (Run AFTER feature_engineering.py)
================================================================================
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_transactions.csv")
FEAT_PATH  = os.path.join(BASE_DIR, "data", "processed", "customer_features.csv")
RFM_PATH   = os.path.join(BASE_DIR, "data", "processed", "rfm_segments.csv")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: BUILD RFM TABLE
# ─────────────────────────────────────────────────────────────────────────────
def build_rfm_table(df: pd.DataFrame, snapshot_date: pd.Timestamp) -> pd.DataFrame:
    """
    Compute the three RFM components per customer.

    Parameters:
        df            (pd.DataFrame)  : Cleaned transaction data.
        snapshot_date (pd.Timestamp)  : Reference "today" date.

    Returns:
        pd.DataFrame: One row per customer with Recency, Frequency, Monetary.
    """
    print("=" * 65)
    print("  STEP 1: COMPUTING RFM VALUES")
    print("=" * 65)

    # Group by customer and compute R, F, M in one pass
    rfm = df.groupby("CustomerID").agg(
        Recency   = ("InvoiceDate",  lambda x: (snapshot_date - x.max()).days),
        Frequency = ("InvoiceNo",    "nunique"),
        Monetary  = ("TotalPrice",   "sum")
    ).reset_index()

    # Round Monetary to 2 decimal places for cleanliness
    rfm["Monetary"] = rfm["Monetary"].round(2)

    print(f"✅ RFM table built for {len(rfm):,} customers\n")
    print("  Sample RFM values (first 5 customers):")
    print(rfm.head(5).to_string(index=False))
    print()

    return rfm


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: SCORE EACH DIMENSION (1–5 quintile scoring)
# ─────────────────────────────────────────────────────────────────────────────
def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Assign a score of 1–5 to each RFM dimension using quintiles.

    Quintile approach:
        pd.qcut() divides data into 5 equal-frequency groups.
        labels=[1,2,3,4,5] assign numeric scores to each bucket.

    Important: Recency is REVERSED.
        A customer who bought 2 days ago is BETTER than one who bought 300 days ago.
        So we give score 5 to LOW recency and score 1 to HIGH recency.
        This is done by using labels=[5,4,3,2,1] (descending).

    Handling duplicates:
        If many customers have the same value (e.g., Frequency=1),
        duplicates=True tells qcut to handle ties without throwing an error.
    """
    print("=" * 65)
    print("  STEP 2: SCORING RFM DIMENSIONS (1 = Worst, 5 = Best)")
    print("=" * 65)

    # ── Recency Score (lower days = better = score 5) ─────────────────────────
    rfm["R_Score"] = pd.qcut(
        rfm["Recency"],
        q=5,
        labels=[5, 4, 3, 2, 1],   # Note: reversed! Low recency → Score 5
        duplicates="drop"
    ).astype(int)

    # ── Frequency Score (higher orders = better = score 5) ───────────────────
    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),  # rank() breaks ties
        q=5,
        labels=[1, 2, 3, 4, 5],
        duplicates="drop"
    ).astype(int)

    # ── Monetary Score (higher spend = better = score 5) ─────────────────────
    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"],
        q=5,
        labels=[1, 2, 3, 4, 5],
        duplicates="drop"
    ).astype(int)

    # ── Combined RFM Score ────────────────────────────────────────────────────
    # Additive score ranges from 3 (worst: 1+1+1) to 15 (best: 5+5+5)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    # ── String label for easy filtering (e.g., "555", "411") ─────────────────
    rfm["RFM_Label"] = (
        rfm["R_Score"].astype(str) +
        rfm["F_Score"].astype(str) +
        rfm["M_Score"].astype(str)
    )

    print("✅ RFM scores assigned (1–5 per dimension)")
    print(f"\n  Score distribution (RFM_Score):\n{rfm['RFM_Score'].value_counts().sort_index()}\n")

    return rfm


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: ASSIGN CUSTOMER SEGMENTS
# ─────────────────────────────────────────────────────────────────────────────
def assign_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Map RFM scores to human-readable customer segments.

    Segmentation rules are based on industry-standard RFM thresholds.
    These are the same categories used by CRM tools like HubSpot, Klaviyo, etc.

    Segment Descriptions:
    ┌───────────────────┬──────────────────────────────────────────────────┐
    │ Segment           │ Description                                      │
    ├───────────────────┼──────────────────────────────────────────────────┤
    │ Champion          │ R≥4, F≥4, M≥4 — Your best customers             │
    │ Loyal Customer    │ F≥3, M≥3 — Buy regularly and spend well          │
    │ Potential Loyal   │ R≥3, F≤3 — Recent with growing frequency         │
    │ Recent Customer   │ R≥4, F≤2 — Just started buying                   │
    │ Promising         │ R≥3, M≤3 — Recent but haven't spent much yet     │
    │ Needs Attention   │ R around 3, F/M around 3 — Could go either way   │
    │ About to Sleep    │ R≤2, F/M medium — Declining engagement            │
    │ At Risk           │ R≤2, F≥3 — Used to be good but haven't returned  │
    │ Can't Lose Them   │ R≤2, F≥4 — Were top customers, now dormant       │
    │ Hibernating       │ R≤2, F≤2 — Long gone, low value                  │
    │ Lost              │ R=1, very low RFM — Churned customers             │
    └───────────────────┴──────────────────────────────────────────────────┘

    Implementation uses nested np.where + np.select for readability.
    """
    print("=" * 65)
    print("  STEP 3: ASSIGNING CUSTOMER SEGMENTS")
    print("=" * 65)

    # Shorthand references for cleaner condition writing
    R = rfm["R_Score"]
    F = rfm["F_Score"]
    M = rfm["M_Score"]
    Score = rfm["RFM_Score"]

    # Conditions evaluated in order — first match wins
    conditions = [
        (R >= 4) & (F >= 4) & (M >= 4),             # Champion
        (F >= 3) & (M >= 3),                          # Loyal Customer
        (R >= 4) & (F >= 2) & (M >= 2),              # Potential Loyal
        (R >= 4) & (F <= 1),                          # Recent Customer (new)
        (R >= 3) & (Score >= 9),                      # Promising
        (R == 3) & (F >= 2) & (M >= 2),              # Needs Attention
        (R <= 2) & (F >= 4) & (M >= 4),              # Can't Lose Them
        (R <= 2) & (F >= 3),                          # At Risk
        (R <= 2) & (F <= 2) & (M >= 2),              # About to Sleep
        (Score <= 5),                                  # Lost
    ]
    segment_labels = [
        "Champion",
        "Loyal Customer",
        "Potential Loyal",
        "New Customer",
        "Promising",
        "Needs Attention",
        "Can't Lose Them",
        "At Risk",
        "Hibernating",
        "Lost",
    ]

    # np.select: returns the corresponding label for the first True condition
    rfm["Segment"] = np.select(conditions, segment_labels, default="Others")

    # Print segment counts
    segment_counts = rfm["Segment"].value_counts().reset_index()
    segment_counts.columns = ["Segment", "Count"]
    segment_counts["Percentage"] = (segment_counts["Count"] / len(rfm) * 100).round(1)
    segment_counts = segment_counts.sort_values("Count", ascending=False)

    print("✅ Segments assigned!\n")
    print("  Customer Segment Distribution:")
    print("  " + "─" * 45)
    for _, row in segment_counts.iterrows():
        bar = "█" * int(row["Percentage"] // 2)
        print(f"  {row['Segment']:<20} {row['Count']:>5,}  ({row['Percentage']:>5.1f}%)  {bar}")
    print()

    return rfm


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: IDENTIFY SPECIAL CUSTOMER GROUPS
# ─────────────────────────────────────────────────────────────────────────────
def identify_customer_groups(rfm: pd.DataFrame, customer_df: pd.DataFrame) -> None:
    """
    Print out actionable customer group lists for business use.

    Groups:
        Top 10 Customers       → Rank by TotalRevenue
        Repeat Customers       → TotalOrders > 1
        At-Risk Customers      → Segment = "At Risk" or "Can't Lose Them"
        High-Value Customers   → CustomerTier = "Platinum" or "Gold"
        New Customers          → Segment = "New Customer"
    """
    print("=" * 65)
    print("  STEP 4: SPECIAL CUSTOMER GROUP ANALYSIS")
    print("=" * 65)

    # Merge RFM with customer features for a combined view
    combined = rfm.merge(customer_df, on="CustomerID", how="left")

    # ── Top 10 Customers by Revenue ───────────────────────────────────────────
    print("\n🏆 TOP 10 CUSTOMERS BY REVENUE:")
    print("  " + "─" * 60)
    top10 = combined.nlargest(10, "Monetary")[
        ["CustomerID", "Monetary", "Frequency", "Recency", "Segment", "PrimaryCountry"]
    ]
    for i, row in top10.iterrows():
        print(f"  #{int(i)+1:2} | CustomerID: {row['CustomerID']:>6} | "
              f"Revenue: £{row['Monetary']:>10,.2f} | "
              f"Segment: {row['Segment']}")
    print()

    # ── At-Risk Customers ─────────────────────────────────────────────────────
    at_risk = combined[combined["Segment"].isin(["At Risk", "Can't Lose Them"])]
    print(f"⚠️  AT-RISK CUSTOMERS: {len(at_risk):,}")
    print(f"   Total revenue at risk: £{at_risk['Monetary'].sum():,.2f}")
    print(f"   Average days since last purchase: {at_risk['Recency'].mean():.0f} days\n")

    # ── High-Value Customers ──────────────────────────────────────────────────
    high_val = combined[combined["Segment"].isin(["Champion", "Loyal Customer"])]
    print(f"💎 HIGH-VALUE CUSTOMERS: {len(high_val):,}")
    print(f"   Total revenue contributed: £{high_val['Monetary'].sum():,.2f}")
    rev_share = high_val["Monetary"].sum() / combined["Monetary"].sum() * 100
    print(f"   Share of total revenue: {rev_share:.1f}%\n")

    # ── Repeat Customers ──────────────────────────────────────────────────────
    repeat = combined[combined["Frequency"] > 1]
    print(f"🔁 REPEAT CUSTOMERS: {len(repeat):,} ({len(repeat)/len(combined)*100:.1f}%)")
    print(f"   Avg orders per repeat customer: {repeat['Frequency'].mean():.1f}")
    print(f"   Avg revenue per repeat customer: £{repeat['Monetary'].mean():.2f}\n")

    # ── New Customers ─────────────────────────────────────────────────────────
    new_custs = combined[combined["Segment"] == "New Customer"]
    print(f"🆕 NEW CUSTOMERS: {len(new_custs):,}")
    print(f"   Avg first-order value: £{new_custs['Monetary'].mean():.2f}\n")


# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
def save_rfm(rfm: pd.DataFrame, filepath: str) -> None:
    """Save RFM segmented data to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    rfm.to_csv(filepath, index=False)
    print(f"💾 RFM segments saved to: {filepath}\n")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load cleaned transactions
    df = pd.read_csv(CLEAN_PATH, parse_dates=["InvoiceDate"])
    customer_df = pd.read_csv(FEAT_PATH, parse_dates=["FirstPurchase", "LastPurchase"])

    # Snapshot date
    SNAPSHOT_DATE = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    # Build and score RFM
    rfm = build_rfm_table(df, SNAPSHOT_DATE)
    rfm = score_rfm(rfm)
    rfm = assign_segments(rfm)

    # Analyse groups
    identify_customer_groups(rfm, customer_df)

    # Save
    save_rfm(rfm, RFM_PATH)

    print("=" * 65)
    print("  ✅ RFM ANALYSIS COMPLETE")
    print("=" * 65)
    print(f"\n  Next step → Run: python scripts/visualizations.py\n")
