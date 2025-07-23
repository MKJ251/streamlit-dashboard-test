import streamlit as st
import plotly.express as px

def show_delivery_tab(filtered_df, palettes, show_kpi_cards_with_yoy=None):
    QUALITATIVE_DARK, QUALITATIVE_BOLD, _ = palettes

    st.header("🚚 Delivery & Service Performance")
    if show_kpi_cards_with_yoy:
        show_kpi_cards_with_yoy(filtered_df, palettes)
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Delivery Status Distribution")
        status_counts = filtered_df["delivery_status"].value_counts().reset_index(name='count')
        status_counts.columns = ['delivery_status', 'count']
        if not status_counts.empty:
            fig = px.pie(
                status_counts,
                names="delivery_status",
                values="count",
                color_discrete_sequence=QUALITATIVE_BOLD
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(status_counts, use_container_width=True)
        else:
            st.info("No delivery status data for current filters.")

    with col2:
        st.subheader("Delay Reasons")
        delay_df = filtered_df[filtered_df["delivery_status"] == "Delayed"]
        delay_counts = delay_df["delay_reason"].value_counts().reset_index(name='count')
        delay_counts.columns = ['delay_reason', 'count']
        if not delay_counts.empty:
            fig = px.bar(
                delay_counts,
                x="delay_reason",
                y="count",
                color_discrete_sequence=QUALITATIVE_DARK
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(delay_counts, use_container_width=True)
        else:
            st.info("No delayed shipments for current filters.")

    st.subheader("Customer Satisfaction Trend")
    if not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x="week",
            y="customer_satisfaction_score",
            color="region",
            color_discrete_sequence=QUALITATIVE_BOLD
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No satisfaction data for current filters.")
