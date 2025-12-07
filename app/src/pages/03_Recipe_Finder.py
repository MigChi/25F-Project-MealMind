import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('Quick Recipe Finder')
st.write('See what you can make with what you already have')

logger.info("Quick Recipe Finder page")

API_BASE_URL = "http://api:4000"

# Back button
if st.button("Back to Dashboard"):
    st.switch_page('pages/00_Pol_Strat_Home.py')

st.write('')
st.write('')

# User Story 4: Recipe suggestions based on current ingredients
st.subheader("Recipes You Can Make Right Now")
st.caption("Based on ingredients currently in your fridge")

try:
    response = requests.get(f"{API_BASE_URL}/inventory-items/{user_id}")
    user_ingredients = response.json()

    response = requests.get(f"{API_BASE_URL}/recipes", params={"category_id": category_id})

    
