# Power BI Dashboard Guide
## E-Commerce Customer Analysis — Dashboard Design Specification

---

## Overview

This guide describes exactly how to build a 3-page Power BI dashboard from the output CSV files of this project. Each page corresponds to a key business question.

**Input Files (from data/processed/):**
- `cleaned_transactions.csv`
- `customer_features.csv`
- `rfm_segments.csv`

---

## Page 1: Revenue Overview Dashboard

**Business Question:** How is revenue performing over time, and where is it coming from?

### KPI Cards (Top Row)
Place 4 KPI cards across the top of the page:

| Card | Measure | DAX Formula |
|------|---------|-------------|
| Total Revenue | Revenue | `Total Revenue = SUM(cleaned_transactions[TotalPrice])` |
| Total Orders | Orders | `Total Orders = DISTINCTCOUNT(cleaned_transactions[InvoiceNo])` |
| Avg Order Value | AOV | `AOV = [Total Revenue] / [Total Orders]` |
| Active Customers | Customers | `Active Customers = DISTINCTCOUNT(cleaned_transactions[CustomerID])` |

### Charts

**1. Monthly Revenue Trend (Line Chart)**
- X-axis: `InvoiceDate` (Month–Year hierarchy)
- Y-axis: `Total Revenue`
- Add a reference line at average monthly revenue
- Enable drill-down to weekly / daily

**2. Revenue by Country (Filled Map)**
- Location: `Country`
- Values: `Total Revenue`
- Color saturation from white (low) to dark blue (high)

**3. Top 10 Products by Revenue (Horizontal Bar Chart)**
- Y-axis: `Description` (Top 10 filter)
- X-axis: `Total Revenue`
- Color: single accent color

**4. Revenue by Day of Week (Column Chart)**
- X-axis: Day name (create column: `Day = FORMAT(cleaned_transactions[InvoiceDate], "dddd")`)
- Y-axis: `Total Revenue`
- Sort by weekday order, not alphabetically

### Slicers (Right Panel)
- Date Range slicer (InvoiceDate)
- Country multi-select slicer
- Year slicer

### DAX Measures for Page 1
```dax
Total Revenue = SUM(cleaned_transactions[TotalPrice])

Total Orders = DISTINCTCOUNT(cleaned_transactions[InvoiceNo])

AOV = 
DIVIDE(
    [Total Revenue],
    [Total Orders],
    0
)

Revenue YoY Growth = 
VAR current_year = CALCULATE([Total Revenue], DATESYTD(cleaned_transactions[InvoiceDate]))
VAR prior_year   = CALCULATE([Total Revenue], DATEADD(cleaned_transactions[InvoiceDate], -1, YEAR))
RETURN DIVIDE(current_year - prior_year, prior_year, 0)

Revenue vs Avg = 
[Total Revenue] - AVERAGEX(
    VALUES(cleaned_transactions[YearMonth]),
    [Total Revenue]
)
```

---

## Page 2: Customer Segmentation Dashboard

**Business Question:** Who are my most valuable customers and how are they segmented?

### KPI Cards (Top Row)
| Card | Measure | DAX Formula |
|------|---------|-------------|
| Total Customers | Count | `Total Customers = DISTINCTCOUNT(rfm_segments[CustomerID])` |
| Champion Customers | Count | `Champions = CALCULATE([Total Customers], rfm_segments[Segment] = "Champion")` |
| At-Risk Revenue | Revenue | `At Risk Revenue = CALCULATE(SUM(rfm_segments[Monetary]), rfm_segments[Segment] = "At Risk")` |
| Avg Customer LTV | CLV | `Avg CLV = AVERAGE(customer_features[CustomerLifetimeValue])` |

### Charts

**1. Customer Segment Donut Chart**
- Values: `CustomerID` (count)
- Legend: `Segment`
- Use distinct colors per segment (set manually in format pane)

**2. Segment Revenue vs Customer Count (Scatter Chart)**
- X-axis: Customer count per segment
- Y-axis: Total revenue per segment
- Size: Avg Order Value
- Labels: Segment names
- This reveals which segments punch above or below their weight.

