-- ============================================================================
-- File    : ecommerce_analysis.sql
-- Project : E-Commerce Customer Analysis
-- Author  : Your Name
--
-- Purpose :
--   SQL queries that mirror the Python analysis, allowing the same insights
--   to be derived directly from a database (PostgreSQL / SQLite / BigQuery).
--
-- Assumptions:
--   Table: transactions
--   Columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate,
--             UnitPrice, CustomerID, Country, TotalPrice
--
--   All cleaning (removing cancellations, nulls, etc.) is assumed done
--   beforehand OR handled via WHERE clauses in each query.
--
-- Usage:
--   Load cleaned_transactions.csv into your DB tool of choice, then run.
--   In SQLite: .import cleaned_transactions.csv transactions
-- ============================================================================


-- ============================================================================
-- SECTION 1: DATA OVERVIEW
-- ============================================================================

-- 1.1 Total transactions, customers, products, and revenue
-- Business purpose: Quick high-level snapshot of the dataset
SELECT
    COUNT(*)                                    AS total_transactions,
    COUNT(DISTINCT CustomerID)                  AS unique_customers,
    COUNT(DISTINCT StockCode)                   AS unique_products,
    COUNT(DISTINCT InvoiceNo)                   AS total_orders,
    ROUND(SUM(TotalPrice), 2)                   AS total_revenue,
    ROUND(AVG(TotalPrice), 2)                   AS avg_revenue_per_line
FROM transactions;


-- 1.2 Date range of the dataset
-- Business purpose: Understand the time window we are analysing
SELECT
    MIN(InvoiceDate)   AS earliest_date,
    MAX(InvoiceDate)   AS latest_date,
    -- DATEDIFF calculates days between two dates (BigQuery / MySQL syntax)
    -- SQLite uses: CAST(julianday(MAX(InvoiceDate)) - julianday(MIN(InvoiceDate)) AS INT)
    DATEDIFF(MAX(InvoiceDate), MIN(InvoiceDate)) AS total_days_covered
FROM transactions;


-- ============================================================================
-- SECTION 2: REVENUE ANALYSIS
-- ============================================================================

-- 2.1 Monthly revenue trend
-- Business purpose: Identify seasonal patterns and growth trends
SELECT
    -- SUBSTR extracts the first 7 characters of InvoiceDate (YYYY-MM)
    SUBSTR(InvoiceDate, 1, 7)    AS year_month,
    ROUND(SUM(TotalPrice), 2)    AS total_revenue,
    COUNT(DISTINCT InvoiceNo)    AS total_orders,
    COUNT(DISTINCT CustomerID)   AS active_customers,
    ROUND(AVG(TotalPrice), 2)    AS avg_order_line_value
FROM transactions
GROUP BY SUBSTR(InvoiceDate, 1, 7)
ORDER BY year_month;


