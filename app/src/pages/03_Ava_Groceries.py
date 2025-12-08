import streamlit as st
import requests
from datetime import date, timedelta
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"
user = st.session_state.get("user", {"id": 1})
user_id = user.get("id", 1)


st.title("🛒 Weekly Groceries")
st.caption("Log what you bought so you don’t double-buy or waste it.")




def fetch_categories():
    try:
        resp = requests.get(f"{API_BASE_URL}/categories", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []




def fetch_ingredients():
    try:
        resp = requests.get(f"{API_BASE_URL}/ingredients", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []




# ------------------------------------------------------
# Add groceries  -> POST /inventory-items
# ------------------------------------------------------




st.subheader("Add This Week’s Groceries")


categories = fetch_categories()
ingredients = fetch_ingredients()


ingredient_options = {}
for ing in ingredients:
    label = ing.get("Name") or f"Ingredient #{ing.get('IngredientID')}"
    cat = ing.get("CategoryName")
    if cat:
        label += f" ({cat})"
    ingredient_options[label] = ing


ingredient_labels = list(ingredient_options.keys())
ingredient_labels.insert(0, "➕ New ingredient")


with st.form("groceries_form"):
    col1, col2, col3 = st.columns(3)


    with col1:
        selected_label = st.selectbox("Ingredient", ingredient_labels)
        selected_ing = ingredient_options.get(selected_label)


        name_default = selected_ing.get("Name") if selected_ing else ""
        ingredient_name = (st.text_input("Ingredient name", value=name_default) or "")


        cat_labels = [c.get("CategoryName") for c in categories if c.get("CategoryName")]
        cat_labels = sorted(set(cat_labels))
        cat_labels.insert(0, "➕ New category")


        selected_cat_label = st.selectbox("Category", cat_labels)
        new_category_name = ""
        if selected_cat_label == "➕ New category":
            new_category_name = (st.text_input("New category name", value="") or "")


    with col2:
        quantity = st.number_input("Quantity", min_value=0.1, step=0.5, value=1.0)
        unit = st.text_input("Unit", value="piece")


    with col3:
        days_last = st.number_input("How many days will it last?", min_value=1, value=7)
        purchase_date = st.date_input("Purchase date", value=date.today())


    submitted = st.form_submit_button("Add grocery item")


    if submitted:
        if not ingredient_name.strip():
            st.error("Ingredient name is required.")
        else:
            ingredient_id = None


            # Existing ingredient: maybe update name/category
            if selected_ing:
                ingredient_id = selected_ing.get("IngredientID")
                payload_ing = {}


                if ingredient_name.strip() != (selected_ing.get("Name") or "").strip():
                    payload_ing["name"] = ingredient_name.strip()


                current_cat = selected_ing.get("CategoryName")
                if selected_cat_label == "➕ New category":
                    if new_category_name.strip():
                        payload_ing["category_name"] = new_category_name.strip()
                else:
                    if selected_cat_label and selected_cat_label != current_cat:
                        for c in categories:
                            if c.get("CategoryName") == selected_cat_label:
                                payload_ing["category_id"] = c.get("CategoryID")
                                break


                if payload_ing:
                    try:
                        uresp = requests.put(
                            f"{API_BASE_URL}/ingredients/{ingredient_id}",
                            json=payload_ing,
                            timeout=5,
                        )
                        if uresp.status_code not in (200, 201):
                            st.error(f"Failed to update ingredient: {uresp.text}")
                            st.stop()
                    except Exception as e:
                        st.error(f"Error updating ingredient: {e}")
                        st.stop()


            # New ingredient
            else:
                ing_payload = {"name": ingredient_name.strip()}
                if selected_cat_label == "➕ New category":
                    if new_category_name.strip():
                        ing_payload["category_name"] = new_category_name.strip()
                else:
                    for c in categories:
                        if c.get("CategoryName") == selected_cat_label:
                            ing_payload["category_id"] = c.get("CategoryID")
                            break


                try:
                    iresp = requests.post(
                        f"{API_BASE_URL}/ingredients",
                        json=ing_payload,
                        timeout=5,
                    )
                    if iresp.status_code not in (200, 201):
                        st.error(f"Failed to create ingredient: {iresp.text}")
                        st.stop()
                    ing_data = iresp.json()
                    ingredient_id = (
                        ing_data.get("IngredientID")
                        or ing_data.get("ingredient_id")
                    )
                except Exception as e:
                    st.error(f"Error creating ingredient: {e}")
                    st.stop()


            if ingredient_id is None:
                st.error("Could not determine ingredient ID.")
            else:
                exp_date = purchase_date + timedelta(days=int(days_last))
                payload = {
                    "user_id": user_id,
                    "ingredient_id": int(ingredient_id),
                    "quantity": float(quantity),
                    "unit": unit,
                    "expiration_date": str(exp_date),
                }
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/inventory-items", json=payload, timeout=5
                    )
                    if resp.status_code in (200, 201):
                        msg = "Grocery item added to your inventory."
                        try:
                            data = resp.json()
                            backend_msg = data.get("message")
                            if backend_msg:
                                msg = backend_msg
                        except Exception:
                            pass
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(f"Add failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error talking to API: {e}")


st.write("---")




# ------------------------------------------------------
# Recently added items -> GET /inventory-items
# ------------------------------------------------------




st.subheader("Recently Added Items")


try:
    resp = requests.get(
        f"{API_BASE_URL}/inventory-items",
        params={"user_id": user_id},
        timeout=5,
    )
    if resp.status_code == 200:
        rows = resp.json()
        if not rows:
            st.info("No inventory yet. Start by adding items above.")
        else:
            for row in rows:
                name = row.get("IngredientName") or f"Ingredient #{row.get('IngredientID')}"
                cat = row.get("CategoryName")
                label = name
                if cat:
                    label += f" ({cat})"


                st.write(
                    f"- {label} • "
                    f"{row.get('Quantity')} {row.get('Unit')} • "
                    f"Added {row.get('AddedDate')} • "
                    f"Expires {row.get('ExpirationDate')}"
                )
    else:
        st.error(f"Error: {resp.text}")
except Exception as e:
    st.error(f"Error connecting to API: {e}")




