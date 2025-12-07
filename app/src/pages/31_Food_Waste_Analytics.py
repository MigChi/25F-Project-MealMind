import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

SideBarLinks()

st.title('Food Waste Analytics')
st.write('Identify what users waste most and recommend features to reduce waste')

logger.info("Food Waste Analytics page")

API_BASE_URL = "http://api:4000"

if st.button("Back to Analyst Dashboard"):
    st.switch_page('pages/30_Analyst_Home.py')

st.write('')
st.write('')

# User Story 1: Aggregated charts showing most wasted foods
st.subheader("Most Wasted Ingredients")
st.caption("Based on expired/removed items from user inventories")

# Filters
col1, col2 = st.columns(2)

with col1:
    period_id = st.number_input("Period ID (optional)", min_value=0, value=0, 
                                help="Leave as 0 for all periods")

with col2:
    segment_id = st.number_input("Segment ID (optional)", min_value=0, value=0,
                                 help="Leave as 0 for all segments")

if st.button("Load Waste Data", type="primary"):
    st.session_state['load_waste'] = True

st.write('')

if st.session_state.get('load_waste', False):
    try:
        params = {}
        if period_id > 0:
            params['period_id'] = period_id
        if segment_id > 0:
            params['segment_id'] = segment_id
        
        response = requests.get(
            f"{API_BASE_URL}/analytics/waste-statistics",
            params=params
        )
        
        if response.status_code == 200:
            waste_data = response.json()
            
            if waste_data:
                st.success(f"Loaded waste data for {len(waste_data)} ingredients")
                
                # Create bar chart
                chart_data = {}
                for item in waste_data[:10]:
                    ingredient_id = item.get('IngredientID', 'Unknown')
                    category = item.get('CategoryName', 'Unknown')
                    total_wasted = item.get('TotalWastedAmount', 0)
                    
                    label = f"{category} (ID: {ingredient_id})"
                    chart_data[label] = float(total_wasted) if total_wasted else 0
                
                st.bar_chart(chart_data)
                
                st.write('')
                st.write('')
                
                # Detailed table
                st.subheader("Detailed Waste Analysis")
                
                for item in waste_data:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                    
                    with col1:
                        category = item.get('CategoryName', 'Unknown')
                        ingredient_id = item.get('IngredientID', 'N/A')
                        st.write(f"**{category}**")
                        st.caption(f"Ingredient ID: {ingredient_id}")
                    
                    with col2:
                        total_wasted = item.get('TotalWastedAmount', 0)
                        st.write(f"{total_wasted:.2f}")
                        st.caption("Total wasted")
                    
                    with col3:
                        waste_rate = item.get('AvgWasteRatePercent', 0)
                        if waste_rate:
                            st.write(f"{waste_rate:.1f}%")
                            st.caption("Avg waste rate")
                        else:
                            st.write("N/A")
                    
                    with col4:
                        cat_id = item.get('CategoryID', 'N/A')
                        st.caption(f"Category ID: {cat_id}")
                    
                    st.divider()
                
                st.write('')
                st.write('')
                
                # Calculate insights
                total_waste = sum(float(item.get('TotalWastedAmount', 0)) for item in waste_data)
                avg_waste_rate = sum(float(item.get('AvgWasteRatePercent', 0)) for item in waste_data) / len(waste_data) if waste_data else 0
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Waste Amount", f"{total_waste:.2f} units")
                
                with col2:
                    st.metric("Average Waste Rate", f"{avg_waste_rate:.1f}%")
                
            else:
                st.info("No waste data found for the selected filters")
                st.write("Try adjusting the Period ID or Segment ID filters")
        else:
            st.error(f"Error loading waste data: Status {response.status_code}")
            
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.warning("Make sure Docker containers are running: `docker compose up`")

st.write('')
st.write('')

# Get demographic segments for reference
st.subheader("Available Demographic Segments")

try:
    response = requests.get(f"{API_BASE_URL}/analytics/demographic-segments")
    
    if response.status_code == 200:
        segments = response.json()
        
        if segments:
            with st.expander(f"View {len(segments)} Demographic Segments"):
                for segment in segments:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        name = segment.get('Name', 'Unknown')
                        segment_id = segment.get('SegmentID', 'N/A')
                        st.write(f"**{name}** (ID: {segment_id})")
                    
                    with col2:
                        age_min = segment.get('AgeMin', 'N/A')
                        age_max = segment.get('AgeMax', 'N/A')
                        st.write(f"Age: {age_min}-{age_max}")
                    
                    with col3:
                        region = segment.get('Region', 'N/A')
                        st.write(f"Region: {region}")
                    
                    st.divider()
        else:
            st.info("No demographic segments defined yet")
    else:
        st.warning("Unable to load demographic segments")
except Exception as e:
    st.warning(f"Could not load segments: {str(e)}")

st.write('')
st.write('')

# User Story 4: Export report
st.subheader("Export Food Waste Report")

col1, col2, col3 = st.columns(3)

with col1:
    report_format = st.selectbox("Export format", ["PDF", "Excel", "CSV"])

with col2:
    include_charts = st.checkbox("Include visualizations", value=True)

with col3:
    if st.button("Generate Report", type="primary", use_container_width=True):
        st.success(f"Food waste report generated as {report_format}")
        st.download_button("Download Report", 
                          data="Sample report data", 
                          file_name=f"food_waste_report.{report_format.lower()}")

st.write('')
st.write('')

# Recommendations based on data
st.subheader("Data-Driven Recommendations")

with st.expander("See feature recommendations to reduce waste"):
    st.write("""
    **Based on waste analytics, we recommend:**
    
    1. **Enhanced Expiration Alerts**
       - Target categories with highest waste rates
       - Send notifications 2 days before expiration
       - Priority: High
    
    2. **Smart Shopping Lists**
       - Suggest quantities based on usage patterns
       - Prevent over-purchasing
       - Priority: Medium
    
    3. **Use It Up Recipe Suggestions**
       - Daily suggestions using expiring items
       - Reduce forgotten ingredients
       - Priority: High
    
    4. **Portion Size Guidance**
       - Help users buy appropriate amounts
       - Especially for single-person households
       - Priority: Medium
    
    5. **Freezer Management Feature**
       - Track frozen items separately
       - Extend ingredient life
       - Priority: Low
    """)