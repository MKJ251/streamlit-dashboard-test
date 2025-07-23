import streamlit as st
import pandas as pd
import plotly.express as px

# Muted, professional palettes
MUTED_QUALITATIVE = [
    '#5478a6',  # steel blue
    '#8bb6d6',  # light blue
    '#a6c5ae',  # soft moss
    '#f6c28b',  # muted gold
    '#dbb2ff',  # lavender
    '#4173a6',  # deeper blue
    '#e8d19e'   # sand
]

MUTED_SEQUENTIAL = [
    '#08306b',
    '#08519c',
    '#2171b5',
    '#4292c6',
    '#6baed6',
    '#9ecae1',
    '#c6dbef'
]

def show_kpi_cards_with_yoy(filtered_df, palettes=None):
    current_year = filtered_df['week'].dt.year.max()
    previous_year = current_year - 1

    curr_year_df = filtered_df[filtered_df['week'].dt.year == current_year]
    prev_year_df = filtered_df[filtered_df['week'].dt.year == previous_year]

    curr_vals = curr_year_df.agg({
        'revenue_total': 'sum',
        'profit': 'sum',
        'repeat_purchase_flag': 'mean',
        'roas': 'mean'
    })

    prev_vals = prev_year_df.agg({
        'revenue_total': 'sum',
        'profit': 'sum',
        'repeat_purchase_flag': 'mean',
        'roas': 'mean'
    })

    kpi_yoy = ((curr_vals - prev_vals) / prev_vals) * 100

    total_revenue = curr_vals['revenue_total'] / 1_000_000
    total_profit = curr_vals['profit'] / 1_000_000
    repeat_rate = curr_vals['repeat_purchase_flag'] * 100
    roas_avg = curr_vals['roas']

    def arrow(val):
        if val is None or (isinstance(val, float) and (val != val)):
            return ""
        elif val > 0:
            return f' <span style="color:#1AA83B;font-size:15px;">&#9650; {val:.1f}%</span>'
        elif val < 0:
            return f' <span style="color:#E02424;font-size:15px;">&#9660; {abs(val):.1f}%</span>'
        else:
            return ' <span style="color:#888888;font-size:15px;">0.0%</span>'

    st.markdown(
        """
        <style>
        .kpi-card {
            background: linear-gradient(135deg, #eef2f5 30%, #d8e2ed 100%);
            border-radius: 12px;
            padding: 18px 15px;
            box-shadow: 0 2px 8px rgba(19,43,70,0.07);
            text-align:center;
            font-weight:600;
            color:#26334d;
            font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
            user-select:none;
        }
        .kpi-value { font-size: 30px; margin-top: 5px; color: #205184; }
        .kpi-label { font-size: 15px; color: #556080; }
        .kpi-delta { font-size: 15px; font-weight: 500; margin-top: 2px; }
        .download-btn-container {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class='kpi-card'>💰<div class='kpi-value'>{total_revenue:.2f} Mn</div>
                <div class='kpi-label'>Total Revenue</div>
                <div class='kpi-delta'>{arrow(kpi_yoy['revenue_total'])}</div></div>""",
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"""<div class='kpi-card'>📈<div class='kpi-value'>{total_profit:.2f} Mn</div>
                <div class='kpi-label'>Total Profit</div>
                <div class='kpi-delta'>{arrow(kpi_yoy['profit'])}</div></div>""",
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            f"""<div class='kpi-card'>♻️<div class='kpi-value'>{repeat_rate:.1f}%</div>
                <div class='kpi-label'>Repeat Rate</div>
                <div class='kpi-delta'>{arrow(kpi_yoy['repeat_purchase_flag'])}</div></div>""",
            unsafe_allow_html=True)
    with col4:
        st.markdown(
            f"""<div class='kpi-card'>🎯<div class='kpi-value'>{roas_avg:.2f}</div>
                <div class='kpi-label'>ROAS Avg</div>
                <div class='kpi-delta'>{arrow(kpi_yoy['roas'])}</div></div>""",
            unsafe_allow_html=True)

