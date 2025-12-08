import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Maya – Admin Dashboard", page_icon="🖥️")
SideBarLinks()

user = st.session_state.get("user", {"first_name": "Maya"})
first_name = user.get("first_name", "Maya")

st.title(f"Welcome, {first_name} (System Admin)")
st.write("Keep data clean, recipes up to date, and the system healthy.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Admin Tasks")
    st.write("• Add / update / remove recipes")
    st.write("• Monitor for data quality issues")
    st.write("• Watch system metrics and alerts")

with col2:
    st.subheader("Jump to tools")
    if st.button("Recipe Management", use_container_width=True):
        st.switch_page("pages/21_Maya_Recipe_Management.py")
    if st.button("Data Quality Monitor", use_container_width=True):
        st.switch_page("pages/22_Maya_Data_Quality.py")
    if st.button("System Health Monitor", use_container_width=True):
        st.switch_page("pages/23_Maya_System_Health.py")

st.write("---")
st.caption("Use the sidebar to switch personas or explore other areas of MealMind.")

