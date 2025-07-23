# logistics_dashboard_app.py – Revenue & Profitability Enhanced
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mindmetric Logistics Dashboard", layout="wide")

# --- Load Data ---
df = pd.read_csv("logistics_mmm_extended_data.csv")
df['week'] = pd.to_datetime(df['week'])

# --- Derived Metrics ---
df["profit"] = (df["revenue_total"] * df["profit_margin"] / 100).round(2)
df["revenue_per_order"] = (df["revenue_total"] / df["order_count"]).round(2)
df["profit_per_order"] = (df["profit"] / df["order_count"]).round(2)
df["cpc"] = (df["campaign_cost"] / df["leads_generated"]).round(2)
df["roas"] = ((df["conversions"] * df["avg_transaction_value"]) / df["campaign_cost"]).round(2)
df["conversion_rate"] = (df["conversions"] / df["leads_generated"]).round(3)

# --- Sidebar Filters ---
logo = Image.open("mindmetric_logo.png")
logo = logo.resize((100, int(logo.height * 100 / logo.width)))
st.sidebar.image(logo)
st.sidebar.title("🔍 Filters")

raw_date_range = st.sidebar.date_input("Select Date Range", [df['week'].min().date(), df['week'].max().date()])
start_date = pd.to_datetime(raw_date_range[0])
end_date = pd.to_datetime(raw_date_range[1])
regions = st.sidebar.multiselect("Select Region", df['region'].unique(), default=list(df['region'].unique()))
customer_types = st.sidebar.multiselect("Select Customer Type", df['customer_type'].unique(), default=list(df['customer_type'].unique()))
product_types = st.sidebar.multiselect("Select Product Type", df['product_type'].unique(), default=list(df['product_type'].unique()))
delivery_statuses = st.sidebar.multiselect("Select Delivery Status", df['delivery_status'].unique(), default=list(df['delivery_status'].unique()))
campaign_types = st.sidebar.multiselect("Select Campaign Type", df['campaign_type'].unique(), default=list(df['campaign_type'].unique()))

# --- Filtered Data ---
filtered_df = df[
    (df['week'] >= start_date) &
    (df['week'] <= end_date) &
    (df['region'].isin(regions)) &
    (df['customer_type'].isin(customer_types)) &
    (df['product_type'].isin(product_types)) &
    (df['delivery_status'].isin(delivery_statuses)) &
    (df['campaign_type'].isin(campaign_types))
]

# --- Comparison Data ---
def get_comparison_data(df, start_date, end_date):
    delta = end_date - start_date
    last_year_range = [start_date - timedelta(weeks=52), end_date - timedelta(weeks=52)]
    prev_period_range = [start_date - delta, start_date - timedelta(days=1)]
    df_yoy = df[(df['week'] >= last_year_range[0]) & (df['week'] <= last_year_range[1])]
    df_mom = df[(df['week'] >= prev_period_range[0]) & (df['week'] <= prev_period_range[1])]
    return df_yoy, df_mom

df_yoy, df_mom = get_comparison_data(df, start_date, end_date)

# --- KPI Cards ---
def show_kpi_cards(df, df_yoy, df_mom):
    def sparkline(series):
        fig, ax = plt.subplots(figsize=(2.2, 0.5))
        ax.plot(series[-8:], color='#0052CC')
        ax.axis('off')
        st.pyplot(fig)

    total_revenue = df['revenue_total'].sum()
    total_profit = df['profit'].sum()
    roas_avg = df['roas'].mean()

    rev_yoy = df_yoy['revenue_total'].sum()
    profit_mom = df_mom['profit'].sum()
    roas_mom = df_mom['roas'].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue (Mn)", f"{total_revenue / 1e6:.2f}", 
                  delta=f"YoY: {(total_revenue-rev_yoy)/rev_yoy*100:.1f}%" if rev_yoy else "N/A")
        sparkline(df['revenue_total'])
    with col2:
        st.metric("Total Profit (Mn)", f"{total_profit / 1e6:.2f}", 
                  delta=f"MoM: {(total_profit-profit_mom)/profit_mom*100:.1f}%" if profit_mom else "N/A")
        sparkline(df['profit'])
    with col3:
        st.metric("ROAS Avg", f"{roas_avg:.2f}", 
                  delta=f"MoM: {(roas_avg-roas_mom)/roas_mom*100:.1f}%" if roas_mom else "N/A")
        sparkline(df['roas'])

# --- Tabs ---
tabs = st.tabs(["📈 Revenue & Profitability", "🎯 Campaign Performance", "🚚 Delivery & Service", "📣 Brand & Incidents"])

# --- Revenue Tab ---
with tabs[0]:
    show_kpi_cards(filtered_df, df_yoy, df_mom)

    st.subheader("Revenue Trends by Region")
    fig = px.line(filtered_df, x="week", y="revenue_total", color="region")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profit Trends by Customer Type")
    fig = px.line(filtered_df, x="week", y="profit", color="customer_type")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Revenue & Profit by Product Type")
    grouped = filtered_df.groupby("product_type")[["revenue_total", "profit"]].sum().reset_index()
    fig = px.bar(grouped, x="product_type", y=["revenue_total", "profit"], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profit by Delivery Status")
    grouped = filtered_df.groupby("delivery_status")["profit"].sum().reset_index()
    fig = px.bar(grouped, x="delivery_status", y="profit")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Repeat Rate by Region")
    grouped = filtered_df.groupby("region")["repeat_purchase_flag"].mean().reset_index()
    fig = px.bar(grouped, x="region", y="repeat_purchase_flag")
    st.plotly_chart(fig, use_container_width=True)