def generate_auto_insights(filtered_df):
    # Example: most revenue by region
    if filtered_df.empty:
        insight_lines = ["No data available for current filters."]
    else:
        top_region = (
            filtered_df.groupby('region')['revenue_total']
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )
        top_region_amount = filtered_df.groupby('region')['revenue_total'].sum().max()

        # Top customer type
        top_custtype = (
            filtered_df.groupby('customer_type')['revenue_total']
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )
        top_custtype_amt = filtered_df.groupby('customer_type')['revenue_total'].sum().max()
        
        # Fastest growing region (by week over week)
        regions = filtered_df['region'].unique()
        growth = {}
        for region in regions:
            region_df = filtered_df[filtered_df['region'] == region].sort_values('week')
            week_sum = region_df.groupby('week')['revenue_total'].sum()
            if len(week_sum) > 1:
                pct_growth = (week_sum.iloc[-1] - week_sum.iloc[0]) / week_sum.iloc[0] * 100
                growth[region] = pct_growth
        fastest_growing_region = max(growth, key=growth.get) if growth else None
        fastest_growth_value = growth[fastest_growing_region] if growth else 0

        # Highest ROAS by delivery mode
        deliv_group = filtered_df.groupby('delivery_mode')['roas'].mean()
        if not deliv_group.empty:
            top_roas_mode = deliv_group.idxmax()
            top_roas_val = deliv_group.max()
        else:
            top_roas_mode = top_roas_val = None

        insight_lines = [
            f"- **Highest Revenue Region:** {top_region} ({top_region_amount:,.0f})",
            f"- **Segment Leader:** {top_custtype} customers drove the most revenue ({top_custtype_amt:,.0f})",
        ]
        if growth:
            insight_lines.append(f"- **Fastest Growing Market:** {fastest_growing_region} ({fastest_growth_value:.1f}% growth)")
        if top_roas_mode is not None:
            insight_lines.append(f"- **Best ROAS Delivery Mode:** {top_roas_mode} (Avg ROAS: {top_roas_val:.2f})")
        else:
            insight_lines.append("- No ROAS data available.")

    return "\n".join(insight_lines)

