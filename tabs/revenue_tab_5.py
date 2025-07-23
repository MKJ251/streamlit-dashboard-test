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

def generate_auto_insights(filtered_df, corr_df_dict):
    lines = []
    if filtered_df.empty:
        lines = ["No data available for current filters."]
    else:
        # Top region and customer type
        top_region = (
            filtered_df.groupby('region')['revenue_total']
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )
        top_region_amount = filtered_df.groupby('region')['revenue_total'].sum().max()
        top_custtype = (
            filtered_df.groupby('customer_type')['revenue_total']
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )
        top_custtype_amt = filtered_df.groupby('customer_type')['revenue_total'].sum().max()
        lines.append(f"- **Highest Revenue Region:** {top_region} ({top_region_amount:,.0f})")
        lines.append(f"- **Segment Leader:** {top_custtype} customers drove the most revenue ({top_custtype_amt:,.0f})")
        # Correlation takeaways:
        if corr_df_dict:
            takeaway_lines = []
            for seg, corr_df in corr_df_dict.items():
                # highest association (absolute value), but show positive/negative separately
                max_corr = corr_df.abs().max().max()
                where = corr_df.abs() == max_corr
                reg = corr_df.index[where.any(axis=1)][0]
                seg_val = corr_df.columns[where.loc[where.any(axis=1)].any()]
                real_corr = corr_df.loc[reg, seg_val]
                sign = "positive" if real_corr > 0 else "negative"
                takeaway_lines.append(f"- **Strongest {seg.title()}-Region Association:** {reg} & {seg_val} ({sign} correlation: {real_corr:.2f})")
            lines.append("**Correlation Insights:**")
            lines += takeaway_lines
    return "\n".join(lines)

def correlation_heatmap_by_segment(filtered_df, primary="region"):
    """Returns dict of (segment, corr_df) for each segment, and shows heatmaps."""
    segments = [
        ("customer_type", "Customer Type"),
        ("delivery_mode", "Delivery Mode"),
        ("package_weight_class", "Package Weight Class"),
        ("service_channel", "Service Channel"),
        ("account_type", "Account Type"),
        ("customer_tier", "Customer Tier"),
    ]
    corr_df_dict = {}
    st.markdown("### Correlation of Revenue Between Region and Key Segments")
    for seg, seg_label in segments:
        # Pivot table: rows are regions, columns are segment categories; values are revenue sums over time
        try:
            pivot = filtered_df.pivot_table(
                index=primary, columns=seg, values="revenue_total", aggfunc="sum", fill_value=0
            )
            if pivot.shape[1] > 1 and pivot.shape[0] > 1:
                corr_df = pivot.corr().transpose() if pivot.shape[0] < pivot.shape[1] else pivot.corr()
                corr_df_dict[seg] = corr_df
                fig = px.imshow(
                    corr_df,
                    text_auto=".2f",
                    color_continuous_scale="RdBu",
                    title=f"Correlation Heatmap: Region vs {seg_label}",
                    aspect="auto"
                )
                fig.update_layout(margin=dict(l=40, r=40, t=60, b=40))
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            continue
    return corr_df_dict

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
    corr_df_dict = {}  # updated below after chart, injected for insights
    auto_insight_box = st.expander("📌 Auto Insights", expanded=True)
    # content for auto insights is added after heatmap so we capture correlation insights

    st.markdown("### Executive Summary")
    show_kpi_cards_with_yoy(filtered_df, palettes)
    st.write("")

    st.markdown("**Revenue Trend by Region**")
    rev_trend_region = filtered_df.groupby(['week', 'region'])['revenue_total'].sum().reset_index()
    fig_trend_region = px.line(
        rev_trend_region, x='week', y='revenue_total', color='region',
        color_discrete_sequence=MUTED_SEQUENTIAL,
        labels={"week": "Week", "revenue_total": "Revenue"}
    )
    fig_trend_region.update_layout(template="plotly_white")
    st.plotly_chart(fig_trend_region, use_container_width=True)

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

    st.markdown("**Weekly Customer Acquisition Cost**")
    cac_trend = filtered_df.groupby('week')['customer_acquisition_cost'].mean().reset_index()
    fig_cac = px.line(
        cac_trend, x='week', y='customer_acquisition_cost',
        color_discrete_sequence=MUTED_SEQUENTIAL, labels={"customer_acquisition_cost": "Avg Acquisition Cost"}
    )
    fig_cac.update_layout(template="plotly_white")
    st.plotly_chart(fig_cac, use_container_width=True)

    st.markdown("**Weekly Customer Churn Rate**")
    churn_trend = filtered_df.groupby('week')['customer_churn_rate'].mean().reset_index()
    fig_churn = px.line(
        churn_trend, x='week', y='customer_churn_rate',
        color_discrete_sequence=MUTED_SEQUENTIAL, labels={"customer_churn_rate": "Avg Churn Rate"}
    )
    fig_churn.update_layout(template="plotly_white")
    st.plotly_chart(fig_churn, use_container_width=True)

    # Correlation analysis and charts at the bottom
    corr_df_dict = correlation_heatmap_by_segment(filtered_df)
    
    # Now fill in the Auto Insights expander with final insights, including correlation takeaways
    with auto_insight_box:
        st.markdown(generate_auto_insights(filtered_df, corr_df_dict))
