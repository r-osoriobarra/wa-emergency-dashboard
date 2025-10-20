"""
WA Emergency Services Dashboard
Main navigation file

Author: University Student
Libraries: Streamlit, Plotly, Matplotlib, Seaborn
"""

import streamlit as st
import sys
import os

# Add src folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import dashboard pages
from dashboards import summary, dfes_dashboard, ses_dashboard, slswa_dashboard, forecast_dashboard
from bom_ingest import get_observations, get_forecasts
from transforms import apply_all_transforms

# Page setup
st.set_page_config(
    page_title="WA Emergency Dashboard",
    page_icon="🌡️",
    layout="wide"
)

# Load global CSS style
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# DEFINE load_all_data FUNCTION FIRST (before sidebar)
@st.cache_data(ttl=600)
def load_all_data():
    """Load data from BOM"""
    obs_df, obs_time = get_observations()
    fcst_df, fcst_time = get_forecasts()
    
    if not obs_df.empty:
        obs_df = apply_all_transforms(obs_df)
    
    return obs_df, fcst_df, obs_time, fcst_time

# Initialize session state for active tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Sidebar
with st.sidebar:
    st.title("🌡️ WA Emergency Services")
    st.markdown("---")
    
    # Navigation buttons
    st.subheader("🧭 Quick Navigation")
    
    # Navigation buttons - update session state and rerun
    if st.button("Summary", use_container_width=True, 
                 type="primary" if st.session_state.active_tab == 0 else "secondary"):
        st.session_state.active_tab = 0
        st.rerun()
    
    if st.button("DFES Fire Risk", use_container_width=True,
                 type="primary" if st.session_state.active_tab == 1 else "secondary"):
        st.session_state.active_tab = 1
        st.rerun()
    
    if st.button("SES Storm", use_container_width=True,
                 type="primary" if st.session_state.active_tab == 2 else "secondary"):
        st.session_state.active_tab = 2
        st.rerun()
    
    if st.button("SLSWA Coastal", use_container_width=True,
                 type="primary" if st.session_state.active_tab == 3 else "secondary"):
        st.session_state.active_tab = 3
        st.rerun()

    if st.button("7-Day Forecast", use_container_width=True,
             type="primary" if st.session_state.active_tab == 4 else "secondary"):
        st.session_state.active_tab = 4
        st.rerun()
    
    st.markdown("---")
    
    # Refresh button
    st.subheader("🔄 Data Control")
    
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        new_obs_df, new_fcst_df, new_obs_time, new_fcst_time = load_all_data()

        # Update timestamps only if data changed
        if not new_obs_df.equals(st.session_state.df_obs):
            st.session_state.obs_time = new_obs_time
        if not new_fcst_df.equals(st.session_state.df_fcst):
            st.session_state.fcst_time = new_fcst_time

        # Store new data
        st.session_state.df_obs = new_obs_df
        st.session_state.df_fcst = new_fcst_df

        st.rerun()

    # Always show last known update
    if 'obs_time' in st.session_state and 'fcst_time' in st.session_state:
        st.caption(
            f"<div style='line-height:1.5;'>"
            f"<b>Last update</b><br>"
            f"Observations: {st.session_state.obs_time.strftime('%Y-%m-%d %H:%M:%S')}<br>"
            f"Forecasts: {st.session_state.fcst_time.strftime('%Y-%m-%d %H:%M:%S')}"
            f"</div>", unsafe_allow_html=True
        )
    else:
        st.caption("Loading data timestamps...")

    st.markdown("---")
    
    # Info section
    st.subheader("ℹ️ About")
    st.markdown("""
    **Data Source:**  
    Bureau of Meteorology
    
    **Update Frequency:**
    - Observations: 10 min
    - Forecasts: 1 hour
    
    **Coverage:**  
    ~145 WA stations
    """)

# Load data once (initial load)
with st.spinner("Loading data from BOM..."):
    df_obs, df_fcst, obs_time, fcst_time = load_all_data()

    # Save initial timestamps only if not already set
    if 'obs_time' not in st.session_state:
        st.session_state.obs_time = obs_time
    if 'fcst_time' not in st.session_state:
        st.session_state.fcst_time = fcst_time
    if 'df_obs' not in st.session_state:
        st.session_state.df_obs = df_obs
    if 'df_fcst' not in st.session_state:
        st.session_state.df_fcst = df_fcst

if df_obs.empty:
    st.error("❌ No data available. Please check your internet connection.")
    st.stop()

# Show quick stats in sidebar
with st.sidebar:
    st.markdown("---")
    st.caption("Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Stations", len(df_obs))
    with col2:
        st.metric("Updated", obs_time.strftime('%H:%M') if obs_time else "N/A")

# Display the active dashboard directly (no tabs UI conflict)
st.markdown("---")

if st.session_state.active_tab == 0:
    summary.show(df_obs, df_fcst, obs_time, fcst_time)
elif st.session_state.active_tab == 1:
    dfes_dashboard.show(df_obs)
elif st.session_state.active_tab == 2:
    ses_dashboard.show(df_obs)
elif st.session_state.active_tab == 3:
    slswa_dashboard.show(df_obs)
elif st.session_state.active_tab == 4:
    forecast_dashboard.show(df_fcst)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    WA Emergency Services Dashboard<br>
    Data source: Bureau of Meteorology
</div>
""", unsafe_allow_html=True)