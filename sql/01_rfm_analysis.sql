-- File: sql/01_rfm_analysis.sql

-- Calculate RFM Scores
WITH rfm_calc AS (
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
        -- Recency (days since last purchase)
        CURRENT_DATE - DATE(last_purchase_date) as recency,
        frequency,
        monetary,
        -- Calculate percentile ranks
        NTILE(5) OVER (ORDER BY CURRENT_DATE - DATE(last_purchase_date) DESC) as r_score,
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
    -- Customer Segmentation
    CASE 
        WHEN (r_score + f_score + m_score) >= 13 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Loyal Customers'
        WHEN (r_score + f_score + m_score) >= 7 THEN 'Potential Loyalists'
        WHEN (r_score >= 4 AND f_score <= 2) THEN 'At Risk'
        WHEN (r_score <= 2) THEN 'Lost'
        ELSE 'Regular'
    END as customer_segment
FROM rfm_scores
ORDER BY rfm_score DESC;

-- Save as view
CREATE OR REPLACE VIEW customer_rfm AS
-- (same query as above)
