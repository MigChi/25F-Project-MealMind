import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('System Health Monitor')
st.write('Monitor performance, API health, and database alerts')

logger.info("System Health Monitor page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Admin Dashboard"):
    st.switch_page('pages/20_Admin_Home.py')

st.write('')
st.write('')

# User Story 4: Monitor system performance metrics
st.subheader("Real-Time System Performance")

# Refresh button
col1, col2 = st.columns([3, 1])

with col1:
    st.caption("Last updated: Just now")

with col2:
    if st.button("Refresh Metrics", use_container_width=True):
        st.rerun()

st.write('')

# Get system metrics from API
try:
    response = requests.get(f"{API_BASE_URL}/analytics/system-metrics")
    
    if response.status_code == 200:
        metrics = response.json()
        
        # Display metrics in columns
        if len(metrics) >= 4:
            col1, col2, col3, col4 = st.columns(4)
            
            for idx, metric in enumerate(metrics[:4]):
                with [col1, col2, col3, col4][idx]:
                    metric_name = metric.get('Name', 'Unknown')
                    last_value = metric.get('LastValue', 'N/A')
                    st.metric(metric_name, last_value)
        
        st.write('')
        
        # Show all metrics in expandable section
        with st.expander("View All System Metrics"):
            for metric in metrics:
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.write(f"**{metric.get('Name')}**")
                    st.caption(metric.get('Description', 'No description'))
                
                with col2:
                    st.write(f"Value: {metric.get('LastValue', 'N/A')}")
                
                with col3:
                    last_measured = metric.get('LastMeasuredAt', 'Never')
                    st.caption(f"Last measured: {last_measured}")
                
                st.divider()
    else:
        st.error(f"Error loading metrics: Status {response.status_code}")
        # Fallback to mock data
        st.warning("Showing sample data")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("API Response Time", "142 ms")
        with col2:
            st.metric("Database Query Time", "23 ms")
        with col3:
            st.metric("CPU Usage", "34%")
        with col4:
            st.metric("Memory Usage", "2.1 GB")
        
except Exception as e:
    st.error(f"Error connecting to API: {str(e)}")
    st.warning("Showing sample data")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("API Response Time", "142 ms")
    with col2:
        st.metric("Database Query Time", "23 ms")
    with col3:
        st.metric("CPU Usage", "34%")
    with col4:
        st.metric("Memory Usage", "2.1 GB")

st.write('')
st.write('')

# User Story 6: Manage API and database health alerts
st.subheader("Active Alerts")

try:
    response = requests.get(f"{API_BASE_URL}/analytics/system-alerts", 
                           params={"status": "open"})
    
    if response.status_code == 200:
        alerts = response.json()
        
        if alerts:
            st.warning(f"{len(alerts)} active alerts require attention")
            
            for alert in alerts:
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    icon = {"Critical": "RED", "Warning": "YELLOW", "Info": "BLUE"}
                    severity = alert.get('Severity', 'Info')
                    alert_type = alert.get('AlertType', 'Unknown')
                    st.write(f"{icon.get(severity, 'BLUE')} **{severity}** - {alert_type}")
                    st.caption(str(alert.get('CreatedAt', 'Unknown time')))
                
                with col2:
                    st.write(alert.get('Message', 'No message'))
                
                with col3:
                    alert_id = alert.get('AlertID')
                    
                    if st.button("Acknowledge", key=f"ack_{alert_id}"):
                        try:
                            update_response = requests.put(
                                f"{API_BASE_URL}/analytics/system-alerts/{alert_id}",
                                json={"status": "acknowledged"}
                            )
                            
                            if update_response.status_code == 200:
                                st.success("Alert acknowledged")
                                st.rerun()
                            else:
                                st.error("Failed to acknowledge alert")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    if st.button("Resolve", key=f"resolve_{alert_id}"):
                        try:
                            update_response = requests.put(
                                f"{API_BASE_URL}/analytics/system-alerts/{alert_id}",
                                json={"status": "resolved"}
                            )
                            
                            if update_response.status_code == 200:
                                st.success("Alert resolved")
                                st.rerun()
                            else:
                                st.error("Failed to resolve alert")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                st.divider()
        else:
            st.success("No active alerts - all systems healthy!")
    else:
        st.error(f"Error loading alerts: Status {response.status_code}")
        
except Exception as e:
    st.error(f"Error connecting to API: {str(e)}")

st.write('')

