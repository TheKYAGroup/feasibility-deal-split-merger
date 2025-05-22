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
    with st.spinner("Reading and processing files..."):
        feasibility_df = pd.read_excel(feasibility_file)
        hubspot_df = pd.read_excel(hubspot_file)

        # Normalize column names
        feasibility_df.columns = feasibility_df.columns.str.strip().str.lower().str.replace('\xa0', ' ', regex=True).str.replace('\n', ' ', regex=True)
        hubspot_df.columns = hubspot_df.columns.str.strip().str.lower().str.replace('\xa0', ' ', regex=True).str.replace('\n', ' ', regex=True)

        st.subheader("Detected Feasibility Columns")
        st.write(feasibility_df.columns.tolist())

        st.subheader("Detected HubSpot Columns")
        st.write(hubspot_df.columns.tolist())

        # Check for required columns
        if 'project id' not in feasibility_df.columns:
            st.error("❌ 'Project ID' column not found in Feasibility file. Please double check the column name.")
        elif 'intacct project id' not in hubspot_df.columns:
            st.error("❌ 'Intacct Project ID' column not found in HubSpot file. Please double check the column name.")
        else:
            feasibility_df['project id'] = feasibility_df['project id'].astype(str).str.strip()
            hubspot_df['intacct project id'] = hubspot_df['intacct project id'].astype(str).str.strip()

            hubspot_trimmed = hubspot_df[[
                'intacct project id', 'deal split amount', 'deal split percentage', 'deal split owner']]

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
