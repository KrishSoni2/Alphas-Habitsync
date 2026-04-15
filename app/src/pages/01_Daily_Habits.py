# Sahib Chawla
# View and complete daily habits
# Supports User Stories: 1.2, 1.3, 1.4

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Daily Habits')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Daily Habits")
st.write("View your habits and mark them as complete.")

user_id = st.session_state.get('user_id', 1)

# ---- Fetch habits for the user ----
try:
    response = requests.get(f"{API_BASE}/habits/user/{user_id}")
    habits = response.json()
except Exception as e:
    st.error(f"Could not connect to API: {e}")
    habits = []

if len(habits) == 0:
    st.info("You have no habits yet. Go to Create Habit to add some!")
else:
    # ---- Filter by category ----
    categories = list(set([h.get('category_name', 'Unknown') for h in habits]))
    categories.insert(0, "All")
    selected_category = st.selectbox("Filter by Category:", categories)

    if selected_category != "All":
        habits = [h for h in habits if h.get('category_name') == selected_category]

    st.write(f"**Showing {len(habits)} habits**")
    st.write("---")

    # ---- Display habits ----
    for habit in habits:
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.write(f"**{habit['name']}**")
            st.write(f"Category: {habit.get('category_name', 'N/A')} | "
                     f"Frequency: {habit.get('frequency', 'N/A')}")

        with col2:
            st.write(f"Daily Goal: {habit.get('daily_goal', 1)}")

        with col3:
            if st.button("Complete", key=f"complete_{habit['habit_id']}"):
                try:
                    payload = {
                        "habit_id": habit['habit_id'],
                        "user_id": user_id,
                        "status": "completed"
                    }
                    result = requests.post(
                        f"{API_BASE}/habits/complete", json=payload
                    )
                    response_payload = result.json()
                    if result.status_code == 201:
                        streak_text = ""
                        if response_payload.get('current_streak'):
                            streak_text = (
                                f" Current streak: {response_payload['current_streak']}."
                            )
                        st.success(
                            f"Marked '{habit['name']}' as complete!{streak_text}"
                        )
                        st.rerun()
                    elif result.status_code == 200:
                        st.info(response_payload.get('message', 'Habit already logged today.'))
                    else:
                        st.error(response_payload.get('error', 'Failed to log completion.'))
                except Exception as e:
                    st.error(f"Error: {e}")

        st.write("---")

# ---- Recent completions ----
st.subheader("Recent Activity")
try:
    log_response = requests.get(f"{API_BASE}/habits/logs/{user_id}")
    logs = log_response.json()

    if len(logs) > 0:
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("No recent activity.")
except Exception as e:
    st.error(f"Could not load activity: {e}")
