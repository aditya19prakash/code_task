# pages/4_⚙️_Upload_Data.py

import streamlit as st
import pandas as pd
from database import problems_collection

# --- AUTHENTICATION CHECK ---
if not st.session_state.get("authenticated"):
    st.error("Please log in to view this page.")
    st.stop()

# --- PAGE LAYOUT ---
st.title("⚙️ Upload Company Problem List")
company_name = st.text_input("**Enter Company Name**")
uploaded_csv = st.file_uploader("**Upload Problem List CSV**", type=["csv"])

if uploaded_csv:
    try:
        df = pd.read_csv(uploaded_csv)
        st.markdown("### Map Your CSV Columns")
        csv_columns = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        problem_col = col1.selectbox("Problem Name Column", csv_columns)
        link_col = col2.selectbox("Problem Link Column", [None] + csv_columns)
        difficulty_col = col1.selectbox("Difficulty Column", [None] + csv_columns)
        acceptance_col = col2.selectbox("Acceptance Rate Column", [None] + csv_columns)
        topic_col = col1.selectbox("Topic(s) Column (comma-separated)", [None] + csv_columns)
        
        if st.button("Sync to Database", type="primary"):
            if not company_name:
                st.warning("Please enter a company name.")
            else:
                with st.spinner("Processing... This may take a moment."):
                    for index, row in df.iterrows():
                        topics_list = []
                        if topic_col and pd.notna(row[topic_col]):
                            topics_list = [topic.strip() for topic in str(row[topic_col]).split(',')]
                        
                        # More robust parsing for acceptance rate
                        acceptance_value = "N/A"
                        if acceptance_col and pd.notna(row[acceptance_col]):
                            try:
                                acceptance_str = str(row[acceptance_col]).replace('%', '').strip()
                                acceptance_value = float(acceptance_str)
                            except (ValueError, TypeError):
                                acceptance_value = "N/A" # Keep as N/A if conversion fails

                        problem_doc = {
                            "name": row[problem_col],
                            "link": row[link_col] if link_col and pd.notna(row[link_col]) else "#",
                            "company": company_name.strip(),
                            "difficulty": row[difficulty_col] if difficulty_col and pd.notna(row[difficulty_col]) else "N/A",
                            "acceptance": acceptance_value,
                            "topics": topics_list,
                        }
                        # Use update_one with upsert=True to add new or update existing problems by name
                        problems_collection.update_one(
                            {"name": row[problem_col]}, 
                            {"$set": problem_doc}, 
                            upsert=True
                        )
                st.success("Sync complete!")
    except Exception as e:
        st.error(f"An error occurred: {e}")