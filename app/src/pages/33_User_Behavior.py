import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('User Behavior Insights')
st.write('Understand how different user groups interact with the app')

logger.info("User Behavior Insights page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Analyst Dashboard"):
    st.switch_page('pages/30_Analyst_Home.py')

st.write('')
st.write('')

# User Story 3: Demographics analysis
try:
    response = requests.get(f"{API_BASE_URL}/demographic-segments")
    behavior_data = response.json()
    
    # Display filtered results
    st.subheader(f"Behavior Analysis: {user_type} ({age_group})")
    
    # Key metrics for selected demographic
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Users in Group", "347")
    with col2:
        st.metric("Avg Sessions/Week", "4.2")
    with col3:
        st.metric("Avg Time/Session", "14.3 min")
    with col4:
        st.metric("Recipes per Week", "3.7")
    
    st.write('')
    st.write('')
    
    # Cooking habits comparison
    st.subheader("Cooking Habits by Demographics")
    
    # MOCK comparative data
    demographic_comparison = [
        {"group": "College Students (18-24)", "recipes_per_week": 2.1, "budget": 40, "quick_meals": 85},
        {"group": "Young Professionals (25-34)", "recipes_per_week": 3.7, "budget": 80, "quick_meals": 72},
        {"group": "Families (35-44)", "recipes_per_week": 5.2, "budget": 120, "quick_meals": 45},
        {"group": "Empty Nesters (45-54)", "recipes_per_week": 4.1, "budget": 95, "quick_meals": 38},
        {"group": "Retirees (55+)", "recipes_per_week": 3.9, "budget": 75, "quick_meals": 28}
    ]
    
    st.write("**Recipes Cooked Per Week by Age Group:**")
    st.bar_chart({item["group"]: item["recipes_per_week"] for item in demographic_comparison})
    
    st.write('')
    
    st.write("**Average Weekly Food Budget by Age Group:**")
    st.bar_chart({item["group"]: item["budget"] for item in demographic_comparison})
    
    st.write('')
    st.write('')
    
    # Detailed demographic table
    st.subheader("Detailed Comparison")
    
    for demo in demographic_comparison:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.write(f"**{demo['group']}**")
        
        with col2:
            st.write(f"{demo['recipes_per_week']:.1f} recipes/week")
        
        with col3:
            st.write(f"${demo['budget']}/week budget")
        
        with col4:
            st.write(f"{demo['quick_meals']}% prefer quick meals")
        
        st.divider()
    
    st.write('')
    st.write('')
    
    # User preferences by demographic
    st.subheader("Recipe Preferences by User Type")
    
    preferences = {
        "College Students": ["Budget Friendly (78%)", "Quick Meals (85%)", "One-Pot Meals (67%)"],
        "Young Professionals": ["High Protein (72%)", "Meal Prep (68%)", "Health-Conscious (65%)"],
        "Families": ["Kid-Friendly (81%)", "Large Batches (75%)", "Balanced Meals (70%)"],
        "Retirees": ["Traditional Recipes (69%)", "Slow Cooker (62%)", "Heart Healthy (58%)"]
    }
    
    for user_group, prefs in preferences.items():
        with st.expander(f"{user_group} - Top Preferences"):
            for pref in prefs:
                st.write(f"- {pref}")

except Exception as e:
    st.error(f"Error loading behavior data: {str(e)}")

st.write('')
st.write('')
