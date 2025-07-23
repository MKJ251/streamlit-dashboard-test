import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image

# --- Compact filter summary with modern style ---
def render_filter_summary(date_range, regions, customer_types, delivery_modes, package_weight_classes, service_channels, account_types, customer_tiers):
    summary_parts = []
    if date_range:
        summary_parts.append(f"Date: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
    if regions:
        summary_parts.append(f"Region: {', '.join(regions)}")
    if customer_types:
        summary_parts.append(f"Customer Type: {', '.join(customer_types)}")
    if delivery_modes:
        summary_parts.append(f"Delivery Mode: {', '.join(delivery_modes)}")
    if package_weight_classes:
        summary_parts.append(f"Weight Class: {', '.join(package_weight_classes)}")
    if service_channels:
        summary_parts.append(f"Service Channel: {', '.join(service_channels)}")
    if account_types:
        summary_parts.append(f"Account Type: {', '.join(account_types)}")
    if customer_tiers:
        summary_parts.append(f"Customer Tier: {', '.join(customer_tiers)}")
    if summary_parts:
        summary_text = " | ".join(summary_parts)
    else:
        summary_text = "No filters applied: showing all data."
    filter_icon = "🧭"
    st.markdown(f"""
        <div style="
            font-size:13px;
            color:#476072;
            background:rgba(230,238,245,0.6);
            border-left: 4px solid #8bb6d6;
            border-radius:6px;
            padding:7px 14px;
            margin-bottom:13px;
            display:flex;
            align-items:center;
            max-width:98%;">
            <span style='font-size:15px;margin-right:8px'>{filter_icon}</span>
            <span style='flex:1'><i>{summary_text}</i></span>
        </div>
        """, unsafe_allow_html=True)

def simple_login():
    credentials = {"admin": "aliceadmin123", "bob": "bob456"}
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in credentials and password == credentials[username]:
                st.session_state["authenticated"] = True
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        st.stop()

simple_login()

# --- Main_app.py content starts here ---
from tabs.revenue_tab import show_revenue_tab, show_kpi_cards_with_yoy
from tabs.campaign_tab import show_campaign_tab
from tabs.delivery_tab import show_delivery_tab
from tabs.brand_tab import show_brand_tab
from tabs.download_tab import show_download_tab

st.set_page_config(page_title="Logistics Dashboard", layout="wide")

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

# --- Sidebar Branding and Executive Filters ---
logo = Image.open("mindmetric_logo.png")
logo = logo.resize((100, int(logo.height * 100 / logo.width)))
st.sidebar.image(logo)

st.sidebar.markdown(
    "<div style='font-family:Segoe UI;color:#003366;font-weight:600;font-size:16px;margin-top:10px;'>"
    "Turning Logistics Insights into ROI 🚀"
    "</div>", unsafe_allow_html=True
)
st.sidebar.markdown("---")

with st.sidebar.expander("Filter Options", expanded=True):
    date_range = st.date_input(
        "Select Date Range",
        [df['week'].min(), df['week'].max()],
        help="Filter data by date range"
    )
    regions = st.multiselect("Select Region", df['region'].unique(), default=list(df['region'].unique()))
    customer_types = st.multiselect("Select Customer Type", df['customer_type'].unique(), default=list(df['customer_type'].unique()))
    delivery_modes = st.multiselect("Select Delivery Mode", df['delivery_mode'].unique(), default=list(df['delivery_mode'].unique()))
    package_weight_classes = st.multiselect("Select Package Weight Class", df['package_weight_class'].unique(), default=list(df['package_weight_class'].unique()))
    service_channels = st.multiselect("Select Service Channel", df['service_channel'].unique(), default=list(df['service_channel'].unique()))
    account_types = st.multiselect("Select Account Type", df['account_type'].unique(), default=list(df['account_type'].unique()))
    customer_tiers = st.multiselect("Select Customer Tier", df['customer_tier'].unique(), default=list(df['customer_tier'].unique()))

# --- Filter Data ---
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])
filtered_df = df[
    (df['week'] >= start_date) &
    (df['week'] <= end_date) &
    (df['region'].isin(regions)) &
    (df['customer_type'].isin(customer_types)) &
    (df['delivery_mode'].isin(delivery_modes)) &
    (df['package_weight_class'].isin(package_weight_classes)) &
    (df['service_channel'].isin(service_channels)) &
    (df['account_type'].isin(account_types)) &
    (df['customer_tier'].isin(customer_tiers))
]

# --- Color Palettes ---
QUALITATIVE_DARK = px.colors.qualitative.Dark24
QUALITATIVE_BOLD = px.colors.qualitative.Bold
SEQ_VIRIDIS = px.colors.sequential.Viridis
palettes = (QUALITATIVE_DARK, QUALITATIVE_BOLD, SEQ_VIRIDIS)

# --- Show Filter Summary Indicator ---
render_filter_summary(
    date_range=date_range,
    regions=regions,
    customer_types=customer_types,
    delivery_modes=delivery_modes,
    package_weight_classes=package_weight_classes,
    service_channels=service_channels,
    account_types=account_types,
    customer_tiers=customer_tiers
)

tabs = st.tabs([
    "📈 Revenue & Profitability",
    "🎯 Campaign Performance",
    "🚚 Delivery & Service",
    "📣 Brand & Incidents",
    "📤 Download Data"
])

with tabs[0]:
    show_revenue_tab(filtered_df, palettes, show_kpi_cards_with_yoy)

with tabs[1]:
    show_campaign_tab(filtered_df, palettes, show_kpi_cards_with_yoy)

with tabs[2]:
    show_delivery_tab(filtered_df, palettes, show_kpi_cards_with_yoy)

with tabs[3]:
    show_brand_tab(filtered_df, palettes, show_kpi_cards_with_yoy)

with tabs[4]:
    show_download_tab(filtered_df)
