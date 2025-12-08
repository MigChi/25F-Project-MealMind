import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(page_title="Maya – Recipe Management", page_icon="📖")
SideBarLinks()


API_BASE_URL = "http://api:4000"


st.title("📖 Recipe Management")
st.caption("Add, update, and remove recipes from the central database.")


tab_add, tab_update, tab_delete = st.tabs(["Add Recipe", "Update Recipe", "Remove Recipe"])


# --- Add recipe (POST /recipes) ---
with tab_add:
    st.subheader("Add New Recipe")
    with st.form("add_recipe"):
        name = st.text_input("Recipe name")
        prep_time = st.number_input(
            "Prep time (minutes)", min_value=5, max_value=240, value=30
        )
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        instructions = st.text_area("Instructions", height=150)
        submit = st.form_submit_button("Create recipe")


        if submit:
            if not name or not instructions:
                st.error("Name and instructions are required.")
            else:
                payload = {
                    "name": name,
                    "prep_time_minutes": prep_time,
                    "difficulty_level": difficulty,
                    "instructions": instructions,
                    "status": "Active",
                }
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/recipes", json=payload, timeout=8
                    )
                    if resp.status_code in (200, 201):
                        st.success("Recipe created.")
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {e}")


# --- Update recipe (PUT /recipes/<id>) ---
with tab_update:
    st.subheader("Update Existing Recipe")


    search = st.text_input("Filter recipes by name (client-side filter)")
    try:
        # Only show active recipes for editing by default
        list_resp = requests.get(
            f"{API_BASE_URL}/recipes",
            params={"status": "Active"},
            timeout=8,
        )
        if list_resp.status_code == 200:
            recipes = list_resp.json()


            # Optional client-side name filter
            if search:
                recipes = [
                    r
                    for r in recipes
                    if search.lower()
                    in (r.get("Name") or r.get("name", "")).lower()
                ]


            if not recipes:
                st.info("No recipes match this filter.")
            else:
                names = [
                    f"{r.get('RecipeId') or r.get('recipe_id')} – {r.get('Name') or r.get('name')}"
                    for r in recipes
                ]
                choice = st.selectbox("Select recipe to edit", names)
                idx = names.index(choice)
                rec = recipes[idx]
                rid = rec.get("RecipeId") or rec.get("recipe_id")


                cur_name = rec.get("Name") or rec.get("name", "")
                cur_prep = rec.get("PrepTimeMinutes") or rec.get(
                    "prep_time_minutes", 30
                )
                cur_diff = rec.get("DifficultyLevel") or rec.get(
                    "difficulty_level", "Easy"
                )


                with st.form("edit_recipe"):
                    new_name = st.text_input("Recipe name", value=cur_name)
                    new_prep = st.number_input(
                        "Prep time (minutes)",
                        value=int(cur_prep),
                        min_value=5,
                    )
                    new_diff = st.selectbox(
                        "Difficulty",
                        ["Easy", "Medium", "Hard"],
                        index=(
                            ["Easy", "Medium", "Hard"].index(cur_diff)
                            if cur_diff in ["Easy", "Medium", "Hard"]
                            else 0
                        ),
                    )
                    new_instructions = st.text_area(
                        "Instructions (leave blank to keep current)",
                        value="",
                        height=150,
                    )
                    save = st.form_submit_button("Save changes")


                    if save:
                        payload = {
                            "name": new_name,
                            "prep_time_minutes": new_prep,
                            "difficulty_level": new_diff,
                        }
                        if new_instructions.strip():
                            payload["instructions"] = new_instructions


                        try:
                            uresp = requests.put(
                                f"{API_BASE_URL}/recipes/{rid}",
                                json=payload,
                                timeout=8,
                            )
                            if uresp.status_code == 200:
                                st.success("Recipe updated.")
                            else:
                                st.error(f"Update failed: {uresp.text}")
                        except Exception as e:
                            st.error(f"Error updating recipe: {e}")
        else:
            st.error(f"Error fetching recipes: {list_resp.text}")
    except Exception as e:
        st.error(f"Error: {e}")


# --- Remove recipe (DELETE /recipes/<id>) ---
with tab_delete:
    st.subheader("Remove Recipe")


    try:
        # Again, show only active recipes for deletion
        list_resp = requests.get(
            f"{API_BASE_URL}/recipes",
            params={"status": "Active"},
            timeout=8,
        )
        if list_resp.status_code == 200:
            recipes = list_resp.json()
            if not recipes:
                st.info("No recipes to remove.")
            else:
                names = [
                    f"{r.get('RecipeId') or r.get('recipe_id')} – {r.get('Name') or r.get('name')}"
                    for r in recipes
                ]
                choice = st.selectbox(
                    "Select recipe to remove",
                    names,
                    key="delete_choice",
                )
                idx = names.index(choice)
                rec = recipes[idx]
                rid = rec.get("RecipeId") or rec.get("recipe_id")


                st.warning(
                    "This will mark the recipe as inactive (soft delete) and hide it from normal views."
                )


                if st.button("Delete this recipe", type="primary"):
                    try:
                        dresp = requests.delete(
                            f"{API_BASE_URL}/recipes/{rid}", timeout=5
                        )
                        if dresp.status_code == 200:
                            st.success("Recipe removed.")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {dresp.text}")
                    except Exception as e:
                        st.error(f"Error deleting recipe: {e}")
        else:
            st.error(f"Error: {list_resp.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")


