# account_info_page.py

import streamlit as st
from database import users_collection, problems_collection
import requests
from bs4 import BeautifulSoup

def fetch_leetcode_solved(username):
    try:
        url = f"https://leetcode-stats-api.herokuapp.com/{username}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("totalSolved", "N/A")
    except:
        pass
    return "N/A"

def fetch_gfg_solved(username):
    try:
        url = f"https://auth.geeksforgeeks.org/user/{username}/practice/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            count_tag = soup.find("h5", string="Coding Score")
            solved_tag = soup.find("div", class_="score_card_value")
            if solved_tag:
                return solved_tag.text.strip()
    except:
        pass
    return "N/A"

def account_info_page():
    st.title("👤 Account Information")
    st.header(f"Welcome, {st.session_state.username.capitalize()}!")
    st.divider()

    user_data = users_collection.find_one({"username": st.session_state.username}) or {}
    user_progress = user_data.get("progress", {})
    total_problems = problems_collection.count_documents({})
    solved_count = sum(1 for data in user_progress.values() if data.get("solved"))
    revised_count = sum(1 for data in user_progress.values() if data.get("revised"))

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Problems", total_problems)
    col2.metric("Problems Solved", solved_count)
    col3.metric("Problems Revised", revised_count)

    st.divider()

    st.subheader("🌐 External Accounts")

    leetcode = user_data.get("leetcode", "")
    gfg = user_data.get("gfg", "")

    new_leetcode = st.text_input("LeetCode Username", value=leetcode)
    new_gfg = st.text_input("GeeksforGeeks Username", value=gfg)

    if st.button("💾 Save Usernames"):
        users_collection.update_one(
            {"username": st.session_state.username},
            {"$set": {"leetcode": new_leetcode, "gfg": new_gfg}},
            upsert=True
        )
        st.success("Usernames saved!")
        st.rerun()

    if leetcode:
        st.info(f"🔎 Fetching LeetCode stats for `{leetcode}`...")
        lc_solved = fetch_leetcode_solved(leetcode)
        st.metric(label="✅ LeetCode Solved", value=lc_solved)

    if gfg:
        st.info(f"🔎 Fetching GeeksforGeeks stats for `{gfg}`...")
        gfg_solved = fetch_gfg_solved(gfg)
        st.metric(label="✅ GFG Solved (approx.)", value=gfg_solved)
