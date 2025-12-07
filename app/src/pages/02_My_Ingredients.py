import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
from datetime import datetime, timedelta

SideBarLinks()

st.title('My Fridge Ingredients')
st.write('Track what you have so you know what you can cook')

logger.info("Fridge Ingredients page")

API_BASE_URL = "http://api:4000"

# Back button
if st.button("Back to Dashboard"):
    st.switch_page('pages/00_Pol_Strat_Home.py')

st.write('')
st.write('')

# Quick stats
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Ingredients", "15")
with col2:
    st.metric("Expiring This Week", "3")
with col3:
    st.metric("Ready to Cook With", "12")

st.write('')
st.write('')

# Expiration alerts (User Story 5)
st.subheader("Expiration Alerts")

try:
    expiring_items = requests.get(f"{API_BASE_URL}/inventory-items/expiring")
    
    if expiring_items:
        st.warning(f"You have {len(expiring_items)} ingredients expiring soon!")
        
        for item in expiring_items:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                if item['days_left'] <= 1:
                    st.write(f"**USE TODAY: {item['name']}**")
                else:
                    st.write(f"**Use Soon: {item['name']}**")
            
            with col2:
                st.write(f"{item['quantity']} {item['unit']}")
                if item['days_left'] == 0:
                    st.caption("Expires today")
                elif item['days_left'] == 1:
                    st.caption("Expires tomorrow")
                else:
                    st.caption(f"Expires in {item['days_left']} days")
            
            with col3:
                if st.button("Used It", key=f"used_{item['id']}"):
                    response = requests.delete(f"{API_BASE_URL}/inventory-items/<int: ingredient_id")
                    st.success("Removed from fridge")
                    st.rerun()
    else:
        st.success("No ingredients expiring soon. You're good!")
        
except Exception as e:
    st.error(f"Error loading alerts: {str(e)}")

st.write('')
st.write('')

# All current ingredients
st.subheader("All My Ingredients")

# Filter options
col1, col2 = st.columns(2)
with col1:
    category_filter = st.selectbox("Filter by category", 
                                   ["All", "Proteins", "Vegetables", "Fruits", "Dairy", "Grains", "Condiments"])
with col2:
    sort_by = st.selectbox("Sort by", ["Name", "Quantity", "Expiration Date"])

st.write('')

try:
    response = requests.get(f"{API_BASE_URL}/inventory-items/{user_id}")
    ingredients = response.json()
    
    for item in ingredients:
        # Calculate days until expiry
        expiry = datetime.strptime(item['expiry_date'], "%Y-%m-%d")
        days_left = (expiry - datetime.now()).days
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            st.write(f"**{item['name']}**")
            st.caption(item['category'])
        
        with col2:
            # Editable quantity (User Story 2)
            new_qty = st.number_input(
                "Quantity",
                value=float(item['quantity']),
                min_value=0.0,
                step=0.5,
                key=f"qty_{item['id']}",
                label_visibility="collapsed"
            )
            st.caption(item['unit'])
            
            # If quantity changed, update it
            if new_qty != item['quantity']:
                if st.button("Update", key=f"update_{item['id']}"):
                    payload = {"quantity": new_qty, "unit": item['unit']}
                    response = requests.put(f"{API_BASE_URL}/inventory-items/<int:ingredient_id>", json = payload)
                    st.success(f"Updated {item['name']}")
                    st.rerun()
        
        with col3:
            if days_left < 0:
                st.write("EXPIRED")
            elif days_left <= 2:
                st.write(f"**{days_left} days left**")
            elif days_left <= 7:
                st.write(f"{days_left} days")
            else:
                st.write("Fresh")
        
        with col4:
            # Remove ingredient (User Story 3)
            if st.button("Remove", key=f"remove_{item['id']}"):
                response = requests.delete(f"{API_BASE_URL}/inventory-items/<int:inventory_id>")
                st.success(f"Removed {item['name']}")
                st.rerun()
        
        st.divider()
        
except Exception as e:
    st.error(f"Error loading ingredients: {str(e)}")

st.write('')
st.write('')

st.write('')
st.write('')

# Quick tips
with st.expander("How to keep your fridge list accurate"):
    st.write("""
    **Adding ingredients:**
    - Add items right after grocery shopping
    - Check expiration dates on packages
    - Estimate dates for produce (usually 5-7 days)
    
    **Updating quantities:**
    - Update after cooking to reflect what you used
    - If you eat half, change quantity to 0.5
    - Keep it current so recipe suggestions work
    
    **Removing ingredients:**
    - Remove when completely used up
    - Remove expired items immediately
    - This helps the app suggest better recipes
    """)