import pandas as pd
import numpy as np

# Step 1: Create weekly timeline
weeks = pd.date_range(start='2022-01-01', periods=156, freq='W-SUN')
np.random.seed(42)  # For reproducibility

# Step 2: Base data structure
df = pd.DataFrame({"week": weeks})

# --- Existing KPIs (your original variables) ---
df["app_downloads"] = np.random.randint(8000, 15000, size=156)
df["weekly_transactions"] = np.random.randint(20000, 50000, size=156)
df["revenue_total"] = np.random.uniform(5000000, 12000000, size=156).round(2)
df["repeat_transactions"] = np.random.randint(8000, 20000, size=156)
df["intercity_shipments"] = np.random.randint(2000, 8000, size=156)
df["parcel_deliveries"] = np.random.randint(10000, 30000, size=156)
df["avg_transaction_value"] = np.random.uniform(200, 400, size=156).round(2)

# --- Media Spend and Engagement (existing) ---
df["tv_spend"] = np.random.uniform(5, 25, size=156).round(2)
df["tv_grp"] = (df["tv_spend"] * np.random.uniform(1.5, 3.0, size=156)).round(2)

df["meta_spend"] = np.random.uniform(3, 15, size=156).round(2)
df["meta_impressions"] = (df["meta_spend"] * np.random.uniform(100000, 300000, size=156)).astype(int)

df["youtube_spend"] = np.random.uniform(2, 12, size=156).round(2)
df["youtube_views"] = (df["youtube_spend"] * np.random.uniform(80000, 250000, size=156)).astype(int)

df["google_search_spend"] = np.random.uniform(4, 20, size=156).round(2)
df["google_clicks"] = (df["google_search_spend"] * np.random.uniform(5000, 15000, size=156)).astype(int)

df["affiliate_spend"] = np.random.uniform(1, 10, size=156).round(2)
df["affiliate_clicks"] = (df["affiliate_spend"] * np.random.uniform(2000, 8000, size=156)).astype(int)

df["influencer_spend"] = np.random.uniform(0.5, 5, size=156).round(2)
df["influencer_reach"] = (df["influencer_spend"] * np.random.uniform(10000, 50000, size=156)).astype(int)

df["app_install_campaign_spend"] = np.random.uniform(2, 10, size=156).round(2)
df["app_install_clicks"] = (df["app_install_campaign_spend"] * np.random.uniform(3000, 10000, size=156)).astype(int)

# --- Owned Media / Organic Touchpoints (existing) ---
df["push_notifications_sent"] = np.random.randint(200000, 400000, size=156)
df["email_sent"] = np.random.randint(100000, 300000, size=156)
df["sms_sent"] = np.random.randint(50000, 150000, size=156)
df["website_visits"] = np.random.randint(100000, 500000, size=156)
df["blog_articles_published"] = np.random.randint(0, 5, size=156)
df["social_posts"] = np.random.randint(5, 20, size=156)

# --- Control / Contextual Variables (existing) ---
df["price_discount_index"] = np.random.uniform(5, 20, size=156).round(2)
df["competitor_spend_index"] = np.random.uniform(50, 100, size=156).round(2)
df["fuel_price_index"] = np.random.uniform(90, 120, size=156).round(2)
df["rainfall_index"] = np.random.uniform(0, 100, size=156).round(2)
df["holiday_flag"] = np.random.choice([0, 1], size=156, p=[0.8, 0.2])
df["covid_wave_dummy"] = np.random.choice([0, 1], size=156, p=[0.95, 0.05])
df["city_expansion_count"] = np.random.randint(0, 3, size=156)
df["new_app_version_flag"] = np.random.choice([0, 1], size=156, p=[0.9, 0.1])

# --- NEW Variables for Strategic Questions ---

# 1. Customer Segments & Regions
regions = ['North', 'South', 'East', 'West', 'Central']
customer_types = ['B2B', 'B2C']

df["region"] = np.random.choice(regions, size=156)
df["customer_type"] = np.random.choice(customer_types, size=156)
df["order_count"] = np.random.randint(1000, 5000, size=156)
df["profit_margin"] = np.random.uniform(5, 20, size=156).round(2)  # in %
df["repeat_purchase_flag"] = np.random.choice([0, 1], size=156, p=[0.6, 0.4])

