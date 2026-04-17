# Sahib Chawla
# HabitSync Home Page - role selection and login

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync')
API_BASE = "http://web-api:4000"

# Show sidebar links
SideBarLinks(show_home=True)

st.image('assets/HabitSync Logo.png', width=250)
st.title('HabitSync')
st.subheader('Your Habit Tracking Companion')
st.write('')
st.write('Hi! As which user would you like to log in?')

fallback_users = {
    "everyday_user": [
        {"user_id": 1, "name": "Sahib Chawla"},
        {"user_id": 5, "name": "Alice Thompson"},
        {"user_id": 6, "name": "Ben Martinez"},
        {"user_id": 7, "name": "Clara Johnson"}
    ],
    "wellness_coach": [
        {"user_id": 2, "name": "Kenny Chen"},
        {"user_id": 8, "name": "Diana Flores"},
        {"user_id": 9, "name": "Ethan Park"}
    ],
    "system_admin": [
        {"user_id": 3, "name": "Krish Soni"},
        {"user_id": 10, "name": "Fiona Lee"}
    ],
    "data_analyst": [
        {"user_id": 4, "name": "Matvey Rolett"},
        {"user_id": 11, "name": "Grace Kim"}
    ]
}


def load_users_by_role():
    try:
        response = requests.get(f"{API_BASE}/admin/users", timeout=3)
        response.raise_for_status()
        users = response.json()
    except Exception:
        return fallback_users

    role_map = {role: [] for role in fallback_users}
    for user in users:
        role = user.get('role')
        if role not in role_map or not user.get('is_active'):
            continue
        role_map[role].append({
            "user_id": user['user_id'],
            "name": f"{user['first_name']} {user['last_name']}"
        })

    for role, defaults in fallback_users.items():
        role_map[role] = sorted(role_map[role], key=lambda item: item['name']) or defaults

    return role_map


users_by_role = load_users_by_role()

# ---- Everyday User Selection ----
st.write("### Everyday User")
everyday_users = users_by_role['everyday_user']
selected_everyday = st.selectbox(
    "Select an Everyday User:",
    options=[u["name"] for u in everyday_users],
    key="everyday_select"
)

if st.button("Login as Everyday User", type='primary', use_container_width=True):
    user = next(u for u in everyday_users if u["name"] == selected_everyday)
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'everyday_user'
    st.session_state['first_name'] = user["name"].split()[0]
    st.session_state['user_id'] = user["user_id"]
    st.switch_page('pages/00_Everyday_User_Home.py')

st.write("---")

# ---- Wellness Coach Selection ----
st.write("### Wellness Coach")
coach_users = users_by_role['wellness_coach']
selected_coach = st.selectbox(
    "Select a Wellness Coach:",
    options=[u["name"] for u in coach_users],
    key="coach_select"
)

if st.button("Login as Wellness Coach", type='primary', use_container_width=True):
    user = next(u for u in coach_users if u["name"] == selected_coach)
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'wellness_coach'
    st.session_state['first_name'] = user["name"].split()[0]
    st.session_state['user_id'] = user["user_id"]
    st.switch_page('pages/10_Wellness_Coach_Home.py')

st.write("---")

# ---- System Admin Selection ----
st.write("### System Administrator")
admin_users = users_by_role['system_admin']
selected_admin = st.selectbox(
    "Select a System Administrator:",
    options=[u["name"] for u in admin_users],
    key="admin_select"
)

if st.button("Login as System Administrator", type='primary', use_container_width=True):
    user = next(u for u in admin_users if u["name"] == selected_admin)
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'system_admin'
    st.session_state['first_name'] = user["name"].split()[0]
    st.session_state['user_id'] = user["user_id"]
    st.switch_page('pages/20_System_Admin_Home.py')

st.write("---")

# ---- Data Analyst Selection ----
st.write("### Data Analyst")
analyst_users = users_by_role['data_analyst']
selected_analyst = st.selectbox(
    "Select a Data Analyst:",
    options=[u["name"] for u in analyst_users],
    key="analyst_select"
)

if st.button("Login as Data Analyst", type='primary', use_container_width=True):
    user = next(u for u in analyst_users if u["name"] == selected_analyst)
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'data_analyst'
    st.session_state['first_name'] = user["name"].split()[0]
    st.session_state['user_id'] = user["user_id"]
    st.switch_page('pages/30_Data_Analyst_Home.py')
