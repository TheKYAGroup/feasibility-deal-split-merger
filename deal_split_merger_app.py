import streamlit as st
import pandas as pd

st.set_page_config(page_title="Feasibility + Deal Splits Merger", layout="centered")
st.title("🧩 Merge Feasibility Report with HubSpot Deal Splits")

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

        # Normalize column names
        feasibility_df.columns = feasibility_df.columns.str.strip().str.lower()
        hubspot_df.columns = hubspot_df.columns.str.strip().str.lower()

        # Display for debugging
        st.write("Feasibility Columns:", list(feasibility_df.columns))
        st.write("HubSpot Columns:", list(hubspot_df.columns))

        # Normalize keys
        feasibility_df['project id'] = feasibility_df['project id'].astype(str).str.strip()
        hubspot_df['intacct project id'] = hubspot_df['intacct project id'].astype(str).str.strip()

        # Filter relevant columns from HubSpot
        hubspot_trimmed = hubspot_df[[
            'intacct project id', 'deal split amount', 'deal split percentage', 'deal split owner']]

        # Merge
        merged_df = pd.merge(
            feasibility_df,
            hubspot_trimmed,
            how='left',
            left_on='project id',
            right_on='intacct project id'
        )

        merged_df.drop(columns=['intacct project id'], inplace=True)

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
