# problem_list_page.py

import streamlit as st
import datetime
import random
from database import problems_collection, users_collection, notes_collection

def get_difficulty_color(difficulty):
    """Returns a color based on difficulty, case-insensitively."""
    difficulty_title = difficulty.title() if isinstance(difficulty, str) else ""
    if difficulty_title == "Easy": return "#28a745"
    elif difficulty_title == "Medium": return "#ffc107"
    elif difficulty_title == "Hard": return "#dc3545"
    else: return "#6c757d"

def render_tag(text, color, text_color="white"):
    """Renders a styled HTML tag."""
    return f"<span style='background-color: {color}; color: {text_color}; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 4px 10px; margin-right: 5px;'>{text}</span>"

def problem_list_page():
    st.title("📋 Problem List Dashboard")

    # --- Note Editor View ---
    if st.session_state.get("editing_note_for"):
        problem = st.session_state.editing_note_for
        st.subheader(f"📝 Note Editor for: {problem.get('name', 'Unknown Problem')}")
        
        user_note = notes_collection.find_one({"problem_id": problem["_id"], "username": st.session_state.username})
        current_note = user_note.get("note_text", "") if user_note else ""
        new_note = st.text_area("Your personal notes:", value=current_note, height=300, label_visibility="collapsed")

        col1, col2 = st.columns([0.2, 0.8])
        if col1.button("💾 Save Note", use_container_width=True, type="primary"):
            notes_collection.update_one(
                {"problem_id": problem["_id"], "username": st.session_state.username},
                {"$set": {"note_text": new_note}},
                upsert=True
            )
            st.toast("Note saved!")
            st.session_state.editing_note_for = None
            st.rerun()
        if col2.button("⬅️ Back to List", use_container_width=True):
            st.session_state.editing_note_for = None
            st.rerun()
        return

    # --- Main Problem List View ---
    st.subheader("Filters")

    # --- Filter Setup ---
    # CORRECTED: Simplified and correct way to get unique company tags.
    company_list = ["All"] + sorted(problems_collection.distinct("company_tag"))
    difficulty_list = ["All"] + sorted(problems_collection.distinct("difficulty"))
    topic_list = sorted(problems_collection.distinct("topics"))

    filter_cols = st.columns(4)
    selected_company = filter_cols[0].selectbox("**Company**", options=company_list)
    selected_difficulty = filter_cols[1].selectbox("**Difficulty**", options=difficulty_list)
    selected_topics = filter_cols[2].multiselect("**Topics (Intersection)**", options=topic_list)

    # --- Database Query ---
    query = {}
    if selected_company != "All": query["company_tag"] = selected_company
    if selected_difficulty != "All": query["difficulty"] = selected_difficulty
    if selected_topics: query["topics"] = {"$all": selected_topics}
    
    problem_list = list(problems_collection.find(query).sort("name", 1))

    with filter_cols[3]:
        st.write("")
        st.write("")
        if st.button("🎲 Random", use_container_width=True, disabled=not problem_list):
            if problem_list:
                pick = random.choice(problem_list)
                st.info(f"**Random Pick:** [{pick.get('name', 'Unnamed Problem')}]({pick.get('link', '#')})")

    st.divider()

    # --- Pagination ---
    problems_per_page = 25
    total_problems = len(problem_list)
    total_pages = max((total_problems - 1) // problems_per_page + 1, 1)

    if "problem_list_page_number" not in st.session_state or st.session_state.problem_list_page_number > total_pages:
        st.session_state.problem_list_page_number = 1
    
    col_page = st.columns([1, 4])[0]
    page_num = col_page.number_input(
        "Page", min_value=1, max_value=total_pages, key="problem_list_page_number", step=1, format="%d"
    )

    start_idx = (page_num - 1) * problems_per_page
    end_idx = start_idx + problems_per_page
    problems_to_display = problem_list[start_idx:end_idx]

    # --- Display Problems ---
    user_data = users_collection.find_one({"username": st.session_state.username})
    user_progress = user_data.get("progress", {}) if user_data else {}

    for problem in problems_to_display:
        problem_id_str = str(problem["_id"])
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 0.17, 0.17, 0.16])
            
            # Column 1: Problem Details and Tags
            with col1:
                st.markdown(f"<div style='font-size: 22px; font-weight: bold;'>{problem.get('name', 'Unnamed Problem')}</div>", unsafe_allow_html=True)
                
                tags_html = ""
                # Company Tags
                for company in problem.get("company_tag", []):
                    tags_html += render_tag(company, "#007bff")
                
                # CORRECTED: Difficulty Tag with proper color and title case display
                difficulty = problem.get("difficulty")
                if difficulty:
                    tags_html += render_tag(difficulty.title(), get_difficulty_color(difficulty))
                
                # Topic Tags
                for topic in problem.get("topics", []):
                    tags_html += render_tag(topic, "#6c757d")
                
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write(f"**Link:** [{problem.get('link', '#')}]({problem.get('link', '#')})")

            # Column 2: Solve Button and Date
            with col2:
                problem_progress = user_progress.get(problem_id_str, {})
                solved = problem_progress.get("solved", False)

                if st.button("✅ Solved" if solved else "Solve", key=f"solve_{problem_id_str}", use_container_width=True):
                    users_collection.update_one(
                        {"username": st.session_state.username},
                        {"$set": {
                            f"progress.{problem_id_str}.solved": not solved,
                            f"progress.{problem_id_str}.solved_at": datetime.datetime.now(datetime.timezone.utc) if not solved else None
                        }},
                        upsert=True
                    )
                    st.rerun()

                if solved:
                    solved_at_date = problem_progress.get("solved_at")
                    if isinstance(solved_at_date, datetime.datetime):
                        date_str = solved_at_date.strftime("%Y-%m-%d")
                        st.markdown(f"<p style='font-size:12px; text-align:center; color:#28a745; margin-top: 5px;'>{date_str}</p>", unsafe_allow_html=True)

            # Column 3: Revise Button
            with col3:
                revised = user_progress.get(problem_id_str, {}).get("revised", False)
                if st.button("🔄 Revised" if revised else "Revise", key=f"revise_{problem_id_str}", use_container_width=True):
                    users_collection.update_one(
                        {"username": st.session_state.username},
                        {"$set": {f"progress.{problem_id_str}.revised": not revised}},
                        upsert=True
                    )
                    st.rerun()

            # Column 4: Notes Button
            with col4:
                note = notes_collection.find_one({"problem_id": problem["_id"], "username": st.session_state.username})
                note_exists = note and note.get("note_text")
                if st.button("📝 Notes" if note_exists else "🗒️ Notes", key=f"note_{problem_id_str}", use_container_width=True):
                    st.session_state.editing_note_for = problem
                    st.rerun()

            st.divider()