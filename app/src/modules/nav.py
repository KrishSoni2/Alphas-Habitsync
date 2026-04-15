# Sahib Chawla
# Navigation module for sidebar links

import streamlit as st


def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def EverydayUserHomeNav():
    st.sidebar.page_link(
        "pages/00_Everyday_User_Home.py", label="Everyday User Home", icon="👤"
    )


def DailyHabitsNav():
    st.sidebar.page_link(
        "pages/01_Daily_Habits.py", label="Daily Habits", icon="✅"
    )


def HabitStreaksNav():
    st.sidebar.page_link(
        "pages/02_Habit_Streaks.py", label="Habit Streaks", icon="🔥"
    )


def CreateHabitNav():
    st.sidebar.page_link(
        "pages/03_Create_Habit.py", label="Create Habit", icon="➕"
    )


def WellnessCoachHomeNav():
    st.sidebar.page_link(
        "pages/10_Wellness_Coach_Home.py", label="Wellness Coach Home", icon="🏋️"
    )


def GroupDashboardNav():
    st.sidebar.page_link(
        "pages/11_Group_Dashboard.py", label="Group Dashboard", icon="👥"
    )


def AssignHabitsNav():
    st.sidebar.page_link(
        "pages/12_Assign_Habits.py", label="Assign Habits", icon="📋"
    )


def SendNotesNav():
    st.sidebar.page_link(
        "pages/13_Send_Notes.py", label="Send Notes", icon="💬"
    )


def AdminHomeNav():
    st.sidebar.page_link(
        "pages/20_System_Admin_Home.py", label="Admin Home", icon="⚙️"
    )


def ManageCategoriesNav():
    st.sidebar.page_link(
        "pages/21_Manage_Categories.py", label="Manage Categories", icon="📂"
    )


def FlaggedContentNav():
    st.sidebar.page_link(
        "pages/22_Flagged_Content.py", label="Flagged Content", icon="🚩"
    )


def UserManagementNav():
    st.sidebar.page_link(
        "pages/23_User_Management.py", label="User Management", icon="👤"
    )


def AnalystHomeNav():
    st.sidebar.page_link(
        "pages/30_Data_Analyst_Home.py", label="Data Analyst Home", icon="📊"
    )


def CompletionTrendsNav():
    st.sidebar.page_link(
        "pages/31_Completion_Trends.py", label="Completion Trends", icon="📈"
    )


def GroupImpactNav():
    st.sidebar.page_link(
        "pages/32_Group_Impact.py", label="Group Impact", icon="🤝"
    )


def PlatformGrowthNav():
    st.sidebar.page_link(
        "pages/33_Platform_Growth.py", label="Platform Growth", icon="🌱"
    )


def SideBarLinks(show_home=False):
    """Show sidebar links based on the logged-in user's role."""
    if show_home:
        HomeNav()

    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        if not show_home:
            HomeNav()
        return

    role = st.session_state.get('role', '')

    if role == 'everyday_user':
        EverydayUserHomeNav()
        DailyHabitsNav()
        HabitStreaksNav()
        CreateHabitNav()

    elif role == 'wellness_coach':
        WellnessCoachHomeNav()
        GroupDashboardNav()
        AssignHabitsNav()
        SendNotesNav()

    elif role == 'system_admin':
        AdminHomeNav()
        ManageCategoriesNav()
        FlaggedContentNav()
        UserManagementNav()

    elif role == 'data_analyst':
        AnalystHomeNav()
        CompletionTrendsNav()
        GroupImpactNav()
        PlatformGrowthNav()

    if st.sidebar.button("Logout"):
        del st.session_state['role']
        del st.session_state['authenticated']
        st.switch_page('Home.py')
