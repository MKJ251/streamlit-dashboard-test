col1, col2, col3 = st.columns(3)
with col1:
    region = st.selectbox('Region', df['region'].unique())
with col2:
    customer = st.selectbox('Customer Type', df['customer_type'].unique())
with col3:
    date_range = st.date_input('Date Range', ...)
