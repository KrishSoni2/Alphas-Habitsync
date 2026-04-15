# Sahib Chawla
# Everyday User persona landing page

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Everyday User')
SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'User')}!")
st.subheader("Your Everyday Habit Dashboard")

st.write("Use the sidebar to navigate to your features:")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("### Daily Habits")
    st.write("View and complete your habits for today.")
    if st.button("Go to Daily Habits", use_container_width=True):
        st.switch_page('pages/01_Daily_Habits.py')

with col2:
    st.write("### Habit Streaks")
    st.write("Track your streaks and completion history.")
    if st.button("Go to Habit Streaks", use_container_width=True):
        st.switch_page('pages/02_Habit_Streaks.py')

with col3:
    st.write("### Create Habit")
    st.write("Add a new habit and set your goals.")
    if st.button("Go to Create Habit", use_container_width=True):
        st.switch_page('pages/03_Create_Habit.py')
