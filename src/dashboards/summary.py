"""
Summary Dashboard
Project context and introduction
"""

import streamlit as st

def show(df_obs, df_fcst, obs_time, fcst_time):
    """Display summary dashboard with project context"""
    
    st.header("WA Emergency Services Dashboard")
    st.write("Real-time weather monitoring for Western Australian emergency services")
    
    # Data status metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Observation Stations", len(df_obs))
    col2.metric("Forecast Locations", len(df_fcst))
    col3.metric("Valid Data Points", df_obs['fire_risk_score'].notna().sum())
    
    st.markdown("---")
    
    # PROJECT CONTEXT SECTION
    st.subheader("📋 Project Context")
    
    # ========== CONTEXT HERE ==========
    st.markdown("""
    **Pending, general context**
    - Problem definition and message
    - Goal
    - Narrative
    - Target audience
    - Summarised introduction to the dataset.
    - A summary of the types of dataset analysis you did through data exploration and discovery.
    - Hypothesis.          
    """)
    # ==================================
    
    st.markdown("---")
    
    # Stakeholder information
    st.subheader("👥 Stakeholders")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔥 DFES")
        st.write("**Department of Fire and Emergency Services**")
        st.write("Monitors fire-weather risk based on temperature, humidity, and wind conditions")
    
    with col2:
        st.markdown("### 🌧️ WA SES")
        st.write("**State Emergency Service**")
        st.write("Tracks rainfall intensity, storm activity, and severe weather events")
    
    with col3:
        st.markdown("### 🌊 SLSWA")
        st.write("**Surf Life Saving WA**")
        st.write("Monitors coastal exposure, wind conditions, and marine safety")
    
    st.markdown("---")
    
    # Technical information
    st.subheader("🔧 Technical Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Data Source:**
        - Bureau of Meteorology (BOM)
        - Observations: Every 10 minutes
        - Forecasts: Hourly updates
        - Coverage: ~145 stations across WA
        """)
    
    with col2:
        st.markdown("""
        **Technologies Used:**
        - **Plotly**: Interactive geospatial maps
        - **Matplotlib**: Statistical visualizations
        - **Seaborn**: Advanced data analysis
        - **Streamlit**: Dashboard framework
        """)
    
    st.markdown("---")
    
    # Methodology
    st.subheader("📊 Methodology")
    
    st.markdown("""
    **Risk Score Calculation:**
    
    Risk scores use z-score normalization to compare variables on the same scale:
    
    - **Fire Risk** = z(temperature) - z(humidity) + 0.5 × z(wind_speed)
    - **Coastal Exposure** = z(wind_speed) + 0.7 × z(gust_speed)
    
    **Risk Bands:**
    - **Low**: Score < 0.0
    - **Moderate**: Score 0.0 - 0.8
    - **High**: Score 0.8 - 1.6
    - **Extreme**: Score > 1.6
    """)
    
    st.markdown("---")
    
    # Limitations
    st.subheader("⚠️ Limitations")
    
    st.info("""
    - Snapshot data only (no historical trends)
    - Some stations may have missing sensors
    - Rainfall accumulations are estimates
    - No marine/swell data integrated
    - 'rain_probability' field not available in all datasets
    """)