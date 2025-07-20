# database.py

import streamlit as st
import pymongo
import socket

# @st.cache_resource
def init_connection():
    """Initializes and returns a reusable connection to MongoDB."""
    try:
        connection_string = "mongodb+srv://adiprakash1962001:08NtMEDr3JegxFcH@cluster0.mxx9w0f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = pymongo.MongoClient(connection_string)
        return client
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        st.stop()

def get_db_collections():
    """Returns all necessary database collections."""
    try:
        client = init_connection()
        db = client.get_database("codetrack_db")
        problems_collection = db.problems
        users_collection = db.users
        notes_collection = db.notes
        return problems_collection, users_collection, notes_collection
    except Exception as e:
        st.error(f"Failed to get database collections: {e}")
        st.stop()

def check_internet_connection():
    """Checks for an active internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

# Initialize collections for use in other modules
problems_collection, users_collection, notes_collection = get_db_collections()