import streamlit as st
import requests
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"




st.title("🥬 Food Waste Analytics")
st.caption("See which ingredients are wasted most across users.")




col1, col2 = st.columns(2)
with col1:
    time_period_id = st.number_input("TimePeriodID (0 for all)", min_value=0, value=0)
with col2:
    segment_id = st.number_input("DemographicSegmentID (0 for all)", min_value=0, value=0)




if st.button("Load waste statistics", type="primary", use_container_width=True):
    params = {}
    # Back end expects period_id and segment_id
    if time_period_id > 0:
        params["period_id"] = time_period_id
    if segment_id > 0:
        params["segment_id"] = segment_id


    try:
        # Back end route is /waste-statistics (no /analytics prefix)
        resp = requests.get(f"{API_BASE_URL}/waste-statistics", params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if not data:
                st.info("No waste data for this selection.")
                st.stop()


            # Build chart data (top 10 ingredients)
            labels = []
            values = []
            for row in data[:10]:
                ing_label = row.get("IngredientName") or f"ID {row.get('IngredientID')}"
                total = float(row.get("TotalWastedAmount", 0) or 0)
                labels.append(ing_label)
                values.append(total)


            chart_data = {
                "Ingredient": labels,
                "TotalWastedAmount": values,
            }
            st.bar_chart(chart_data, x="Ingredient", y="TotalWastedAmount")


            st.write("---")
            st.subheader("Details")
            for row in data:
                ing_label = row.get("IngredientName") or f"Ingredient {row.get('IngredientID')}"
                total = float(row.get("TotalWastedAmount", 0) or 0)
                rate = row.get("AvgWasteRatePercent")
                st.write(
                    f"- **{ing_label}** – wasted {total:.2f} units "
                    f"(avg rate: {rate}%)"
                )
        else:
            st.error(f"Error: {resp.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")