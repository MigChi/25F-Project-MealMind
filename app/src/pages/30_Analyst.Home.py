import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title('Data Analyst Dashboard')
st.write('High-level insights and user behavior analytics')

st.write(f"### Hi {st.session_state['first_name']}! Here are today\'s key metrics:")

logger.info("Data Analyst Home Page")

st.write('')
st.write('')

# Key metrics overview
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Active Users", "1,247", delta="+89 (7.7%)")
with col2:
    st.metric("Recipes Created Today", "34", delta="+12")
with col3:
    st.metric("Avg Engagement Time", "12.5 min", delta="+1.3 min")
with col4:
    st.metric("Food Waste Reduced", "234 lbs", delta="+45 lbs")

st.write('')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Recipe Views", "4,567", delta="+456")
with col2:
    st.metric("Meal Plans Created", "892", delta="+67")
with col3:
    st.metric("Ingredients Tracked", "15,234", delta="+1,234")
with col4:
    st.metric("User Satisfaction", "4.6/5.0", delta="+0.2")

st.write('')
st.write('')

# Navigation to analytics tools
st.subheader("Analytics Tools")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Food Waste Analytics',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/31_Food_Waste_Analytics.py')
    st.caption("See what users waste most and why")

with col2:
    if st.button('Recipe Trends',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/32_Recipe_Trends.py')
    st.caption("Track recipe popularity and patterns")

with col3:
    if st.button('User Behavior Insights',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/33_User_Behavior.py')
    st.caption("Understand how different groups use the app")

st.write('')
st.write('')

# Quick insights
st.subheader("Today's Insights")

col1, col2 = st.columns(2)

with col1:
    st.info("**Top Wasted Food:** Lettuce accounts for 18% of reported waste this week")
    st.success("**Trending Recipe:** Chicken Stir Fry views up 45% this month")

with col2:
    st.warning("**User Drop-off:** 23% of new users don't complete profile setup")
    st.info("**Peak Usage:** Most active time is 6-8 PM on weekdays")

st.write('')
st.write('')

# Recent reports
st.subheader("Recent Reports Generated")

reports = [
    {"name": "Weekly User Engagement Report", "date": "2024-12-05", "type": "PDF"},
    {"name": "Monthly Recipe Analytics", "date": "2024-12-01", "type": "Excel"},
    {"name": "Q4 Food Waste Summary", "date": "2024-11-28", "type": "PDF"}
]

for report in reports:
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.write(f"**{report['name']}**")
        st.caption(f"Generated: {report['date']}")
    
    with col2:
        st.caption(report['type'])
    
    with col3:
        if st.button("Download", key=f"dl_{report['name']}"):
            st.success("Report downloaded!")

st.write('')
st.write('')

# Quick actions
with st.expander("Quick Analytics Actions"):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate Weekly Summary Report"):
            st.info("Generating report...")
        
        if st.button("Export User Behavior Data"):
            st.success("Data exported to CSV")
    
    with col2:
        if st.button("Refresh All Dashboards"):
            st.info("Refreshing analytics data...")
        
        if st.button("Schedule Monthly Report"):
            st.success("Report scheduled")