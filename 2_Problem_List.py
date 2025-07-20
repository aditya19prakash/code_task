import streamlit as st
from utils.db_connector import get_db_collections
import datetime
import random

def problem_list_dashboard():
    # --- Authentication Check ---
    if not st.session_state.get("logged_in"):
         st.switch_page("pages/1_Login.py")

    st.set_page_config(page_title="Problem List", page_icon="📋", layout="wide")
    st.title("📋 Problem List Dashboard")
    st.sidebar.write(f"Logged in as: **{st.session_state.get('username')}**")

    problems, users, notes = get_db_collections()

    if "editing_note_for" not in st.session_state:
        st.session_state.editing_note_for = None

    def get_difficulty_color(difficulty):
        if difficulty == "Easy": return "#28a745"
        elif difficulty == "Medium": return "#ffc107"
        elif difficulty == "Hard": return "#dc3545"
        else: return "#6c757d"

    def render_tag(text, color, text_color="white"):
        return f"<span style='background-color: {color}; color: {text_color}; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 4px 10px; margin-right: 5px;'>{text}</span>"

    # --- In-Page Note Editor ---
    if st.session_state.editing_note_for:
        problem = st.session_state.editing_note_for
        st.title("📝 Note Editor")
        st.markdown(f"### {problem.get('name', 'Unknown Problem')}")
        st.divider()

        user_note = notes.find_one({"problem_id": problem["_id"], "username": st.session_state.username})
        current_note = user_note.get("note_text", "") if user_note else ""

        new_note = st.text_area("Your personal notes:", value=current_note, height=300, label_visibility="collapsed")

        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("💾 Save Note", use_container_width=True, type="primary"):
                notes.update_one(
                    {"problem_id": problem["_id"], "username": st.session_state.username},
                    {"$set": {"note_text": new_note}},
                    upsert=True
                )
                st.toast("Note saved!")
                st.session_state.editing_note_for = None
                st.rerun()
        with col2:
            if st.button("⬅️ Back to Problem List", use_container_width=True):
                st.session_state.editing_note_for = None
                st.rerun()
    else:
        try:
            st.subheader("Filters")
            company_list = ["All"] + sorted(problems.distinct("company"))
            difficulty_list = ["All"] + sorted(problems.distinct("difficulty"))
            topic_list = sorted(problems.distinct("topics"))

            filter_cols = st.columns(4)
            with filter_cols[0]: selected_company = st.selectbox("**Company**", options=company_list)
            with filter_cols[1]: selected_difficulty = st.selectbox("**Difficulty**", options=difficulty_list)
            with filter_cols[2]: selected_topics = st.multiselect("**Topics (Intersection)**", options=topic_list)

            query = {}
            if selected_company != "All": query["company"] = selected_company
            if selected_difficulty != "All": query["difficulty"] = selected_difficulty
            if selected_topics: query["topics"] = {"$all": selected_topics}

            problem_list = list(problems.find(query).sort("name", 1))

            with filter_cols[3]:
                st.write(""); st.write("")
                if st.button("Pick a Random Question 🎲", use_container_width=True, disabled=not problem_list):
                    if problem_list:
                        picked = random.choice(problem_list)
                        st.info(f"**Random Pick:** [{picked['name']}]({picked.get('link', '#')})")
            st.divider()

            if not problem_list:
                st.info("No problems match your filter criteria.")
            else:
                user_data = users.find_one({"username": st.session_state.username})
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
                            if problem.get("acceptance"):
                                try:
                                    rate = float(problem["acceptance"])
                                    formatted_rate = f"🎯 {rate:.3f}%"
                                except (ValueError, TypeError): formatted_rate = f"🎯 {problem['acceptance']}"
                                tags_html += render_tag(formatted_rate, "#17a2b8")
                            st.markdown(tags_html, unsafe_allow_html=True)
                            st.markdown(f"**Link:** [{problem.get('link', '#')}]({problem.get('link', '#')})")
                        with col2:
                            solved_status = user_progress.get(problem_id_str, {}).get("solved", False)
                            if st.button("✅ Solved" if solved_status else "Mark Solved", key=f"solve_{problem_id_str}", use_container_width=True):
                                users.update_one({"username": st.session_state.username}, {"$set": {f"progress.{problem_id_str}.solved": not solved_status, f"progress.{problem_id_str}.solved_at": datetime.datetime.now(datetime.timezone.utc) if not solved_status else None}}, upsert=True)
                                st.rerun()
                        with col3:
                            revised_status = user_progress.get(problem_id_str, {}).get("revised", False)
                            if st.button("🔄 Revised" if revised_status else "Mark Revised", key=f"revise_{problem_id_str}", use_container_width=True):
                                users.update_one({"username": st.session_state.username}, {"$set": {f"progress.{problem_id_str}.revised": not revised_status}}, upsert=True)
                                st.rerun()
                        with col4:
                            user_note = notes.find_one({"problem_id": problem["_id"], "username": st.session_state.username})
                            note_exists = user_note and user_note.get("note_text")
                            if st.button("📝 View Note" if note_exists else "🗒️ Add Note", key=f"note_{problem_id_str}", use_container_width=True):
                                st.session_state.editing_note_for = problem
                                st.rerun()
                        st.divider()
        except Exception as e:
            st.error(f"An error occurred: {e}")

