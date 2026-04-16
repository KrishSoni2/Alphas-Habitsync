# Matvey Rolett (Data Analyst)
# Data Analyst landing page

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Data Analyst')
SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'User')}!")
st.subheader("Data Analytics Dashboard")

st.write("Use the sidebar to navigate to your analytics features:")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("### Completion Trends")
    st.write("View completion rates by category and over time.")
    if st.button("Go to Completion Trends", use_container_width=True):
        st.switch_page('pages/31_Completion_Trends.py')

with col2:
    st.write("### Group Impact")
    st.write("Compare group vs solo user performance.")
    if st.button("Go to Group Impact", use_container_width=True):
        st.switch_page('pages/32_Group_Impact.py')

with col3:
    st.write("### Platform Growth")
    st.write("Track user growth and popular habits.")
    if st.button("Go to Platform Growth", use_container_width=True):
        st.switch_page('pages/33_Platform_Growth.py')
