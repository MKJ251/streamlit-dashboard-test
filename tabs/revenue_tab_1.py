# ------ tabs/revenue_tab.py ------

import streamlit as st
import plotly.express as px

def show_kpi_cards_with_yoy(filtered_df, palettes):
    QUALITATIVE_DARK, QUALITATIVE_BOLD, _ = palettes
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
        .kpi-card{background:linear-gradient(135deg,#d0e6f7,#a3c4f3);border-radius:12px;padding:20px 15px;box-shadow:0 4px 15px rgba(19,43,70,0.2);text-align:center;font-weight:700;color:#003366;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;user-select:none;}.kpi-value{font-size:30px;margin-top:5px;color:#001f4d;}.kpi-label{font-size:16px;color:#004080;}.kpi-delta{font-size:15px;font-weight:500;margin-top:2px;}
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

def show_revenue_tab(filtered_df, palettes, show_kpi_cards_with_yoy):
    QUALITATIVE_DARK, QUALITATIVE_BOLD, _ = palettes
    st.markdown("### Executive Summary")
    show_kpi_cards_with_yoy(filtered_df, palettes)
    st.write("")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Revenue by Region**")
        rev_by_region = filtered_df.groupby('region')['revenue_total'].sum().reset_index()
        fig_region = px.bar(
            rev_by_region, x='region', y='revenue_total', color='region',
            color_discrete_sequence=QUALITATIVE_DARK, title=None
        )
        fig_region.update_layout(template="plotly_white", xaxis_title="Region", yaxis_title="Total Revenue")
        st.plotly_chart(fig_region, use_container_width=True)
    with col2:
        st.markdown("**Revenue by Customer Type (B2B vs B2C)**")
        rev_by_custtype = filtered_df.groupby('customer_type')['revenue_total'].sum().reset_index()
        fig_custtype = px.bar(
            rev_by_custtype, x='customer_type', y='revenue_total', color='customer_type',
            color_discrete_sequence=QUALITATIVE_BOLD, title=None
        )
        fig_custtype.update_layout(template="plotly_white", xaxis_title="Customer Type", yaxis_title="Total Revenue")
        st.plotly_chart(fig_custtype, use_container_width=True)

    st.markdown("**Revenue Trend by Region**")
    rev_trend_region = filtered_df.groupby(['week', 'region'])['revenue_total'].sum().reset_index()
    fig_trend_region = px.line(
        rev_trend_region, x='week', y='revenue_total', color='region',
        color_discrete_sequence=QUALITATIVE_DARK
    )
    fig_trend_region.update_layout(template="plotly_white", xaxis_title="Week", yaxis_title="Revenue")
    st.plotly_chart(fig_trend_region, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Revenue by Delivery Mode**")
        rev_by_mode = filtered_df.groupby('delivery_mode')['revenue_total'].sum().reset_index()
        fig_mode = px.bar(
            rev_by_mode, x='delivery_mode', y='revenue_total', color='delivery_mode',
            color_discrete_sequence=QUALITATIVE_DARK
        )
        fig_mode.update_layout(template="plotly_white", xaxis_title="Delivery Mode", yaxis_title="Revenue")
        st.plotly_chart(fig_mode, use_container_width=True)
    with col4:
        st.markdown("**Revenue by Package Weight Class**")
        rev_by_pkg = filtered_df.groupby('package_weight_class')['revenue_total'].sum().reset_index()
        fig_pkg = px.bar(
            rev_by_pkg, x='package_weight_class', y='revenue_total', color='package_weight_class',
            color_discrete_sequence=QUALITATIVE_BOLD
        )
        fig_pkg.update_layout(template="plotly_white", xaxis_title="Weight Class", yaxis_title="Revenue")
        st.plotly_chart(fig_pkg, use_container_width=True)

    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown("**Revenue by Service Channel**")
        pie_service = filtered_df.groupby('service_channel')['revenue_total'].sum().reset_index()
        fig_service = px.pie(
            pie_service, names='service_channel', values='revenue_total',
            color_discrete_sequence=QUALITATIVE_DARK
        )
        fig_service.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_service, use_container_width=True)
    with col6:
        st.markdown("**Revenue by Account Type**")
        pie_account = filtered_df.groupby('account_type')['revenue_total'].sum().reset_index()
        fig_account = px.pie(
            pie_account, names='account_type', values='revenue_total',
            color_discrete_sequence=QUALITATIVE_BOLD
        )
        fig_account.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_account, use_container_width=True)
    with col7:
        st.markdown("**Revenue by Customer Tier**")
        pie_tier = filtered_df.groupby('customer_tier')['revenue_total'].sum().reset_index()
        fig_tier = px.pie(
            pie_tier, names='customer_tier', values='revenue_total',
            color_discrete_sequence=QUALITATIVE_DARK
        )
        fig_tier.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_tier, use_container_width=True)

    st.markdown("---")
    st.subheader("Customer Metrics Trends (Weekly)")
    st.markdown("**Weekly Customer Acquisition Cost**")
    cac_trend = filtered_df.groupby('week')['customer_acquisition_cost'].mean().reset_index()
    fig_cac = px.line(
        cac_trend, x='week', y='customer_acquisition_cost',
        color_discrete_sequence=QUALITATIVE_DARK, labels={"customer_acquisition_cost": "Avg Acquisition Cost"}
    )
    fig_cac.update_layout(template="plotly_white", xaxis_title="Week", yaxis_title="Acquisition Cost")
    st.plotly_chart(fig_cac, use_container_width=True)

    st.markdown("**Weekly Customer Churn Rate**")
    churn_trend = filtered_df.groupby('week')['customer_churn_rate'].mean().reset_index()
    fig_churn = px.line(
        churn_trend, x='week', y='customer_churn_rate',
        color_discrete_sequence=QUALITATIVE_BOLD, labels={"customer_churn_rate": "Avg Churn Rate"}
    )
    fig_churn.update_layout(template="plotly_white", xaxis_title="Week", yaxis_title="Churn Rate")
    st.plotly_chart(fig_churn, use_container_width=True)
