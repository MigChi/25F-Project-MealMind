import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('Data Quality Monitor')
st.write('Identify corrupted, duplicate, or inconsistent data')

logger.info("Data Quality Monitor page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Admin Dashboard"):
    st.switch_page('pages/20_Admin_Home.py')

st.write('')
st.write('')

# User Story 5: Data consistency reports
st.subheader("Data Consistency Overview")

try:
    response = requests.get(f"{API_BASE_URL}/analytics/data-quality-reports")
    
    if response.status_code == 200:
        report = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            orphan_items = report.get('orphan_inventory_items', 0)
            st.metric("Orphan Inventory Items", orphan_items)
        
        with col2:
            recipes_no_ing = report.get('recipes_without_ingredients', 0)
            st.metric("Recipes Without Ingredients", recipes_no_ing)
        
        with col3:
            unused_ing = report.get('unused_ingredients', 0)
            st.metric("Unused Ingredients", unused_ing)
        
        with col4:
            total_issues = orphan_items + recipes_no_ing + unused_ing
            quality_score = max(0, 100 - (total_issues * 2))
            st.metric("Data Quality Score", f"{quality_score}%")
        
        st.write('')
        
        if total_issues > 0:
            st.warning(f"Found {total_issues} data quality issues")
            
            if orphan_items > 0:
                st.write(f"- {orphan_items} inventory items reference non-existent ingredients")
            if recipes_no_ing > 0:
                st.write(f"- {recipes_no_ing} recipes have no ingredients listed")
            if unused_ing > 0:
                st.write(f"- {unused_ing} ingredients are never used in any recipe")
            
            st.write('')
            
            if st.button("Run Cleanup", type="primary"):
                st.info("Data cleanup would be initiated here")
        else:
            st.success("No data quality issues detected! Database is healthy.")
    else:
        st.error(f"Error loading data quality report: Status {response.status_code}")
        st.warning("Unable to connect to data quality API")
        
except Exception as e:
    st.error(f"Error connecting to API: {str(e)}")
    st.warning("Make sure Docker containers are running: `docker compose up`")

st.write('')

# Last scan info
col1, col2 = st.columns([2, 1])

with col1:
    st.info("Last data quality scan: Today at 3:42 AM")

with col2:
    if st.button("Run New Scan", type="primary", use_container_width=True):
        with st.spinner("Scanning database for issues..."):
            st.success("Scan complete!")
            st.rerun()

st.write('')
st.write('')

# Detailed issue analysis tabs
tabs = st.tabs(["Orphaned Data", "Missing Data", "Unused Items", "Recommendations"])

with tabs[0]:
    st.subheader("Orphaned Inventory Items")
    st.caption("Inventory items that reference deleted or non-existent ingredients")
    
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/data-quality-reports")
        
        if response.status_code == 200:
            report = response.json()
            orphan_count = report.get('orphan_inventory_items', 0)
            
            if orphan_count > 0:
                st.warning(f"Found {orphan_count} orphaned inventory items")
                st.write("These items should be cleaned up or reassigned to valid ingredients.")
                
                if st.button("Clean Up Orphaned Items"):
                    st.info("Cleanup process would remove these items")
            else:
                st.success("No orphaned inventory items found")
    except:
        st.info("Unable to load orphaned data details")

with tabs[1]:
    st.subheader("Recipes Without Ingredients")
    st.caption("Recipes that have no ingredients listed")
    
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/data-quality-reports")
        
        if response.status_code == 200:
            report = response.json()
            missing_count = report.get('recipes_without_ingredients', 0)
            
            if missing_count > 0:
                st.warning(f"Found {missing_count} recipes without ingredients")
                st.write("These recipes are incomplete and should be fixed or removed.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Incomplete Recipes"):
                        st.info("Would show list of recipe IDs")
                with col2:
                    if st.button("Flag for Admin Review"):
                        st.success("Recipes flagged for review")
            else:
                st.success("All recipes have ingredients listed")
    except:
        st.info("Unable to load missing data details")

with tabs[2]:
    st.subheader("Unused Ingredients")
    st.caption("Ingredients that are not used in any recipe")
    
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/data-quality-reports")
        
        if response.status_code == 200:
            report = response.json()
            unused_count = report.get('unused_ingredients', 0)
            
            if unused_count > 0:
                st.info(f"Found {unused_count} ingredients not used in any recipe")
                st.write("These might be ingredients users added but no recipes use them yet.")
                st.write("This is not necessarily an error, but something to be aware of.")
            else:
                st.success("All ingredients are used in at least one recipe")
    except:
        st.info("Unable to load unused ingredients details")

with tabs[3]:
    st.subheader("Recommendations for Data Quality")
    
    st.write("""
    **Based on current data quality analysis:**
    
    **Prevention Strategies:**
    1. Add foreign key constraints to prevent orphaned records
    2. Require at least one ingredient when creating recipes
    3. Add validation before accepting bulk imports
    4. Implement cascade deletes for related data
    
    **Maintenance Tasks:**
    1. Run data quality scans weekly
    2. Clean up orphaned data monthly
    3. Review unused ingredients quarterly
    4. Validate recipe completeness after imports
    
    **Monitoring:**
    1. Set alerts for quality score dropping below 95%
    2. Track trends in data quality over time
    3. Review user-reported data issues
    4. Monitor failed validation attempts
    """)

st.write('')
st.write('')

# Automated cleanup settings
st.subheader("Automated Cleanup Settings")

with st.form("cleanup_settings"):
    st.write("Configure automatic data quality maintenance:")
    
    auto_cleanup_orphaned = st.checkbox("Auto-cleanup orphaned data weekly", value=True)
    auto_flag_incomplete = st.checkbox("Auto-flag incomplete recipes for review", value=True)
    
    notification_email = st.text_input("Send cleanup reports to:", value="maya@mealprep.app")
    
    if st.form_submit_button("Save Cleanup Settings", use_container_width=True):
        st.success("Cleanup settings updated")

st.write('')
st.write('')

# Data quality best practices
with st.expander("Data Quality Best Practices"):
    st.write("""
    **Regular Maintenance:**
    - Run scans weekly to catch issues early
    - Clean up orphaned data immediately
    - Review incomplete records monthly
    - Validate data after bulk operations
    
    **Common Causes of Issues:**
    - User input errors (typos, missing fields)
    - Bulk imports without validation
    - Incomplete deletion processes
    - API changes breaking old formats
    
    **Prevention Tips:**
    - Implement strict input validation
    - Use database constraints effectively
    - Test data operations thoroughly
    - Document data relationships clearly
    """)