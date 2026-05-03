# File: python/load_data_to_db.py

import pandas as pd
from sqlalchemy import create_engine

# Database connection
DB_USER = 'postgres'
DB_PASSWORD = '123456'  # Change this
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'commerce'

# Create connection
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

print("Loading data from CSV files...")
customers = pd.read_csv('A:/e commerse/ecommerce-intelligence-system/data/customers.csv')
products = pd.read_csv('A:/e commerse/ecommerce-intelligence-system/data/products.csv')
transactions = pd.read_csv('A:/e commerse/ecommerce-intelligence-system/data/transactions.csv')

from sqlalchemy import text

with engine.begin() as conn:
    print("Clearing existing data...")
    conn.execute(text("TRUNCATE TABLE transactions, customers, products CASCADE;"))

print("Inserting customers...")
customers.to_sql('customers', engine, if_exists='append', index=False)

print("Inserting products...")
products.to_sql('products', engine, if_exists='append', index=False)

print("Inserting transactions...")
transactions.to_sql('transactions', engine, if_exists='append', index=False, chunksize=1000)

print("✅ Data loaded successfully!")

# Verify
print("\nData counts in database:")
print(f"Customers: {pd.read_sql('SELECT COUNT(*) FROM customers', engine).values[0][0]}")
print(f"Products: {pd.read_sql('SELECT COUNT(*) FROM products', engine).values[0][0]}")
print(f"Transactions: {pd.read_sql('SELECT COUNT(*) FROM transactions', engine).values[0][0]}")