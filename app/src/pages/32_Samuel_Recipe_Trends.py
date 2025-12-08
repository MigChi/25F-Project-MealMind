import streamlit as st
import requests
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"




st.title("📈 Recipe Trends")
st.caption("Track popularity of recipes (and categories) over time.")




# Optional filters for time period and demographic segment
col1, col2 = st.columns(2)
with col1:
    time_period_id = st.number_input(
        "TimePeriodID (0 for all)", min_value=0, value=0
    )
with col2:
    segment_id = st.number_input(
        "DemographicSegmentID (0 for all)", min_value=0, value=0
    )




if st.button("Load recipe usage statistics", type="primary", use_container_width=True):
    params = {}
    if time_period_id > 0:
        params["period_id"] = time_period_id
    if segment_id > 0:
        params["segment_id"] = segment_id


    try:
        # Backend route is /recipe-usage-statistics (no /analytics prefix)
        resp = requests.get(
            f"{API_BASE_URL}/recipe-usage-statistics", params=params, timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            if not data:
                st.info("No usage data available for this selection.")
                st.stop()


            # Aggregate by recipe name using TotalUsageCount
            recipes = []
            counts = []
            for row in data:
                name = row.get("Name") or f"Recipe {row.get('RecipeID')}"
                total_usage = float(row.get("TotalUsageCount", 0) or 0)
                recipes.append(name)
                counts.append(total_usage)


            st.subheader("Usage by Recipe (Top)")
            chart_data = {
                "Recipe": recipes,
                "TotalUsageCount": counts,
            }
            # Use recipe names as x-axis labels
            st.bar_chart(chart_data, x="Recipe", y="TotalUsageCount")


            st.write("---")
            st.subheader("Raw rows")
            for row in data[:20]:
                st.write(row)
        else:
            st.error(f"Error: {resp.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")