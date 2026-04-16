# Matvey Rolett (Data Analyst)
# Group vs Solo comparison and activity heatmap - User Stories 4.3, 4.4

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Group Impact')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Group Impact Analysis")
st.write("Compare group users vs solo users and view activity patterns.")

# Group vs Solo Comparison
st.subheader("Group vs Solo Comparison")

try:
    response = requests.get(f"{API_BASE}/analytics/group-vs-solo")
    comparison = response.json()

    if len(comparison) > 0:
        df = pd.DataFrame(comparison)

        col1, col2 = st.columns(2)

        for item in comparison:
            user_type = item.get('user_type', 'unknown')
            count = item.get('completion_count', 0)

            if user_type == 'group_user':
                with col1:
                    st.metric("Group Users - Completions", count)
            else:
                with col2:
                    st.metric("Solo Users - Completions", count)

        st.bar_chart(df.set_index('user_type')['completion_count'])
    else:
        st.info("No comparison data available.")

except Exception as e:
    st.error(f"Could not load comparison data: {e}")

st.write("---")

# Activity Heatmap (by hour)
st.subheader("Activity Heatmap - Completions by Hour of Day")

try:
    response = requests.get(f"{API_BASE}/analytics/heatmap")
    heatmap = response.json()

    if len(heatmap) > 0:
        df = pd.DataFrame(heatmap)
        df['completion_hour'] = df['completion_hour'].astype(int)

        # Create a bar chart showing completions by hour
        st.bar_chart(df.set_index('completion_hour')['total_completions'])

        st.write("**Peak Activity Hours:**")
        df_sorted = df.sort_values('total_completions', ascending=False)
        top_hours = df_sorted.head(3)
        for _, row in top_hours.iterrows():
            hour = int(row['completion_hour'])
            count = int(row['total_completions'])
            if hour < 12:
                time_str = f"{hour}:00 AM"
            elif hour == 12:
                time_str = "12:00 PM"
            else:
                time_str = f"{hour - 12}:00 PM"
            st.write(f"- {time_str}: {count} completions")
    else:
        st.info("No heatmap data available.")

except Exception as e:
    st.error(f"Could not load heatmap data: {e}")
