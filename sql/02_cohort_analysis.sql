-- File: sql/02_cohort_analysis.sql

WITH cohort_items AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(transaction_date)) as cohort_month
    FROM transactions
    GROUP BY customer_id
),
user_activities AS (
    SELECT 
        t.customer_id,
        DATE_TRUNC('month', t.transaction_date) as activity_month,
        ci.cohort_month
    FROM transactions t
    JOIN cohort_items ci ON t.customer_id = ci.customer_id
),
cohort_size AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) as num_users
    FROM cohort_items
    GROUP BY cohort_month
),
retention_table AS (
    SELECT 
        ua.cohort_month,
        ua.activity_month,
        COUNT(DISTINCT ua.customer_id) as num_users
    FROM user_activities ua
    GROUP BY ua.cohort_month, ua.activity_month
)
SELECT 
    rt.cohort_month,
    rt.activity_month,
    cs.num_users as cohort_size,
    rt.num_users as active_users,
    ROUND(100.0 * rt.num_users / cs.num_users, 2) as retention_rate,
    EXTRACT(MONTH FROM AGE(rt.activity_month, rt.cohort_month)) as month_number
FROM retention_table rt
JOIN cohort_size cs ON rt.cohort_month = cs.cohort_month
ORDER BY rt.cohort_month, rt.activity_month;