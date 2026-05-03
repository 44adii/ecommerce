# File: python/customer_segmentation.py

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://postgres:123456@localhost:5432/commerce')

# Load RFM data
print("Loading RFM data...")
query = """
SELECT 
    customer_id,
    (SELECT DATE(MAX(transaction_date)) FROM transactions) - DATE(MAX(transaction_date)) as recency,
    COUNT(DISTINCT invoice_no) as frequency,
    SUM(total_amount) as monetary
FROM transactions
GROUP BY customer_id
"""

df = pd.read_sql(query, engine)

print(f"Total customers: {len(df)}")

# Prepare features
features = ['recency', 'frequency', 'monetary']
X = df[features]

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Elbow method to find optimal k
print("\nFinding optimal number of clusters...")
inertias = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Plot elbow curve
plt.figure(figsize=(10, 6))
plt.plot(K_range, inertias, 'bo-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method For Optimal k')
plt.grid(True)
plt.savefig('outputs/elbow_curve.png', dpi=300, bbox_inches='tight')
print("📊 Elbow curve saved to outputs/elbow_curve.png")

# Train final model with k=5
optimal_k = 5
print(f"\nTraining K-Means with k={optimal_k}...")
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)

# Analyze clusters
print("\n📊 Cluster Analysis:")
cluster_summary = df.groupby('cluster').agg({
    'recency': ['mean', 'median'],
    'frequency': ['mean', 'median'],
    'monetary': ['mean', 'median'],
    'customer_id': 'count'
}).round(2)

cluster_summary.columns = ['_'.join(col) for col in cluster_summary.columns]
cluster_summary = cluster_summary.rename(columns={'customer_id_count': 'customer_count'})
print(cluster_summary)

# Assign cluster names based on characteristics
def assign_cluster_name(row):
    cluster = row['cluster']
    summary = cluster_summary.loc[cluster]
    
    if summary['recency_mean'] < 60 and summary['monetary_mean'] > df['monetary'].quantile(0.75):
        return 'Champions'
    elif summary['frequency_mean'] > df['frequency'].quantile(0.75):
        return 'Loyal Customers'
    elif summary['recency_mean'] > 180:
        return 'Lost Customers'
    elif summary['monetary_mean'] < df['monetary'].quantile(0.25):
        return 'Low Spenders'
    else:
        return 'Potential Loyalists'

df['cluster_name'] = df.apply(assign_cluster_name, axis=1)

# Visualization with PCA
print("\nCreating cluster visualization...")
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

df['pca1'] = X_pca[:, 0]
df['pca2'] = X_pca[:, 1]

plt.figure(figsize=(12, 8))
scatter = plt.scatter(df['pca1'], df['pca2'], c=df['cluster'], cmap='viridis', alpha=0.6)
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
plt.title('Customer Segmentation (K-Means Clustering)')
plt.colorbar(scatter, label='Cluster')
plt.grid(True, alpha=0.3)
plt.savefig('outputs/customer_clusters.png', dpi=300, bbox_inches='tight')
print("📊 Cluster visualization saved to outputs/customer_clusters.png")

# Save results
df.to_csv('outputs/customer_segments.csv', index=False)
print("\n✅ Segmentation complete!")
print("📁 Results saved to outputs/customer_segments.csv")

# Print segment distribution
print("\n📊 Segment Distribution:")
print(df['cluster_name'].value_counts())