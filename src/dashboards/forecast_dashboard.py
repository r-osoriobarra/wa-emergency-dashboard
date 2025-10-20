"""
Forecast Dashboard
7-day weather forecast for all WA localities
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from transforms import get_weather_emoji

def show(df_fcst):
    """Display 7-day forecast dashboard"""
    
    st.header("📅 7-Day Weather Forecast")
    
    # Dashboard description
    st.info("""
    **How to read this dashboard:**
    - 📅 Table shows 7-day forecast for each locality
    - Each cell shows weather icon and description
    """)
    
    if df_fcst.empty:
        st.warning("No forecast data available")
        return
    
    st.markdown("---")
    
    # 7-DAY FORECAST TABLE
    st.subheader("📋 7-Day Forecast by Location")
    
    # Get unique locations
    locations = sorted(df_fcst['locality_name'].unique())
    
    # Create forecast table for each location
    forecast_data = []
    
    for location in locations:
        # Filter data for this location
        location_fcst = df_fcst[df_fcst['locality_name'] == location].copy()
        
        # Sort by period index and limit to 7 days
        if 'period_index' in location_fcst.columns:
            location_fcst = location_fcst.sort_values('period_index').head(7)
        else:
            location_fcst = location_fcst.head(7)
        
        # Create row with location
        row = {'Location': location}
        
        # Add each day's forecast
        for idx, forecast_row in location_fcst.iterrows():
            period = int(forecast_row['period_index']) if pd.notna(forecast_row['period_index']) else 0
            
            # Get emoji and description
            emoji = get_weather_emoji(forecast_row['icon_code'])
            description = forecast_row['precis_text'] if pd.notna(forecast_row['precis_text']) else 'N/A'
            
            # Combine emoji and short description
            day_forecast = f"{emoji} {description}"
            
            # Add to row
            day_labels = ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
            day_name = day_labels[period] if period < len(day_labels) else f"Day {period+1}"
            row[day_name] = day_forecast
        
        forecast_data.append(row)
    
    # Convert to DataFrame
    forecast_df = pd.DataFrame(forecast_data)
    
    # Display the table
    st.dataframe(forecast_df, use_container_width=True, hide_index=True, height=600)
    
    st.markdown("---")
    
    # TOP LOCATIONS
    st.subheader("🔥 Top 5 Hottest Locations (Max Temp)")
    
    # Get max temp per location across all periods
    max_temps = df_fcst.groupby('locality_name')['max_temp'].max().sort_values(ascending=False).head(5)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Display as table
        top_hot = pd.DataFrame({
            'Location': max_temps.index,
            'Max Temp (°C)': max_temps.values.round(1)
        })
        st.dataframe(top_hot, use_container_width=True, hide_index=True)
    
    with col2:
        # Bar chart
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(max_temps.index, max_temps.values, color='orangered')
        ax.set_xlabel('Max Temperature (°C)', fontsize=10)
        ax.set_title('Hottest Locations', fontsize=11, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)