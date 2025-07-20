
def coding_history_page():
    st.title("🗓️ Your Coding History")
    # (Complete coding history logic from previous versions goes here)
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
