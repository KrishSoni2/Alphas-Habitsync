# Krish Soni - Flagged Content Management (User Story 3.3)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Flagged Content')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Flagged Content")
st.write("Review content that has been flagged by users.")

# Get flagged content
try:
    response = requests.get(f"{API_BASE}/admin/flagged")
    flagged_items = response.json()
except Exception as e:
    st.error(f"Could not load flagged content: {e}")
    flagged_items = []

# Filter by status
status_filter = st.selectbox("Filter by Status:", ["All", "open", "reviewed", "resolved"])

if status_filter != "All":
    flagged_items = [f for f in flagged_items if f.get('status') == status_filter]

st.write(f"**Showing {len(flagged_items)} flagged items**")
st.write("---")

if len(flagged_items) == 0:
    st.info("No flagged content to review.")
else:
    for item in flagged_items:
        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            st.write(f"**Type:** {item.get('content_type', 'N/A')}")
            st.write(f"**Reason:** {item.get('reason', 'No reason provided')}")
            reporter = f"{item.get('reporter_first', '')} {item.get('reporter_last', '')}"
            st.write(f"**Reported by:** {reporter}")
            st.write(f"**Date:** {item.get('created_at', 'N/A')}")

        with col2:
            current_status = item.get('status', 'open')
            st.write(f"**Status:** {current_status}")

        with col3:
            if current_status == 'open':
                if st.button("Resolve",
                             key=f"resolve_{item['flag_id']}"):
                    try:
                        result = requests.put(
                            f"{API_BASE}/admin/flagged/{item['flag_id']}",
                            json={"status": "resolved"}
                        )
                        if result.status_code == 200:
                            st.success("Marked as resolved!")
                            st.rerun()
                        else:
                            st.error("Failed to resolve.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.button("Delete", key=f"del_flag_{item['flag_id']}"):
                try:
                    result = requests.delete(
                        f"{API_BASE}/admin/flagged/{item['flag_id']}"
                    )
                    if result.status_code == 200:
                        st.success("Flagged item deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.write("---")
