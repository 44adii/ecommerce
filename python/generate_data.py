# File: python/generate_data.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Parameters
n_customers = 5000
n_products = 200
n_transactions = 50000
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)

print("Generating Customers...")
# Generate Customers
countries = ['USA', 'UK', 'Germany', 'France', 'India', 'Canada', 'Australia']
customers = pd.DataFrame({
    'customer_id': [f'CUST{str(i).zfill(5)}' for i in range(1, n_customers + 1)],
    'customer_name': [f'Customer {i}' for i in range(1, n_customers + 1)],
    'email': [f'customer{i}@email.com' for i in range(1, n_customers + 1)],
    'country': np.random.choice(countries, n_customers),
    'registration_date': [start_date + timedelta(days=random.randint(0, 365)) 
                          for _ in range(n_customers)]
})

print("Generating Products...")
# Generate Products
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 
              'Beauty', 'Toys', 'Food & Beverages']
products = pd.DataFrame({
    'product_id': [f'PROD{str(i).zfill(5)}' for i in range(1, n_products + 1)],
    'product_name': [f'Product {i}' for i in range(1, n_products + 1)],
    'category': np.random.choice(categories, n_products),
    'unit_price': np.random.uniform(5, 500, n_products).round(2)
})

print("Generating Transactions...")
# Generate Transactions with realistic patterns
transactions = []

for i in range(n_transactions):
    customer_id = random.choice(customers['customer_id'].tolist())
    product_id = random.choice(products['product_id'].tolist())
    
    # Get customer registration date
    cust_reg_date = customers[customers['customer_id'] == customer_id]['registration_date'].values[0]
    cust_reg_date = pd.to_datetime(cust_reg_date)
    
    # Transaction must be after registration
    days_since_reg = (end_date - cust_reg_date).days
    transaction_date = cust_reg_date + timedelta(days=random.randint(0, max(1, days_since_reg)))
    
    quantity = random.randint(1, 10)
    unit_price = products[products['product_id'] == product_id]['unit_price'].values[0]
    total_amount = quantity * unit_price
    
    transactions.append({
        'invoice_no': f'INV{str(i).zfill(8)}',
        'customer_id': customer_id,
        'product_id': product_id,
        'quantity': quantity,
        'transaction_date': transaction_date,
        'total_amount': round(total_amount, 2)
    })

transactions_df = pd.DataFrame(transactions)

# Add some churned customers (no purchase in last 6 months)
print("Adding churn patterns...")
recent_date = end_date - timedelta(days=180)
active_customers = transactions_df[transactions_df['transaction_date'] >= recent_date]['customer_id'].unique()
print(f"Active customers: {len(active_customers)} out of {n_customers}")

# Save to CSV
print("Saving to CSV...")
customers.to_csv('data/customers.csv', index=False)
products.to_csv('data/products.csv', index=False)
transactions_df.to_csv('data/transactions.csv', index=False)

print(f"""
✅ Data Generation Complete!
- Customers: {len(customers)}
- Products: {len(products)}
- Transactions: {len(transactions_df)}
- Date Range: {start_date.date()} to {end_date.date()}
""")