-- 2.2 Revenue by day of week
-- Business purpose: Find the best day to run promotions
SELECT
    CASE CAST(strftime('%w', InvoiceDate) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END                          AS day_of_week,
    ROUND(SUM(TotalPrice), 2)    AS total_revenue,
    COUNT(DISTINCT InvoiceNo)    AS orders
FROM transactions
GROUP BY strftime('%w', InvoiceDate)
ORDER BY strftime('%w', InvoiceDate);


-- 2.3 Revenue by country (Top 10)
-- Business purpose: Identify international market opportunities
SELECT
    Country,
    ROUND(SUM(TotalPrice), 2)          AS total_revenue,
    COUNT(DISTINCT CustomerID)          AS customer_count,
    COUNT(DISTINCT InvoiceNo)           AS order_count,
    ROUND(SUM(TotalPrice) * 100.0 /
        (SELECT SUM(TotalPrice) FROM transactions), 2) AS revenue_share_pct
FROM transactions
GROUP BY Country
ORDER BY total_revenue DESC
LIMIT 10;


-- 2.4 Year-over-year revenue comparison
-- Business purpose: Measure annual business growth
SELECT
    strftime('%Y', InvoiceDate)    AS year,
    ROUND(SUM(TotalPrice), 2)      AS total_revenue,
    COUNT(DISTINCT CustomerID)     AS unique_customers,
    COUNT(DISTINCT InvoiceNo)      AS total_orders,
    ROUND(AVG(TotalPrice), 2)      AS avg_order_line_value
FROM transactions
GROUP BY strftime('%Y', InvoiceDate)
ORDER BY year;


-- ============================================================================
-- SECTION 3: PRODUCT ANALYSIS
-- ============================================================================

-- 3.1 Top 10 products by revenue
-- Business purpose: Focus inventory and marketing on star products
SELECT
    StockCode,
    Description,
    ROUND(SUM(TotalPrice), 2)         AS total_revenue,
    SUM(Quantity)                      AS total_units_sold,
    COUNT(DISTINCT InvoiceNo)          AS orders_containing_product,
    ROUND(AVG(UnitPrice), 2)           AS avg_unit_price
FROM transactions
WHERE Description IS NOT NULL
  AND Description != ''
GROUP BY StockCode, Description
ORDER BY total_revenue DESC
LIMIT 10;


-- 3.2 Top 10 products by volume (units sold)
-- Business purpose: Identify high-demand / fast-moving products
SELECT
    StockCode,
    Description,
    SUM(Quantity)                      AS total_units_sold,
    ROUND(SUM(TotalPrice), 2)          AS total_revenue,
    COUNT(DISTINCT CustomerID)         AS customers_who_bought
FROM transactions
WHERE Description IS NOT NULL
GROUP BY StockCode, Description
ORDER BY total_units_sold DESC
LIMIT 10;


-- 3.3 Products with declining sales (compare first vs second half of dataset)
-- Business purpose: Early warning on products losing popularity
WITH first_half AS (
    SELECT StockCode, SUM(TotalPrice) AS revenue_h1
    FROM transactions
    WHERE InvoiceDate < (
        SELECT DATE(MIN(InvoiceDate), '+' ||
               CAST((julianday(MAX(InvoiceDate)) - julianday(MIN(InvoiceDate))) / 2 AS INT)
               || ' days')
        FROM transactions
    )
    GROUP BY StockCode
),
second_half AS (
    SELECT StockCode, SUM(TotalPrice) AS revenue_h2
    FROM transactions
    WHERE InvoiceDate >= (
        SELECT DATE(MIN(InvoiceDate), '+' ||
               CAST((julianday(MAX(InvoiceDate)) - julianday(MIN(InvoiceDate))) / 2 AS INT)
               || ' days')
        FROM transactions
    )
    GROUP BY StockCode
)
SELECT
    f.StockCode,
    ROUND(f.revenue_h1, 2)                               AS revenue_first_half,
    ROUND(s.revenue_h2, 2)                               AS revenue_second_half,
    ROUND(s.revenue_h2 - f.revenue_h1, 2)               AS revenue_change,
    ROUND((s.revenue_h2 - f.revenue_h1) * 100.0 /
          NULLIF(f.revenue_h1, 0), 1)                    AS pct_change
FROM first_half f
JOIN second_half s ON f.StockCode = s.StockCode
WHERE f.revenue_h1 > 100   -- Only meaningful products
ORDER BY pct_change ASC
LIMIT 15;


-- ============================================================================
-- SECTION 4: CUSTOMER ANALYSIS
-- ============================================================================

-- 4.1 Customer-level aggregation (the base customer table)
-- Business purpose: One row per customer with key metrics
SELECT
    CustomerID,
    Country,
    MIN(InvoiceDate)                          AS first_purchase,
    MAX(InvoiceDate)                          AS last_purchase,
    COUNT(DISTINCT InvoiceNo)                 AS total_orders,
    ROUND(SUM(TotalPrice), 2)                 AS total_revenue,
    ROUND(SUM(TotalPrice) /
          COUNT(DISTINCT InvoiceNo), 2)        AS avg_order_value,
    SUM(Quantity)                             AS total_items_purchased,
    -- Days since last purchase (using SQLite date math)
    CAST(julianday('now') -
         julianday(MAX(InvoiceDate)) AS INT)   AS recency_days
FROM transactions
GROUP BY CustomerID, Country
ORDER BY total_revenue DESC;


-- 4.2 Top 20 customers by total revenue
-- Business purpose: Identify VIP customers for premium treatment
SELECT
    CustomerID,
    Country,
    COUNT(DISTINCT InvoiceNo)           AS total_orders,
    ROUND(SUM(TotalPrice), 2)           AS total_revenue,
    ROUND(SUM(TotalPrice) /
          COUNT(DISTINCT InvoiceNo), 2)  AS avg_order_value,
    RANK() OVER (ORDER BY SUM(TotalPrice) DESC) AS revenue_rank
FROM transactions
GROUP BY CustomerID, Country
ORDER BY total_revenue DESC
LIMIT 20;


-- 4.3 Repeat customers vs one-time buyers
-- Business purpose: Understand customer retention rates
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-Time Buyer'
        WHEN order_count BETWEEN 2 AND 5 THEN 'Occasional Buyer (2-5 orders)'
        WHEN order_count BETWEEN 6 AND 15 THEN 'Regular Buyer (6-15 orders)'
        ELSE 'Loyal Buyer (15+ orders)'
    END                             AS buyer_type,
    COUNT(CustomerID)               AS customer_count,
    ROUND(SUM(total_revenue), 2)    AS total_revenue,
    ROUND(AVG(avg_order_value), 2)  AS avg_order_value
FROM (
    SELECT
        CustomerID,
        COUNT(DISTINCT InvoiceNo)           AS order_count,
        SUM(TotalPrice)                     AS total_revenue,
        SUM(TotalPrice) /
          COUNT(DISTINCT InvoiceNo)          AS avg_order_value
    FROM transactions
    GROUP BY CustomerID
) customer_summary
GROUP BY buyer_type
ORDER BY total_revenue DESC;


-- 4.4 Customer spending distribution (percentile analysis)
-- Business purpose: Understand revenue concentration (Pareto effect)
WITH customer_revenue AS (
    SELECT
        CustomerID,
        ROUND(SUM(TotalPrice), 2) AS total_revenue
    FROM transactions
    GROUP BY CustomerID
),
ranked AS (
    SELECT *,
           NTILE(10) OVER (ORDER BY total_revenue DESC) AS revenue_decile
    FROM customer_revenue
)
SELECT
    revenue_decile                          AS decile,
    COUNT(*)                                AS customer_count,
    ROUND(SUM(total_revenue), 2)            AS decile_revenue,
    ROUND(SUM(total_revenue) * 100.0 /
        (SELECT SUM(total_revenue) FROM customer_revenue), 2) AS pct_of_total_revenue
FROM ranked
GROUP BY revenue_decile
ORDER BY revenue_decile;


-- ============================================================================
-- SECTION 5: RFM ANALYSIS IN SQL
-- ============================================================================

-- 5.1 Compute raw RFM values
-- Business purpose: Foundation for customer segmentation
WITH snapshot AS (
    -- The reference "today" date — one day after the last transaction
    SELECT DATE(MAX(InvoiceDate), '+1 day') AS snapshot_date
    FROM transactions
),
rfm_base AS (
    SELECT
        t.CustomerID,
        -- Recency: days since last purchase
        CAST(julianday(s.snapshot_date) - julianday(MAX(t.InvoiceDate)) AS INT) AS recency,
        -- Frequency: number of unique orders
        COUNT(DISTINCT t.InvoiceNo)                                               AS frequency,
        -- Monetary: total amount spent
        ROUND(SUM(t.TotalPrice), 2)                                               AS monetary
    FROM transactions t, snapshot s
    GROUP BY t.CustomerID
)
SELECT * FROM rfm_base ORDER BY monetary DESC;


-- 5.2 RFM scoring using NTILE (quintile scoring)
-- Business purpose: Score each customer 1–5 per RFM dimension
WITH snapshot AS (
    SELECT DATE(MAX(InvoiceDate), '+1 day') AS snapshot_date FROM transactions
),
rfm_base AS (
    SELECT
        t.CustomerID,
        CAST(julianday(s.snapshot_date) - julianday(MAX(t.InvoiceDate)) AS INT) AS recency,
        COUNT(DISTINCT t.InvoiceNo)   AS frequency,
        ROUND(SUM(t.TotalPrice), 2)   AS monetary
    FROM transactions t, snapshot s
    GROUP BY t.CustomerID
),
rfm_scored AS (
    SELECT
        CustomerID,
        recency,
        frequency,
        monetary,
        -- Recency: lower = better → REVERSED scoring (5=best)
        6 - NTILE(5) OVER (ORDER BY recency ASC)   AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
    FROM rfm_base
)
SELECT
    CustomerID,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score)           AS rfm_score,
    -- Assign segments based on score combinations
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champion'
        WHEN f_score >= 3 AND m_score >= 3                   THEN 'Loyal Customer'
        WHEN r_score >= 4 AND f_score >= 2                   THEN 'Potential Loyal'
        WHEN r_score >= 4 AND f_score <= 1                   THEN 'New Customer'
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4  THEN "Can't Lose Them"
        WHEN r_score <= 2 AND f_score >= 3                   THEN 'At Risk'
        WHEN (r_score + f_score + m_score) <= 5              THEN 'Lost'
        ELSE 'Others'
    END AS segment
