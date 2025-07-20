# pages/3_👤_Account_Information.py

import streamlit as st
from database import problems_collection, users_collection

# --- AUTHENTICATION CHECK ---
if not st.session_state.get("authenticated"):
    st.error("Please log in to view this page.")
    st.stop()
    
# --- CACHED DATA FUNCTIONS ---
@st.cache_data(ttl=60)
def get_user_progress(username):
    user_data = users_collection.find_one({"username": username})
    return user_data.get("progress", {}) if user_data else {}

@st.cache_data(ttl=600)
def get_total_problem_count():
    return problems_collection.count_documents({})

# --- PAGE LAYOUT ---
st.title("👤 Account Information")
st.header(f"Welcome, {st.session_state.username.capitalize()}!")
st.divider()

user_progress = get_user_progress(st.session_state.username)
total_problems = get_total_problem_count()

solved_count = sum(1 for data in user_progress.values() if data.get("solved"))
revised_count = sum(1 for data in user_progress.values() if data.get("revised"))

col1, col2, col3 = st.columns(3)
col1.metric("Total Problems", total_problems)
col2.metric("Problems Solved", f"{solved_count}")
col3.metric("Problems Revised", revised_count)