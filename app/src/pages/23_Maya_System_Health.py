import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(page_title="Maya – System Health", page_icon="📊")
SideBarLinks()


API_BASE_URL = "http://api:4000"


st.title("📊 System Health Monitor")
st.caption("View metrics and manage system alerts.")


# --- Metrics ---
st.subheader("Key System Metrics")


try:
    # Backend route: @analytics_bp.route("/system-metrics", methods=["GET"])
    mresp = requests.get(f"{API_BASE_URL}/system-metrics", timeout=8)
    if mresp.status_code == 200:
        metrics = mresp.json()
        if metrics:
            cols = st.columns(4)
            for i, metric in enumerate(metrics[:4]):
                name = metric.get("Name", "Metric")
                last_value = metric.get("LastValue", "N/A")
                cols[i].metric(name, last_value)
        else:
            st.info("No metrics defined yet.")
    else:
        st.error(f"Error metrics: {mresp.text}")
except Exception as e:
    st.error(f"Error contacting API: {e}")


st.write("---")


# --- Alerts ---
st.subheader("Active Alerts")


try:
    # Backend route: @analytics_bp.route("/system-alerts", methods=["GET"])
    aresp = requests.get(
        f"{API_BASE_URL}/system-alerts",
        params={"status": "open"},
        timeout=8,
    )
    if aresp.status_code == 200:
        alerts = aresp.json()
        if not alerts:
            st.success("No active alerts. All good! ✅")
        else:
            for alert in alerts:
                aid = alert.get("AlertID")
                severity = alert.get("Severity", "Info")
                msg = alert.get("Message", "")
                created = alert.get("CreatedAt", "")


                cols = st.columns([3, 2, 1])
                with cols[0]:
                    st.write(f"**{severity}** – {msg}")
                    st.caption(f"Created: {created}")
                with cols[1]:
                    st.caption(f"Metric ID: {alert.get('MetricID')}")
                with cols[2]:
                    if st.button("Acknowledge", key=f"ack_{aid}"):
                        try:
                            uresp = requests.put(
                                f"{API_BASE_URL}/system-alerts/{aid}",
                                json={"status": "acknowledged"},
                                timeout=5,
                            )
                            if uresp.status_code == 200:
                                st.success("Alert acknowledged.")
                                st.rerun()
                            else:
                                st.error(f"Update failed: {uresp.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if st.button("Resolve", key=f"res_{aid}"):
                        try:
                            uresp = requests.put(
                                f"{API_BASE_URL}/system-alerts/{aid}",
                                json={"status": "resolved"},
                                timeout=5,
                            )
                            if uresp.status_code == 200:
                                st.success("Alert resolved.")
                                st.rerun()
                            else:
                                st.error(f"Update failed: {uresp.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
    else:
        st.error(f"Alerts error: {aresp.text}")
except Exception as e:
    st.error(f"Error contacting API: {e}")


st.write("---")
st.subheader("Create Manual Alert")


with st.form("new_alert"):
    col1, col2 = st.columns(2)
    with col1:
        metric_id = st.number_input("Metric ID", min_value=1, value=1)
        alert_type = st.text_input("Alert type", value="Manual admin alert")
    with col2:
        severity = st.selectbox("Severity", ["Info", "Warning", "Critical"])
        message = st.text_area("Message", height=80)
    submit = st.form_submit_button("Create Alert")
    if submit:
        if not message.strip():
            st.error("Message required.")
        else:
            payload = {
                "metric_id": int(metric_id),
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "status": "open",
            }
            try:
                # Backend route: @analytics_bp.route("/system-alerts", methods=["POST"])
                resp = requests.post(
                    f"{API_BASE_URL}/system-alerts",
                    json=payload,
                    timeout=8,
                )
                if resp.status_code in (200, 201):
                    st.success("Alert created.")
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Error creating alert: {e}")


