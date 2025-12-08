import streamlit as st
import requests
from modules.nav import SideBarLinks




SideBarLinks()
API_BASE_URL = "http://api:4000"




st.title("👥 User Behavior Insights")
st.caption("Compare behavior between demographic segments.")




st.subheader("Available Demographic Segments")


segments = []
try:
    # Backend route is /demographic-segments (no /analytics prefix)
    resp = requests.get(f"{API_BASE_URL}/demographic-segments", timeout=8)
    if resp.status_code == 200:
        segments = resp.json()
        if segments:
            options = {
                f"{s.get('SegmentID')} – {s.get('Name')}": s for s in segments
            }
            label = st.selectbox("Choose a segment", list(options.keys()))
            seg = options[label]


            st.write(f"**Age range:** {seg.get('AgeMin')}–{seg.get('AgeMax')}")
            st.write(f"**Region:** {seg.get('Region')}")
        else:
            st.info("No demographic segments defined yet.")
    else:
        st.error(f"Error: {resp.text}")
except Exception as e:
    st.error(f"Error connecting to API: {e}")


st.write("---")
st.subheader("Generate Combined Analytics Report")


# Time period filter for all analytics endpoints
period_id = st.number_input(
    "TimePeriodID (0 for all)", min_value=0, value=0, step=1
)


if segments:
    selected_ids = st.multiselect(
        "Include segments in comparison",
        [s.get("SegmentID") for s in segments],
        format_func=lambda i: next(
            (s["Name"] for s in segments if s["SegmentID"] == i), str(i)
        ),
    )
else:
    selected_ids = []




if st.button("Generate report", type="primary", use_container_width=True):
    # --- Overall summary (uses GET /analytics/reports) ---
    summary_params = {}
    if period_id > 0:
        summary_params["period_id"] = period_id


    try:
        summary_resp = requests.get(
            f"{API_BASE_URL}/analytics/reports",
            params=summary_params,
            timeout=10,
        )
        if summary_resp.status_code == 200:
            overall = summary_resp.json()
            st.subheader("Overall Summary (All Segments)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Waste", overall.get("total_waste", 0))
            c2.metric("Total Recipe Usage", overall.get("total_recipe_usage", 0))
            c3.metric("Total Unique Users", overall.get("total_unique_users", 0))
        else:
            st.error(f"Summary error: {summary_resp.text}")
    except Exception as e:
        st.error(f"Error calling summary API: {e}")


    st.write("---")
    st.subheader("Breakdown by Segment")


    if not selected_ids:
        st.caption("Select one or more segments above to see per-segment behavior.")
    else:
        for seg_id in selected_ids:
            seg = next((s for s in segments if s["SegmentID"] == seg_id), None)
            if not seg:
                continue


            st.markdown(f"### Segment {seg_id} – {seg.get('Name')}")


            base_params = {}
            if period_id > 0:
                base_params["period_id"] = period_id
            base_params["segment_id"] = seg_id


            # --- Waste statistics for this segment (GET /waste-statistics) ---
            total_waste = 0.0
            try:
                wresp = requests.get(
                    f"{API_BASE_URL}/waste-statistics",
                    params=base_params,
                    timeout=10,
                )
                if wresp.status_code == 200:
                    wdata = wresp.json()
                    total_waste = sum(
                        float(row.get("TotalWastedAmount", 0) or 0)
                        for row in wdata
                    )
                else:
                    st.error(
                        f"Waste statistics error for segment {seg_id}: {wresp.text}"
                    )
            except Exception as e:
                st.error(f"Error loading waste stats for segment {seg_id}: {e}")


            # --- Recipe usage statistics for this segment (GET /recipe-usage-statistics) ---
            total_usage = 0
            total_unique_users = 0
            try:
                uresp = requests.get(
                    f"{API_BASE_URL}/recipe-usage-statistics",
                    params=base_params,
                    timeout=10,
                )
                if uresp.status_code == 200:
                    udata = uresp.json()
                    total_usage = sum(
                        int(row.get("TotalUsageCount", 0) or 0)
                        for row in udata
                    )
                    total_unique_users = sum(
                        int(row.get("TotalUniqueUsers", 0) or 0)
                        for row in udata
                    )
                else:
                    st.error(
                        f"Usage statistics error for segment {seg_id}: {uresp.text}"
                    )
            except Exception as e:
                st.error(f"Error loading usage stats for segment {seg_id}: {e}")


            # --- Display per-segment metrics ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Waste", f"{total_waste:.2f}")
            c2.metric("Total Recipe Uses", total_usage)
            c3.metric("Total Unique Users", total_unique_users)


            st.caption(
                f"Age {seg.get('AgeMin')}–{seg.get('AgeMax')} • Region: {seg.get('Region')}"
            )
            st.write("---")