def show_revenue_tab(filtered_df, palettes=None, show_kpi_cards_with_yoy_func=None):
    # Prepare CSV for download
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')

    # Right-aligned Download CSV button at top of tab content
    st.markdown(
        """
        <div class="download-btn-container">
        """, unsafe_allow_html=True
    )
    st.download_button(
        label="📄 Download Filtered Data (CSV)",
        data=csv_data,
        file_name="logistics_revenue_filtered_data.csv",
        mime="text/csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Auto Insights Section ---
    with st.expander("📌 Auto Insights", expanded=True):
        st.markdown(generate_auto_insights(filtered_df))

    st.markdown("### Executive Summary")
    show_kpi_cards_with_yoy(filtered_df, palettes)
    st.write("")

    # Revenue Trend by Region (full width)
    st.markdown("**Revenue Trend by Region**")
    rev_trend_region = filtered_df.groupby(['week', 'region'])['revenue_total'].sum().reset_index()
    fig_trend_region = px.line(
        rev_trend_region, x='week', y='revenue_total', color='region',
        color_discrete_sequence=MUTED_SEQUENTIAL,
        labels={"week": "Week", "revenue_total": "Revenue"}
    )
    fig_trend_region.update_layout(template="plotly_white")
    st.plotly_chart(fig_trend_region, use_container_width=True)

    # Revenue by Region and Customer Type (pie) side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Revenue by Region**")
        rev_by_region = filtered_df.groupby('region')['revenue_total'].sum().reset_index()
        fig_region = px.bar(
            rev_by_region, x='region', y='revenue_total', color='region',
            color_discrete_sequence=MUTED_QUALITATIVE,
            labels={"region": "Region", "revenue_total": "Total Revenue"}
        )
        fig_region.update_layout(template="plotly_white")
        st.plotly_chart(fig_region, use_container_width=True)
    with col2:
        st.markdown("**Revenue by Customer Type (B2B vs B2C)**")
        rev_by_custtype = filtered_df.groupby('customer_type')['revenue_total'].sum().reset_index()
        fig_custtype_pie = px.pie(
            rev_by_custtype,
            names='customer_type',
            values='revenue_total',
            hole=0,
            color_discrete_sequence=MUTED_QUALITATIVE
        )
        fig_custtype_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_custtype_pie, use_container_width=True)

    # Revenue by Delivery Mode and Package Weight Class side by side
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Revenue by Delivery Mode**")
        rev_by_mode = filtered_df.groupby('delivery_mode')['revenue_total'].sum().reset_index()
        fig_mode = px.bar(
            rev_by_mode, x='delivery_mode', y='revenue_total', color='delivery_mode',
            color_discrete_sequence=MUTED_QUALITATIVE,
            labels={"delivery_mode": "Delivery Mode", "revenue_total": "Revenue"}
        )
        fig_mode.update_layout(template="plotly_white")
        st.plotly_chart(fig_mode, use_container_width=True)
    with col4:
        st.markdown("**Revenue by Package Weight Class**")
        rev_by_pkg = filtered_df.groupby('package_weight_class')['revenue_total'].sum().reset_index()
        fig_pkg = px.bar(
            rev_by_pkg, x='package_weight_class', y='revenue_total', color='package_weight_class',
            color_discrete_sequence=MUTED_QUALITATIVE,
            labels={"package_weight_class": "Weight Class", "revenue_total": "Revenue"}
        )
        fig_pkg.update_layout(template="plotly_white")
        st.plotly_chart(fig_pkg, use_container_width=True)

    # Revenue by Service Channel, Account Type, Customer Tier - donuts side by side
    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown("**Revenue by Service Channel**")
        pie_service = filtered_df.groupby('service_channel')['revenue_total'].sum().reset_index()
        fig_service = px.pie(
            pie_service, names='service_channel', values='revenue_total',
            hole=0.4,
            color_discrete_sequence=MUTED_QUALITATIVE
        )
        fig_service.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_service, use_container_width=True)
    with col6:
        st.markdown("**Revenue by Account Type**")
        pie_account = filtered_df.groupby('account_type')['revenue_total'].sum().reset_index()
        fig_account = px.pie(
            pie_account, names='account_type', values='revenue_total',
            hole=0.4,
            color_discrete_sequence=MUTED_QUALITATIVE
        )
        fig_account.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_account, use_container_width=True)
    with col7:
        st.markdown("**Revenue by Customer Tier**")
        pie_tier = filtered_df.groupby('customer_tier')['revenue_total'].sum().reset_index()
        fig_tier = px.pie(
            pie_tier, names='customer_tier', values='revenue_total',
            hole=0.4,
            color_discrete_sequence=MUTED_QUALITATIVE
        )
        fig_tier.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_tier, use_container_width=True)

    st.markdown("---")
    st.subheader("Customer Metrics Trends (Weekly)")

    # Weekly Customer Acquisition Cost
    st.markdown("**Weekly Customer Acquisition Cost**")
    cac_trend = filtered_df.groupby('week')['customer_acquisition_cost'].mean().reset_index()
    fig_cac = px.line(
        cac_trend, x='week', y='customer_acquisition_cost',
        color_discrete_sequence=MUTED_SEQUENTIAL, labels={"customer_acquisition_cost": "Avg Acquisition Cost"}
    )
    fig_cac.update_layout(template="plotly_white")
    st.plotly_chart(fig_cac, use_container_width=True)

    # Weekly Customer Churn Rate
    st.markdown("**Weekly Customer Churn Rate**")
    churn_trend = filtered_df.groupby('week')['customer_churn_rate'].mean().reset_index()
    fig_churn = px.line(
        churn_trend, x='week', y='customer_churn_rate',
        color_discrete_sequence=MUTED_SEQUENTIAL, labels={"customer_churn_rate": "Avg Churn Rate"}
    )
    fig_churn.update_layout(template="plotly_white")
    st.plotly_chart(fig_churn, use_container_width=True)
