import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

# Show appropriate sidebar links
SideBarLinks()

st.title('Quick Meals - Under 30 Minutes')

logger.info("Quick Meals feature page")

# Flask API base URL
API_BASE_URL = "http://api:4000"

# Back button
if st.button("Back to Dashboard"):
    st.switch_page('pages/00_Pol_Strat_Home.py')

st.write('')
st.write('')

# Filters
st.subheader("Filter Recipes")
col1, col2, col3 = st.columns(3)

with col1:
    max_time = st.slider("Max Prep Time (min)", 5, 60, 30)
with col2:
    difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
with col3:
    max_cost = st.slider("Max Cost ($)", 2, 20, 10)

st.write('')
st.write('')

# Display recipes
st.subheader("Available Quick Meals")

try:
    response = requests.get(f"{API_BASE_URL}/recipes")
    recipes = response.json()
    
    # Display each recipe
    for recipe in recipes:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(recipe['name'])
                st.write(f"**{recipe['prep_time']} minutes** | "
                        f"**{recipe['difficulty'].title()}** | "
                        f"**${recipe['cost']:.2f}** | "
                        f"**{recipe['calories']} cal**")
                
                st.write("**Ingredients:**", ", ".join(recipe['ingredients']))
            
            with col2:
                if st.button("View Details", key=f"view_{recipe['recipe_id']}"):
                    st.info(f"Viewing: {recipe['name']}")
                
                if st.button("Add to Plan", key=f"add_{recipe['recipe_id']}"):
                    st.success(f"Added {recipe['name']} to your meal plan!")
            
            st.divider()

except Exception as e:
    st.error(f"Error loading recipes: {str(e)}")
    logger.error(f"Error in Quick Meals: {str(e)}")