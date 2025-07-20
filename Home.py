# Home.py

import streamlit as st
from database import problems_collection, users_collection, notes_collection
import pandas as pd
import plotly.graph_objects as go
import datetime
import random
from io import StringIO

# --- HELPER FUNCTIONS FOR STYLING ---
def get_difficulty_color(difficulty):
    if difficulty == "Easy": return "#28a745"
    elif difficulty == "Medium": return "#ffc107"
    elif difficulty == "Hard": return "#dc3545"
    else: return "#6c757d"

def render_tag(text, color, text_color="white"):
    return f"<span style='background-color: {color}; color: {text_color}; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 4px 10px; margin-right: 5px;'>{text}</span>"

# =====================================================================================
# PAGE DEFINITIONS
# =====================================================================================

def problem_list_page():
    st.title("📋 Problem List Dashboard")

    if "editing_note_for" not in st.session_state:
        st.session_state.editing_note_for = None
    
    if st.session_state.editing_note_for:
        problem = st.session_state.editing_note_for
        st.subheader(f"📝 Note Editor for: {problem.get('name', 'Unknown Problem')}")
        user_note = notes_collection.find_one({"problem_id": problem["_id"], "username": st.session_state.username})
        current_note = user_note.get("note_text", "") if user_note else ""
        new_note = st.text_area("Your personal notes:", value=current_note, height=300, label_visibility="collapsed")
        
        col1, col2 = st.columns([0.2, 0.8])
        if col1.button("💾 Save Note", use_container_width=True, type="primary"):
            notes_collection.update_one({"problem_id": problem["_id"], "username": st.session_state.username}, {"$set": {"note_text": new_note}}, upsert=True)
            st.toast("Note saved!")
            st.session_state.editing_note_for = None
            st.rerun()
        if col2.button("⬅️ Back to List", use_container_width=True):
            st.session_state.editing_note_for = None
            st.rerun()
    else:
        st.subheader("Filters")
        company_list = ["All"] + sorted(problems_collection.distinct("company"))
        difficulty_list = ["All"] + sorted(problems_collection.distinct("difficulty"))
        topic_list = sorted(problems_collection.distinct("topics"))

        filter_cols = st.columns(4)
        selected_company = filter_cols[0].selectbox("**Company**", options=company_list)
        selected_difficulty = filter_cols[1].selectbox("**Difficulty**", options=difficulty_list)
        selected_topics = filter_cols[2].multiselect("**Topics (Intersection)**", options=topic_list)
        
        query = {}
        if selected_company != "All": query["company"] = selected_company
        if selected_difficulty != "All": query["difficulty"] = selected_difficulty
        if selected_topics: query["topics"] = {"$all": selected_topics}
        
        problem_list = list(problems_collection.find(query).sort("name", 1))

        with filter_cols[3]:
            st.write(""); st.write("")
            if st.button("🎲 Random", use_container_width=True, disabled=not problem_list):
                if problem_list: st.info(f"**Random Pick:** [{random.choice(problem_list)['name']}]({random.choice(problem_list).get('link', '#')})")
        
        st.divider()

        user_data = users_collection.find_one({"username": st.session_state.username})
        user_progress = user_data.get("progress", {}) if user_data else {}
        for problem in problem_list:
            problem_id_str = str(problem["_id"])
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 0.17, 0.17, 0.16])
                with col1:
                    st.markdown(f"### {problem['name']}")
                    tags_html = ""
                    if problem.get("company"): tags_html += render_tag(problem["company"], "#007bff")
                    if problem.get("difficulty"): tags_html += render_tag(problem["difficulty"], get_difficulty_color(problem["difficulty"]))
                    if "topics" in problem:
                        for topic in problem["topics"]: tags_html += render_tag(topic, "#6c757d")
                    st.markdown(tags_html, unsafe_allow_html=True)
                    st.markdown(f"**Link:** [{problem.get('link', '#')}]({problem.get('link', '#')})")

                with col2:
                    solved_status = user_progress.get(problem_id_str, {}).get("solved", False)
                    if st.button("✅ Solved" if solved_status else "Solve", key=f"solve_{problem_id_str}", use_container_width=True):
                        users_collection.update_one({"username": st.session_state.username}, {"$set": {f"progress.{problem_id_str}.solved": not solved_status, f"progress.{problem_id_str}.solved_at": datetime.datetime.now(datetime.timezone.utc) if not solved_status else None}}, upsert=True)
                        st.rerun()
                with col3:
                    revised_status = user_progress.get(problem_id_str, {}).get("revised", False)
                    if st.button("🔄 Revised" if revised_status else "Revise", key=f"revise_{problem_id_str}", use_container_width=True):
                        users_collection.update_one({"username": st.session_state.username}, {"$set": {f"progress.{problem_id_str}.revised": not revised_status}}, upsert=True)
                        st.rerun()
                with col4:
                    user_note = notes_collection.find_one({"problem_id": problem["_id"], "username": st.session_state.username})
                    note_exists = user_note and user_note.get("note_text")
                    if st.button("📝 Notes" if note_exists else "🗒️ Notes", key=f"note_{problem_id_str}", use_container_width=True):
                        st.session_state.editing_note_for = problem
                        st.rerun()
                st.divider()

