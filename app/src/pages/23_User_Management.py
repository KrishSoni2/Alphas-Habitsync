# Krish Soni - User Management (User Stories 3.4, 3.5)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - User Management')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("User Management")
st.write("View and manage user accounts on the platform.")

# Get all users
try:
    response = requests.get(f"{API_BASE}/admin/users")
    users = response.json()
except Exception as e:
    st.error(f"Could not load users: {e}")
    users = []

# Filter by role
if len(users) > 0:
    roles = list(set([u.get('role', 'unknown') for u in users]))
    roles.insert(0, "All")
    selected_role = st.selectbox("Filter by Role:", roles)

    if selected_role != "All":
        users = [u for u in users if u.get('role') == selected_role]

    # Filter by status
    status_filter = st.selectbox("Filter by Status:", ["All", "Active", "Inactive"])
    if status_filter == "Active":
        users = [u for u in users if u.get('is_active')]
    elif status_filter == "Inactive":
        users = [u for u in users if not u.get('is_active')]

    st.write(f"**Showing {len(users)} users**")
    st.write("---")

    # Display users
    for user in users:
        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            st.write(f"**{name}**")
            st.write(f"Email: {user.get('email', 'N/A')} | Role: {user.get('role', 'N/A')}")

        with col2:
            status = "Active" if user.get('is_active') else "Inactive"
            st.write(f"**Status:** {status}")
            st.write(f"Joined: {user.get('created_at', 'N/A')}")

        with col3:
            is_active = user.get('is_active', True)
            button_label = "Deactivate" if is_active else "Activate"

            if st.button(button_label,
                         key=f"toggle_{user['user_id']}"):
                try:
                    payload = {"is_active": not is_active}
                    result = requests.put(
                        f"{API_BASE}/admin/users/{user['user_id']}/status",
                        json=payload
                    )
                    if result.status_code == 200:
                        action = "deactivated" if is_active else "activated"
                        st.success(f"User {action}!")
                        st.rerun()
                    else:
                        st.error("Failed to update user status.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.write("---")
else:
    st.info("No users found.")

st.write("---")
st.subheader("Platform Groups Overview")

try:
    group_response = requests.get(f"{API_BASE}/admin/groups")
    platform_groups = group_response.json()
except Exception as e:
    st.error(f"Could not load platform groups: {e}")
    platform_groups = []

if len(platform_groups) > 0:
    active_groups = [group for group in platform_groups if group.get('is_active')]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Groups", len(platform_groups))
    with col2:
        st.metric("Active Groups", len(active_groups))

    group_rows = [
        {
            "name": group.get('name'),
            "creator": f"{group.get('creator_first', '')} {group.get('creator_last', '')}".strip(),
            "members": group.get('member_count', 0),
            "visibility": "Public" if group.get('is_public') else "Private",
            "status": "Active" if group.get('is_active') else "Inactive"
        }
        for group in platform_groups
    ]
    st.dataframe(group_rows, use_container_width=True)
else:
    st.info("No groups found.")
