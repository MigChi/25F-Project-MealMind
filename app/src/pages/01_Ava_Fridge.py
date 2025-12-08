import streamlit as st
import requests
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"
user = st.session_state.get("user", {"id": 1})
user_id = user.get("id", 1)


st.title("🧊 My Fridge")
st.caption("See what you have, what’s expiring, and keep quantities accurate.")




# ---------- Helpers for ingredient + category metadata ----------




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




# ---------- Expiring items (GET /inventory-items/expiring) ----------




st.subheader("Expiration Alerts")


try:
    resp = requests.get(
        f"{API_BASE_URL}/inventory-items/expiring",
        params={"user_id": user_id, "days_ahead": 7},
        timeout=5,
    )
    if resp.status_code == 200:
        expiring = resp.json()
        if not expiring:
            st.success("Nothing expiring in the next 7 days. Nice!")
        else:
            for row in expiring:
                ingredient_id = row.get("IngredientID")
                days_to_expire = row.get("days_to_expire")
                qty = row.get("Quantity")
                unit = row.get("Unit")
                exp_date = row.get("ExpirationDate")
                added_date = row.get("AddedDate")
                name = row.get("IngredientName") or f"Ingredient #{ingredient_id}"
                cat = row.get("CategoryName")


                label = name
                if cat:
                    label += f" ({cat})"


                cols = st.columns([3, 2, 2])
                with cols[0]:
                    if days_to_expire is not None and days_to_expire <= 0:
                        st.error(f"EXPIRED: {label}")
                    else:
                        st.warning(f"Use soon: {label}")
                    st.caption(f"Expires on {exp_date}")
                with cols[1]:
                    st.write(f"{qty} {unit}")
                    st.caption(f"{days_to_expire} days left")
                with cols[2]:
                    if st.button(
                        "Used it",
                        key=f"used_{ingredient_id}_{added_date}_{exp_date}",
                    ):
                        try:
                            del_resp = requests.delete(
                                f"{API_BASE_URL}/inventory-items/{ingredient_id}",
                                params={
                                    "user_id": user_id,
                                    "added_date": added_date,
                                },
                                timeout=5,
                            )
                            if del_resp.status_code == 200:
                                st.success("Removed from fridge")
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {del_resp.text}")
                        except Exception as e:
                            st.error(f"Error deleting item: {e}")
    else:
        st.error(f"Error fetching expiring items: {resp.text}")
except Exception as e:
    st.error(f"Error connecting to API: {e}")


st.write("---")




# ---------- Add new inventory item with ingredient name + category ----------




st.subheader("Add an Ingredient")


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


with st.form("add_inventory"):
    col1, col2 = st.columns(2)


    # Ingredient selection + editing
    with col1:
        selected_label = st.selectbox("Ingredient", ingredient_labels)
        selected_ing = ingredient_options.get(selected_label)


        name_default = selected_ing.get("Name") if selected_ing else ""
        # Guard against None -> always a string
        ingredient_name = (st.text_input("Ingredient name", value=name_default) or "")


        # Category selector
        cat_labels = [c.get("CategoryName") for c in categories if c.get("CategoryName")]
        cat_labels = sorted(set(cat_labels))
        cat_labels.insert(0, "➕ New category")


        selected_cat_label = st.selectbox("Category", cat_labels)
        new_category_name = ""
        if selected_cat_label == "➕ New category":
            new_category_name = (st.text_input("New category name", value="") or "")


    # Quantity / unit / expiration date
    with col2:
        quantity = st.number_input(
            "Quantity", min_value=0.1, step=0.5, value=1.0
        )
        unit = st.text_input("Unit (e.g. cups, g, piece)", value="piece")
        exp_date = st.date_input(
            "Expiration date (optional)", help="Leave as-is if unknown"
        )


    submitted = st.form_submit_button("Add to fridge")


    if submitted:
        if not ingredient_name.strip():
            st.error("Ingredient name is required.")
        else:
            # Determine or create ingredient
            ingredient_id = None


            # Existing ingredient: maybe update name/category
            if selected_ing:
                ingredient_id = selected_ing.get("IngredientID")
                payload_ing = {}


                # detect name change
                if ingredient_name.strip() != (selected_ing.get("Name") or "").strip():
                    payload_ing["name"] = ingredient_name.strip()


                # detect category change
                current_cat = selected_ing.get("CategoryName")
                if selected_cat_label == "➕ New category":
                    if new_category_name.strip():
                        payload_ing["category_name"] = new_category_name.strip()
                else:
                    if selected_cat_label and selected_cat_label != current_cat:
                        # find CategoryID for selected_cat_label
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
                    # find CategoryID by name
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
                        # Use backend message if present, otherwise a generic success
                        msg = "Ingredient added!"
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
                    st.error(f"Error connecting to API: {e}")


st.write("---")




# ---------- All inventory items (GET /inventory-items) + update + delete ----------




st.subheader("All Items in My Fridge")


try:
    resp = requests.get(
        f"{API_BASE_URL}/inventory-items",
        params={"user_id": user_id},
        timeout=5,
    )
    if resp.status_code == 200:
        items = resp.json()
        if not items:
            st.info("Your fridge is empty in the database. Try adding something above.")
        else:
            for row in items:
                ingredient_id = row.get("IngredientID")
                added_date = row.get("AddedDate")
                qty = float(row.get("Quantity", 0))
                unit = row.get("Unit", "")
                exp_date = row.get("ExpirationDate")
                category = row.get("CategoryName", "Uncategorized")
                name = row.get("IngredientName") or f"Ingredient #{ingredient_id}"


                row_key = f"{user_id}-{ingredient_id}-{added_date}"


                cols = st.columns([3, 2, 2, 1])
                with cols[0]:
                    st.write(f"**{name}**")
                    st.caption(f"Category: {category}")
                    st.caption(f"Added on: {added_date}")


                with cols[1]:
                    new_qty = st.number_input(
                        "Quantity",
                        value=qty,
                        min_value=0.0,
                        step=0.5,
                        key=f"qty_{row_key}",
                        label_visibility="collapsed",
                    )
                    st.caption(unit)


                with cols[2]:
                    st.caption(f"Expires: {exp_date}")


                with cols[3]:
                    if st.button("Save", key=f"save_{row_key}"):
                        payload = {"quantity": new_qty}
                        try:
                            uresp = requests.put(
                                f"{API_BASE_URL}/inventory-items/{ingredient_id}",
                                params={
                                    "user_id": user_id,
                                    "added_date": added_date,
                                },
                                json=payload,
                                timeout=5,
                            )
                            if uresp.status_code == 200:
                                st.success("Updated")
                                st.rerun()
                            else:
                                st.error(f"Update failed: {uresp.text}")
                        except Exception as e:
                            st.error(f"Error updating: {e}")
                        st.stop()


                    if st.button("Remove", key=f"del_{row_key}"):
                        try:
                            dresp = requests.delete(
                                f"{API_BASE_URL}/inventory-items/{ingredient_id}",
                                params={
                                    "user_id": user_id,
                                    "added_date": added_date,
                                },
                                timeout=5,
                            )
                            if dresp.status_code == 200:
                                st.success("Removed")
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {dresp.text}")
                        except Exception as e:
                            st.error(f"Error deleting: {e}")
    else:
        st.error(f"Error fetching inventory: {resp.text}")
except Exception as e:
    st.error(f"Error connecting to API: {e}")




