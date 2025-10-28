import streamlit as st

def show(df_obs, df_fcst, obs_time, fcst_time):
    
    st.header("WA Emergency Services Dashboard")
    st.write("Real-time weather monitoring for Western Australian emergency services")
    
    # Data status metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Observation Stations", len(df_obs))
    col2.metric("Forecast Locations", len(df_fcst))
    col3.metric("Valid Data Points", df_obs['fire_risk_score'].notna().sum())
    
    st.markdown("---")
    
    # Presentation
    st.subheader("Project Context")
    
    st.markdown("""
    Project Overview
    Western Australia faces constant threats from extreme weather events: bushfires, floods, dangerous storms, and hazardous coastal tides. Every day, emergency service agencies must make critical decisions to protect lives, homes, and infrastructure.
    The Bureau of Meteorology operates 140+ weather stations across Western Australia, collecting real-time data every 10 minutes. However, this data arrives in complex XML formats that are difficult for ground personnel to interpret quickly during emergencies.
    This project bridges that gap by transforming raw meteorological data into clear, visual, actionable insights. The interactive dashboard delivers real-time weather intelligence to three critical emergency services:

    DFES - Fire risk monitoring and firefighting response
    WA SES - Flood and storm awareness and coordination
    SLSWA - Coastal hazard and water safety monitoring

    Built on data-driven risk hypotheses, the dashboard converts temperature, humidity, wind, pressure, and rainfall measurements into intuitive visual indicators. Emergency responders can now monitor conditions in real time, anticipate hazards, and make faster decisions that save lives.
    The system demonstrates how accessible data visualization and modern web technology can enhance emergency response coordination across multiple agencies in a region with some of Australia's most unpredictable and dangerous weather conditions.          
    """)
   
    st.markdown("---")
    
    # Technical information
    st.subheader("Technical Details")
    
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
    st.subheader("Limitations")
    
    st.info("""
    - Snapshot data only (no historical trends)
    - Some stations may have missing sensors
    - Rainfall accumulations are estimates
    - No marine/swell data integrated
    - 'rain_probability' field not available in all datasets
    """)