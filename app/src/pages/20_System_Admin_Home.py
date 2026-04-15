# Krish Soni - System Admin Home

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - System Admin')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title(f"Welcome, Admin {st.session_state.get('first_name', 'User')}!")
st.subheader("System Administration Dashboard")

# Platform Metrics
st.write("### Platform Overview")
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
    st.error(f"Could not load metrics: {e}")

st.write("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("### Manage Categories")
    st.write("Create, edit, and delete habit categories.")
    if st.button("Go to Manage Categories", use_container_width=True):
        st.switch_page('pages/21_Manage_Categories.py')

with col2:
    st.write("### Flagged Content")
    st.write("Review and resolve flagged content.")
    if st.button("Go to Flagged Content", use_container_width=True):
        st.switch_page('pages/22_Flagged_Content.py')

with col3:
    st.write("### User Management")
    st.write("View and manage user accounts.")
    if st.button("Go to User Management", use_container_width=True):
        st.switch_page('pages/23_User_Management.py')
