# pages/2_🗓️_Coding_History.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
from database import users_collection

# --- AUTHENTICATION CHECK ---
if not st.session_state.get("authenticated"):
    st.error("Please log in to view this page.")
    st.stop()

# --- CACHED DATA FUNCTION ---
@st.cache_data(ttl=60) # Cache user data for 1 minute
def get_user_progress(username):
    user_data = users_collection.find_one({"username": username})
    return user_data.get("progress", {}) if user_data else {}

# --- PAGE LAYOUT ---
st.title("🗓️ Your Coding History")

user_progress = get_user_progress(st.session_state.username)
solve_dates = [data["solved_at"] for data in user_progress.values() if data.get("solved") and data.get("solved_at")]

if not solve_dates:
    st.info("You haven't solved any problems yet. Go solve some to see your history!")
else:
    df = pd.DataFrame(solve_dates, columns=["solved_at"])
    df['date'] = pd.to_datetime(df['solved_at']).dt.date
    activity = df.groupby('date').size().reset_index(name='count').set_index('date')
    
    # Create a full date range for the last year for the heatmap
    all_days = pd.date_range(end=datetime.date.today(), periods=365, freq='D').to_series().dt.date
    activity = activity.reindex(all_days, fill_value=0)
    
    data = pd.DataFrame({'date': activity.index, 'count': activity['count']})
    data['day_of_week'] = data['date'].dt.dayofweek
    data['week_of_year'] = data['date'].dt.isocalendar().week
    # Handle edge case for weeks at the start of the year
    data.loc[(data['date'].dt.month == 1) & (data['week_of_year'] > 50), 'week_of_year'] = 0
    
    fig = go.Figure(data=go.Heatmap(
        z=data['count'], 
        x=data['week_of_year'], 
        y=data['day_of_week'], 
        colorscale='Greens', 
        showscale=False,
        hoverongaps=False,
        text=data.apply(lambda row: f"{row['date'].strftime('%b %d, %Y')}<br>{int(row['count'])} solved", axis=1),
        hoverinfo='text'
    ))
    fig.update_layout(
        title_text='Problems Solved in the Last Year', 
        height=300,
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        )
    )
    st.plotly_chart(fig, use_container_width=True)