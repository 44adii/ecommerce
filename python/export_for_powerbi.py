# File: python/export_for_powerbi.py

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:123456@localhost:5432/commerce')

print("Exporting data for Power BI...")

# 1. Main transactions with enriched data
query_main = """
SELECT 
    t.transaction_id,
    t.invoice_no,
    t.customer_id,
    c.customer_name,
    c.country,
    t.product_id,
    p.product_name,
    p.category,
    t.quantity,
    t.transaction_date,
    t.total_amount,
    EXTRACT(YEAR FROM t.transaction_date) as year,
    EXTRACT(MONTH FROM t.transaction_date) as month,
    EXTRACT(DAY FROM t.transaction_date) as day,
    TO_CHAR(t.transaction_date, 'Day') as day_of_week
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
JOIN products p ON t.product_id = p.product_id
"""
df_main = pd.read_sql(query_main, engine)
df_main.to_csv('outputs/powerbi_transactions.csv', index=False)
print("✅ Main transactions exported")

# 2. RFM Analysis
query_rfm = """
WITH global_max AS (
    SELECT DATE(MAX(transaction_date)) as max_date FROM transactions
),
rfm_calc AS (
    SELECT 
        customer_id,
        MAX(transaction_date) as last_purchase_date,
        COUNT(DISTINCT invoice_no) as frequency,
        SUM(total_amount) as monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT 
        customer_id,
        (SELECT max_date FROM global_max) - DATE(last_purchase_date) as recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY (SELECT max_date FROM global_max) - DATE(last_purchase_date) DESC) as r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) as m_score
    FROM rfm_calc
)
SELECT 
    customer_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) as rfm_score,
    CASE 
        WHEN (r_score + f_score + m_score) >= 13 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Loyal Customers'
        WHEN (r_score + f_score + m_score) >= 7 THEN 'Potential Loyalists'
        WHEN (r_score >= 4 AND f_score <= 2) THEN 'At Risk'
        WHEN (r_score <= 2) THEN 'Lost'
        ELSE 'Regular'
    END as customer_segment
FROM rfm_scores
"""
df_rfm = pd.read_sql(query_rfm, engine)
df_rfm.to_csv('outputs/powerbi_rfm.csv', index=False)
print("✅ RFM analysis exported")

# 3. Customer CLV
query_clv = """
WITH customer_metrics AS (
    SELECT 
        customer_id,
        MIN(transaction_date) as first_purchase,
        MAX(transaction_date) as last_purchase,
        COUNT(DISTINCT invoice_no) as total_orders,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_order_value,
        EXTRACT(MONTH FROM AGE(MAX(transaction_date), MIN(transaction_date))) as lifespan_months
    FROM transactions
    GROUP BY customer_id
)
SELECT 
    customer_id,
    total_orders,
    total_spent,
    avg_order_value,
    lifespan_months,
    CASE 
        WHEN lifespan_months > 0 
        THEN (total_spent / NULLIF(lifespan_months, 0)) * 12 * 3
        ELSE total_spent
    END as estimated_clv
FROM customer_metrics
"""
df_clv = pd.read_sql(query_clv, engine)
df_clv.to_csv('outputs/powerbi_clv.csv', index=False)
print("✅ CLV data exported")

# 4. Churn predictions
df_churn = pd.read_csv('outputs/churn_predictions.csv')
df_churn.to_csv('outputs/powerbi_churn.csv', index=False)
print("✅ Churn predictions exported")

# 5. Customer segments from K-Means
df_segments = pd.read_csv('outputs/customer_segments.csv')
df_segments[['customer_id', 'cluster', 'cluster_name', 'recency', 'frequency', 'monetary']].to_csv('outputs/powerbi_segments.csv', index=False)
print("✅ Customer segments exported")

print("\n✅ All data exported for Power BI!")
print("📁 Files location: outputs/ folder")