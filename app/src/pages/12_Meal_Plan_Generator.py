import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('Weekly Meal Plan Generator')
st.write('Automatically generate a simple meal plan - no decision fatigue')

logger.info("Meal Plan Generator page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Dashboard"):
    st.switch_page('pages/10_USAID_Worker_Home.py')

st.write('')
st.write('')

# User Story 2: Update dietary preferences
st.subheader("Your Meal Preferences")
st.caption("Update these so your meal plans match your health goals")

with st.form("update_preferences"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Dietary Goals**")
        high_protein = st.checkbox("High Protein", value=True)
        low_carb = st.checkbox("Low Carb", value=False)
        vegetarian = st.checkbox("Vegetarian", value=False)
        dairy_free = st.checkbox("Dairy Free", value=False)
    
    with col2:
        st.write("**Nutrition Targets**")
        daily_calories = st.number_input("Target calories/day", min_value=1200, max_value=3000, value=2000, step=100)
        protein_goal = st.number_input("Protein goal (g/day)", min_value=50, max_value=200, value=120, step=10)
        
    cooking_skill = st.select_slider("Cooking difficulty", 
                                     options=["Very Easy", "Easy", "Medium", "Advanced"],
                                     value="Easy")
    
    max_prep_time = st.slider("Max prep time per meal (minutes)", 10, 60, 30, step=5)
    
    update_prefs = st.form_submit_button("Update My Preferences", use_container_width=True)
    
    if update_prefs:
        payload = {
            "user_id": st.session_state.get('user_id',2)
        }
        response=requests.put(f"{API_BASE_URL}/profile/diet-profile", json = payload)
        st.success("Preferences updated! Generate a new meal plan to see changes.")

st.write('')
st.write('')

# User Story 5: Generate weekly meal plan
st.subheader("Generate Your Meal Plan")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Plan starting from")
    meals_per_day = st.selectbox("Meals per day", [1, 2, 3], index=2)

with col2:
    include_budget = st.checkbox("Stay within weekly budget", value=True)
    if include_budget:
        weekly_budget = st.number_input("Weekly budget ($)", min_value=20, max_value=200, value=80, step=10)

if st.button("Generate My Weekly Meal Plan", type="primary", use_container_width=True):
    with st.spinner("Generating your personalized meal plan..."):
        payload = {
            "user_id": st.session_state.get('user_id',2),
            "diet_types":
        }
        response = requests.post(f"{API_BASE_URL}/diet-profile", json = payload)
        plan = response.json()

        st.success("Meal plan generated!")
        st.balloons()
        st.session_state['has_plan'] = True
        st.rerun()

st.write('')
st.write('')

# Display generated meal plan
if st.session_state.get('has_plan', False):
    st.subheader("This Week's Meal Plan")
    st.caption("Simple meals that match your preferences and budget")
    
    # MOCK PLAN DATA
    days = [
        {"day": "Monday", "meals": ["Greek Yogurt Bowl", "Chicken Stir Fry", "Baked Salmon"]},
        {"day": "Tuesday", "meals": ["Protein Smoothie", "Turkey Sandwich", "Pasta Primavera"]},
        {"day": "Wednesday", "meals": ["Oatmeal with Berries", "Chicken Salad", "Beef Tacos"]},
        {"day": "Thursday", "meals": ["Egg White Omelette", "Leftover Pasta", "Grilled Chicken"]},
        {"day": "Friday", "meals": ["Greek Yogurt", "Tuna Salad", "Stir Fry Leftovers"]},
        {"day": "Saturday", "meals": ["Pancakes", "Burger Bowl", "Salmon with Rice"]},
        {"day": "Sunday", "meals": ["Breakfast Burrito", "Meal Prep", "Simple Pasta"]}
    ]
    
    total_cost = 0
    
    for day_plan in days:
        with st.expander(f"**{day_plan['day']}**", expanded=(day_plan['day'] == "Monday")):
            for i, meal in enumerate(day_plan['meals']):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    meal_time = ["Breakfast", "Lunch", "Dinner"][i]
                    st.write(f"**{meal_time}:** {meal}")
                
                with col2:
                    meal_cost = 6.50 if i == 2 else 4.00  # Mock cost
                    st.write(f"${meal_cost:.2f}")
                    total_cost += meal_cost
                
                with col3:
                    # User Story 6: View step-by-step instructions
                    if st.button("View Recipe", key=f"recipe_{day_plan['day']}_{i}"):
                        st.session_state['selected_meal'] = meal
                        st.switch_page('pages/13_Budget_Meal_Finder.py')
    
    st.write('')
    st.info(f"**Total weekly cost:** ${total_cost:.2f} / ${weekly_budget if include_budget else 'No limit'}")
    
    if include_budget and total_cost > weekly_budget:
        st.warning("Plan exceeds budget. Adjust preferences or increase budget.")
    elif include_budget:
        st.success("Plan is within your budget!")
    
    st.write('')
    
    # Save or regenerate
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save This Plan", use_container_width=True):
            st.success("Meal plan saved!")
    
    with col2:
        if st.button("Generate New Plan", use_container_width=True):
            st.session_state['has_plan'] = False
            st.rerun()

st.write('')
st.write('')

# Shopping list for the plan
if st.session_state.get('has_plan', False):
    st.subheader("Shopping List for This Plan")
    st.caption("Items you need to buy for the week")
    
    st.write("**Proteins:**")
    st.write("- Chicken breast (3 lbs)")
    st.write("- Salmon fillet (1.5 lbs)")
    st.write("- Ground beef (1 lb)")
    
    st.write("**Vegetables:**")
    st.write("- Bell peppers (4)")
    st.write("- Broccoli (2 heads)")
    st.write("- Lettuce (1 bag)")
    
    st.write("**Pantry:**")
    st.write("- Rice (2 lbs)")
    st.write("- Pasta (2 boxes)")
    
    if st.button("Download Shopping List"):
        st.info("Shopping list downloaded!")