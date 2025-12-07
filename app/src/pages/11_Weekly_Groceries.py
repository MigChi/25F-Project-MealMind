import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
from datetime import datetime, timedelta

SideBarLinks()

st.title('Weekly Groceries Tracker')
st.write('Track what you bought to avoid duplicates and food waste')

logger.info("Weekly Groceries page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Dashboard"):
    st.switch_page('pages/10_USAID_Worker_Home.py')

st.write('')
st.write('')

# User Story 1: Add weekly groceries
st.subheader("Add This Week's Groceries")
st.caption("Log items right after shopping so you remember what you have")

with st.form("add_groceries"):
    st.write("**Quick Add Multiple Items**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ingredient_id = st.text_input("Item ID")
        quantity = st.number_input("Quantity", min_value=0.1, step=0.5, value=1.0)
        unit = st.selectbox("Unit", ["lbs", "oz", "count", "container", "bag", "bunch"])
    
    with col2:
        estimated_expiry = st.number_input("Lasts how many days?", min_value=1, value=7, step=1)
    
    submitted = st.form_submit_button("Add to Groceries", use_container_width=True)
    
    if submitted:
        if item_name and quantity > 0:
            expiry_date = purchase_date + timedelta(days=estimated_expiry)
            
            payload = {
                "user_id": st.session_state.get('user_id', 2),
                "ingredient_id": ingredient_id,
                "quantity": quantity,
                "unit": unit,
                "expiration_date": estimated_expiry,
                "status":
            }

            response = requests.post(f"{API_BASE_URL}/inventory-items")

            st.success(f"Added {item_name} to your groceries")
            st.rerun()
        else:
            st.error("Please enter item name and quantity")

st.write('')
st.write('')

# User Story 3: View and remove items
st.subheader("Current Grocery Inventory")
st.caption("Remove expired or spoiled items to keep your list accurate")

# Filter by week
week_filter = st.radio("Show items from:", 
                      ["This week", "Last 2 weeks", "All items"],
                      horizontal=True)

st.write('')

try:
    response = requests.get(f"{API_BASE_URL}/inventory-items/{user_id}")
    groceries = response.json()
    
    # Group by status
    expired = [g for g in groceries if g['status'] == 'expired']
    expiring = [g for g in groceries if g['status'] == 'expiring']
    fresh = [g for g in groceries if g['status'] == 'fresh']
    
    # Show expired items first
    if expired:
        st.error(f"Expired Items ({len(expired)}) - Remove these")
        for item in expired:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{item['name']}**")
                st.caption(f"Expired on {item['expiry_date']}")
            
            with col2:
                st.write(f"{item['quantity']} {item['unit']}")
            
            with col3:
                # User Story 3: Remove expired items
                if st.button("Remove", key=f"remove_{item['id']}"):
                    response = requests.delete(f"{API_BASE_URL}/inventory-items/<int:ingredient_id")
                    st.success("Removed expired item")
                    st.rerun()
        
        st.write('')
    
    # Show expiring soon
    if expiring:
        st.warning(f"Expiring Soon ({len(expiring)}) - Use these first")
        for item in expiring:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{item['name']}**")
                expiry = datetime.strptime(item['expiry_date'], "%Y-%m-%d")
                days_left = (expiry - datetime.now()).days
                st.caption(f"Expires in {days_left} days")
            
            with col2:
                st.write(f"{item['quantity']} {item['unit']}")
            
            with col3:
                if st.button("Used It", key=f"used_{item['id']}"):
                    response = requests.delete(f"{API_BASE_URL}/inventory-items/<int:ingredient_id")
                    st.success("Removed from inventory")
                    st.rerun()
        
        st.write('')
    
    # Show fresh items
    st.success(f"Fresh Items ({len(fresh)})")
    for item in fresh:
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        
        with col1:
            st.write(f"{item['name']}")
            st.caption(item['category'])
        
        with col2:
            st.write(f"{item['quantity']} {item['unit']}")
        
        with col3:
            purchase = datetime.strptime(item['purchase_date'], "%Y-%m-%d")
            days_ago = (datetime.now() - purchase).days
            st.caption(f"Bought {days_ago} days ago")
        
        with col4:
            if st.button("Remove", key=f"del_{item['id']}"):
                response = requests.delete(f"{API_BASE_URL}/inventory-items/<int: ingredient_id")
                st.success("Removed")
                st.rerun()
        
        st.divider()
        
except Exception as e:
    st.error(f"Error loading groceries: {str(e)}")

st.write('')
st.write('')

# Shopping list - avoid duplicates
st.subheader("Before Your Next Shopping Trip")
st.caption("Check what you already have to avoid buying duplicates")

st.write("**You already have these proteins:**")
st.write("- Chicken Breast (2 lbs)")
st.write("- Salmon Fillet (1.5 lbs)")

st.write("**You already have these vegetables:**")
st.write("- Bell Peppers (3)")

st.info("Don't buy more of these until you use what you have!")

st.write('')

# Tips for tracking groceries
with st.expander("Tips to reduce food waste"):
    st.write("""
    **Right after shopping:**
    - Add all items to the app immediately
    - Be realistic about expiration dates
    - Check what you already have before buying more
    
    **During the week:**
    - Check this list before ordering takeout
    - Remove items as you use them completely
    - Mark items as expired to keep list accurate
    
    **Before next shopping trip:**
    - Review what's still fresh
    - Plan meals around what you have
    - Only buy what you'll actually use
    """)