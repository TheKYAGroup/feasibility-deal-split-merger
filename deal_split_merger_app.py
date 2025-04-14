import streamlit as st
import pandas as pd

st.set_page_config(page_title="Feasibility + Deal Splits Merger", layout="centered")
st.title("Merge Feasibility Report with HubSpot Deal Splits")

st.write("""
Upload your **Feasibility** report from Sage Intacct and your **HubSpot** Deal Splits report.
This app will match them by **Project ID** and add the deal split information into the feasibility report.
""")

feasibility_file = st.file_uploader("📁 Upload Feasibility Report (Excel)", type=[".xlsx"])
hubspot_file = st.file_uploader("📁 Upload HubSpot Deal Splits Report (Excel)", type=[".xlsx"])

if feasibility_file and hubspot_file:
    with st.spinner("Merging reports..."):
        feasibility_df = pd.read_excel(feasibility_file)
        hubspot_df = pd.read_excel(hubspot_file)

        # Normalize keys
        feasibility_df['Project ID'] = feasibility_df['Project ID'].astype(str).str.strip()
        hubspot_df['Intacct Project ID'] = hubspot_df['Intacct Project ID'].astype(str).str.strip()

        # Filter relevant columns from HubSpot
        hubspot_trimmed = hubspot_df[[
            'Intacct Project ID', 'Deal split amount', 'Deal Split Percentage', 'Deal Split Owner']]

        # Merge
        merged_df = pd.merge(
            feasibility_df,
            hubspot_trimmed,
            how='left',
            left_on='Project ID',
            right_on='Intacct Project ID'
        )

        merged_df.drop(columns=['Intacct Project ID'], inplace=True)

        st.success("✅ Merging complete! Preview below:")
        st.dataframe(merged_df.head(20))

        # Download
        output = pd.ExcelWriter("merged_output.xlsx", engine='xlsxwriter')
        merged_df.to_excel(output, index=False)
        output.close()

        with open("merged_output.xlsx", "rb") as f:
            st.download_button(
                label="📥 Download Merged Report",
                data=f,
                file_name="Feasibility_with_Deal_Splits.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
