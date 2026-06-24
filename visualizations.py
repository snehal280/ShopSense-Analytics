"""
================================================================================
Script  : visualizations.py
Project : E-Commerce Customer Analysis
Author  : Your Name

Purpose :
    Generate all EDA and business insight visualizations.
    Charts are saved to the reports/ folder as PNG files.

Charts Generated:
    01. Monthly Revenue Trend (line chart)
    02. Revenue by Day of Week (bar chart)
    03. Revenue by Hour of Day (bar chart)
    04. Top 10 Products by Revenue (horizontal bar)
    05. Top 10 Countries by Revenue (horizontal bar)
    06. Customer Segment Distribution (pie + bar)
    07. RFM Score Distribution (heatmap)
    08. Revenue Distribution per Segment (box plot)
    09. Recency vs Monetary scatter (bubble chart)
    10. Customer Tier Distribution (donut chart)
    11. Repeat vs One-Time Customer Revenue share
    12. AOV Distribution (histogram)

How to run:
    python scripts/visualizations.py
    (Run AFTER rfm_analysis.py)
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings

# Suppress non-critical warnings (e.g. matplotlib font cache)
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH  = os.path.join(BASE_DIR, "data", "processed", "cleaned_transactions.csv")
FEAT_PATH   = os.path.join(BASE_DIR, "data", "processed", "customer_features.csv")
RFM_PATH    = os.path.join(BASE_DIR, "data", "processed", "rfm_segments.csv")
REPORT_DIR  = os.path.join(BASE_DIR, "reports", "charts")

# Create output directory if it doesn't exist
os.makedirs(REPORT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLE SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
# Set a consistent visual theme for all charts
PALETTE      = "viridis"          # Color palette
BG_COLOR     = "#0f1117"          # Dark background (portfolio-friendly)
TEXT_COLOR   = "#e0e0e0"          # Light text
ACCENT_COLOR = "#4fc3f7"          # Bright accent
GRID_COLOR   = "#2a2a3e"          # Subtle grid lines
FIG_DPI      = 150                # High resolution output

def apply_dark_style():
    """Apply a consistent dark-mode style to all matplotlib figures."""
    plt.rcParams.update({
        "figure.facecolor"  : BG_COLOR,
        "axes.facecolor"    : "#1a1a2e",
        "axes.edgecolor"    : GRID_COLOR,
        "axes.labelcolor"   : TEXT_COLOR,
        "text.color"        : TEXT_COLOR,
        "xtick.color"       : TEXT_COLOR,
        "ytick.color"       : TEXT_COLOR,
        "grid.color"        : GRID_COLOR,
        "grid.linestyle"    : "--",
        "grid.alpha"        : 0.5,
        "font.family"       : "sans-serif",
        "font.size"         : 10,
        "axes.titlesize"    : 13,
        "axes.titleweight"  : "bold",
        "figure.dpi"        : FIG_DPI,
    })

def save_fig(filename: str) -> None:
    """Save the current figure to the reports/charts directory."""
    path = os.path.join(REPORT_DIR, filename)
    plt.savefig(path, bbox_inches="tight", facecolor=BG_COLOR, dpi=FIG_DPI)
    plt.close()
    print(f"  ✅ Saved: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: Monthly Revenue Trend
# ─────────────────────────────────────────────────────────────────────────────
def plot_monthly_revenue(df: pd.DataFrame) -> None:
    """
    Line chart showing total revenue per month over the dataset's timeframe.

    Business value:
      - Identifies seasonal peaks (e.g., holiday surge in Nov–Dec).
      - Shows whether the business is growing, flat, or declining.
    """
    print("\n📈 Chart 1: Monthly Revenue Trend")

    # Group revenue by year-month period
    monthly = df.groupby("YearMonth")["TotalPrice"].sum().reset_index()
    monthly.columns = ["YearMonth", "Revenue"]

    fig, ax = plt.subplots(figsize=(14, 5))

    # Line plot with markers for each month
    ax.plot(monthly["YearMonth"], monthly["Revenue"],
            color=ACCENT_COLOR, linewidth=2.5, marker="o", markersize=5)

    # Shade area under the line for visual depth
    ax.fill_between(range(len(monthly)), monthly["Revenue"],
                    color=ACCENT_COLOR, alpha=0.15)

    # Format y-axis as £ currency (British Pounds)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"£{x/1000:.0f}K"
    ))

    # Rotate x-axis labels for readability
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly["YearMonth"], rotation=45, ha="right", fontsize=8)

    ax.set_title("Monthly Revenue Trend", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (£)")
    ax.grid(True, axis="y")

    plt.tight_layout()
    save_fig("01_monthly_revenue_trend.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Revenue by Day of Week
# ─────────────────────────────────────────────────────────────────────────────
def plot_revenue_by_day(df: pd.DataFrame) -> None:
    """
    Bar chart showing which day of the week generates the most revenue.

    Business value:
      - Helps plan marketing campaigns (e.g., launch promotions on best days).
      - Informs staffing and inventory decisions.
    """
    print("📊 Chart 2: Revenue by Day of Week")

    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday",
                  "Friday", "Saturday", "Sunday"]

    # Group revenue by DayOfWeek (0=Monday … 6=Sunday)
    day_rev = df.groupby("DayOfWeek")["TotalPrice"].sum().reindex(range(7)).fillna(0)

    colors = [ACCENT_COLOR if v == day_rev.max() else "#2d6a8a" for v in day_rev.values]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(day_labels, day_rev.values, color=colors, width=0.6, edgecolor="none")

    # Add revenue labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height * 1.01,
                f"£{height/1000:.0f}K", ha="center", va="bottom",
                fontsize=8, color=TEXT_COLOR)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}K"))
    ax.set_title("Total Revenue by Day of Week", pad=15)
    ax.set_ylabel("Revenue (£)")
    ax.set_xlabel("Day of Week")
    ax.grid(True, axis="y")

    plt.tight_layout()
    save_fig("02_revenue_by_day.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 3: Revenue by Hour of Day
# ─────────────────────────────────────────────────────────────────────────────
def plot_revenue_by_hour(df: pd.DataFrame) -> None:
    """
    Shows peak shopping hours throughout the day.
    Useful for scheduling email campaigns and flash sales.
    """
    print("🕐 Chart 3: Revenue by Hour of Day")

    hour_rev = df.groupby("Hour")["TotalPrice"].sum()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(hour_rev.index, hour_rev.values, color="#7986cb", edgecolor="none", width=0.7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}K"))
    ax.set_xticks(range(24))
    ax.set_xlabel("Hour of Day (24h)")
    ax.set_ylabel("Revenue (£)")
    ax.set_title("Revenue by Hour of Day", pad=15)
    ax.grid(True, axis="y")

    plt.tight_layout()
    save_fig("03_revenue_by_hour.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 4: Top 10 Products by Revenue
# ─────────────────────────────────────────────────────────────────────────────
def plot_top_products(df: pd.DataFrame) -> None:
    """
    Horizontal bar chart of the 10 highest-revenue products.

    Business value:
      - Identifies star products (focus marketing on these).
      - Highlights which products to ensure are always in stock.
    """
    print("🏅 Chart 4: Top 10 Products by Revenue")

    product_rev = (
        df.groupby("Description")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # Truncate long product names for display
    product_rev["Description"] = product_rev["Description"].str[:35]

    fig, ax = plt.subplots(figsize=(11, 6))
    colors = sns.color_palette("viridis", n_colors=10)
    ax.barh(product_rev["Description"][::-1], product_rev["TotalPrice"][::-1],
            color=colors[::-1], edgecolor="none", height=0.7)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}K"))
    ax.set_xlabel("Total Revenue (£)")
    ax.set_title("Top 10 Products by Revenue", pad=15)
    ax.grid(True, axis="x")

    plt.tight_layout()
    save_fig("04_top_products_revenue.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 5: Top 10 Countries by Revenue
# ─────────────────────────────────────────────────────────────────────────────
def plot_revenue_by_country(df: pd.DataFrame) -> None:
    """
    Horizontal bar chart showing which countries generate the most revenue.
    UK dominates — but international markets show growth opportunity.
    """
    print("🌍 Chart 5: Revenue by Country (Top 10)")

    country_rev = (
        df.groupby("Country")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(11, 6))
    colors = sns.color_palette("magma", n_colors=10)
    ax.barh(country_rev["Country"][::-1], country_rev["TotalPrice"][::-1],
            color=colors[::-1], edgecolor="none", height=0.7)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}K"))
    ax.set_xlabel("Total Revenue (£)")
    ax.set_title("Top 10 Countries by Revenue", pad=15)
    ax.grid(True, axis="x")

    plt.tight_layout()
    save_fig("05_revenue_by_country.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 6: Customer Segment Distribution
# ─────────────────────────────────────────────────────────────────────────────
def plot_segment_distribution(rfm: pd.DataFrame) -> None:
    """
    Combined donut + bar chart showing how customers are distributed
    across RFM segments.

    This is a portfolio highlight chart — recruiters love it!
    """
    print("🎯 Chart 6: Customer Segment Distribution")

    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # ── Left: Donut chart ─────────────────────────────────────────────────────
    ax1 = axes[0]
    colors = sns.color_palette("tab20", n_colors=len(seg_counts))
    wedges, texts, autotexts = ax1.pie(
        seg_counts["Count"],
        labels=seg_counts["Segment"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.80,
        wedgeprops=dict(width=0.55, edgecolor=BG_COLOR, linewidth=2)  # donut hole
    )
    for text in texts:
        text.set_color(TEXT_COLOR)
        text.set_fontsize(8)
    for autotext in autotexts:
        autotext.set_color(TEXT_COLOR)
        autotext.set_fontsize(7)
    ax1.set_title("Customer Segments (Donut)", pad=15)

    # ── Right: Horizontal bar ─────────────────────────────────────────────────
    ax2 = axes[1]
    sorted_seg = seg_counts.sort_values("Count")
    bars = ax2.barh(sorted_seg["Segment"], sorted_seg["Count"],
                    color=colors[:len(sorted_seg)], edgecolor="none", height=0.7)
    for bar in bars:
        width = bar.get_width()
        ax2.text(width + 5, bar.get_y() + bar.get_height() / 2,
                 f"{int(width):,}", va="center", fontsize=8, color=TEXT_COLOR)
    ax2.set_xlabel("Number of Customers")
    ax2.set_title("Customer Count by Segment", pad=15)
    ax2.grid(True, axis="x")

    plt.suptitle("RFM Customer Segmentation", fontsize=15, fontweight="bold",
                 color=TEXT_COLOR, y=1.01)
    plt.tight_layout()
    save_fig("06_customer_segments.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 7: RFM Heatmap (Average Monetary by R×F Score)
# ─────────────────────────────────────────────────────────────────────────────
def plot_rfm_heatmap(rfm: pd.DataFrame) -> None:
    """
    Heatmap: x-axis = Frequency Score, y-axis = Recency Score,
             color = Average Monetary (spend).

    Interpretation:
      - Top-right quadrant (R=5, F=5) = Champions (bright yellow).
      - Bottom-left quadrant (R=1, F=1) = Lost customers (dark).
    """
    print("🗺️  Chart 7: RFM Heatmap")

    pivot = rfm.pivot_table(
        index="R_Score", columns="F_Score", values="Monetary", aggfunc="mean"
    ).sort_index(ascending=False)

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        pivot, annot=True, fmt=".0f", cmap="YlOrRd",
        linewidths=0.5, linecolor="#333", ax=ax,
        cbar_kws={"label": "Avg Monetary (£)"}
    )
    ax.set_title("RFM Heatmap: Avg Spend by Recency × Frequency Score", pad=15)
    ax.set_xlabel("Frequency Score (1=Low, 5=High)")
    ax.set_ylabel("Recency Score (1=Old, 5=Recent)")

    plt.tight_layout()
    save_fig("07_rfm_heatmap.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 8: Revenue per Segment (Box Plot)
# ─────────────────────────────────────────────────────────────────────────────
def plot_revenue_per_segment(rfm: pd.DataFrame) -> None:
    """
    Box plot showing the distribution of individual customer revenue (Monetary)
    within each RFM segment.

    Box plots show median, quartiles, and outliers — far richer than bar charts.
    """
    print("📦 Chart 8: Revenue Distribution per Segment (Box Plot)")

    # Sort segments by median monetary for a logical ordering
    order = (rfm.groupby("Segment")["Monetary"]
             .median().sort_values(ascending=False).index.tolist())

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.boxplot(
        data=rfm, x="Segment", y="Monetary",
        order=order, palette="viridis",
        flierprops=dict(marker="o", color=ACCENT_COLOR, alpha=0.4, markersize=3),
        ax=ax
    )
    ax.set_yscale("log")  # Log scale because revenue is highly skewed
    ax.set_ylabel("Monetary Value (£, log scale)")
    ax.set_xlabel("Customer Segment")
    ax.set_title("Revenue Distribution per Customer Segment", pad=15)
    ax.tick_params(axis="x", rotation=35)
    ax.grid(True, axis="y")

    plt.tight_layout()
    save_fig("08_revenue_per_segment_boxplot.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 9: Recency vs Monetary Scatter
# ─────────────────────────────────────────────────────────────────────────────
def plot_recency_vs_monetary(rfm: pd.DataFrame) -> None:
    """
    Scatter plot: x = Recency (days), y = Monetary (£), color = Segment.

    Visual insight:
      - Top-left = Champions: recent buyers who spent a lot.
      - Bottom-right = Lost/At Risk: haven't bought in a long time, low spend.
    """
    print("🔵 Chart 9: Recency vs Monetary Scatter")

    # Sample 2000 points for performance (scatter is slow with 4000+ points)
    sample = rfm.sample(min(2000, len(rfm)), random_state=42)

    fig, ax = plt.subplots(figsize=(12, 7))
    segments = sample["Segment"].unique()
    palette  = sns.color_palette("tab10", n_colors=len(segments))
    seg_color = dict(zip(segments, palette))

    for seg in segments:
        subset = sample[sample["Segment"] == seg]
        ax.scatter(subset["Recency"], subset["Monetary"],
                   c=[seg_color[seg]], label=seg, alpha=0.6, s=30, edgecolors="none")

    ax.set_xlabel("Recency (Days Since Last Purchase)")
    ax.set_ylabel("Monetary Value (£)")
    ax.set_yscale("log")
    ax.set_title("Recency vs Monetary Value by Segment", pad=15)
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    ax.grid(True)

    plt.tight_layout()
    save_fig("09_recency_vs_monetary.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 10: AOV Distribution (Histogram)
# ─────────────────────────────────────────────────────────────────────────────
def plot_aov_distribution(customer_df: pd.DataFrame) -> None:
    """
    Histogram showing the distribution of Average Order Values across customers.

    Most customers cluster in the low-AOV range.
    A long right tail = a few very high-value customers (important for targeting).
    """
    print("📊 Chart 10: AOV Distribution")

    # Remove extreme outliers (top 1%) for a cleaner chart
    p99 = customer_df["AvgOrderValue"].quantile(0.99)
    data = customer_df[customer_df["AvgOrderValue"] <= p99]["AvgOrderValue"]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(data, bins=60, color=ACCENT_COLOR, edgecolor="none", alpha=0.8)

    median_val = data.median()
    mean_val   = data.mean()
    ax.axvline(median_val, color="#f9a825", linestyle="--", linewidth=1.5,
               label=f"Median: £{median_val:.0f}")
    ax.axvline(mean_val, color="#ef5350", linestyle="--", linewidth=1.5,
               label=f"Mean: £{mean_val:.0f}")

    ax.set_xlabel("Average Order Value (£)")
    ax.set_ylabel("Number of Customers")
    ax.set_title("Distribution of Customer Average Order Value (AOV)", pad=15)
    ax.legend()
    ax.grid(True, axis="y")

    plt.tight_layout()
    save_fig("10_aov_distribution.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 11: Repeat vs One-Time Customer Revenue Split
# ─────────────────────────────────────────────────────────────────────────────
def plot_repeat_vs_new(customer_df: pd.DataFrame) -> None:
    """
    Compare revenue contribution of repeat customers vs one-time buyers.
    Demonstrates the Pareto principle in customer value.
    """
    print("🔁 Chart 11: Repeat vs One-Time Customer Revenue")

    repeat_rev = customer_df[customer_df["IsRepeatCustomer"] == 1]["TotalRevenue"].sum()
    onetime_rev = customer_df[customer_df["IsRepeatCustomer"] == 0]["TotalRevenue"].sum()

    repeat_count = (customer_df["IsRepeatCustomer"] == 1).sum()
    onetime_count = (customer_df["IsRepeatCustomer"] == 0).sum()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Revenue split
    axes[0].pie(
        [repeat_rev, onetime_rev],
        labels=["Repeat Customers", "One-Time Buyers"],
        autopct="%1.1f%%",
        colors=["#4fc3f7", "#f06292"],
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor=BG_COLOR)
    )
    axes[0].set_title("Revenue Share", pad=15)

    # Count split
    axes[1].pie(
        [repeat_count, onetime_count],
        labels=["Repeat Customers", "One-Time Buyers"],
        autopct="%1.1f%%",
        colors=["#4fc3f7", "#f06292"],
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor=BG_COLOR)
    )
    axes[1].set_title("Customer Count Share", pad=15)

    plt.suptitle("Repeat vs One-Time Customers: Revenue & Count",
                 fontsize=13, fontweight="bold", color=TEXT_COLOR)
    plt.tight_layout()
    save_fig("11_repeat_vs_onetime.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 12: Customer Tier Revenue Contribution
# ─────────────────────────────────────────────────────────────────────────────
def plot_tier_revenue(customer_df: pd.DataFrame) -> None:
    """
    Bar chart showing revenue contribution by customer tier.
    Highlights the disproportionate value of Platinum customers.
    """
    print("💎 Chart 12: Revenue by Customer Tier")

    tier_order  = ["Platinum", "Gold", "Silver", "Bronze"]
    tier_colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#5d8aa8"]

    tier_rev = (
        customer_df.groupby("CustomerTier")["TotalRevenue"]
        .agg(["sum", "count", "mean"])
        .reindex(tier_order)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(tier_rev["CustomerTier"], tier_rev["sum"],
                  color=tier_colors, edgecolor="none", width=0.5)

    for bar, count, mean in zip(bars, tier_rev["count"], tier_rev["mean"]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height * 1.01,
                f"£{height/1000:.0f}K\n({int(count):,} custs)",
                ha="center", va="bottom", fontsize=8.5, color=TEXT_COLOR)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}K"))
    ax.set_ylabel("Total Revenue (£)")
    ax.set_xlabel("Customer Tier")
    ax.set_title("Revenue Contribution by Customer Tier", pad=15)
    ax.grid(True, axis="y")

    plt.tight_layout()
    save_fig("12_revenue_by_tier.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    apply_dark_style()

    print("=" * 65)
    print("  LOADING DATA FOR VISUALIZATIONS")
    print("=" * 65)

    df          = pd.read_csv(CLEAN_PATH, parse_dates=["InvoiceDate"])
    customer_df = pd.read_csv(FEAT_PATH,  parse_dates=["FirstPurchase", "LastPurchase"])
    rfm         = pd.read_csv(RFM_PATH)

    print(f"✅ Transactions loaded : {len(df):,}")
    print(f"✅ Customers loaded    : {len(customer_df):,}")
    print(f"✅ RFM records loaded  : {len(rfm):,}")

    print("\n" + "=" * 65)
    print("  GENERATING ALL CHARTS")
    print("=" * 65)

    plot_monthly_revenue(df)
    plot_revenue_by_day(df)
    plot_revenue_by_hour(df)
    plot_top_products(df)
    plot_revenue_by_country(df)
    plot_segment_distribution(rfm)
    plot_rfm_heatmap(rfm)
    plot_revenue_per_segment(rfm)
    plot_recency_vs_monetary(rfm)
    plot_aov_distribution(customer_df)
    plot_repeat_vs_new(customer_df)
    plot_tier_revenue(customer_df)

    print("\n" + "=" * 65)
    print(f"  ✅ ALL 12 CHARTS SAVED TO: {REPORT_DIR}")
    print("=" * 65)
    print("\n  Your project is now fully analysed and visualised!")
    print("  Open the reports/charts/ folder to view all PNG files.\n")
