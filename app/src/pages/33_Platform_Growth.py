# Matvey Rolett (Data Analyst)
# Platform growth and popular habits - User Stories 4.5, 4.6

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Platform Growth')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Platform Growth")
st.write("Track user growth and popular habits on the platform.")

# User Growth Over Time
st.subheader("User Growth Over Time")

try:
    response = requests.get(f"{API_BASE}/analytics/user-growth")
    growth = response.json()

    if len(growth) > 0:
        df = pd.DataFrame(growth)
        st.line_chart(df.set_index('month')['new_users'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No growth data available.")

except Exception as e:
    st.error(f"Could not load growth data: {e}")

st.write("---")

# Top 10 Most Popular Habits
st.subheader("Top 10 Most Popular Habits")

try:
    response = requests.get(f"{API_BASE}/analytics/popular-habits")
    popular = response.json()

    if len(popular) > 0:
        df = pd.DataFrame(popular)

        # Display as a table with rank numbers
        df.index = range(1, len(df) + 1)
        df.index.name = "Rank"
        st.dataframe(df, use_container_width=True)

        # Also show as a bar chart
        st.bar_chart(df.set_index('name')['times_logged'])
    else:
        st.info("No popular habits data available.")

except Exception as e:
    st.error(f"Could not load popular habits: {e}")

st.write("---")

# Platform Summary Metrics
st.subheader("Platform Summary")

try:
    response = requests.get(f"{API_BASE}/admin/metrics")
    metrics = response.json()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", metrics.get('total_users', 0))
    with col2:
        st.metric("Active Users", metrics.get('active_users', 0))
    with col3:
        st.metric("Habits Logged Today", metrics.get('habits_logged_today', 0))
    with col4:
        st.metric("Total Groups", metrics.get('total_groups', 0))

except Exception as e:
    st.error(f"Could not load platform metrics: {e}")