**3. RFM Score Heatmap (Matrix Visual)**
- Rows: R_Score (1–5)
- Columns: F_Score (1–5)
- Values: Average Monetary
- Conditional formatting: Green gradient (low to high)

**4. Top 20 Customers Table**
- Columns: CustomerID, Country, Total Orders, Total Revenue, Avg Order Value, Segment, Customer Tier
- Sort: Total Revenue DESC
- Conditional formatting on Total Revenue column

**5. Customer Tier Donut**
- Values: `CustomerID` count
- Legend: `CustomerTier` (Bronze / Silver / Gold / Platinum)
- Colors: Bronze=#CD7F32, Silver=#C0C0C0, Gold=#FFD700, Platinum=#E5E4E2

### DAX Measures for Page 2
```dax
Total Customers = DISTINCTCOUNT(rfm_segments[CustomerID])

Champions = 
CALCULATE(
    [Total Customers],
    rfm_segments[Segment] = "Champion"
)

At Risk Revenue = 
CALCULATE(
    SUM(rfm_segments[Monetary]),
    rfm_segments[Segment] IN {"At Risk", "Can't Lose Them"}
)

Avg CLV = AVERAGE(customer_features[CustomerLifetimeValue])

Repeat Rate = 
DIVIDE(
    CALCULATE(
        [Total Customers],
        customer_features[IsRepeatCustomer] = 1
    ),
    [Total Customers],
    0
)
```

---

## Page 3: Product & Operational Dashboard

**Business Question:** What products drive revenue, and what are the operational patterns?

### KPI Cards
| Card | Measure |
|------|---------|
| Total Products | `DISTINCTCOUNT(cleaned_transactions[StockCode])` |
| Units Sold | `SUM(cleaned_transactions[Quantity])` |
| Peak Revenue Hour | Custom (see below) |
| Top Country (non-UK) | Configured as filter card |

### Charts

**1. Product Revenue Treemap**
- Group: `Description`
- Values: `Total Revenue`
- Color: Revenue intensity
- Treemap shows hierarchy — biggest boxes = biggest products

**2. Revenue by Hour (Column Chart)**
- X-axis: Hour (0–23) — create: `Hour = HOUR(cleaned_transactions[InvoiceDate])`)
- Y-axis: Total Revenue

**3. Country Revenue Map + Table**
- Show top 10 countries in a table alongside the map
- Columns: Country, Revenue, Customer Count, % of Total

**4. Quantity vs Revenue Scatter (Product Level)**
- X-axis: Total units sold per product
- Y-axis: Total revenue per product
- Outliers = low-quantity but high-revenue items (premium products)

### Conditional Formatting Tips
- In all tables: apply **data bars** on Revenue columns
- Use **traffic light icons** (red/yellow/green) on Recency:
  - Red: > 180 days
  - Yellow: 60–180 days
  - Green: < 60 days

---

## Power BI Data Model (Relationships)

```
cleaned_transactions  ──[CustomerID]──►  customer_features
cleaned_transactions  ──[CustomerID]──►  rfm_segments
customer_features     ──[CustomerID]──►  rfm_segments
```

- All relationships: **Many-to-One** (transactions to customers)
- Cross-filter direction: **Single** (from transactions to customers)

---

## Recommended Dashboard Theme

Use the **"Executive Dark"** theme or apply these colors manually:
- Background: `#0f1117`
- Card background: `#1a1a2e`
- Accent: `#4fc3f7` (light blue)
- Positive: `#66bb6a` (green)
- Negative: `#ef5350` (red)
- Neutral: `#ffa726` (orange)

**Font:** Segoe UI (Power BI default, professional)

---

## Publishing Recommendations

1. Publish to **Power BI Service** and share the dashboard link in your portfolio.
2. Enable **Row-Level Security (RLS)** if sharing with stakeholders (restrict country/segment access).
3. Set **automatic daily refresh** if connected to a live database.
4. Add **tooltips pages** — hover over any chart point to see a mini-dashboard.

---

*This dashboard design follows Microsoft's Power BI best practices and is interview-ready for Data Analyst roles.*
