# Home.py

import streamlit as st
from problem_list_page import problem_list_page
from coding_history_page import coding_history_page
from account_info_page import account_info_page
from upload_data_page import upload_data_page

def home():
    """The main function that controls page navigation after login."""
    st.sidebar.title("Navigation")

    pages = {
        "Problem List": problem_list_page,
        "Coding History": coding_history_page,
        "Account Information": account_info_page,
        "Upload Data": upload_data_page,
    }

    page_labels = {
        "Problem List": "📋 Problem List",
        "Coding History": "🗓️ Coding History",
        "Account Information": "👤 Account Info",
        "Upload Data": "⚙️ Upload Data"
    }

    page_selection = st.sidebar.selectbox(
        "Select a Page",
        options=list(pages.keys()),
        format_func=lambda x: page_labels[x]
    )

    pages[page_selection]()
