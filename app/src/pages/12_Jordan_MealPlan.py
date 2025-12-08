import streamlit as st
import requests
from datetime import date
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"
user = st.session_state.get("user", {"id": 3})
user_id = user.get("id", 3)




st.title("📅 Weekly Meal Plan")
st.caption("Generate a weekly meal plan that respects your diet and budget.")




st.subheader("Plan Settings")




col1, col2 = st.columns(2)
with col1:
    start = st.date_input("Week starting", value=date.today())
    meals_per_day = st.selectbox("Meals per day", [1, 2, 3], index=2)
with col2:
    respect_budget = st.checkbox("Respect my weekly budget", value=True)
    include_leftovers = st.checkbox("Include leftovers for some meals", value=True)




if st.button("Generate Meal Plan", type="primary", use_container_width=True):
    payload = {
        "user_id": user_id,
        "start_date": str(start),
        "meals_per_day": meals_per_day,
        "respect_budget": respect_budget,
        "include_leftovers": include_leftovers,
    }
    try:
        resp = requests.post(f"{API_BASE_URL}/meal-plans", json=payload, timeout=8)
        if resp.status_code in (200, 201):
            plan = resp.json()
            st.session_state["current_plan"] = plan
            st.success("Meal plan generated and saved.")
        else:
            st.error(f"Error: {resp.text}")
    except Exception as e:
        st.error(f"Error calling API: {e}")




st.write("---")
st.subheader("My Saved Meal Plans")




try:
    list_resp = requests.get(
        f"{API_BASE_URL}/meal-plans", params={"user_id": user_id}, timeout=5
    )
    if list_resp.status_code == 200:
        plans = list_resp.json()
        if not plans:
            st.info("No saved plans yet. Generate one above.")
        else:
            plan_options = {
                f"Plan #{p.get('MealPlanID')} starting {p.get('StartDate')}": p
                for p in plans
            }
            selected_label = st.selectbox(
                "Select a plan", list(plan_options.keys())
            )
            selected_plan = plan_options[selected_label]


            st.write(f"### {selected_label}")
            plan_id = selected_plan.get("MealPlanID")


            # Load full details
            detail_resp = requests.get(
                f"{API_BASE_URL}/meal-plans/{plan_id}",
                timeout=5,
            )
            if detail_resp.status_code == 200:
                details = detail_resp.json()
                st.caption(
                    f"From {details.get('StartDate')} to {details.get('EndDate')} "
                    f"• Saved: {bool(details.get('IsSaved'))}"
                )


                entries = details.get("entries", [])
                if not entries:
                    st.caption("This plan has no entries yet.")
                else:
                    st.write("**Meals in this plan:**")
                    for entry in entries:
                        st.write(
                            f"- {entry.get('Date')} • {entry.get('MealType')}: "
                            f"{entry.get('RecipeName') or 'No recipe assigned'}"
                        )


                st.write("")
                if st.button(
                    "Delete this meal plan",
                    type="primary",
                    use_container_width=True,
                    key=f"delete_plan_{plan_id}",
                ):
                    try:
                        dresp = requests.delete(
                            f"{API_BASE_URL}/meal-plans/{plan_id}",
                            timeout=5,
                        )
                        if dresp.status_code == 200:
                            st.success("Meal plan deleted.")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {dresp.text}")
                    except Exception as e:
                        st.error(f"Error deleting plan: {e}")
            else:
                st.error(f"Error loading details: {detail_resp.text}")
    else:
        st.error(f"Error fetching meal plans: {list_resp.text}")
except Exception as e:
    st.error(f"Error: {e}")