# 2. Marketing Campaign Effectiveness
campaign_channels = ['Digital', 'Print', 'Referral', 'Social', 'Affiliate']
df["campaign_id"] = np.random.randint(1000, 1100, size=156)
df["campaign_channel"] = np.random.choice(campaign_channels, size=156)
df["leads_generated"] = np.random.randint(500, 3000, size=156)
df["conversions"] = np.random.randint(200, 1500, size=156)
df["conversion_rate"] = (df["conversions"] / df["leads_generated"]).round(3)
df["campaign_cost"] = np.random.uniform(10000, 100000, size=156).round(2)
df["roi"] = ((df["conversions"] * df["avg_transaction_value"]) - df["campaign_cost"]) / df["campaign_cost"]
df["customer_acquisition_cost"] = (df["campaign_cost"] / df["conversions"]).round(2)

# 3. Delivery Performance by Region
delivery_statuses = ['On-Time', 'Delayed', 'Failed']
delay_reasons = ['Traffic', 'Weather', 'Operational', 'Other']

df["delivery_status"] = np.random.choice(delivery_statuses, size=156, p=[0.75, 0.20, 0.05])
df["actual_delivery_time_hrs"] = np.random.uniform(12, 72, size=156).round(1)
df["estimated_delivery_time_hrs"] = df["actual_delivery_time_hrs"] - np.random.uniform(-5, 5, size=156).round(1)
df["delay_reason"] = np.where(df["delivery_status"] == 'Delayed', np.random.choice(delay_reasons, size=156), None)
df["courier_partner"] = np.random.choice(['Partner_A', 'Partner_B', 'Partner_C'], size=156)

# 4. Competitive Performance
competitors = ['Competitor_X', 'Competitor_Y', 'Competitor_Z']
df["competitor_name"] = np.random.choice(competitors, size=156)
df["market_share_estimate"] = np.random.uniform(10, 50, size=156).round(2)  # %
df["pricing_index"] = np.random.uniform(80, 120, size=156).round(2)
df["customer_churn_rate"] = np.random.uniform(0, 0.1, size=156).round(3)
df["customer_feedback_score"] = np.random.uniform(3, 5, size=156).round(2)  # out of 5

# 5. Customer Complaints & Service Issues
complaint_types = ['Delay', 'Lost Parcel', 'Damaged Goods', 'Other']
df["complaint_id"] = np.random.randint(20000, 21000, size=156)
df["complaint_type"] = np.random.choice(complaint_types, size=156, p=[0.5, 0.2, 0.2, 0.1])
df["resolution_time_hrs"] = np.random.uniform(1, 48, size=156).round(1)
df["customer_satisfaction_score"] = np.random.uniform(1, 5, size=156).round(2)

# 6. Brand Visibility & Engagement
media_channels = ['Social Media', 'News', 'Blogs', 'Forums']
df["media_channel"] = np.random.choice(media_channels, size=156)
df["mentions_count"] = np.random.randint(100, 1000, size=156)
df["sentiment_score"] = np.random.uniform(-1, 1, size=156).round(2)  # -1 negative, +1 positive
df["engagement_rate"] = np.random.uniform(0.01, 0.2, size=156).round(3)

# 7. Infrastructure & Regulatory Impact
incident_types = ['Connectivity', 'Regulatory', 'Compliance', 'Other']
df["incident_id"] = np.random.randint(30000, 30100, size=156)
df["incident_type"] = np.random.choice(incident_types, size=156)
df["impact_duration_hrs"] = np.random.uniform(0, 24, size=156).round(1)
df["shipment_affected_count"] = np.random.randint(0, 500, size=156)

# --- NEW: Additional Executive Dashboard Columns ---

delivery_modes = ['Standard', 'Express', 'Same-day', 'Pickup']
package_weight_classes = ['Light', 'Medium', 'Heavy', 'Oversized']
service_channels = ['App', 'Website', 'Call Center', 'Partner API']
account_types = ['Individual', 'Corporate', 'Government', 'SME']
customer_tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']

df["delivery_mode"] = np.random.choice(delivery_modes, size=len(df))
df["package_weight_class"] = np.random.choice(package_weight_classes, size=len(df))
df["service_channel"] = np.random.choice(service_channels, size=len(df))
df["account_type"] = np.random.choice(account_types, size=len(df))
df["customer_tier"] = np.random.choice(customer_tiers, size=len(df))

# --- Save to CSV ---
df.to_csv("logistics_mmm_extended_data.csv", index=False)
print("✅ Updated data file with executive dashboard columns.")

# --- Save to CSV ---
df.to_csv("logistics_mmm_extended_data.csv", index=False)

print("✅ Extended CSV file 'logistics_mmm_extended_data.csv' created with 156 weeks of data.")

# Optional: Display first few rows
print(df.head())
