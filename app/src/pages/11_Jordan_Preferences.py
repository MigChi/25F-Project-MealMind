import streamlit as st
import requests
from modules.nav import SideBarLinks


SideBarLinks()
API_BASE_URL = "http://api:4000"
user = st.session_state.get("user", {"id": 3})
user_id = user.get("id", 3)


st.title("🥗 Diet & Budget Preferences")
st.caption("Set up your dietary profile and weekly grocery budget.")


# --- Load existing profiles if they exist ---
diet_profile = None
budget_profile = None
has_diet = False
has_budget = False


# Diet profile (UsersBudgetProfile: UserID, DietTypes, Notes)
try:
    dresp = requests.get(
        f"{API_BASE_URL}/diet-profile",
        params={"user_id": user_id},
        timeout=5,
    )
    if dresp.status_code == 200:
        diet_profile = dresp.json()
        has_diet = True
except Exception:
    pass


# Budget profile (UserBudgetProfile: UserID, WeeklyBudgetAmount, Currency)
try:
    bresp = requests.get(
        f"{API_BASE_URL}/budget-profile",
        params={"user_id": user_id},
        timeout=5,
    )
    if bresp.status_code == 200:
        budget_profile = bresp.json()
        has_budget = True
except Exception:
    pass


# ---- Map DietTypes string -> checkbox booleans ----
diet_types_raw = ""
if diet_profile:
    # DB column name is DietTypes
    diet_types_raw = diet_profile.get("DietTypes") or diet_profile.get("diet_types") or ""
diet_flags = {t.strip() for t in diet_types_raw.split(",") if t.strip()}


st.subheader("Dietary Preferences")


col1, col2 = st.columns(2)
with col1:
    vegetarian = st.checkbox(
        "Vegetarian",
        value="vegetarian" in diet_flags,
    )
    vegan = st.checkbox(
        "Vegan",
        value="vegan" in diet_flags,
    )
    dairy_free = st.checkbox(
        "Dairy free",
        value="dairy_free" in diet_flags,
    )
with col2:
    gluten_free = st.checkbox(
        "Gluten free",
        value="gluten_free" in diet_flags,
    )
    high_protein = st.checkbox(
        "High protein focus",
        value="high_protein" in diet_flags,
    )
    low_carb = st.checkbox(
        "Low carb focus",
        value="low_carb" in diet_flags,
    )


notes = st.text_area(
    "Diet notes",
    value=(diet_profile.get("Notes") if diet_profile else "") or "",
    help="Any additional constraints or preferences.",
)


st.write("---")
st.subheader("Weekly Budget")


default_budget = 80.0
default_currency = "USD"
if budget_profile:
    # DB column names
    wb = budget_profile.get("WeeklyBudgetAmount")
    if wb is not None:
        try:
            default_budget = float(wb)
        except Exception:
            pass
    default_currency = budget_profile.get("Currency", default_currency)


weekly_budget = st.number_input(
    "Weekly grocery budget ($)",
    min_value=10.0,
    max_value=500.0,
    value=float(default_budget),
    step=5.0,
)


currency = st.text_input(
    "Currency",
    value=default_currency,
    max_chars=3,
)


if st.button("Save Preferences", type="primary", use_container_width=True):
    # Build diet_types CSV from the checkboxes
    diet_types_list = []
    if vegetarian:
        diet_types_list.append("vegetarian")
    if vegan:
        diet_types_list.append("vegan")
    if dairy_free:
        diet_types_list.append("dairy_free")
    if gluten_free:
        diet_types_list.append("gluten_free")
    if high_protein:
        diet_types_list.append("high_protein")
    if low_carb:
        diet_types_list.append("low_carb")


    diet_types_str = ",".join(diet_types_list)


    diet_payload = {
        "user_id": user_id,
        "diet_types": diet_types_str,
        "notes": notes,
    }


    budget_payload = {
        "user_id": user_id,
        "weekly_budget_amount": float(weekly_budget),
        "currency": currency,
    }


    try:
        # Diet profile: POST if new, else PUT
        if has_diet:
            dsave = requests.put(
                f"{API_BASE_URL}/diet-profile",
                json=diet_payload,
                timeout=5,
            )
        else:
            dsave = requests.post(
                f"{API_BASE_URL}/diet-profile",
                json=diet_payload,
                timeout=5,
            )


        # Budget profile: POST if new, else PUT
        if has_budget:
            bsave = requests.put(
                f"{API_BASE_URL}/budget-profile",
                json=budget_payload,
                timeout=5,
            )
        else:
            bsave = requests.post(
                f"{API_BASE_URL}/budget-profile",
                json=budget_payload,
                timeout=5,
            )


        if dsave.status_code in (200, 201) and bsave.status_code in (200, 201):
            st.success("Preferences saved successfully.")
        else:
            st.error(f"Diet resp: {dsave.text}\nBudget resp: {bsave.text}")
    except Exception as e:
        st.error(f"Error saving preferences: {e}")




