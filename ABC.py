import pandas as pd
import streamlit as st

st.title("ABC Analysis Generator")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, delimiter=';')

    with st.form("abc_form"):
        weight_pick = st.slider("Weight of the pick values: ", min_value=0.1, max_value=10.0, value=1.0)
        weight_inbound = st.slider("Weight of the inbound values: ", min_value=0.1, max_value=10.0, value=1.0)
        weight_replen = st.slider("Weight of the pick replenishment: ", min_value=0.1, max_value=10.0, value=1.0)
        
        col1, col2 = st.columns(2)
        with col1:
            A = st.slider("Percentage of A items: ", min_value=1, max_value=100, value=20)
        with col2:
            B = st.slider("Percentage of B items: ", min_value=1, max_value=100, value=30)
        
        submit_button = st.form_submit_button("Generate new ABC")

    if submit_button:
        def abc_analysis(group):
            total_items = len(group)
            a_count = int(total_items * (A / 100))
            b_count = int(total_items * (B / 100))
            c_count = total_items - a_count - b_count

            group = group.sort_values(by='ABC_VALUE', ascending=False).reset_index(drop=True)
            group['ABC_CATEGORY'] = ['A'] * a_count + ['B'] * b_count + ['C'] * c_count

            return group

        data['ABC_VALUE'] = round((data['APPROACHES_PICKING'] * weight_pick) + 
                                  (data['APPROACHES_PUTAWAY'] * weight_inbound) + 
                                  (data['APPROACHES_REPLEN'] * weight_replen), 0)

        abc_rank = data.groupby(['STANDARD_SL', 'SKU'])['ABC_VALUE'].sum().reset_index()

        result = abc_rank.groupby('STANDARD_SL').apply(abc_analysis).reset_index(drop=True)

        final_result = result[['STANDARD_SL', 'SKU', 'ABC_CATEGORY']]

        st.table(final_result.head(10))


        final_result.to_excel('ABC_Categories.xlsx', index=False)

        st.download_button(
            label="Download ABC Categories Excel",
            data=open('ABC_Categories.xlsx', 'rb').read(),
            file_name='ABC_Categories.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
