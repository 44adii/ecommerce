# File: python/churn_prediction.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sqlalchemy import create_engine
import joblib

# Database connection
engine = create_engine('postgresql://postgres:123456@localhost:5432/commerce')

# Load data
print("Loading data from database...")
query = """
SELECT 
    t.customer_id,
    COUNT(DISTINCT t.invoice_no) as total_orders,
    SUM(t.total_amount) as total_spent,
    AVG(t.total_amount) as avg_order_value,
    MAX(t.transaction_date) as last_purchase_date,
    MIN(t.transaction_date) as first_purchase_date,
    COUNT(DISTINCT p.category) as unique_categories,
    c.country
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
JOIN products p ON t.product_id = p.product_id
GROUP BY t.customer_id, c.country
"""

df = pd.read_sql(query, engine)

# Feature Engineering
print("Engineering features...")
df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
df['first_purchase_date'] = pd.to_datetime(df['first_purchase_date'])
current_date = df['last_purchase_date'].max()

df['days_since_last_purchase'] = (current_date - df['last_purchase_date']).dt.days
df['customer_lifetime_days'] = (df['last_purchase_date'] - df['first_purchase_date']).dt.days
df['purchase_frequency'] = df['total_orders'] / (df['customer_lifetime_days'] + 1)

# Define churn (no purchase in last 180 days)
df['is_churned'] = (df['days_since_last_purchase'] > 180).astype(int)

print(f"Churned customers: {df['is_churned'].sum()} ({df['is_churned'].mean()*100:.2f}%)")

# Prepare features
features = ['total_orders', 'total_spent', 'avg_order_value', 
            'days_since_last_purchase', 'customer_lifetime_days', 
            'purchase_frequency', 'unique_categories']

# One-hot encode country
df_encoded = pd.get_dummies(df, columns=['country'], prefix='country')
country_cols = [col for col in df_encoded.columns if col.startswith('country_')]
features.extend(country_cols)

X = df_encoded[features]
y = df_encoded['is_churned']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# Train Random Forest
print("\n" + "="*50)
print("Training Random Forest Classifier...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
rf_model.fit(X_train, y_train)

# Predictions
y_pred_rf = rf_model.predict(X_test)
y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]

print("\n📊 Random Forest Results:")
print(classification_report(y_test, y_pred_rf))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba_rf):.4f}")

# Feature Importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🔝 Top 10 Important Features:")
print(feature_importance.head(10))

# Train Logistic Regression
print("\n" + "="*50)
print("Training Logistic Regression...")
lr_model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr_model.fit(X_train, y_train)

y_pred_lr = lr_model.predict(X_test)
y_pred_proba_lr = lr_model.predict_proba(X_test)[:, 1]

print("\n📊 Logistic Regression Results:")
print(classification_report(y_test, y_pred_lr))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba_lr):.4f}")

# Save models
print("\nSaving models...")
joblib.dump(rf_model, 'models/churn_rf_model.pkl')
joblib.dump(lr_model, 'models/churn_lr_model.pkl')
joblib.dump(features, 'models/feature_names.pkl')

# Save predictions
predictions_df = df_encoded[['customer_id']].copy()
predictions_df['churn_probability_rf'] = rf_model.predict_proba(X)[:, 1]
predictions_df['churn_prediction_rf'] = rf_model.predict(X)
predictions_df['actual_churn'] = y

predictions_df.to_csv('outputs/churn_predictions.csv', index=False)

print("\n✅ Models saved successfully!")
print("📁 Predictions saved to outputs/churn_predictions.csv")