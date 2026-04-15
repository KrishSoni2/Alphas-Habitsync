# Author: Kenneith Chu Chen
# Wellness Coach landing page

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Wellness Coach')
SideBarLinks()

st.title(f"Welcome, Coach {st.session_state.get('first_name', 'User')}!")
st.subheader("Wellness Coach Dashboard")

st.write("Use the sidebar to navigate to your features:")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("### Group Dashboard")
    st.write("View and manage your accountability groups.")
    if st.button("Go to Group Dashboard", use_container_width=True):
        st.switch_page('pages/11_Group_Dashboard.py')

with col2:
    st.write("### Assign Habits")
    st.write("Assign habits to group members.")
    if st.button("Go to Assign Habits", use_container_width=True):
        st.switch_page('pages/12_Assign_Habits.py')

with col3:
    st.write("### Send Notes")
    st.write("Send motivational notes to members.")
    if st.button("Go to Send Notes", use_container_width=True):
        st.switch_page('pages/13_Send_Notes.py')
