# Resume Bullets & Interview Preparation
## E-Commerce Customer Analysis Project

---

## ✅ Resume Bullet Points

Copy and customise these bullet points for your resume / CV.
Tip: Always quantify results where possible. Recruiters love numbers.

---

### Data Analyst / Junior Data Analyst Role

```
• Conducted end-to-end customer behavior analysis on 1M+ transactions from a UK-based 
  e-commerce retailer using Python (Pandas, NumPy, Matplotlib, Seaborn), uncovering 
  actionable insights that informed strategic marketing decisions.

• Engineered 12+ customer-level features including Average Order Value (AOV), Customer 
  Lifetime Value (CLV), Purchase Frequency, and Customer Lifespan using Pandas groupby 
  aggregations and datetime operations.

• Implemented RFM (Recency, Frequency, Monetary) segmentation using quintile scoring, 
  classifying 5,800+ customers into 10 actionable segments (Champions, At Risk, etc.) 
  and identifying £800K+ in recoverable revenue from at-risk segments.

• Applied the Pareto Principle analysis and confirmed top 20% of customers generate 80% 
  of revenue, enabling targeted retention strategy for high-value customer cohorts.

• Built 12 publication-quality data visualisations (line charts, heatmaps, box plots, 
  scatter plots, donut charts) using Matplotlib and Seaborn, revealing peak revenue 
  months, best-performing products, and customer spending distribution.

• Wrote 20+ optimised SQL queries (Window Functions, CTEs, NTILE) to replicate Python 
  analysis in a database environment, enabling real-time querying of business KPIs.

• Designed a 3-page Power BI interactive dashboard with 15+ KPI metrics and DAX measures, 
  enabling stakeholder self-service analytics across Revenue, Segmentation, and Product views.

• Delivered 8 data-driven business recommendations including targeted email campaign 
  scheduling, VIP loyalty programme design, and international market expansion strategy.
```

---

### Shorter Version (For space-constrained CVs)

```
• Performed RFM customer segmentation on 1M+ e-commerce transactions; identified 
  £800K+ at-risk revenue and top 20% customers driving 80% of total revenue.

• Built end-to-end Python analytics pipeline: data cleaning → feature engineering 
  → segmentation → 12 Seaborn/Matplotlib visualisations → Power BI dashboard.

• Authored 20+ SQL queries (CTEs, Window Functions) for customer retention, cohort, 
  and Pareto analysis; documented 8 strategic business recommendations.
```

---

### For "Projects" Section of Resume

```
E-Commerce Customer Analysis                                          [GitHub Link]
Tools: Python | Pandas | Seaborn | SQL | Power BI

• Analysed 1M+ transactions to identify customer segments, revenue trends, and 
  product performance for a UK-based online retailer.
• Applied RFM segmentation (quintile scoring) to classify 5,800+ customers into 
  10 actionable groups; flagged £800K in at-risk revenue.
• Delivered a 3-page Power BI dashboard with 15 KPIs and 8 strategic recommendations.
```

---

## 🎤 Interview Questions & Detailed Answers

### SECTION A: Project-Specific Questions

---

**Q1. Tell me about this project. What did you do and why?**

*Answer:*
"This is an end-to-end customer analytics project built on the UCI Online Retail II dataset — a real dataset from a UK-based online retailer with over 1 million transactions spanning 2009 to 2011.

My goal was to simulate what a data analyst would do at an e-commerce company: understand who the customers are, how they behave, and what actions the business should take to grow revenue and improve retention.

I built a complete Python pipeline covering data cleaning, feature engineering, RFM segmentation, EDA with 12 visualisations, SQL analysis, and a Power BI dashboard. The key finding was that the top 20% of customers generate 80% of revenue, and there was approximately £800K in recoverable revenue sitting in dormant 'At Risk' segments."

---

**Q2. What is RFM Analysis? Explain it simply.**

*Answer:*
"RFM stands for Recency, Frequency, and Monetary.

- **Recency** asks: how recently did the customer buy? A customer who bought yesterday is more likely to buy again than one who bought 2 years ago.
- **Frequency** asks: how often do they buy? A customer with 20 orders is more loyal than one with 1 order.
- **Monetary** asks: how much have they spent in total? Higher spenders are more valuable.

We score each customer 1 to 5 on each dimension using quintiles — equal-sized groups. A score of 5 means best, 1 means worst. The combined RFM score ranges from 3 to 15 and tells us exactly where each customer stands.

Champions score 5-5-5: they bought recently, buy often, and spend the most. Lost customers score 1-1-1: they haven't bought in ages, rarely bought, and spent very little."

---

**Q3. Why did you choose this specific dataset?**

