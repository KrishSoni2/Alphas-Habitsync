# Krish Soni - Manage Categories (User Stories 3.1, 3.6)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide', page_title='HabitSync - Manage Categories')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Manage Categories & Default Habits")

# Categories Section
st.subheader("Habit Categories")

try:
    response = requests.get(f"{API_BASE}/admin/categories")
    categories = response.json()

    if len(categories) > 0:
        for cat in categories:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{cat['name']}**")
                st.write(f"{cat.get('description', 'No description')}")
            with col2:
                st.write(f"Created: {cat.get('created_at', 'N/A')}")
            with col3:
                if st.button("Delete", key=f"del_cat_{cat['category_id']}"):
                    try:
                        result = requests.delete(
                            f"{API_BASE}/admin/categories/{cat['category_id']}"
                        )
                        if result.status_code == 200:
                            st.success(f"Deleted '{cat['name']}'")
                            st.rerun()
                        else:
                            st.error("Failed to delete. Category may be in use.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            st.write("---")
    else:
        st.info("No categories found.")

except Exception as e:
    st.error(f"Could not load categories: {e}")

# Add Category
st.subheader("Add New Category")

with st.form("add_category_form"):
    cat_name = st.text_input("Category Name:")
    cat_desc = st.text_area("Description:")
    submitted = st.form_submit_button("Add Category")

    if submitted:
        if not cat_name:
            st.error("Please enter a category name.")
        else:
            try:
                payload = {"name": cat_name, "description": cat_desc}
                result = requests.post(
                    f"{API_BASE}/admin/categories", json=payload
                )
                if result.status_code == 201:
                    st.success(f"Category '{cat_name}' created!")
                    st.rerun()
                else:
                    st.error("Failed to create category.")
            except Exception as e:
                st.error(f"Error: {e}")

# Edit Category
st.subheader("Edit Category")

try:
    response = requests.get(f"{API_BASE}/admin/categories")
    categories = response.json()
except Exception as e:
    categories = []

if len(categories) > 0:
    cat_names_edit = [c['name'] for c in categories]
    selected_cat = st.selectbox("Select Category to Edit:", cat_names_edit)
    cat_to_edit = next(c for c in categories if c['name'] == selected_cat)

    with st.form("edit_category_form"):
        new_name = st.text_input("New Name:", value=cat_to_edit['name'])
        new_desc = st.text_area("New Description:",
                                 value=cat_to_edit.get('description', ''))
        edit_submitted = st.form_submit_button("Update Category")

        if edit_submitted:
            try:
                payload = {"name": new_name, "description": new_desc}
                result = requests.put(
                    f"{API_BASE}/admin/categories/{cat_to_edit['category_id']}",
                    json=payload
                )
                if result.status_code == 200:
                    st.success("Category updated!")
                    st.rerun()
                else:
                    st.error("Failed to update category.")
            except Exception as e:
                st.error(f"Error: {e}")

# Default Habits
st.write("---")
st.subheader("Default Suggested Habits")

try:
    response = requests.get(f"{API_BASE}/admin/default-habits")
    defaults = response.json()

    if len(defaults) > 0:
        st.dataframe(defaults, use_container_width=True)
    else:
        st.info("No default habits set.")

except Exception as e:
    st.error(f"Could not load default habits: {e}")
