# Author: Kenneith Chu Chen
# Group Dashboard - view and manage groups (User Stories 2.1, 2.3, 2.6)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Group Dashboard')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Group Dashboard")

user_id = st.session_state.get('user_id', 2)

# Get all groups for directory view
try:
    all_groups_response = requests.get(f"{API_BASE}/groups/")
    all_groups = all_groups_response.json()
except Exception:
    all_groups = []

# Get groups for this coach
try:
    response = requests.get(f"{API_BASE}/groups/user/{user_id}")
    groups = response.json()
except Exception as e:
    st.error(f"Could not load groups: {e}")
    groups = []

if len(groups) == 0:
    st.info("You are not part of any groups yet. Create one below!")
else:
    # Select a group
    group_names = [g['name'] for g in groups]
    selected_group_name = st.selectbox("Select a Group:", group_names)
    selected_group = next(g for g in groups if g['name'] == selected_group_name)
    group_id = selected_group['group_id']

    try:
        group_detail_response = requests.get(f"{API_BASE}/groups/{group_id}")
        group_detail = (
            group_detail_response.json()
            if group_detail_response.status_code == 200 else selected_group
        )
    except Exception:
        group_detail = selected_group

    st.write(f"**Description:** {group_detail.get('description', 'N/A')}")
    st.write(f"**Members:** {selected_group.get('member_count', 0)} | "
             f"**Your Role:** {selected_group.get('role', 'N/A')}")
    st.caption(
        "Created by "
        f"{group_detail.get('creator_first', 'Unknown')} "
        f"{group_detail.get('creator_last', '')} | "
        f"{'Public' if group_detail.get('is_public') else 'Private'} group"
    )

    st.write("---")

    # Group Members
    st.subheader("Group Members")
    try:
        members_response = requests.get(
            f"{API_BASE}/groups/{group_id}/members"
        )
        members = members_response.json()

        if len(members) > 0:
            for member in members:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    name = f"{member['first_name']} {member['last_name']}"
                    status = "Active" if member.get('is_active') else "Inactive"
                    st.write(f"**{name}** ({member.get('role', 'member')}) - {status}")
                with col2:
                    st.write(f"Joined: {member.get('joined_at', 'N/A')}")
                with col3:
                    if member.get('is_active') and member.get('role') != 'leader':
                        if st.button("Remove",
                                     key=f"remove_{member['user_id']}"):
                            try:
                                result = requests.delete(
                                    f"{API_BASE}/groups/{group_id}/members/{member['user_id']}"
                                )
                                if result.status_code == 200:
                                    st.success(f"Removed {name}")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove member.")
                            except Exception as e:
                                st.error(f"Error: {e}")
        else:
            st.info("No members in this group.")

    except Exception as e:
        st.error(f"Could not load members: {e}")

    # Group Summary
    st.write("---")
    st.subheader("Group Summary")
    try:
        summary_response = requests.get(
            f"{API_BASE}/groups/{group_id}/summary"
        )
        summary = summary_response.json()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Habit Logs", summary.get('total_logs', 0))
        with col2:
            st.metric("Total Members", summary.get('total_members', 0))
        with col3:
            st.metric("Assigned Habits", summary.get('total_assigned_habits', 0))
    except Exception as e:
        st.error(f"Could not load summary: {e}")

# Create New Group
st.write("---")
st.subheader("Create a New Group")

with st.form("create_group_form"):
    group_name = st.text_input("Group Name:")
    group_desc = st.text_area("Description:")
    is_public = st.checkbox("Make group public?", value=True)

    submitted = st.form_submit_button("Create Group")
    if submitted:
        if not group_name:
            st.error("Please enter a group name.")
        else:
            try:
                payload = {
                    "name": group_name,
                    "description": group_desc,
                    "creator_id": user_id,
                    "is_public": is_public
                }
                result = requests.post(f"{API_BASE}/groups/", json=payload)
                if result.status_code == 201:
                    st.success(f"Group '{group_name}' created!")
                    st.rerun()
                else:
                    st.error("Failed to create group.")
            except Exception as e:
                st.error(f"Error: {e}")

st.write("---")
st.subheader("Community Group Directory")

if len(all_groups) > 0:
    active_groups = [group for group in all_groups if group.get('is_active')]
    public_groups = [group for group in active_groups if group.get('is_public')]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("All Groups", len(all_groups))
    with col2:
        st.metric("Active Groups", len(active_groups))
    with col3:
        st.metric("Public Groups", len(public_groups))

    directory_rows = [
        {
            "name": group.get('name'),
            "creator": f"{group.get('creator_first', '')} {group.get('creator_last', '')}".strip(),
            "members": group.get('member_count', 0),
            "visibility": "Public" if group.get('is_public') else "Private",
            "status": "Active" if group.get('is_active') else "Inactive"
        }
        for group in active_groups
    ]
    st.dataframe(directory_rows, use_container_width=True)
else:
    st.info("No groups available on the platform yet.")