*Answer:*
"I chose the UCI Online Retail II dataset for several reasons:
1. **Real data** — it's actual transaction data from a real UK company, not synthetic.
2. **Well-documented** — widely used in academic papers and data science tutorials, so I can benchmark my findings.
3. **Rich for analysis** — it has all the columns needed for RFM: customer ID, invoice date, quantity, and price.
4. **Appropriate size** — 1 million+ rows is big enough to be realistic but manageable on a laptop.
5. **Interview-recognised** — many data analyst interviewers are familiar with it, which helps when discussing the project."

---

**Q4. What data cleaning steps did you perform and why?**

*Answer:*
"I performed 7 key cleaning steps:

1. **Removed duplicates** — exact copy rows that would inflate metrics.
2. **Dropped rows with missing CustomerID** — you can't do customer analysis without a customer identifier.
3. **Removed cancelled orders** — invoices starting with 'C' are refunds, not purchases. Including them would understate revenue.
4. **Filtered Quantity ≤ 0** — negative quantities represent returns; zero is meaningless for revenue.
5. **Filtered Price ≤ 0** — free items and data errors.
6. **Removed test StockCodes** — codes like 'POST', 'DOT', and 'BANK CHARGES' are not real products.
7. **Fixed data types** — InvoiceDate was read as a string; I converted it to datetime so date math works correctly.

After cleaning, I retained about 75% of the original rows — a healthy retention rate that shows the dataset was mostly good quality."

---

**Q5. What is Customer Lifetime Value (CLV) and how did you calculate it?**

*Answer:*
"Customer Lifetime Value is the total revenue a business can expect from a customer over their entire relationship.

I used a simplified historical CLV formula:
- First I calculated the customer's annual purchase rate (orders per year based on their active lifespan).
- Then multiplied: CLV = Average Order Value × Annual Purchase Frequency.

This gives an annualised revenue expectation per customer. For example, a customer with an AOV of £300 who orders 4 times per year has a CLV of £1,200 per year.

I noted this is a simplified model. In an advanced project, I would use the BG/NBD model (Beta-Geometric/Negative Binomial Distribution) combined with the Gamma-Gamma model for a more accurate probabilistic prediction."

---

**Q6. Explain what a quartile and quintile are.**

*Answer:*
"A **quartile** divides data into 4 equal groups: Q1 (bottom 25%), Q2 (50%), Q3 (75%), Q4 (top 25%).

A **quintile** divides data into 5 equal groups. For RFM scoring, I used quintiles because I wanted 5 score levels (1–5).

Pandas' `pd.qcut()` function does this automatically — it finds the cut-off values that create 5 groups with equal numbers of customers in each group. This is better than fixed thresholds because it adapts to the actual data distribution."

---

**Q7. What SQL concepts did you use in this project?**

*Answer:*
"I used several advanced SQL concepts:

- **CTEs (Common Table Expressions)** — used `WITH` clauses to build RFM scores in steps, making the query readable and modular.
- **Window Functions** — used `NTILE(5) OVER (ORDER BY ...)` to create quintile scores, and `RANK() OVER (...)` to rank customers by revenue.
- **Subqueries** — for finding first purchase dates and doing cohort calculations.
- **CASE WHEN** — for assigning segment labels based on score conditions.
- **GROUP BY + HAVING** — for aggregating at customer level.
- **DATEDIFF / julianday** — for calculating days between dates (recency).

These are exactly the SQL skills tested in data analyst interviews."

---

**Q8. What is the Pareto Principle in the context of customer analytics?**

*Answer:*
"The Pareto Principle, also called the 80/20 rule, states that roughly 80% of effects come from 20% of causes.

In customer analytics: **20% of customers generate approximately 80% of revenue**. My analysis confirmed this in the UCI dataset.

Why does this matter for business? It means the business should not treat all customers equally. It should identify that top 20% and invest heavily in retaining them. Losing one Platinum customer is equivalent to losing ten Bronze customers in revenue terms.

The actionable implication: allocate 80% of your CRM budget to the top 20% of customers."

---

### SECTION B: Technical Concepts

---

**Q9. What is the difference between `groupby()` and `pivot_table()` in Pandas?**

*Answer:*
"Both are used for aggregation, but they work differently:

- `groupby()` is more flexible and returns a GroupBy object. You then call `.agg()`, `.sum()`, `.mean()` etc. on it. It's ideal for creating a flat summary table.

- `pivot_table()` reshapes data into a 2D matrix with one column becoming row labels and another becoming column labels. It's perfect for creating cross-tabulations — like our RFM heatmap where rows are R_Score and columns are F_Score.

In this project, I used `groupby()` for customer-level aggregations and `pivot_table()` for the RFM heatmap."

---

