# Sahib Chawla
# View habit streaks and goals
# Supports User Stories: 1.2, 1.5, 1.6

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Habit Streaks')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Habit Streaks & Goals")

user_id = st.session_state.get('user_id', 1)

# ---- Streaks Section ----
st.subheader("Your Streaks")

try:
    response = requests.get(f"{API_BASE}/habits/streaks/{user_id}")
    streaks = response.json()

    if len(streaks) > 0:
        for streak in streaks:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label=streak.get('habit_name', 'Unknown'),
                    value=f"{streak.get('current_streak', 0)} days"
                )
            with col2:
                st.write(f"Longest: {streak.get('longest_streak', 0)} days")
            with col3:
                last_date = streak.get('last_logged_date', 'N/A')
                st.write(f"Last logged: {last_date}")
        st.write("---")
    else:
        st.info("No streaks yet. Start completing habits to build streaks!")

except Exception as e:
    st.error(f"Could not load streaks: {e}")

# ---- Goals Section ----
st.subheader("Your Goals")

try:
    response = requests.get(f"{API_BASE}/habits/goals/{user_id}")
    goals = response.json()

    if len(goals) > 0:
        st.dataframe(goals, use_container_width=True)
    else:
        st.info("No goals set yet.")

except Exception as e:
    st.error(f"Could not load goals: {e}")

# ---- Set New Goal ----
st.subheader("Set a New Goal")

col1, col2 = st.columns(2)
with col1:
    goal_type = st.selectbox("Goal Type:", ["daily", "weekly"])
with col2:
    target_value = st.number_input("Target (number of habits):",
                                    min_value=1, max_value=20, value=3)

if st.button("Set Goal"):
    try:
        payload = {
            "user_id": user_id,
            "goal_type": goal_type,
            "target_value": target_value
        }
        result = requests.post(f"{API_BASE}/habits/goals", json=payload)
        if result.status_code == 201:
            st.success("Goal created successfully!")
            st.rerun()
        else:
            st.error("Failed to create goal.")
    except Exception as e:
        st.error(f"Error: {e}")