FROM rfm_scored
ORDER BY rfm_score DESC;


-- 5.3 Segment summary: revenue and count per segment
-- Business purpose: Executive dashboard-level view of customer segments
WITH snapshot AS (
    SELECT DATE(MAX(InvoiceDate), '+1 day') AS snapshot_date FROM transactions
),
rfm_base AS (
    SELECT
        t.CustomerID,
        CAST(julianday(s.snapshot_date) - julianday(MAX(t.InvoiceDate)) AS INT) AS recency,
        COUNT(DISTINCT t.InvoiceNo)   AS frequency,
        ROUND(SUM(t.TotalPrice), 2)   AS monetary
    FROM transactions t, snapshot s
    GROUP BY t.CustomerID
),
rfm_scored AS (
    SELECT CustomerID, recency, frequency, monetary,
        6 - NTILE(5) OVER (ORDER BY recency ASC)   AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
    FROM rfm_base
),
rfm_segmented AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champion'
            WHEN f_score >= 3 AND m_score >= 3                   THEN 'Loyal Customer'
            WHEN r_score >= 4 AND f_score >= 2                   THEN 'Potential Loyal'
            WHEN r_score >= 4 AND f_score <= 1                   THEN 'New Customer'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4  THEN "Can't Lose Them"
            WHEN r_score <= 2 AND f_score >= 3                   THEN 'At Risk'
            WHEN (r_score + f_score + m_score) <= 5              THEN 'Lost'
            ELSE 'Others'
        END AS segment
    FROM rfm_scored
)
SELECT
    segment,
    COUNT(CustomerID)              AS customer_count,
    ROUND(SUM(monetary), 2)        AS total_revenue,
    ROUND(AVG(monetary), 2)        AS avg_revenue_per_customer,
    ROUND(AVG(recency), 0)         AS avg_recency_days,
    ROUND(AVG(frequency), 1)       AS avg_orders
