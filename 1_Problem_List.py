# pages/1_📋_Problem_List.py

import streamlit as st
import pandas as pd
import random
import datetime
from database import problems_collection, users_collection, notes_collection

# --- AUTHENTICATION CHECK ---
if not st.session_state.get("authenticated"):
    st.error("Please log in to view this page.")
    st.stop()

# --- HELPER FUNCTIONS ---
def get_difficulty_color(difficulty):
    if difficulty == "Easy": return "#28a745"
    elif difficulty == "Medium": return "#ffc107"
    elif difficulty == "Hard": return "#dc3545"
    else: return "#6c757d"

def render_tag(text, color, text_color="white"):
    return f"<span style='background-color: {color}; color: {text_color}; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 4px 10px; margin-right: 5px;'>{text}</span>"

# --- CACHED DATABASE FUNCTIONS for PERFORMANCE ---
@st.cache_data(ttl=300) # Cache for 5 minutes
def get_problems(query={}):
    """Fetches and sorts problems from MongoDB."""
    return list(problems_collection.find(query).sort("name", 1))

@st.cache_data(ttl=300)
def get_distinct_values(field):
    """Gets distinct values for a field for filter options."""
    return problems_collection.distinct(field)

# --- PAGE LAYOUT ---
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
    company_list = ["All"] + sorted(get_distinct_values("company"))
    difficulty_list = ["All"] + sorted(get_distinct_values("difficulty"))
    topic_list = sorted(get_distinct_values("topics"))

    filter_cols = st.columns(4)
    selected_company = filter_cols[0].selectbox("**Company**", options=company_list)
    selected_difficulty = filter_cols[1].selectbox("**Difficulty**", options=difficulty_list)
    selected_topics = filter_cols[2].multiselect("**Topics (Intersection)**", options=topic_list)
    
    query = {}
    if selected_company != "All": query["company"] = selected_company
    if selected_difficulty != "All": query["difficulty"] = selected_difficulty
    if selected_topics: query["topics"] = {"$all": selected_topics}
    
    problem_list = get_problems(query) # Use the cached function

    with filter_cols[3]:
        st.write(""); st.write("")
        if st.button("🎲 Random", use_container_width=True, disabled=not problem_list):
            # FIX: Call random.choice() only once
            picked_problem = random.choice(problem_list)
            st.info(f"**Random Pick:** [{picked_problem['name']}]({picked_problem.get('link', '#')})")
    
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
                    update_doc = {
                        "$set": {
                            f"progress.{problem_id_str}.solved": not solved_status,
                            f"progress.{problem_id_str}.solved_at": datetime.datetime.now(datetime.timezone.utc) if not solved_status else None
                        }
                    }
                    users_collection.update_one({"username": st.session_state.username}, update_doc, upsert=True)
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