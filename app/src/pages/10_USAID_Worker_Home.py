import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title('Beginner Cook Dashboard')
st.write('Simple meal planning for healthy eating on a budget')

st.write(f"### Hi {st.session_state['first_name']}! Let\'s plan some easy, healthy meals.")

logger.info("Professional/Beginner Cook Home Page")

st.write('')
st.write('')


# Navigation to feature pages
st.subheader("What do you need help with?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Weekly Groceries',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/11_Weekly_Groceries.py')
    st.caption("Track what you bought and avoid duplicates")

with col2:
    if st.button('Meal Plan Generator',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/12_Meal_Plan_Generator.py')
    st.caption("Auto-generate a simple weekly plan")

with col3:
    if st.button('Budget Meal Finder',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/13_Budget_Meal_Finder.py')
    st.caption("Find meals within your budget")

st.write('')
st.write('')

# This week's plan preview
st.subheader("This Week's Meal Plan")

st.write("**Monday:** Chicken Stir Fry with Rice")
st.write("**Tuesday:** Pasta with Marinara and Salad")
st.write("**Wednesday:** Baked Salmon with Roasted Vegetables")
st.write("**Thursday:** Black Bean Tacos")
st.write("**Friday:** Leftovers or Easy Meal")

st.caption("Generated based on your budget and preferences")

st.write('')
st.write('')

# Reminders
st.subheader("Reminders")
st.warning("Bell peppers expire in 2 days - use for stir fry tonight!")
st.info("You have all ingredients for Chicken Stir Fry ready to cook")