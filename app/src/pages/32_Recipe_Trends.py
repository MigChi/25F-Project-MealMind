import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('Recipe Trends & Popularity Analytics')
st.write('Track recipe popularity and identify user cooking patterns')

logger.info("Recipe Trends page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Analyst Dashboard"):
    st.switch_page('pages/30_Analyst_Home.py')

st.write('')
st.write('')

# User Story 2: Visualizations of popular recipe categories over time
st.subheader("Popular Recipe Categories Over Time")

# Time range selector
time_period = st.selectbox("Time period", 
                          ["Last 7 days", "Last 30 days", "Last 3 months", "Last 6 months", "Last year"])

st.write('')

try:
    response = requests.get(f"{API_BASE_URL}/system-metrics/recipe-usage-metrics")
    trends_data = response.json()

    st.subheader("Recipe Category Popularity Trends")
    
    # Line chart showing trends
    chart_data = {
        "Quick Meals": [245, 267, 289, 312, 334, 356, 378, 401, 423, 445, 467, 489],
        "High Protein": [189, 198, 207, 216, 225, 234, 243, 252, 261, 270, 279, 288],
        "Vegetarian": [156, 163, 170, 177, 184, 191, 198, 205, 212, 219, 226, 233],
        "Budget Friendly": [234, 229, 224, 219, 214, 209, 204, 199, 194, 189, 184, 179],
        "Meal Prep": [123, 131, 139, 147, 155, 163, 171, 179, 187, 195, 203, 211]
    }
    
    st.line_chart(chart_data)
    
    st.caption("Views per recipe category over the last 12 months")
    
    st.write('')
    st.write('')
    
    # Insights from trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**Growing Categories:**")
        st.write("- Quick Meals: +100% year-over-year")
        st.write("- High Protein: +52% YoY")
        st.write("- Meal Prep: +71% YoY")
    
    with col2:
        st.warning("**Declining Categories:**")
        st.write("- Budget Friendly: -23% YoY")
        st.write("- Comfort Food: -12% YoY")
        st.write("- Slow Cooker: -8% YoY")

except Exception as e:
    st.error(f"Error loading trends: {str(e)}")

st.write('')
st.write('')