import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('Recipe Management')
st.write('Add, update, and remove recipes from the central database')

logger.info("Recipe Management page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Admin Dashboard"):
    st.switch_page('pages/20_Admin_Home.py')

st.write('')
st.write('')

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["Add New Recipe", "Update Existing Recipe", "Remove Recipe"])

# User Story 1: Add new recipes
with tab1:
    st.subheader("Add New Recipe to Database")
    st.caption("Add fresh meal options for users")
    
    with st.form("add_recipe"):
        st.write("**Basic Information**")
        col1, col2 = st.columns(2)
        
        with col1:
            recipe_name = st.text_input("Recipe name", placeholder="e.g., Chicken Teriyaki Bowl")
            prep_time = st.number_input("Prep time (minutes)", min_value=5, max_value=180, value=30, step=5)
            difficulty = st.selectbox("Difficulty", ["Very Easy", "Easy", "Medium", "Hard", "Advanced"])
        
        with col2:
            cuisine_type = st.selectbox("Cuisine type", 
                                       ["American", "Italian", "Mexican", "Asian", "Mediterranean", "Other"])
            servings = st.number_input("Servings", min_value=1, max_value=12, value=4)
            cost_per_serving = st.number_input("Cost per serving ($)", min_value=1.0, max_value=50.0, value=6.0, step=0.5)
        
        st.write('')
        st.write("**Ingredients**")
        ingredients = st.text_area("Enter ingredients (one per line)", 
                                   placeholder="1 lb chicken breast\n2 cups rice\n1 cup broccoli\n2 tbsp soy sauce",
                                   height=150)
        
        st.write('')
        st.write("**Instructions**")
        instructions = st.text_area("Enter cooking instructions (step by step)", 
                                   placeholder="1. Cook rice according to package\n2. Cut chicken into pieces\n3. Heat oil in pan...",
                                   height=200)
        
        st.write('')
        st.write("**Nutrition Information**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            calories = st.number_input("Calories", min_value=0, value=450)
        with col2:
            protein = st.number_input("Protein (g)", min_value=0, value=35)
        with col3:
            carbs = st.number_input("Carbs (g)", min_value=0, value=45)
        with col4:
            fat = st.number_input("Fat (g)", min_value=0, value=12)
        
        st.write('')
        st.write("**Tags and Categories**")
        tags = st.multiselect("Recipe tags", 
                             ["High Protein", "Low Carb", "Vegetarian", "Vegan", "Gluten Free", 
                              "Dairy Free", "Budget Friendly", "Quick", "Meal Prep"])
        
        st.write('')
        submitted = st.form_submit_button("Add Recipe to Database", use_container_width=True)
        
        if submitted:
            if recipe_name and ingredients and instructions:
                payload = {
                    "name": name,
                    "prep_time_minutes": prep_time,
                    "difficulty_level": difficulty
                    "instructions": instructions.split('\n')
                }
                response = requests.post(f"{API_BASE_URL}/recipes", json=payload)
                
                st.success(f"Recipe '{recipe_name}' added successfully!")
                st.balloons()
            else:
                st.error("Please fill in recipe name, ingredients, and instructions")

# User Story 2: Update existing recipes
with tab2:
    st.subheader("Update Existing Recipe")
    st.caption("Keep recipe information accurate and up-to-date")
    
    # Search for recipe to update
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_recipe = st.text_input("Search recipe by name or ID", placeholder="Enter recipe name or ID")
    
    with col2:
        if st.button("Search", use_container_width=True):
            st.session_state['search_query'] = search_recipe
    
    st.write('')
    
    # Display search results
    if st.session_state.get('search_query'):
        try:
            response = requests.get(f"{API_BASE_URL}/recipes", params={"category": category})
            results = response.json()

            results = [
                {"recipe_id": 15, "name": "Chicken Teriyaki Bowl", "status": "active", "last_updated": "2024-11-20"},
                {"recipe_id": 23, "name": "Chicken Stir Fry", "status": "active", "last_updated": "2024-10-15"}
            ]
            
            st.write(f"Found {len(results)} recipes:")
            
            for recipe in results:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{recipe['name']}**")
                    st.caption(f"ID: {recipe['recipe_id']} | Status: {recipe['status']}")
                
                with col2:
                    st.caption(f"Updated: {recipe['last_updated']}")
                
                with col3:
                    if st.button("Edit", key=f"edit_{recipe['recipe_id']}"):
                        st.session_state['editing_recipe'] = recipe['recipe_id']
                        st.rerun()
        
        except Exception as e:
            st.error(f"Error searching recipes: {str(e)}")
    
    st.write('')
    
    # Edit form if recipe selected
    if st.session_state.get('editing_recipe'):
        category_id = st.session_state['editing_recipe']
        
        st.write(f"**Editing Recipe ID: {recipe_id}**")
        
        response = requests.get(f"{API_BASE_URL}/recipes/{category_id}")
        recipe_data = response.json()
        
        
        with st.form("update_recipe"):
            st.write("**Update Recipe Information**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Recipe name", value=current_name)
                new_prep_time = st.number_input("Prep time (minutes)", value=current_prep_time, min_value=5)
                new_difficulty = st.selectbox("Difficulty", 
                                             ["Very Easy", "Easy", "Medium", "Hard", "Advanced"],
                                             index=1)
            
            with col2:
                new_servings = st.number_input("Servings", value=4, min_value=1)
                new_cost = st.number_input("Cost per serving ($)", value=6.5, min_value=1.0, step=0.5)
            
            new_ingredients = st.text_area("Ingredients", 
                                          value="1 lb chicken breast\n2 cups rice\n1 cup teriyaki sauce",
                                          height=100)
            
            new_instructions = st.text_area("Instructions",
                                           value="1. Cook rice\n2. Grill chicken\n3. Add sauce",
                                           height=150)
            
            st.write('')
            col1, col2 = st.columns(2)
            
            with col1:
                update_submitted = st.form_submit_button("Update Recipe", use_container_width=True)
            
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if update_submitted:
                payload = {
                    "name": new_name,
                    "prep_time": new_prep_time,
                    "difficulty": new_difficulty,
                    "instructions": new_instructions
                }
                response = requests.put(f"{API_BASE_URL}/recipes/{recipe_id}", json=payload)

                payload = {

                }
                
                st.success(f"Recipe '{new_name}' updated successfully!")
                st.session_state['editing_recipe'] = None
                st.rerun()
            
            if cancel:
                st.session_state['editing_recipe'] = None
                st.rerun()

# User Story 3: Remove outdated recipes
with tab3:
    st.subheader("Remove or Deactivate Recipes")
    st.caption("Remove broken or invalid content from the database")
    
    st.write("**Why remove a recipe?**")
    st.write("- Outdated or incorrect information")
    st.write("- Broken instructions or missing ingredients")
    st.write("- User complaints or low ratings")
    st.write("- Duplicate entries")
    
    st.write('')
    
    # Filter recipes for removal
    col1, col2 = st.columns(2)
    
    with col1:
        filter_by = st.selectbox("Show recipes", 
                                ["All recipes", "Flagged by users", "Low rated", "Not used in 90 days"])
    
    with col2:
        sort_by = st.selectbox("Sort by", ["Name", "Date added", "Last updated", "Rating"])
    
    st.write('')
    
    try:
        response = requests.get(f"{API_BASE_URL}/recipes", params={"category": category})
        recipes = response.json()
        
        st.write(f"**Recipes for Review ({len(recipes_to_review)})**")
        
        for recipe in recipes_to_review:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{recipe['name']}**")
                    st.caption(f"ID: {recipe['recipe_id']} | Status: {recipe['status']}")
                
                with col2:
                    st.write(f"Issue: {recipe['reason']}")
                    st.caption(f"Last used: {recipe['last_used']}")
                
                with col3:
                    # User Story 3: Remove recipe (DELETE)
                    if st.button("Remove", key=f"remove_{recipe['recipe_id']}", type="primary"):
                        st.session_state[f'confirm_remove_{recipe["recipe_id"]}'] = True
                    
                    if st.button("View", key=f"view_{recipe['recipe_id']}"):
                        st.info(f"Viewing details for {recipe['name']}")
                
                # Confirmation dialog
                if st.session_state.get(f'confirm_remove_{recipe["recipe_id"]}'):
                    st.warning(f"Are you sure you want to remove '{recipe['name']}'? This cannot be undone.")
                    
                    col_a, col_b, col_c = st.columns([1, 1, 2])
                    
                    with col_a:
                        if st.button("Yes, Remove", key=f"confirm_yes_{recipe['recipe_id']}"):
                            response = requests.delete(f"{API_BASE_URL}/recipes/<int: recipe_id")
                            
                            st.success(f"Recipe '{recipe['name']}' removed from database")
                            st.session_state[f'confirm_remove_{recipe["recipe_id"]}'] = False
                            st.rerun()
                    
                    with col_b:
                        if st.button("Cancel", key=f"confirm_no_{recipe['recipe_id']}"):
                            st.session_state[f'confirm_remove_{recipe["recipe_id"]}'] = False
                            st.rerun()
                
                st.divider()
    
    except Exception as e:
        st.error(f"Error loading recipes: {str(e)}")

st.write('')
st.write('')

# Bulk operations
with st.expander("Bulk Recipe Operations"):
    st.write("**Advanced Admin Actions**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export All Recipes (CSV)"):
            st.info("Exporting recipes to CSV...")
        
        if st.button("Run Recipe Validation Check"):
            st.info("Checking all recipes for data issues...")
    
    with col2:
        if st.button("Deactivate All Flagged Recipes"):
            st.warning("This will deactivate all flagged recipes")
        
        if st.button("Regenerate Recipe Search Index"):
            st.info("Rebuilding search index...")