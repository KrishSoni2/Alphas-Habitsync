# Sahib Chawla
# Create a new habit
# Supports User Stories: 1.1, 1.6

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Create Habit')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Create New Habit")
st.write("Add a new habit to track.")

user_id = st.session_state.get('user_id', 1)

# ---- Fetch categories ----
try:
    response = requests.get(f"{API_BASE}/admin/categories")
    categories = response.json()
except Exception as e:
    st.error(f"Could not load categories: {e}")
    categories = []

# ---- Habit Creation Form ----
with st.form("create_habit_form"):
    habit_name = st.text_input("Habit Name:", placeholder="e.g., Drink 8 Glasses of Water")
    description = st.text_area("Description (optional):",
                                placeholder="Describe the intention behind this habit")

    if len(categories) > 0:
        category_names = [c['name'] for c in categories]
        selected_category = st.selectbox("Category:", category_names)
        category_id = next(
            c['category_id'] for c in categories if c['name'] == selected_category
        )
    else:
        st.warning("No categories available.")
        category_id = 1

    frequency = st.radio("Frequency:", ["Daily", "Weekly"])
    daily_goal = st.number_input("Daily Goal:", min_value=1, max_value=10, value=1)
    is_public = st.checkbox("Make this habit public?")

    submitted = st.form_submit_button("Create Habit")

    if submitted:
        if not habit_name:
            st.error("Please enter a habit name.")
        else:
            try:
                payload = {
                    "user_id": user_id,
                    "category_id": category_id,
                    "name": habit_name,
                    "description": description,
                    "frequency": frequency,
                    "daily_goal": daily_goal,
                    "is_public": is_public
                }
                result = requests.post(f"{API_BASE}/habits/", json=payload)
                if result.status_code == 201:
                    st.success(f"Habit '{habit_name}' created successfully!")
                    st.rerun()
                else:
                    st.error(result.json().get('error', 'Failed to create habit.'))
            except Exception as e:
                st.error(f"Error: {e}")

# ---- Show existing habits ----
st.write("---")
st.subheader("Manage Existing Habits")

try:
    response = requests.get(f"{API_BASE}/habits/user/{user_id}")
    habits = response.json()

    if len(habits) > 0:
        st.dataframe(habits, use_container_width=True)

        habit_options = {
            f"{habit['name']} ({habit.get('category_name', 'Unknown')})": habit
            for habit in habits
        }
        selected_habit_label = st.selectbox(
            "Select a habit to edit or delete:",
            list(habit_options.keys())
        )
        selected_habit = habit_options[selected_habit_label]

        if len(categories) > 0:
            category_names = [c['name'] for c in categories]
            default_category_name = selected_habit.get('category_name', category_names[0])
            category_index = (
                category_names.index(default_category_name)
                if default_category_name in category_names else 0
            )
        else:
            category_names = [selected_habit.get('category_name', 'Uncategorized')]
            category_index = 0

        with st.form("edit_habit_form"):
            edit_name = st.text_input(
                "Habit Name:",
                value=selected_habit['name'],
                key=f"edit_name_{selected_habit['habit_id']}"
            )
            edit_description = st.text_area(
                "Description:",
                value=selected_habit.get('description', ''),
                key=f"edit_desc_{selected_habit['habit_id']}"
            )
            edit_category_name = st.selectbox(
                "Category:",
                category_names,
                index=category_index,
                key=f"edit_category_{selected_habit['habit_id']}"
            )
            edit_frequency = st.radio(
                "Frequency:",
                ["Daily", "Weekly"],
                index=0 if selected_habit.get('frequency', 'Daily') == 'Daily' else 1,
                key=f"edit_frequency_{selected_habit['habit_id']}"
            )
            edit_goal = st.number_input(
                "Daily Goal:",
                min_value=1,
                max_value=10,
                value=int(selected_habit.get('daily_goal', 1) or 1),
                key=f"edit_goal_{selected_habit['habit_id']}"
            )
            edit_public = st.checkbox(
                "Make this habit public?",
                value=bool(selected_habit.get('is_public')),
                key=f"edit_public_{selected_habit['habit_id']}"
            )
            update_submitted = st.form_submit_button("Update Habit")

            if update_submitted:
                updated_category_id = selected_habit.get('category_id', 1)
                if len(categories) > 0:
                    updated_category_id = next(
                        category['category_id']
                        for category in categories
                        if category['name'] == edit_category_name
                    )

                try:
                    payload = {
                        "name": edit_name,
                        "description": edit_description,
                        "category_id": updated_category_id,
                        "frequency": edit_frequency,
                        "daily_goal": edit_goal,
                        "is_public": edit_public
                    }
                    result = requests.put(
                        f"{API_BASE}/habits/{selected_habit['habit_id']}",
                        json=payload
                    )
                    if result.status_code == 200:
                        st.success("Habit updated successfully!")
                        st.rerun()
                    else:
                        st.error(result.json().get('error', 'Failed to update habit.'))
                except Exception as e:
                    st.error(f"Error: {e}")

        confirm_delete = st.checkbox(
            f"Confirm delete '{selected_habit['name']}'",
            key=f"confirm_delete_{selected_habit['habit_id']}"
        )
        if st.button("Delete Habit", type='secondary'):
            if not confirm_delete:
                st.error("Please confirm the deletion before continuing.")
            else:
                try:
                    result = requests.delete(
                        f"{API_BASE}/habits/{selected_habit['habit_id']}"
                    )
                    if result.status_code == 200:
                        st.success("Habit deleted successfully!")
                        st.rerun()
                    else:
                        st.error(result.json().get('error', 'Failed to delete habit.'))
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("You have no habits yet.")
except Exception as e:
    st.error(f"Could not load habits: {e}")
