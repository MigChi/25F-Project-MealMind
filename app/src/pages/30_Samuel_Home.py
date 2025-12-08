import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Samuel – Analyst Dashboard", page_icon="📊")
SideBarLinks()

user = st.session_state.get("user", {"first_name": "Samuel"})
first_name = user.get("first_name", "Samuel")

st.title(f"Welcome, {first_name} (Data Analyst)")
st.write("Analyze food waste, recipe usage, and user segments to guide improvements.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Analytics you can explore")
    st.write("• Which ingredients are wasted most.")
    st.write("• Which recipe categories are trending.")
    st.write("• How behavior differs between demographic segments.")

with col2:
    st.subheader("Jump to analytics")
    if st.button("Food Waste Analytics", use_container_width=True):
        st.switch_page("pages/31_Samuel_Waste_Analytics.py")
    if st.button("Recipe Trends", use_container_width=True):
        st.switch_page("pages/32_Samuel_Recipe_Trends.py")
    if st.button("User Behavior Insights", use_container_width=True):
        st.switch_page("pages/33_Samuel_User_Behavior.py")
