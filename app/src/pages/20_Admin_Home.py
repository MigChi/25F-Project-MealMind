import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title('System Administrator Dashboard')
st.write('Maintain data quality and system health')

st.write(f"### Hi {st.session_state['first_name']}! System status overview:")

logger.info("Admin Home Page")

st.write('')
st.write('')

# System health overview (User Story 4, 6)
st.subheader("System Health")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("System Status", "Healthy", delta="Normal")
with col2:
    st.metric("Active Users", "1,247", delta="+23")
with col3:
    st.metric("API Response Time", "142ms", delta="-8ms")
with col4:
    st.metric("Database Size", "2.3 GB", delta="+120 MB")

st.write('')

# Recent alerts
col1, col2 = st.columns([2, 1])

with col1:
    st.warning("3 duplicate ingredient entries detected")
    st.info("Database backup completed successfully")

with col2:
    st.metric("Open Issues", "3")
    st.metric("Errors (24h)", "12")

st.write('')
st.write('')

# Navigation to admin tools
st.subheader("Admin Tools")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Recipe Management',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/21_Recipe_Management.py')
    st.caption("Add, update, or remove recipes")

with col2:
    if st.button('Data Quality Monitor',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/22_Data_Quality.py')
    st.caption("Check for duplicates and corruption")

with col3:
    if st.button('System Health Monitor',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/23_System_Health.py')
    st.caption("Monitor performance and alerts")

st.write('')
st.write('')

# Quick stats
st.subheader("Recent Activity")

st.write("**Today:**")
st.write("- 15 new recipes added by users")
st.write("- 43 recipe updates submitted")
st.write("- 8 recipes flagged for review")
st.write("- 2 data consistency issues resolved")

st.write('')

st.write("**This Week:**")
st.write("- 127 new user registrations")
st.write("- 89 recipes approved")
st.write("- 12 recipes removed (outdated)")
st.write("- Average API response: 145ms")

st.write('')
st.write('')

# Quick actions
with st.expander("Quick Admin Actions"):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Run Data Quality Check"):
            st.info("Data quality scan initiated...")
        
        if st.button("Export Error Logs"):
            st.success("Error logs exported to admin@mealprep.app")
    
    with col2:
        if st.button("Clear Cache"):
            st.success("System cache cleared")
        
        if st.button("Force Database Backup"):
            st.info("Manual backup started...")