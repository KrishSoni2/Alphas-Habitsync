# Author: Kenneith Chu Chen
# Assign habits to groups (User Stories 2.2, 2.5)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Assign Habits')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Assign Habits to Group")

user_id = st.session_state.get('user_id', 2)

# Get groups for this coach
try:
    response = requests.get(f"{API_BASE}/groups/user/{user_id}")
    groups = response.json()
except Exception as e:
    st.error(f"Could not load groups: {e}")
    groups = []

if len(groups) == 0:
    st.info("You have no groups. Create one from the Group Dashboard.")
else:
    # Select a group
    group_names = [g['name'] for g in groups]
    selected_group_name = st.selectbox("Select a Group:", group_names)
    selected_group = next(g for g in groups if g['name'] == selected_group_name)
    group_id = selected_group['group_id']

    # Show current group habits
    st.subheader("Current Group Habits")
    try:
        habits_response = requests.get(
            f"{API_BASE}/groups/{group_id}/habits"
        )
        group_habits = habits_response.json()

        if len(group_habits) > 0:
            st.dataframe(group_habits, use_container_width=True)
        else:
            st.info("No habits assigned to this group yet.")
    except Exception as e:
        st.error(f"Could not load group habits: {e}")

    # Assign a habit
    st.write("---")
    st.subheader("Assign a Habit")

    # Get all available habits
    try:
        all_habits_response = requests.get(
            f"{API_BASE}/habits/user/{user_id}"
        )
        all_habits = all_habits_response.json()
    except Exception as e:
        st.error(f"Could not load habits: {e}")
        all_habits = []

    if len(all_habits) > 0:
        habit_options = {h['name']: h['habit_id'] for h in all_habits}
        selected_habit_name = st.selectbox(
            "Select a Habit to Assign:", list(habit_options.keys())
        )

        if st.button("Assign Habit to Group"):
            try:
                payload = {
                    "habit_id": habit_options[selected_habit_name],
                    "assigned_by": user_id
                }
                result = requests.post(
                    f"{API_BASE}/groups/{group_id}/habits", json=payload
                )
                if result.status_code in (200, 201):
                    message = result.json().get('message', 'Habit assigned to the group.')
                    st.success(f"{message}: {selected_habit_name}")
                    st.rerun()
                else:
                    st.error(result.json().get('error', 'Failed to assign habit.'))
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("No habits available. Create habits first.")

    # Add Members
    st.write("---")
    st.subheader("Add Member to Group")

    try:
        users_response = requests.get(f"{API_BASE}/admin/users")
        all_users = users_response.json()
    except Exception as e:
        all_users = []

    if len(all_users) > 0:
        user_options = {
            f"{u['first_name']} {u['last_name']}": u['user_id']
            for u in all_users
        }
        selected_user_name = st.selectbox(
            "Select User to Add:", list(user_options.keys())
        )
        member_role = st.selectbox("Role:", ["member", "leader"])

        if st.button("Add Member"):
            try:
                payload = {
                    "user_id": user_options[selected_user_name],
                    "role": member_role
                }
                result = requests.post(
                    f"{API_BASE}/groups/{group_id}/members", json=payload
                )
                if result.status_code in (200, 201):
                    message = result.json().get('message', 'Member added to the group.')
                    st.success(f"{message}: {selected_user_name}")
                    st.rerun()
                else:
                    st.error(result.json().get('error', 'Failed to add member.'))
            except Exception as e:
                st.error(f"Error: {e}")
