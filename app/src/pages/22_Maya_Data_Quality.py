import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(page_title="Maya – Data Quality", page_icon="✅")
SideBarLinks()


API_BASE_URL = "http://api:4000"


st.title("✅ Data Quality Monitor")
st.caption("Spot orphaned records, missing data, and unused ingredients.")


try:
    # Backend route: @analytics_bp.route("/data-quality-reports", methods=["GET"])
    resp = requests.get(f"{API_BASE_URL}/data-quality-reports", timeout=8)
    if resp.status_code == 200:
        report = resp.json()
        orphan_items = report.get("orphan_inventory_items", 0)
        recipes_without_ing = report.get("recipes_without_ingredients", 0)
        unused_ing = report.get("unused_ingredients", 0)


        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Orphan inventory items", orphan_items)
        with col2:
            st.metric("Recipes missing ingredients", recipes_without_ing)
        with col3:
            st.metric("Unused ingredients", unused_ing)


        st.write("---")
        if orphan_items == recipes_without_ing == unused_ing == 0:
            st.success("No data quality issues detected. 🎉")
        else:
            st.warning("There are data quality issues to review.")
            if orphan_items:
                st.write(f"- {orphan_items} inventory rows reference missing ingredients.")
            if recipes_without_ing:
                st.write(f"- {recipes_without_ing} recipes have no ingredients.")
            if unused_ing:
                st.write(f"- {unused_ing} ingredients are never used in any recipe.")
    else:
        st.error(f"Error fetching report: {resp.text}")
except Exception as e:
    st.error(f"Error connecting to API: {e}")