-- File: sql/04_advanced_kpis.sql

-- Customer Lifetime Value
WITH customer_metrics AS (
    SELECT 
        customer_id,
        MIN(transaction_date) as first_purchase,
        MAX(transaction_date) as last_purchase,
        COUNT(DISTINCT invoice_no) as total_orders,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_order_value,
        -- Calculate customer lifespan in months
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
    -- Simple CLV calculation
    CASE 
        WHEN lifespan_months > 0 
        THEN (total_spent / NULLIF(lifespan_months, 0)) * 12 * 3  -- Projected 3-year value
        ELSE total_spent
    END as estimated_clv,
    -- Purchase frequency
    CASE 
        WHEN lifespan_months > 0 
        THEN total_orders / NULLIF(lifespan_months, 0) * 12
        ELSE total_orders
    END as annual_purchase_frequency
FROM customer_metrics
ORDER BY estimated_clv DESC;

-- Churn Rate Calculation
WITH customer_last_purchase AS (
    SELECT 
        customer_id,
        MAX(transaction_date) as last_purchase_date,
        CURRENT_DATE - DATE(MAX(transaction_date)) as days_since_purchase
    FROM transactions
    GROUP BY customer_id
),
churn_classification AS (
    SELECT 
        customer_id,
        last_purchase_date,
        days_since_purchase,
        CASE 
            WHEN days_since_purchase > 180 THEN 'Churned'
            WHEN days_since_purchase > 90 THEN 'At Risk'
            ELSE 'Active'
        END as churn_status
    FROM customer_last_purchase
)
SELECT 
    churn_status,
    COUNT(*) as customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM churn_classification
GROUP BY churn_status;

-- Monthly Churn Rate
WITH monthly_active AS (
    SELECT 
        DATE_TRUNC('month', transaction_date) as month,
        COUNT(DISTINCT customer_id) as active_customers
    FROM transactions
    GROUP BY DATE_TRUNC('month', transaction_date)
),
monthly_churn AS (
    SELECT 
        curr.month,
        curr.active_customers as current_month,
        LAG(curr.active_customers) OVER (ORDER BY curr.month) as previous_month,
        LAG(curr.active_customers) OVER (ORDER BY curr.month) - curr.active_customers as churned_customers
    FROM monthly_active curr
)
SELECT 
    month,
    current_month,
    previous_month,
    churned_customers,
    ROUND(100.0 * churned_customers / NULLIF(previous_month, 0), 2) as churn_rate_percentage
FROM monthly_churn
WHERE previous_month IS NOT NULL
ORDER BY month DESC;

-- Customer Retention Rate
WITH first_purchase AS (
    SELECT 
        customer_id,
        MIN(DATE_TRUNC('month', transaction_date)) as first_month
    FROM transactions
    GROUP BY customer_id
),
subsequent_purchases AS (
    SELECT 
        fp.first_month,
        COUNT(DISTINCT CASE WHEN DATE_TRUNC('month', t.transaction_date) > fp.first_month 
                       THEN fp.customer_id END) as retained_customers,
        COUNT(DISTINCT fp.customer_id) as total_customers
    FROM first_purchase fp
    LEFT JOIN transactions t ON fp.customer_id = t.customer_id
    GROUP BY fp.first_month
)
SELECT 
    first_month,
    total_customers,
    retained_customers,
    ROUND(100.0 * retained_customers / total_customers, 2) as retention_rate
FROM subsequent_purchases
ORDER BY first_month DESC;