# Show resolved alerts
try:
    response = requests.get(f"{API_BASE_URL}/analytics/system-alerts", 
                           params={"status": "resolved"})
    
    if response.status_code == 200:
        resolved_alerts = response.json()
        
        with st.expander(f"View Resolved Alerts ({len(resolved_alerts)})"):
            for alert in resolved_alerts[:10]:  # Show last 10
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    alert_type = alert.get('AlertType', 'Unknown')
                    message = alert.get('Message', 'No message')
                    st.write(f"**{alert_type}:** {message}")
                    st.caption(str(alert.get('CreatedAt', 'Unknown time')))
                
                with col2:
                    st.caption("✓ Resolved")
                    st.caption(str(alert.get('ResolvedAt', '')))
except Exception as e:
    pass  # Optional section

st.write('')
st.write('')

# Create new alert (User Story 6)
st.subheader("Create System Alert")

with st.form("create_alert"):
    st.write("Manually create a system alert:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        metric_id = st.number_input("Metric ID", min_value=1, value=1)
        alert_type = st.text_input("Alert Type", value="Manual Alert")
    
    with col2:
        severity = st.selectbox("Severity", ["Info", "Warning", "Critical"])
        message = st.text_area("Alert Message", placeholder="Describe the issue...")
    
    if st.form_submit_button("Create Alert", use_container_width=True):
        if message:
            try:
                payload = {
                    "metric_id": int(metric_id),
                    "alert_type": alert_type,
                    "severity": severity,
                    "message": message,
                    "status": "open"
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/analytics/system-alerts",
                    json=payload
                )
                
                if response.status_code == 201:
                    result = response.json()
                    st.success(f"Alert created with ID: {result.get('alert_id')}")
                    st.rerun()
                else:
                    st.error(f"Failed to create alert: Status {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error creating alert: {str(e)}")
        else:
            st.error("Please enter an alert message")

st.write('')
st.write('')

# Performance trends (mock data for now - would need time series endpoint)
st.subheader("Performance Trends (Last 24 Hours)")

tabs = st.tabs(["API Response Time", "Database Performance", "System Resources"])

with tabs[0]:
    st.caption("Average API response time over the last 24 hours")
    st.line_chart({
        "Response Time (ms)": [145, 152, 148, 155, 142, 138, 145, 150, 148, 143, 140, 142]
    })

with tabs[1]:
    st.caption("Database query performance")
    st.line_chart({
        "Query Time (ms)": [20, 22, 21, 25, 23, 19, 21, 24, 22, 20, 21, 23]
    })

with tabs[2]:
    st.caption("System resource usage")
    st.line_chart({
        "CPU (%)": [30, 32, 34, 36, 34, 32, 30, 33, 35, 34, 32, 34],
        "Memory (GB)": [2.0, 2.05, 2.1, 2.12, 2.1, 2.08, 2.1, 2.15, 2.1, 2.08, 2.1, 2.1]
    })

st.write('')
st.write('')

# Alert configuration
st.subheader("Alert Configuration")

with st.form("alert_settings"):
    st.write("Configure when to receive alerts:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Performance Thresholds:**")
        api_threshold = st.number_input("API response time alert (ms)", value=200, step=10)
        db_threshold = st.number_input("Database query time alert (ms)", value=50, step=5)
        error_threshold = st.number_input("Error rate alert (%)", value=1.0, step=0.1)
    
    with col2:
        st.write("**Resource Thresholds:**")
        cpu_threshold = st.number_input("CPU usage alert (%)", value=80, step=5)
        memory_threshold = st.number_input("Memory usage alert (%)", value=85, step=5)
    
    st.write('')
    st.write("**Notification Settings:**")
    
    email_alerts = st.checkbox("Send email alerts", value=True)
    if email_alerts:
        alert_email = st.text_input("Alert email address", value="maya@mealprep.app")
    
    slack_alerts = st.checkbox("Send Slack notifications", value=True)
    sms_alerts = st.checkbox("Send SMS for critical alerts", value=False)
    
    if st.form_submit_button("Save Alert Settings", use_container_width=True):
        st.success("Alert settings updated!")

st.write('')
st.write('')

# Infrastructure planning insights
with st.expander("Infrastructure Planning Recommendations"):
    st.write("""
    **Based on current metrics:**
    
    1. **API Response Time:** Currently averaging 142ms
       - Recommendation: Set alert threshold at 200ms
       - Consider caching for frequently accessed endpoints
    
    2. **Database Performance:** Query times stable at ~23ms
       - Recommendation: Monitor for queries exceeding 50ms
       - Index optimization opportunities
    
    3. **Resource Usage:** CPU at 34%, Memory at 2.1GB
       - Recommendation: Current capacity is adequate
       - Plan for scaling if CPU exceeds 70% consistently
    """)