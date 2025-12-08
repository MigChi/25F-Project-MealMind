import streamlit as st
import requests
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"




st.title("💸 Budget-Friendly Recipes")
st.caption("Find recipes that fit under a per-meal cost target.")




col1, col2 = st.columns(2)
with col1:
    max_cost = st.slider("Max cost per recipe ($)", 5, 50, 15, 5)
with col2:
    difficulty = st.selectbox("Difficulty", ["Any", "Easy", "Medium", "Hard"])




if st.button("Search recipes", type="primary", use_container_width=True):
    st.session_state["budget_search"] = {"max_cost": max_cost, "difficulty": difficulty}




if "budget_search" in st.session_state:
    params = {
        # NOTE: backend /recipes currently ignores max_cost
        "status": "Active",
    }
    if st.session_state["budget_search"]["difficulty"] != "Any":
        params["difficulty"] = st.session_state["budget_search"]["difficulty"]


    try:
        resp = requests.get(f"{API_BASE_URL}/recipes", params=params, timeout=8)
        if resp.status_code == 200:
            recipes = resp.json()
            if not recipes:
                st.info("No recipes found with those filters.")
            for rec in recipes:
                name = rec.get("Name") or rec.get("name", "Unnamed")
                rid = rec.get("RecipeId") or rec.get("RecipeID") or rec.get("recipe_id")
                prep = rec.get("PrepTimeMinutes") or rec.get("prep_time_minutes", "N/A")
                diff = rec.get("DifficultyLevel") or rec.get("difficulty_level", "Unknown")
                est_cost = rec.get("EstimatedCost") or rec.get("estimated_cost")


                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"### {name}")
                    st.caption(f"Prep: {prep} min • Difficulty: {diff}")
                    if est_cost is not None:
                        try:
                            st.caption(f"Estimated cost: ${float(est_cost):.2f}")
                        except Exception:
                            pass


                with cols[1]:
                    if st.button("See instructions", key=f"inst_{rid}"):
                        try:
                            dresp = requests.get(f"{API_BASE_URL}/recipes/{rid}", timeout=5)
                            if dresp.status_code == 200:
                                detail = dresp.json()


                                st.write("**Ingredients**")
                                ingredients = detail.get("ingredients", [])
                                if isinstance(ingredients, list) and ingredients:
                                    for ing in ingredients:
                                        name = (
                                            ing.get("IngredientName")
                                            or f"Ingredient #{ing.get('IngredientID')}"
                                        )
                                        qty = ing.get("RequiredQuantity")
                                        unit = ing.get("Unit")
                                        cat = ing.get("CategoryName")


                                        pieces = []
                                        if qty is not None:
                                            pieces.append(str(qty))
                                        if unit:
                                            pieces.append(unit)
                                        amount = " ".join(pieces) if pieces else ""
                                        extra = f" (Category: {cat})" if cat else ""
                                        st.write(f"- {name}: {amount}{extra}")
                                else:
                                    st.caption("No ingredients listed for this recipe.")


                                st.write("**Instructions**")
                                instructions = (
                                    detail.get("Instructions")
                                    or detail.get("instructions")
                                    or "No instructions available."
                                )
                                st.write(instructions)
                            else:
                                st.error(f"Error: {dresp.text}")
                        except Exception as e:
                            st.error(f"Error loading recipe: {e}")
                st.divider()
        else:
            st.error(f"Error: {resp.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")


