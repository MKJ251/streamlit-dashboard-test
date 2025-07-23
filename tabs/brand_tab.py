import streamlit as st
import plotly.express as px

def show_brand_tab(filtered_df, palettes, show_kpi_cards_with_yoy=None):
    QUALITATIVE_DARK, QUALITATIVE_BOLD, SEQ_VIRIDIS = palettes

    st.header("📣 Brand Visibility & Incidents")
    if show_kpi_cards_with_yoy:
        show_kpi_cards_with_yoy(filtered_df, palettes)
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Mentions & Sentiment by Channel")
        brand_df = filtered_df.groupby("media_channel")[
            ["mentions_count", "sentiment_score", "engagement_rate"]
        ].mean(numeric_only=True).reset_index()
        if not brand_df.empty:
            fig = px.bar(
                brand_df,
                x="media_channel",
                y="mentions_count",
                color="sentiment_score",
                color_continuous_scale=SEQ_VIRIDIS,
                title="Average Mentions per Channel by Sentiment"
            )
            fig.update_layout(template="plotly_white", xaxis_title="Media Channel", yaxis_title="Avg Mentions")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(brand_df, use_container_width=True)
        else:
            st.info("No brand/channel data for selected filters.")

    with col2:
        st.subheader("Shipment Affected by Incident Type")
        inc_df = filtered_df.groupby("incident_type")["shipment_affected_count"].sum().reset_index()
        if not inc_df.empty:
            fig = px.bar(
                inc_df,
                x="incident_type",
                y="shipment_affected_count",
                color="incident_type",
                color_discrete_sequence=QUALITATIVE_DARK,
                title="Shipments Impacted per Incident Type"
            )
            fig.update_layout(template="plotly_white", xaxis_title="Incident Type", yaxis_title="Total Shipments Affected", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(inc_df, use_container_width=True)
        else:
            st.info("No incident data for selected filters.")
