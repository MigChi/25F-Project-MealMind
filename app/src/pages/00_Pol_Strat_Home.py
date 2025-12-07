import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Hi {st.session_state['first_name']}, welcome to your meal prep dashboard!")
st.write('')
st.write('')

logger.info("Student Home Page")

API_BASE_URL = "http://api:4000"

st.write('')
st.write('')

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('My Ingredients',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/01_My_Ingredients.py')
    st.caption("Add, edit, and track what's in your fridge")

with col2:
    if st.button('Find Recipes',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/02_Recipe_Finder.py')
    st.caption("See what you can make right now")

with col3:
    if st.button('Cooking History',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/03_Cooking_History.py')
    st.caption("Track what you've made")