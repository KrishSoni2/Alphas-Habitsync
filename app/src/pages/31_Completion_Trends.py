# Matvey Rolett (Data Analyst)
# Completion rates and trends - User Stories 4.1, 4.2

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Completion Trends')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Completion Trends")
st.write("Analyze habit completion rates by category and over time.")

# Completion Rates by Category
st.subheader("Completion Rates by Category")

try:
    response = requests.get(f"{API_BASE}/analytics/completion-rates")
    rates = response.json()

    if len(rates) > 0:
        df = pd.DataFrame(rates)
        st.bar_chart(df.set_index('category_name')['completion_count'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No completion data available.")

except Exception as e:
    st.error(f"Could not load completion rates: {e}")

st.write("---")

# Streak Statistics
st.subheader("Streak Statistics")

try:
    response = requests.get(f"{API_BASE}/analytics/streaks")
    stats = response.json()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_current = stats.get('avg_current_streak', 0)
        if avg_current is not None:
            st.metric("Avg Current Streak", f"{float(avg_current):.1f} days")
        else:
            st.metric("Avg Current Streak", "N/A")
    with col2:
        avg_longest = stats.get('avg_longest_streak', 0)
        if avg_longest is not None:
            st.metric("Avg Longest Streak", f"{float(avg_longest):.1f} days")
        else:
            st.metric("Avg Longest Streak", "N/A")
    with col3:
        st.metric("Max Streak", f"{stats.get('max_streak', 0)} days")
    with col4:
        st.metric("Total Streaks", stats.get('total_streaks', 0))

except Exception as e:
    st.error(f"Could not load streak stats: {e}")

st.write("---")

# Daily Completion Trend
st.subheader("Daily Completion Trend")

try:
    response = requests.get(f"{API_BASE}/analytics/daily-completions")
    daily = response.json()

    if len(daily) > 0:
        df = pd.DataFrame(daily)
        df['log_date'] = pd.to_datetime(df['log_date'])
        st.line_chart(df.set_index('log_date')['total_completions'])
    else:
        st.info("No daily completion data available.")

except Exception as e:
    st.error(f"Could not load daily completions: {e}")
