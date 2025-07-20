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






def home():
    """The main function that controls page navigation after login."""
    
    # Define the pages available to logged-in users
    pages = {
        "Problem List": problem_list_page,
        "Coding History": coding_history_page,
        "Account Information": account_info_page,
        "Upload Data": upload_data_page,
    }

    # Use st.navigation to create the sidebar menu
    page_selection = st.sidebar.radio("Navigation", list(pages.keys()))
    menu=st.sidebar.selectbox(
        "Navigation",["Problem List","Coding History","Account Information","Upload Data"]
    )
    if menu=="Problem List":
        add_bank_statement()
    elif menu=="Upload Data":
        add_transaction()
    elif menu=="Account Information":
        show_transactions()
    elif menu =="Coding History":
        portfolio()
 
    
    # Call the function corresponding to the selected page
    pages[page_selection]()