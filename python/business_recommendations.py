# File: python/business_recommendations.py

import pandas as pd
import json

# Load all analysis results
rfm = pd.read_csv('outputs/powerbi_rfm.csv')
churn = pd.read_csv('outputs/powerbi_churn.csv')
segments = pd.read_csv('outputs/powerbi_segments.csv')
clv = pd.read_csv('outputs/powerbi_clv.csv')

# Merge all data
analysis = rfm.merge(churn[['customer_id', 'churn_probability_rf']], on='customer_id')
analysis = analysis.merge(segments[['customer_id', 'cluster_name']], on='customer_id')
analysis = analysis.merge(clv[['customer_id', 'estimated_clv']], on='customer_id')

recommendations = []

# 1. High-Value At-Risk Customers
at_risk_high_value = analysis[
    (analysis['customer_segment'].isin(['At Risk', 'Champions'])) &
    (analysis['churn_probability_rf'] > 0.5) &
    (analysis['estimated_clv'] > analysis['estimated_clv'].quantile(0.75))
]

if len(at_risk_high_value) > 0:
    recommendations.append({
        'priority': 'HIGH',
        'segment': 'At-Risk High-Value Customers',
        'count': len(at_risk_high_value),
        'action': 'Immediate Retention Campaign',
        'tactics': [
            'Send personalized win-back email with 20% discount',
            'Assign account manager for white-glove service',
            'Offer exclusive early access to new products',
            'Schedule 1-on-1 feedback call'
        ],
        'expected_impact': f'Potential revenue at risk: ${at_risk_high_value["estimated_clv"].sum():,.2f}'
    })

# 2. Potential Loyalists - Upsell Opportunity
potential_loyalists = analysis[analysis['customer_segment'] == 'Potential Loyalists']

if len(potential_loyalists) > 0:
    recommendations.append({
        'priority': 'MEDIUM',
        'segment': 'Potential Loyalists',
        'count': len(potential_loyalists),
        'action': 'Upsell & Cross-sell Campaign',
        'tactics': [
            'Send product recommendations based on purchase history',
            'Offer bundle deals (Buy 2 Get 1 Free)',
            'Launch loyalty program with points system',
            'Create educational content about premium products'
        ],
        'expected_impact': f'Potential CLV uplift: ${(potential_loyalists["estimated_clv"].sum() * 0.3):,.2f}'
    })

# 3. Lost Customers - Win-back
lost_customers = analysis[analysis['customer_segment'] == 'Lost']

if len(lost_customers) > 0:
    recommendations.append({
        'priority': 'LOW',
        'segment': 'Lost Customers',
        'count': len(lost_customers),
        'action': 'Win-back Campaign',
        'tactics': [
            'Send "We miss you" email with aggressive discount (30-40%)',
            'Survey to understand why they left',
            'Highlight product improvements since last purchase',
            'Limited-time exclusive offer'
        ],
        'expected_impact': f'If 10% return, revenue: ${(lost_customers["monetary"].sum() * 0.1):,.2f}'
    })

# 4. Champions - Advocate Program
champions = analysis[analysis['customer_segment'] == 'Champions']

if len(champions) > 0:
    recommendations.append({
        'priority': 'MEDIUM',
        'segment': 'Champions',
        'count': len(champions),
        'action': 'Brand Advocacy Program',
        'tactics': [
            'Launch referral program (refer 3, get $50 credit)',
            'Create VIP tier with exclusive benefits',
            'Invite to beta testing new products',
            'Feature in customer success stories'
        ],
        'expected_impact': f'Referral potential: {len(champions) * 3} new customers'
    })

# Generate report
report = {
    'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total_customers_analyzed': len(analysis),
    'summary': {
        'high_priority_actions': len([r for r in recommendations if r['priority'] == 'HIGH']),
        'medium_priority_actions': len([r for r in recommendations if r['priority'] == 'MEDIUM']),
        'low_priority_actions': len([r for r in recommendations if r['priority'] == 'LOW'])
    },
    'recommendations': recommendations
}

# Save as JSON
with open('outputs/business_recommendations.json', 'w') as f:
    json.dump(report, f, indent=2)

# Create readable report
with open('outputs/business_recommendations.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("BUSINESS RECOMMENDATIONS REPORT\n")
    f.write("="*80 + "\n\n")
    f.write(f"Generated: {report['generated_at']}\n")
    f.write(f"Total Customers Analyzed: {report['total_customers_analyzed']:,}\n\n")
    
    for i, rec in enumerate(recommendations, 1):
        f.write(f"\n{'='*80}\n")
        f.write(f"RECOMMENDATION #{i} - {rec['priority']} PRIORITY\n")
        f.write(f"{'='*80}\n")
        f.write(f"Segment: {rec['segment']}\n")
        f.write(f"Customer Count: {rec['count']:,}\n")
        f.write(f"Action: {rec['action']}\n\n")
        f.write("Recommended Tactics:\n")
        for j, tactic in enumerate(rec['tactics'], 1):
            f.write(f"  {j}. {tactic}\n")
        f.write(f"\nExpected Impact: {rec['expected_impact']}\n")

print("✅ Business recommendations generated!")
print("📁 Saved to outputs/business_recommendations.json")
print("📁 Saved to outputs/business_recommendations.txt")