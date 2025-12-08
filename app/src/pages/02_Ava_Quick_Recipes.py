import streamlit as st
import requests
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"
user = st.session_state.get("user", {"id": 1})
user_id = user.get("id", 1)




st.title("⚡ Quick Recipes from My Fridge")
st.caption("Find recipes you can make right now with what you already have in your inventory.")




col1, col2 = st.columns(2)
with col1:
    max_prep = st.slider("Max prep time (minutes)", 5, 60, 30, 5)
with col2:
    limit = st.slider("Max number of recipes to show", 5, 30, 10, 5)




if st.button("Find recipes", type="primary", use_container_width=True):
    st.session_state["run_suggestions"] = True




st.write("---")




def render_ingredients_list(ingredients):
    """Pretty-print a list of ingredient rows from /recipes/{id}."""
    if not ingredients:
        st.caption("No ingredients listed for this recipe.")
        return


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
        st.write(f"- {name}{f': {amount}' if amount else ''}{extra}")




def show_recipe_details(recipe_id):
    """Fetch and display full recipe details (ingredients + instructions)."""
    try:
        dresp = requests.get(f"{API_BASE_URL}/recipes/{recipe_id}", timeout=5)
        if dresp.status_code == 200:
            details = dresp.json()


            st.write("**Ingredients**")
            ingredients = details.get("ingredients", [])
            render_ingredients_list(ingredients)


            st.write("**Instructions**")
            instructions = (
                details.get("Instructions")
                or details.get("instructions")
                or "No instructions available."
            )
            st.write(instructions)
        else:
            st.error(f"Failed to load details: {dresp.text}")
    except Exception as e:
        st.error(f"Error loading details: {e}")




if st.session_state.get("run_suggestions"):
    # --- Call the suggestions API ---
    try:
        resp = requests.get(
            f"{API_BASE_URL}/recipes/suggestions",
            params={
                "user_id": user_id,
                "max_prep_time": max_prep,  # matches backend
                "limit": limit,
            },
            timeout=8,
        )
    except Exception as e:
        st.error(f"Error contacting API: {e}")
        resp = None


    if resp is not None:
        if resp.status_code != 200:
            st.error(f"Suggestions error ({resp.status_code}): {resp.text}")
        else:
            recipes = resp.json()


            if not recipes:
                # Nothing came back – give helpful guidance instead of silence.
                st.info("No matching recipes for your current inventory and prep time.")


                # Check Ava's inventory so we can tell *why*.
                try:
                    inv_resp = requests.get(
                        f"{API_BASE_URL}/inventory-items",
                        params={"user_id": user_id},
                        timeout=5,
                    )
                    if inv_resp.status_code == 200:
                        inventory = inv_resp.json()
                        if not inventory:
                            st.warning(
                                "Your inventory is empty for this user.\n\n"
                                "Add some items in **My Fridge** or **Weekly Groceries** first, "
                                "then try finding quick recipes again."
                            )
                        else:
                            st.caption(
                                f"You currently have {len(inventory)} inventory items, "
                                f"but none of the recipes in this demo use those ingredients "
                                f"with prep time ≤ {max_prep} minutes."
                            )
                    else:
                        st.caption("Could not check inventory details (non-200 response).")
                except Exception:
                    st.caption("Could not check inventory details due to a connection error.")


                # Optional fallback: show a few active recipes so the page never feels empty.
                st.write("---")
                st.subheader("Some example recipes you can browse")
                try:
                    fallback_resp = requests.get(
                        f"{API_BASE_URL}/recipes",
                        params={"status": "Active"},
                        timeout=8,
                    )
                    if fallback_resp.status_code == 200:
                        fallback = fallback_resp.json()[:5]
                        if not fallback:
                            st.caption("No recipes in the system yet.")
                        else:
                            for rec in fallback:
                                rid = (
                                    rec.get("RecipeId")
                                    or rec.get("RecipeID")
                                    or rec.get("recipe_id")
                                )
                                name = rec.get("Name") or rec.get("name", "Unnamed recipe")
                                prep = (
                                    rec.get("PrepTimeMinutes")
                                    or rec.get("prep_time_minutes", "N/A")
                                )
                                diff = (
                                    rec.get("DifficultyLevel")
                                    or rec.get("difficulty_level", "Unknown")
                                )


                                cols = st.columns([3, 1])
                                with cols[0]:
                                    st.write(f"**{name}**")
                                    st.caption(f"Prep: {prep} min • Difficulty: {diff}")
                                with cols[1]:
                                    if st.button("View details", key=f"fb_{rid}"):
                                        show_recipe_details(rid)
                    else:
                        st.caption("Could not load example recipes.")
                except Exception:
                    st.caption("Could not load example recipes due to a connection error.")


            else:
                # We *do* have suggestions — show them.
                for rec in recipes:
                    rid = (
                        rec.get("RecipeId")
                        or rec.get("RecipeID")
                        or rec.get("recipe_id")
                    )
                    name = rec.get("Name") or rec.get("name", "Unnamed recipe")
                    prep = (
                        rec.get("PrepTimeMinutes")
                        or rec.get("prep_time_minutes", "N/A")
                    )
                    diff = (
                        rec.get("DifficultyLevel")
                        or rec.get("difficulty_level", "Unknown")
                    )
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
                        if st.button("View Details", key=f"view_{rid}"):
                            show_recipe_details(rid)


                        # Favorites use the existing API: POST /favorite-recipes
                        if st.button("Favorite", key=f"fav_{rid}"):
                            try:
                                fresp = requests.post(
                                    f"{API_BASE_URL}/favorite-recipes",
                                    json={"user_id": user_id, "recipe_id": rid},
                                    timeout=5,
                                )
                                if fresp.status_code in (200, 201):
                                    st.success("Added to favorites!")
                                else:
                                    st.error(f"Favorite failed: {fresp.text}")
                            except Exception as e:
                                st.error(f"Error favoriting: {e}")


                    st.divider()




st.write("---")
st.subheader("My Favorite Recipes")




try:
    fresp = requests.get(
        f"{API_BASE_URL}/favorite-recipes",
        params={"user_id": user_id},
        timeout=5,
    )
    if fresp.status_code == 200:
        favs = fresp.json()
        if not favs:
            st.caption("No favorites yet.")
        for fav in favs:
            fname = fav.get("Name") or fav.get("name", "Unnamed")
            rid = fav.get("RecipeID") or fav.get("recipe_id")
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"- {fname}")
            with cols[1]:
                if st.button("Remove", key=f"unfav_{rid}"):
                    try:
                        d = requests.delete(
                            f"{API_BASE_URL}/favorite-recipes/{rid}",
                            params={"user_id": user_id},
                            timeout=5,
                        )
                        if d.status_code == 200:
                            st.success("Removed from favorites")
                            st.rerun()
                        else:
                            st.error(f"Failed: {d.text}")
                    except Exception as e:
                        st.error(f"Error removing favorite: {e}")
    else:
        st.error(f"Favorites error: {fresp.text}")
except Exception as e:
    st.error(f"Error connecting to API: {e}")


