-- File: sql/03_revenue_analysis.sql

-- Monthly Revenue Trends
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT invoice_no) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
FROM transactions
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month;

-- Category Performance
SELECT 
    p.category,
    COUNT(DISTINCT t.invoice_no) as orders,
    SUM(t.quantity) as units_sold,
    SUM(t.total_amount) as revenue,
    AVG(t.total_amount) as avg_order_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Top Products
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COUNT(*) as times_purchased,
    SUM(t.quantity) as total_quantity,
    SUM(t.total_amount) as total_revenue
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 20;

-- Region-wise Sales
SELECT 
    c.country,
    COUNT(DISTINCT t.customer_id) as customers,
    COUNT(DISTINCT t.invoice_no) as orders,
    SUM(t.total_amount) as revenue,
    AVG(t.total_amount) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.country
ORDER BY revenue DESC;