FROM rfm_segmented
GROUP BY segment
ORDER BY total_revenue DESC;


-- ============================================================================
-- SECTION 6: BUSINESS KPI QUERIES
-- ============================================================================

-- 6.1 Customer Retention Rate (cohort-based approximation)
-- Business purpose: % of customers who returned after first purchase
WITH first_purchases AS (
    SELECT CustomerID, MIN(SUBSTR(InvoiceDate, 1, 7)) AS first_month
    FROM transactions
    GROUP BY CustomerID
),
subsequent_purchases AS (
    SELECT DISTINCT t.CustomerID
    FROM transactions t
    JOIN first_purchases f ON t.CustomerID = f.CustomerID
    WHERE SUBSTR(t.InvoiceDate, 1, 7) > f.first_month  -- any purchase after first month
)
SELECT
    COUNT(DISTINCT f.CustomerID)  AS total_customers,
    COUNT(DISTINCT s.CustomerID)  AS returning_customers,
    ROUND(COUNT(DISTINCT s.CustomerID) * 100.0 /
          COUNT(DISTINCT f.CustomerID), 2) AS retention_rate_pct
FROM first_purchases f
LEFT JOIN subsequent_purchases s ON f.CustomerID = s.CustomerID;


-- 6.2 Average Order Value (AOV) over time
-- Business purpose: Track if customers are spending more per order month-by-month
SELECT
    SUBSTR(InvoiceDate, 1, 7)      AS year_month,
    COUNT(DISTINCT InvoiceNo)       AS total_orders,
    ROUND(SUM(TotalPrice), 2)       AS total_revenue,
    ROUND(SUM(TotalPrice) /
          COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM transactions
GROUP BY SUBSTR(InvoiceDate, 1, 7)
ORDER BY year_month;


-- 6.3 Revenue per customer over time (cohort revenue)
-- Business purpose: Track how customer cohorts perform over their lifetime
SELECT
    first_month                        AS cohort_month,
    COUNT(DISTINCT c.CustomerID)       AS cohort_size,
    ROUND(SUM(t.TotalPrice), 2)        AS lifetime_revenue,
    ROUND(SUM(t.TotalPrice) /
          COUNT(DISTINCT c.CustomerID), 2) AS revenue_per_customer
FROM transactions t
JOIN (
    SELECT CustomerID, MIN(SUBSTR(InvoiceDate, 1, 7)) AS first_month
    FROM transactions
    GROUP BY CustomerID
) c ON t.CustomerID = c.CustomerID
GROUP BY first_month
ORDER BY cohort_month;


-- 6.4 New customer acquisition per month
-- Business purpose: How many new customers do we gain each month?
SELECT
    SUBSTR(InvoiceDate, 1, 7)          AS month,
    COUNT(DISTINCT CustomerID)          AS new_customers
FROM transactions t
WHERE SUBSTR(InvoiceDate, 1, 7) = (
    -- Subquery: find the FIRST month this customer ever appeared
    SELECT MIN(SUBSTR(InvoiceDate, 1, 7))
    FROM transactions t2
    WHERE t2.CustomerID = t.CustomerID
)
GROUP BY SUBSTR(InvoiceDate, 1, 7)
ORDER BY month;


-- 6.5 Revenue concentration: Pareto analysis (top 20% of customers)
-- Business purpose: Confirm the 80/20 rule — do 20% of customers = 80% of revenue?
WITH customer_revenue AS (
    SELECT CustomerID, ROUND(SUM(TotalPrice), 2) AS total_revenue
    FROM transactions
    GROUP BY CustomerID
    ORDER BY total_revenue DESC
),
totals AS (
    SELECT SUM(total_revenue) AS grand_total, COUNT(*) AS total_customers
    FROM customer_revenue
),
top_20pct AS (
    SELECT SUM(cr.total_revenue) AS top20_revenue,
           COUNT(cr.CustomerID)  AS top20_count
    FROM customer_revenue cr, totals t
    WHERE cr.CustomerID IN (
        SELECT CustomerID FROM customer_revenue
        ORDER BY total_revenue DESC
        LIMIT CAST(t.total_customers * 0.20 AS INT)
    )
)
SELECT
    t.total_customers,
    tp.top20_count                                      AS top_20pct_customers,
    ROUND(tp.top20_revenue, 2)                          AS top_20pct_revenue,
    ROUND(tp.top20_revenue * 100.0 / t.grand_total, 1) AS revenue_share_pct
FROM totals t, top_20pct tp;
