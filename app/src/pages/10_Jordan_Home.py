import streamlit as st
from modules.nav import SideBarLinks

# Page config for this persona's home
st.set_page_config(page_title="Jordan – Health Dashboard", page_icon="💪")

# Sidebar navigation (respects logged-in role)
SideBarLinks()

# Mock user from session (set in Home.py when "Jordan" logs in)
user = st.session_state.get("user", {"first_name": "Jordan"})
first_name = user.get("first_name", "Jordan")

st.title(f"Hi {first_name}, let’s keep you on track 💪")
st.write(
    "This dashboard is for **health-focused professionals** balancing time, "
    "nutrition, and budget."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("What you can do here")
    st.write("• Set or update your **diet preferences** and weekly **budget**.")
    st.write("• Generate a **weekly meal plan** that respects your constraints.")
    st.write("• Explore **budget-friendly recipes** that match your goals.")
    st.write("• Save time by re-using plans that worked well for you.")

with col2:
    st.subheader("Jump to a feature")

    if st.button("Diet & Budget Preferences", use_container_width=True):
        st.switch_page("pages/11_Jordan_Preferences.py")

    if st.button("Weekly Meal Plan", use_container_width=True):
        st.switch_page("pages/12_Jordan_MealPlan.py")

    if st.button("Budget Recipes", use_container_width=True):
        st.switch_page("pages/13_Jordan_Budget_Recipes.py")
