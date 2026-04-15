# Author: Kenneith Chu Chen
# Send notes to group members (User Stories 2.4, 2.5)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Send Notes')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Send Notes")
st.write("Send motivational notes to your group members.")

user_id = st.session_state.get('user_id', 2)

# Get groups for this coach
try:
    response = requests.get(f"{API_BASE}/groups/user/{user_id}")
    groups = response.json()
except Exception as e:
    st.error(f"Could not load groups: {e}")
    groups = []

if len(groups) == 0:
    st.info("You have no groups.")
else:
    # Select a group
    group_names = [g['name'] for g in groups]
    selected_group_name = st.selectbox("Select a Group:", group_names)
    selected_group = next(g for g in groups if g['name'] == selected_group_name)
    group_id = selected_group['group_id']

    # Get group members
    try:
        members_response = requests.get(
            f"{API_BASE}/groups/{group_id}/members"
        )
        members = members_response.json()
    except Exception as e:
        st.error(f"Could not load members: {e}")
        members = []

    # Send Note Form
    st.subheader("Send a Note")

    if len(members) > 0:
        member_options = {
            f"{m['first_name']} {m['last_name']}": m['user_id']
            for m in members
        }
        selected_member = st.selectbox(
            "Send to:", list(member_options.keys())
        )
        message = st.text_area("Message:",
                                placeholder="Type your coaching note here...")

        if st.button("Send Note"):
            if not message:
                st.error("Please enter a message.")
            else:
                try:
                    payload = {
                        "sender_id": user_id,
                        "receiver_id": member_options[selected_member],
                        "group_id": group_id,
                        "message": message
                    }
                    result = requests.post(
                        f"{API_BASE}/groups/notes", json=payload
                    )
                    if result.status_code == 201:
                        st.success(f"Note sent to {selected_member}!")
                        st.rerun()
                    else:
                        st.error("Failed to send note.")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("No members in this group.")

    # Previous Notes
    st.write("---")
    st.subheader("Previous Notes")

    try:
        notes_response = requests.get(f"{API_BASE}/groups/{group_id}/notes")
        notes = notes_response.json()

        if len(notes) > 0:
            for note in notes:
                sender = f"{note.get('sender_first', '')} {note.get('sender_last', '')}"
                receiver = f"{note.get('receiver_first', '')} {note.get('receiver_last', '')}"
                st.write(f"**{sender}** to **{receiver}** ({note.get('sent_at', 'N/A')})")
                st.write(f"> {note.get('message', '')}")
                st.write("---")
        else:
            st.info("No notes yet.")

    except Exception as e:
        st.error(f"Could not load notes: {e}")