def coding_history_page():
    st.title("🗓️ Your Coding History")
    user_data = users_collection.find_one({"username": st.session_state.username})
    user_progress = user_data.get("progress", {}) if user_data else {}
    solve_dates = [data["solved_at"] for data in user_progress.values() if data.get("solved") and data.get("solved_at")]
    
    if not solve_dates:
        st.info("No solved problems with dates found.")
    else:
        df = pd.DataFrame(solve_dates, columns=["solved_at"])
        df['date'] = pd.to_datetime(df['solved_at']).dt.date
        activity = df.groupby('date').size().reset_index(name='count').set_index('date')
        
        all_days = pd.date_range(end=datetime.date.today(), periods=365, freq='D')
        activity = activity.reindex(all_days, fill_value=0)
        
        data = pd.DataFrame({'date': activity.index, 'count': activity['count']})
        data['day_of_week'] = data['date'].dt.dayofweek
        data['week_of_year'] = data['date'].dt.isocalendar().week
        data.loc[(data['date'].dt.month == 1) & (data['week_of_year'] > 50), 'week_of_year'] = 0
        
        fig = go.Figure(data=go.Heatmap(z=data['count'], x=data['week_of_year'], y=data['day_of_week'], colorscale='Greens', showscale=False))
        fig.update_layout(title_text='Problems Solved in the Last Year', height=300)
        st.plotly_chart(fig, use_container_width=True)

def account_info_page():
    st.title("👤 Account Information")
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

def upload_data_page():
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
            topic_col = col1.selectbox("Topic(s) Column", [None] + csv_columns)
            
            if st.button("Sync to Database", type="primary"):
                with st.spinner("Processing..."):
                    for index, row in df.iterrows():
                        topics_list = []
                        if topic_col and pd.notna(row[topic_col]):
                            topics_list = [topic.strip() for topic in str(row[topic_col]).split(',')]
                        
                        acceptance_value = "N/A"
                        if acceptance_col and pd.notna(row[acceptance_col]):
                            try:
                                acceptance_value = float(str(row[acceptance_col]).replace('%',''))
                            except:
                                acceptance_value = "N/A"

                        problem_doc = {
                            "name": row[problem_col],
                            "link": row[link_col] if link_col and pd.notna(row[link_col]) else "#",
                            "company": company_name.strip(),
                            "difficulty": row[difficulty_col] if difficulty_col and pd.notna(row[difficulty_col]) else "N/A",
                            "acceptance": acceptance_value,
                            "topics": topics_list,
                        }
                        problems_collection.update_one({"name": row[problem_col]}, {"$set": problem_doc}, upsert=True)
                st.success("Sync complete!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def home():
    """The main function that controls page navigation after login."""
    st.sidebar.title("Navigation")
    
    # Use st.sidebar.radio for the navigation menu
    page_selection = st.sidebar.radio(
        "Go to",
        ["Problem List", "Coding History", "Account Information", "Upload Data"]
    )
    
    # Define the pages
    pages = {
        "Problem List": problem_list_page,
        "Coding History": coding_history_page,
        "Account Information": account_info_page,
        "Upload Data": upload_data_page,
    }
    
    # Call the function corresponding to the selected page
    pages[page_selection]()