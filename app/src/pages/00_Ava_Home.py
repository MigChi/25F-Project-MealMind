import streamlit as st
from modules.nav import SideBarLinks


st.set_page_config(page_title="Ava – Student Dashboard", page_icon="🧑‍🎓")
SideBarLinks()


user = st.session_state.get("user", {"first_name": "Ava"})
first_name = user.get("first_name", "Ava")


st.title(f"Hi {first_name}, welcome to MealMind 👋")
st.write(
    "This dashboard is for **busy students** who want simple, fast meals and less food waste."
)


col1, col2 = st.columns(2)


with col1:
    st.subheader("Today’s To-Dos")
    st.write("• Check what’s expiring soon in your **Fridge**")
    st.write("• Plan at least one **Quick Recipe** for today")
    st.write("• Log anything new you bought in **Weekly Groceries**")


with col2:
    st.subheader("Jump to a feature")
    if st.button("Go to My Fridge", use_container_width=True):
        st.switch_page("pages/01_Ava_Fridge.py")
    if st.button("Find Quick Recipes", use_container_width=True):
        st.switch_page("pages/02_Ava_Quick_Recipes.py")
    if st.button("Log Weekly Groceries", use_container_width=True):
        st.switch_page("pages/03_Ava_Groceries.py")


st.write("---")
st.caption("Use the sidebar to navigate between Ava’s tools.")


