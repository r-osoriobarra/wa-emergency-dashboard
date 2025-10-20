"""
SES Dashboard
Storm and rainfall monitoring for State Emergency Service
"""

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from transforms import get_rainfall_summary
from components import create_rainfall_bar

def show(df):
    """Display SES storm dashboard"""
    
    st.header("🌧️ WA SES Storm Dashboard")
    
    # Dashboard description
    st.info("""
    **How to read this dashboard:**
    - 🌧️ Rainfall chart shows current precipitation across WA
    - 💨 Wind analysis shows relationship between wind and gusts
    - 🌀 Pressure chart highlights low-pressure systems (storm indicators)
    - Red bars indicate alert conditions
    """)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        rain_min = st.slider(
            "Min Rainfall (mm)",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=0.5,
            help="Show stations with rainfall above this threshold"
        )

    with col2:
        top_n = st.selectbox(
            "Top N Stations",
            options=[10, 15, 20, 50, 100, 150],
            index=0,
            help="Number of rainfall stations to show"
        )

    # Apply filters
    df_filtered = df[(df['rainfall'] >= rain_min) & (df['rainfall'] > 0)].copy()
    
    # Get summary
    summary = get_rainfall_summary(df_filtered)
    
    st.markdown("---")
    
    # KEY METRICS
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Stations with Rain", summary.get('stations_with_rain', 0))
    col2.metric("Max Rainfall", f"{summary.get('max_rainfall', 0):.1f} mm")
    col3.metric("Max Gust", f"{summary.get('max_gust', 0):.0f} km/h")
    col4.metric("Pressure Alerts", summary.get('pressure_alerts', 0))
    
    st.markdown("---")
    
    # RAINFALL SECTION (ALIGNED)
    st.subheader("🌧️ Current Rainfall Activity")
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.caption("Stations with active rainfall (hover for details)")
        
        # Rainfall bar chart (Plotly - interactive tooltips)
        rain_fig = create_rainfall_bar(df_filtered, n=top_n)
        
        rain_fig.update_layout(
            height=500,  # Match map height
            legend=dict(font=dict(color="black"))
        )
        
        st.plotly_chart(rain_fig, use_container_width=True)
    
    with col2:
        st.caption("Rainfall distribution statistics")
        
        rain_data = df_filtered[df_filtered['rainfall'] > 0]['rainfall'].dropna()
        
        if len(rain_data) > 0:
            # Histogram - SAME HEIGHT
            fig, ax = plt.subplots(figsize=(5, 6.5))
            
            ax.hist(rain_data, bins=10, color='skyblue', edgecolor='black')
            
            mean_rain = rain_data.mean()
            median_rain = rain_data.median()
            
            ax.axvline(mean_rain, color='red', linestyle='--',
                      label=f'Mean: {mean_rain:.1f}mm', linewidth=2)
            ax.axvline(median_rain, color='green', linestyle='--',
                      label=f'Median: {median_rain:.1f}mm', linewidth=2)
            
            ax.set_xlabel("Rainfall (mm)", fontsize=11)
            ax.set_ylabel("Count", fontsize=11)
            ax.set_title("Rainfall Distribution", fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            st.info("No rainfall currently")
    
    st.markdown("---")
    
    # WIND ANALYSIS SECTION (WITH HOVER)
    st.subheader("💨 Wind Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Relationship between wind speed and gusts (hover over points)")
        
        # Use Plotly for interactive scatter
        import plotly.express as px
        
        wind_data = df_filtered[['station_name', 'wind_spd_kmh', 'gust_kmh']].dropna()
        
        if len(wind_data) > 0:
            fig = px.scatter(
                wind_data,
                x='wind_spd_kmh',
                y='gust_kmh',
                hover_data={'station_name': True},
                labels={
                    'wind_spd_kmh': 'Wind Speed (km/h)',
                    'gust_kmh': 'Gust Speed (km/h)'
                },
                title='Wind vs Gust Correlation',
                trendline='ols',
                height=400
            )
            
            fig.update_traces(marker=dict(size=8, opacity=0.6))
            fig.update_layout(legend=dict(font=dict(color="black")))
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No wind data available")
    
    with col2:
        st.caption("Wind and gust speed distribution")
        
        # Boxplot comparison
        fig, ax = plt.subplots(figsize=(7, 5))
        
        wind_compare = df_filtered[['wind_spd_kmh', 'gust_kmh']].dropna()
        
        if len(wind_compare) > 0:
            wind_compare.boxplot(ax=ax)
            ax.set_ylabel("Speed (km/h)", fontsize=11)
            ax.set_title("Wind Speed Distribution", fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig)
    
    st.markdown("---")
    
    # PRESSURE ANALYSIS SECTION
    st.subheader("🌀 Atmospheric Pressure Analysis")
    st.caption("Low pressure highlights potential storm activity. Ordered from lowest to highest.")

    import numpy as np
    import plotly.express as px

    pressure_data = (
        df_filtered[['station_name', 'msl_pres']]
        .dropna()
        .sort_values('msl_pres', ascending=True)
        .copy()
    )

    if len(pressure_data) > 0:
        # Calculate mean pressure
        mean_p = pressure_data['msl_pres'].mean()
        
        # Calculate deviation from mean
        pressure_data['deviation'] = pressure_data['msl_pres'] - mean_p
        
        # Define alert: stations with pressure 3+ hPa below mean
        pressure_data['Status'] = np.where(
            pressure_data['deviation'] < -3, 
            'Alert', 
            'Normal'
        )
        
        # Create bar chart
        fig = px.bar(
            pressure_data,
            x='station_name',
            y='deviation',
            color='Status',
            color_discrete_map={'Alert': 'red', 'Normal': 'steelblue'},
            hover_data={
                'station_name': True, 
                'msl_pres': ':.1f',  # Added atmospheric pressure
                'deviation': ':.2f', 
                'Status': True
            },
            labels={
                'station_name': 'Station', 
                'deviation': 'Deviation (hPa)',
                'msl_pres': 'Pressure (hPa)'  # Label for hover
            },
            title='Pressure Deviation from Mean',
            height=450
        )
        
        # Add reference lines
        fig.add_hline(y=0, line_dash='solid', line_color='black',
                    annotation_text=f"Mean ({mean_p:.1f} hPa)", 
                    annotation_position="top left")
        fig.add_hline(y=-3, line_dash='dash', line_color='red',
                    annotation_text="Alert Threshold (-3 hPa)", 
                    annotation_position="bottom left")
        
        # Format layout
        fig.update_layout(
            xaxis={'categoryorder': 'array', 
                'categoryarray': pressure_data['station_name'].tolist()},
            showlegend=True,
            legend=dict(font=dict(color="black"))
        )
        fig.update_xaxes(tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No pressure data available")