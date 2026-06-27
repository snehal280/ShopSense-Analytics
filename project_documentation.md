# Project Documentation
## E-Commerce Customer Analysis — Technical Reference

---

## 1. Project Overview

| Item | Detail |
|------|--------|
| **Project Name** | E-Commerce Customer Analysis |
| **Domain** | Retail Analytics / Customer Intelligence |
| **Type** | End-to-End Data Analytics Portfolio Project |
| **Dataset** | UCI Online Retail II |
| **Language** | Python 3.10+ |
| **Tools** | Pandas, NumPy, Matplotlib, Seaborn, SQL, Power BI |

---

## 2. Dataset Description

### Source
- **Name:** Online Retail II Dataset
- **Repository:** UCI Machine Learning Repository
- **URL:** https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

### Raw Fields

| Column | Type | Description |
|--------|------|-------------|
| `Invoice` | String | Invoice number. Prefix 'C' = cancelled order |
| `StockCode` | String | Product item code |
| `Description` | String | Product name |
| `Quantity` | Integer | Units per transaction. Negatives = returns |
| `InvoiceDate` | DateTime | Date and time of transaction |
| `Price` | Float | Unit price in sterling (£) |
| `Customer ID` | Float | Unique customer identifier (nullable) |
| `Country` | String | Country of customer residence |

### Scale
- **Original rows:** 1,067,371
- **After cleaning:** ~750,000 (retention ~70%)
- **Unique customers:** ~5,800
- **Unique products:** ~3,900
- **Date range:** 01 Dec 2009 – 09 Dec 2011

---

## 3. File-by-File Documentation

---

### 3.1 `scripts/data_cleaning.py`

**Purpose:** Transform raw Excel data into a clean, analysis-ready CSV.

**Key Functions:**

| Function | Description |
|----------|-------------|
| `load_data(filepath)` | Reads both Excel sheets and concatenates them |
| `assess_quality(df)` | Prints dtype, missing value, and duplicate report |
| `clean_data(df)` | Applies 7 cleaning rules (see below) |
| `add_basic_columns(df)` | Adds TotalPrice, Year, Month, YearMonth, DayOfWeek, Hour |
| `save_data(df, filepath)` | Saves cleaned data to CSV |

**Cleaning Rules Applied:**

| Step | Rule | Reason |
|------|------|--------|
| 1 | Remove duplicate rows | Prevents double-counting |
| 2 | Drop null CustomerID | Customer-level analysis requires ID |
| 3 | Remove Invoice starting with 'C' | Cancellations are not purchases |
| 4 | Remove Quantity ≤ 0 | Returns and errors |
| 5 | Remove Price ≤ 0 | Free items and data errors |
| 6 | Remove test StockCodes | Non-product entries |
| 7 | Fix data types | Datetime parsing, int casting |

**Output:** `data/processed/cleaned_transactions.csv`

---

### 3.2 `scripts/feature_engineering.py`

**Purpose:** Compute customer-level business metrics.

**Features Generated:**

| Feature | Formula | Business Use |
|---------|---------|-------------|
| `TotalRevenue` | `SUM(TotalPrice)` | Overall customer value |
| `TotalOrders` | `NUNIQUE(InvoiceNo)` | Loyalty indicator |
| `TotalQuantity` | `SUM(Quantity)` | Purchase volume |
| `AvgOrderValue` | `TotalRevenue / TotalOrders` | Basket size |
| `AvgItemsPerOrder` | `mean(basket_size)` | Buying behaviour |
| `CustomerLifespanDays` | `LastPurchase - FirstPurchase` | Tenure |
| `DaysSinceLastPurchase` | `SnapshotDate - LastPurchase` | Recency proxy |
| `PurchaseFrequencyDays` | `Lifespan / TotalOrders` | Buying cadence |
| `CustomerLifetimeValue` | `AOV × annual_frequency` | Long-term value |
| `PrimaryCountry` | `mode(Country)` | Geography |
| `CustomerTier` | Percentile-based | Revenue tier label |
| `IsRepeatCustomer` | `TotalOrders > 1` | Retention flag |

**Output:** `data/processed/customer_features.csv`

---

### 3.3 `scripts/rfm_analysis.py`

**Purpose:** Perform RFM segmentation and identify customer groups.

**RFM Scoring Method:**

```
Step 1: Compute R (days since last purchase), F (unique orders), M (total spend)
Step 2: Score each using pd.qcut() into quintiles (1–5)
         - R: REVERSED (low days = recent = score 5)
         - F: Normal (high frequency = score 5)
         - M: Normal (high spend = score 5)
Step 3: Combined score = R + F + M (range 3–15)
Step 4: Assign segment labels using np.select() with priority conditions
```

**Segment Definitions:**

| Segment | R_Score | F_Score | M_Score | Action |
|---------|---------|---------|---------|--------|
| Champion | ≥4 | ≥4 | ≥4 | Reward, ask for reviews |
| Loyal Customer | Any | ≥3 | ≥3 | Upsell, loyalty programme |
| Potential Loyal | ≥4 | ≥2 | ≥2 | Offer membership |
| New Customer | ≥4 | ≤1 | Any | Onboarding sequence |
| Can't Lose Them | ≤2 | ≥4 | ≥4 | Personalised win-back |
| At Risk | ≤2 | ≥3 | Any | Reactivation campaign |
| Lost | Any | Any | Score≤5 | Low-cost reactivation or sunset |

**Output:** `data/processed/rfm_segments.csv`

---

### 3.4 `scripts/visualizations.py`

**Purpose:** Generate 12 charts saved as PNG files.

**Charts Generated:**

