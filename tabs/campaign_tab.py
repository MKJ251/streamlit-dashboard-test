import streamlit as st
import plotly.express as px

def show_campaign_tab(filtered_df, palettes, show_kpi_cards_with_yoy=None):
    QUALITATIVE_DARK, QUALITATIVE_BOLD, _ = palettes

    st.header("🎯 Campaign Performance Overview")
    if show_kpi_cards_with_yoy:
        show_kpi_cards_with_yoy(filtered_df, palettes)
    st.write("")

    tab1, tab2 = st.tabs(["📊 Channel Summary", "📈 ROAS vs CAC"])

    with tab1:
        st.subheader("Lead-to-Conversion by Channel")
        conv_df = filtered_df.groupby("campaign_channel")[
            ["leads_generated", "conversions", "campaign_cost", "cpc", "roas", "customer_acquisition_cost"]
        ].mean(numeric_only=True).reset_index()
        st.dataframe(conv_df.round(2), use_container_width=True)

    with tab2:
        if not filtered_df.empty:
            fig = px.scatter(
                conv_df,
                x="customer_acquisition_cost",
                y="roas",
                color="campaign_channel",
                size="conversions",
                hover_name="campaign_channel",
                color_discrete_sequence=QUALITATIVE_BOLD,
                title="ROAS vs Customer Acquisition Cost"
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No campaign data for current filters.")

    st.subheader("Campaign Spend vs App Downloads")
    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="campaign_cost",
            y="app_downloads",
            color="campaign_channel",
            size="conversions",
            color_discrete_sequence=QUALITATIVE_DARK,
            title="Campaign Spend vs App Downloads"
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No campaign performance data for current filters.")
