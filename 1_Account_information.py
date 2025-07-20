def account_info_page():
    st.title("👤 Account Information")
    # (Complete account info logic from previous versions goes here)
    st.header(f"Welcome, {st.session_state.username.capitalize()}!")
    st.divider()
    user_data = users_collection.find_one({"username": st.session_state.username})
    user_progress = user_data.get("progress", {}) if user_data else {}
    
    total_problems = problems_collection.count_documents({})
    solved_count = sum(1 for data in user_progress.values() if data.get("solved"))
    revised_count = sum(1 for data in user_progress.values() if data.get("revised"))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Problems", total_problems)
    col2.metric("Problems Solved", solved_count)
    col3.metric("Problems Revised", revised_count)