| File | Chart Type | Insight |
|------|-----------|---------|
| `01_monthly_revenue_trend.png` | Line | Seasonal trends |
| `02_revenue_by_day.png` | Bar | Best day of week |
| `03_revenue_by_hour.png` | Bar | Peak shopping hours |
| `04_top_products_revenue.png` | Horizontal Bar | Star products |
| `05_revenue_by_country.png` | Horizontal Bar | Geo revenue |
| `06_customer_segments.png` | Donut + Bar | Segment distribution |
| `07_rfm_heatmap.png` | Heatmap | R×F spending matrix |
| `08_revenue_per_segment_boxplot.png` | Box Plot | Revenue spread |
| `09_recency_vs_monetary.png` | Scatter | Customer positioning |
| `10_aov_distribution.png` | Histogram | AOV spread |
| `11_repeat_vs_onetime.png` | Donut | Retention value |
| `12_revenue_by_tier.png` | Bar | Tier contribution |

---

### 3.5 `sql/ecommerce_analysis.sql`

**Purpose:** SQL equivalents of Python analysis for interview readiness.

**Sections:**

| Section | Queries | Topics |
|---------|---------|--------|
| 1 | 2 queries | Data overview, date range |
| 2 | 4 queries | Revenue by month, day, country, YoY |
| 3 | 3 queries | Products by revenue, volume, declining |
| 4 | 4 queries | Customer aggregation, top 20, repeat analysis, Pareto |
| 5 | 3 queries | RFM values, scoring, segment summary |
| 6 | 4 queries | Retention rate, AOV trend, cohort, new customers, Pareto |

---

## 4. How to Run the Full Pipeline

```bash
# Step 1 — Install dependencies
pip install -r requirements.txt

# Step 2 — Place dataset
# → data/raw/online_retail_II.xlsx

# Step 3 — Clean data (~2–5 mins)
python scripts/data_cleaning.py

# Step 4 — Engineer features (~30 secs)
python scripts/feature_engineering.py

# Step 5 — RFM analysis (~30 secs)
python scripts/rfm_analysis.py

# Step 6 — Generate charts (~1–2 mins)
python scripts/visualizations.py

# Step 7 — Run SQL queries
# Open sql/ecommerce_analysis.sql in DBeaver, SQLiteOnline, or any SQL tool
# Import cleaned_transactions.csv as a table named 'transactions'
```

---

## 5. Output Files Reference

```
data/processed/
├── cleaned_transactions.csv   — ~750K rows, 12 columns
├── customer_features.csv      — ~5,800 rows, 16 columns
└── rfm_segments.csv           — ~5,800 rows, 10 columns

reports/
├── final_insights_report.md   — Business findings
├── powerbi_dashboard_guide.md — Dashboard spec
└── charts/
    ├── 01_monthly_revenue_trend.png
    ├── 02_revenue_by_day.png
    ├── 03_revenue_by_hour.png
    ├── 04_top_products_revenue.png
    ├── 05_revenue_by_country.png
    ├── 06_customer_segments.png
    ├── 07_rfm_heatmap.png
    ├── 08_revenue_per_segment_boxplot.png
    ├── 09_recency_vs_monetary.png
    ├── 10_aov_distribution.png
    ├── 11_repeat_vs_onetime.png
    └── 12_revenue_by_tier.png
```

---

## 6. Key Concepts Glossary

| Term | Definition |
|------|-----------|
| **RFM** | Recency, Frequency, Monetary — marketing segmentation framework |
| **AOV** | Average Order Value = Total Revenue / Total Orders |
| **CLV** | Customer Lifetime Value — long-term revenue potential per customer |
| **Quintile** | Division of data into 5 equal-frequency groups |
| **Churn** | A customer who stops buying |
| **Cohort** | Group of customers who first purchased in the same time period |
| **Pareto** | 80/20 principle — 20% of customers = 80% of revenue |
| **Snapshot Date** | The reference "today" date used for recency calculations |
| **B2B** | Business-to-Business — selling to companies, not individuals |

---

## 7. Known Limitations

1. **December 2011 truncation** — Dataset ends mid-December 2011; the apparent revenue drop is a data artifact, not a business decline.
2. **No product categories** — StockCode and Description require manual categorisation for category-level analysis.
3. **Historical CLV only** — The CLV formula is backward-looking; predictive CLV requires probabilistic models.
4. **Single currency** — All prices are in GBP; international comparisons ignore exchange rate effects.
5. **No cost data** — We analyse revenue, not profit. Margin analysis requires COGS data not in the dataset.

---

## 8. Portfolio Presentation Structure

For presenting this project in interviews or portfolio showcases:

```
Slide 1: Problem Statement
  "A UK e-commerce retailer wants to understand who its best customers are 
   and how to grow revenue strategically."

Slide 2: Dataset & Approach
  - UCI dataset facts
  - 5-step pipeline overview

Slide 3: Data Cleaning Findings
  - What was removed and why (highlight judgement calls)

Slide 4: Key Metrics Dashboard
  - Total Revenue, AOV, Unique Customers, Top Country

Slide 5: RFM Segmentation Chart (06_customer_segments.png)
  - Explain each segment and its business meaning

Slide 6: Revenue Insights
  - Monthly trend, day of week, top products

Slide 7: Customer Behaviour
  - Pareto chart, repeat vs one-time, AOV distribution

Slide 8: Business Recommendations
  - 3 highest-impact recommendations with £ impact estimates

Slide 9: Technical Highlight
  - Show SQL RFM query or Python feature engineering code

Slide 10: Next Steps
  - Churn prediction, market basket analysis, cohort analysis
```

---

*Document version: 1.0 | Last updated: 2024*
