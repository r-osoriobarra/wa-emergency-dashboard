"""
SLSWA Dashboard
Coastal safety monitoring for Surf Life Saving WA
"""

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from transforms import get_coastal_summary
from components import create_risk_map, create_top_stations_table

def show(df):
    """Display SLSWA coastal dashboard"""
    
    st.header("🌊 SLSWA Coastal Safety Dashboard")
    
    # Dashboard description
    st.info("""
    **How to read this dashboard:**
    - 🗺️ Map shows coastal exposure risk (red = extreme winds/gusts)
    - 👁️ Visibility alerts help assess marine safety conditions
    - 💨 Wind charts show current and forecasted conditions
    - Higher exposure = more dangerous conditions for beach activities
    """)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        wind_min = st.slider(
            "Min Wind Speed (km/h)",
            min_value=0,
            max_value=50,
            value=10,
            help="Show stations above this wind speed"
        )
    
    with col2:
        exposure_bands = st.multiselect(
            "Exposure Bands",
            options=['Low', 'Moderate', 'High', 'Extreme'],
            default=['Moderate', 'High', 'Extreme', 'Low'],
            help="Filter by exposure level"
        )
    
    with col3:
        show_low_vis = True
    
    # Apply filters
    df_filtered = df[
        (df['wind_spd_kmh'] >= wind_min) &
        (df['exposure_band'].isin(exposure_bands))
    ].copy()
    
    # Get summary
    summary = get_coastal_summary(df_filtered)
    
    st.markdown("---")
    
    # KEY METRICS
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Stations Shown", len(df_filtered))
    col2.metric("Highest Exposure", summary.get('highest_exposure_station', 'N/A')[:20])
    col3.metric("Exposure Score", f"{summary.get('highest_exposure_score', 0):.2f}")
    col4.metric("Low Visibility", summary.get('low_visibility_count', 0))
    
    st.markdown("---")
    
    # MAIN CONTENT: Map and Distribution (ALIGNED)
    st.subheader("📍 Coastal Exposure Map")
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.caption("Interactive map - Marker size represents gust intensity")
        
        # Coastal map (Plotly)
        map_fig = create_risk_map(
            df_filtered,
            score_col='exposure_score',
            band_col='exposure_band',
            title='Coastal Exposure Across WA',
            size_col='gust_kmh'
        )
        
        # Fix legend text color and height
        map_fig.update_layout(
            height=500,
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="black",
                borderwidth=1,
                font=dict(color="black")
            )
        )
        
        st.plotly_chart(map_fig, use_container_width=True)
    
    with col2:
        st.caption("Exposure level distribution")
        
        # Pie chart - SAME HEIGHT
        fig, ax = plt.subplots(figsize=(5, 6.5))
        
        exposure_counts = df_filtered['exposure_band'].value_counts()
        colors = ['green', 'orange', 'darkorange', 'red', 'gray']
        
        ax.pie(exposure_counts.values, labels=exposure_counts.index,
              autopct='%1.1f%%', colors=colors[:len(exposure_counts)], 
              startangle=90, textprops={'fontsize': 10})
        ax.set_title("Exposure Distribution", fontsize=12, fontweight='bold')
        plt.tight_layout()
        
        st.pyplot(fig)
    
    st.markdown("---")
    
    # WIND ANALYSIS SECTION (WITH HOVER)
    st.subheader("💨 Wind Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Wind and gust comparison by exposure level")
        
        # Grouped boxplot (Seaborn)
        fig, ax = plt.subplots(figsize=(7, 5))
        
        wind_data = df_filtered[['wind_spd_kmh', 'gust_kmh', 'exposure_band']].dropna()
        
        if len(wind_data) > 0:
            # Melt data
            wind_melted = wind_data.melt(
                id_vars=['exposure_band'],
                value_vars=['wind_spd_kmh', 'gust_kmh'],
                var_name='Metric',
                value_name='Speed'
            )
            
            sns.boxplot(data=wind_melted, x='exposure_band', y='Speed',
                       hue='Metric',
                       order=['Low', 'Moderate', 'High', 'Extreme'],
                       ax=ax)
            
            ax.set_xlabel("Exposure Band", fontsize=11)
            ax.set_ylabel("Speed (km/h)", fontsize=11)
            ax.set_title("Wind vs Gust by Exposure", fontsize=12, fontweight='bold')
            ax.legend(title="", fontsize=10)
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig)
    
    with col2:
        st.caption("Current wind speed scatter (hover over points)")
        
        # Interactive scatter with Plotly
        import plotly.express as px
        
        scatter_data = df_filtered[['station_name', 'wind_spd_kmh', 'exposure_band']].dropna()
        
        if len(scatter_data) > 0:
            fig = px.scatter(
                scatter_data,
                x=scatter_data.index,
                y='wind_spd_kmh',
                color='exposure_band',
                color_discrete_map={
                    'Low': 'green',
                    'Moderate': 'orange',
                    'High': 'darkorange',
                    'Extreme': 'red'
                },
                hover_data={'station_name': True, 'wind_spd_kmh': ':.1f'},
                labels={'wind_spd_kmh': 'Wind Speed (km/h)', 'index': 'Station'},
                title='Wind Speed by Station',
                height=500
            )
            
            fig.update_layout(
                showlegend=True,
                legend=dict(font=dict(color="black"))
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # VISIBILITY SECTION
    if show_low_vis:
        st.subheader("👁️ Visibility Alerts")
        
        low_vis = df_filtered[df_filtered['vis_km'] < 10].copy()
        
        if len(low_vis) > 0:
            st.warning(f"⚠️ {len(low_vis)} stations with low visibility (< 10km)")
            
            vis_display = low_vis[['station_name', 'vis_km', 'wind_spd_kmh', 'exposure_band']].round(1)
            st.dataframe(vis_display, use_container_width=True, hide_index=True)
        else:
            st.success("✓ All stations have good visibility (> 10km)")
    
    st.markdown("---")
    
    # TOP STATIONS TABLE
    top_n = st.selectbox(
        "Top N Stations",
        options=[10, 15, 20, 50, 100, 150],
        index=1,
        help="Number of stations to show in table"
    )
    st.subheader(f"📋 Top {top_n} Coastal Exposure Stations")
    
    top_stations = create_top_stations_table(
        df_filtered,
        score_col='exposure_score',
        band_col='exposure_band',
        n=top_n,
        columns=['station_name', 'wind_spd_kmh', 'gust_kmh',
                'vis_km', 'exposure_score', 'exposure_band']
    )
    
    st.dataframe(top_stations, use_container_width=True, hide_index=True)
