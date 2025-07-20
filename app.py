# app.py

import streamlit as st
from Home import home
from database import users_collection, check_internet_connection
from utility import hash_password, verify_password

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# --- AUTHENTICATION FUNCTIONS ---
def create_user(username, password):
    """Creates a new user in the database."""
    if not check_internet_connection():
        st.error("No internet connection. Please try again.")
        return False
    if users_collection.find_one({"username": username}):
        st.warning("Username already exists!")
        return False
    else:
        hashed_password = hash_password(password)
        users_data = {"username": username, "password": hashed_password}
        users_collection.insert_one(users_data)
        return True

def check_credentials(username, password) -> bool:
    """Checks user credentials against the database."""
    if not check_internet_connection():
        st.error("No internet connection. Please try again.")
        return False
    user = users_collection.find_one({"username": username})
    if user and verify_password(user["password"], password):
        return True
    return False

# --- MAIN APP LAYOUT ---
try:
    st.set_page_config(page_title="Code Tracker", layout="wide")
except Exception as e:
    st.error(f"Error setting page config: {str(e)}")

st.write("<h1 style='text-align: center;'>Code Tracker</h1>", unsafe_allow_html=True)

# --- LOGIN/SIGNUP INTERFACE ---
if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username").lower()
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True, type="primary"):
                    if not username or ' ' in username or not password:
                        st.error("Username and password cannot be empty or contain spaces.")
                    elif check_credentials(username, password):
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
        
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("New Username").lower()
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if not new_username or ' ' in new_username or not new_password:
                        st.error("Username and password cannot be empty or contain spaces.")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match!")
                    elif create_user(new_username, new_password):
                        st.success("Account created successfully! Please sign in.")
                    # The create_user function already handles the "user exists" warning.

# --- AUTHENTICATED USER INTERFACE ---
else:
    col1, col2, col3 = st.columns([1, 8, 1])
    with col3:
        if st.button("Logout", key="logout"):
            # Clear all session state keys
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    # Call the main home function which contains the navigation
    home()