**Q10. Why did you use `pd.qcut()` instead of `pd.cut()` for RFM scoring?**

*Answer:*
"`pd.cut()` creates bins of equal width (e.g., every £100 gap is a bin). This creates very uneven groups because most customers cluster in the low-revenue range.

`pd.qcut()` creates bins of equal frequency — each bin contains roughly the same number of customers. This ensures our RFM scoring is balanced: 20% of customers in each score bucket, giving a fair distribution.

In RFM analysis, equal-frequency scoring is the industry standard because it prevents one score value from being extremely common while another is almost empty."

---

**Q11. How would you improve this project?**

*Answer:*
"Several directions:

1. **Predictive Churn Model** — Train a logistic regression or Random Forest classifier to predict which customers will churn in the next 30/60/90 days, so the business can act proactively.

2. **Market Basket Analysis** — Use the Apriori algorithm or FP-Growth to discover product association rules (e.g., 'Customers who buy X also buy Y') for recommendation engine input.

3. **Probabilistic CLV** — Replace my simple CLV with the BG/NBD + Gamma-Gamma model, which predicts future purchase behaviour based on historical patterns.

4. **Cohort Retention Analysis** — Build a retention heatmap showing what % of each monthly cohort returns in months 1, 2, 3, etc.

5. **NLP on Product Descriptions** — Use TF-IDF or word embeddings to cluster products into categories automatically (the dataset has no category column)."

---

**Q12. How do you handle outliers in customer spending data?**

*Answer:*
"Customer spending data is almost always right-skewed — a few customers spend enormous amounts while most spend modestly. Outliers here are often real and important (your VIP customers), so you don't blindly remove them.

My approach:
1. **Understand before removing** — I first plotted the distribution and used IQR analysis to understand the outlier magnitude.
2. **Log transformation** — For visualisations like box plots and scatter plots, I applied `log scale` so outliers don't visually dominate.
3. **Segment-level analysis** — Outliers belong to the Platinum/Champion segments — they're reported separately, not averaged in.
4. **Cap only for charts** — For histograms showing the general population, I capped at the 99th percentile purely for display purposes while keeping the full data in all calculations."

---

**Q13. Describe a time you found a surprising insight from data.**

*Answer (for this project):*
"One insight that surprised me was the **day-of-week pattern**. Most people assume online retail peaks on weekends. But this dataset showed Thursday had the highest revenue and weekends had the lowest.

Once I dug deeper, it made sense — this is a B2B (Business-to-Business) wholesaler, not a consumer retailer. Businesses place orders mid-week when their teams are planning inventory, not on weekends. This completely changed the recommended marketing calendar from 'weekend promotions' to 'mid-week email campaigns.'"

---

**Q14. What is the difference between `nunique()` and `count()` in Pandas?**

*Answer:*
"`count()` counts all non-null values in a column — including duplicates.

`nunique()` counts only distinct/unique values.

For frequency in RFM, I used `InvoiceNo.nunique()` because a customer might have 50 rows in the dataset (one per product line) but only 5 unique invoices (5 actual orders). Using `count()` would have massively over-counted orders. `nunique()` correctly gives us the number of distinct shopping trips."

---

### SECTION C: Business & Soft Skills Questions

---

**Q15. How would you present these findings to a non-technical stakeholder?**

*Answer:*
"I would:
1. Start with the business question, not the methodology — 'We found that 7% of your customers generate 34% of your revenue.'
2. Use the Power BI dashboard for visual storytelling — show, don't tell.
3. Translate every finding into a financial impact — '394 at-risk customers represent £800K in potential lost revenue.'
4. Prioritise 3 recommendations with clear ROI estimates, not 20 bullet points.
5. End with 'What do you want to do about this?' — drive decision, not just information.

I avoid jargon like 'quintile', 'RFM', or 'chi-squared' with business stakeholders unless asked."

---

**Q16. What business recommendations came from your analysis?**

*Answer:*
"I made 8 recommendations. The top 3 with highest impact:

1. **Win-back campaign for At-Risk customers** — 394 customers who were previously loyal but haven't bought in 60–180 days. A targeted email sequence offering a personalised discount could recover £200K+ in revenue. Cost: minimal (email marketing).

2. **VIP loyalty programme for Champions** — 412 Champion customers generate 34% of revenue. A dedicated account manager, early access to new products, and exclusive discounts would reduce their churn risk and increase their CLV further.

3. **Mid-week promotional timing** — Data shows Thursday is peak revenue day. Shifting all email campaigns and flash sales to Tuesday–Thursday would improve open rates and conversion."

---

*This document serves as both interview preparation and a portfolio talking-point guide.*
*Customise the numbers with your actual results when you run the project on the real dataset.*
