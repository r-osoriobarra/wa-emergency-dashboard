import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from transforms import get_fire_risk_summary
from components import create_risk_map, create_top_stations_table

def show(df):
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    
    st.header("🔥 DFES Fire Risk Dashboard")
    
    # Dashboard description
    st.info("""
    **How to read this dashboard:**
    - 🗺️ Map shows fire risk across WA (red = extreme, green = low)
    - 📊 Charts show relationship between temperature, humidity, and wind
    - 📈 Higher temperatures + lower humidity + stronger winds = higher fire risk
    - Use filters below to focus on specific risk levels
    """)
    
    # Filters    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp_min = st.slider(
            "Min Temperature (°C)",
            min_value=10,
            max_value=45,
            value=15,
            help="Show stations above this temperature"
        )
    
    with col2:
        risk_bands = st.multiselect(
            "Risk Bands",
            options=['Low', 'Moderate', 'High', 'Extreme'],
            default=['Moderate', 'High', 'Extreme', 'Low'],
            help="Filter by risk level"
        )
    
    # Apply filters
    df_filtered = df[
        (df['air_temperature'] >= temp_min) &
        (df['fire_risk_band'].isin(risk_bands))
    ].copy()

    st.markdown("---")
    
    # Get summary stats
    summary = get_fire_risk_summary(df_filtered)
    
    # key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Stations Shown", len(df_filtered))
    col2.metric("Highest Risk", summary.get('highest_risk_station', 'N/A'))
    col3.metric("Risk Score", f"{summary.get('highest_risk_score', 0):.2f}")
    col4.metric("Extreme Count", summary.get('band_counts', {}).get('Extreme', 0))
    
    st.markdown("---")
    
    # Map and Distribution side by side
    st.subheader("📍 Geographic Distribution")
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.caption("Fire Risk interactive map - Click and drag to pan, scroll to zoom.")
        
        # Interactive map
        map_fig = create_risk_map(
            df_filtered,
            score_col='fire_risk_score',
            band_col='fire_risk_band',
            title='Fire Risk Across WA',
            size_col='wind_spd_kmh'
        )
        
        # Fix legend text color to black
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
        st.caption("Station count by risk level")
        
        # Risk distribution bar chart
        fig, ax = plt.subplots(figsize=(5, 6.5))
        
        band_counts = df_filtered['fire_risk_band'].value_counts()
        band_order = ['Low', 'Moderate', 'High', 'Extreme']
        band_counts = band_counts.reindex(band_order, fill_value=0)
        
        sns.barplot(x=band_counts.index, y=band_counts.values,
                   palette=['green', 'orange', 'darkorange', 'red'], ax=ax)
        
        for i, v in enumerate(band_counts.values):
            ax.text(i, v + 0.5, str(v), ha='center', fontweight='bold', fontsize=12)
        
        ax.set_xlabel("Risk Band", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)
        ax.set_title("Risk Distribution", fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Temperature vs Humidity
    st.subheader("🔍 Risk Factor Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("How temperature and humidity affect fire risk (hover over points)")
        
        import plotly.express as px #for interactive features
        
        scatter_data = df_filtered[
            df_filtered['air_temperature'].notna() & 
            df_filtered['rel_humidity'].notna()
        ].copy()
        
        if len(scatter_data) > 0:
            fig = px.scatter(
                scatter_data,
                x='air_temperature',
                y='rel_humidity',
                color='fire_risk_band',
                color_discrete_map={
                    'Low': 'green',
                    'Moderate': 'orange',
                    'High': 'darkorange',
                    'Extreme': 'red'
                },
                hover_data={
                    'station_name': True,
                    'air_temperature': ':.1f',
                    'rel_humidity': ':.0f',
                    'fire_risk_score': ':.2f',
                    'fire_risk_band': False
                },
                labels={
                    'air_temperature': 'Temperature (°C)',
                    'rel_humidity': 'Humidity (%)',
                    'fire_risk_band': 'Risk Band'
                },
                title='Temperature vs Humidity by Risk',
                height=500
            )
            
            fig.update_layout(
                legend=dict(font=dict(color="black"))
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for selected filters")
    
    with col2:
        st.caption("Wind speed distribution by risk level")
        
        # Boxplot
        fig, ax = plt.subplots(figsize=(7, 5))
        
        wind_data = df_filtered[df_filtered['wind_spd_kmh'].notna()]
        
        if len(wind_data) > 0:
            sns.boxplot(data=wind_data, x='fire_risk_band', y='wind_spd_kmh',
                       order=['Low', 'Moderate', 'High', 'Extreme'],
                       palette=['green', 'orange', 'darkorange', 'red'], ax=ax)
            
            ax.set_xlabel("Risk Band", fontsize=11)
            ax.set_ylabel("Wind Speed (km/h)", fontsize=11)
            ax.set_title("Wind Speed by Risk Level", fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top stations table
    top_n = st.selectbox(
        "Top N Stations",
        options=[10, 15, 20, 50, 100, 150],
        index=1,
        help="Number of stations to show in table"
    )
    st.subheader(f"📋 Top {top_n} High-Risk Stations")

    top_stations = create_top_stations_table(
        df_filtered,
        score_col='fire_risk_score',
        band_col='fire_risk_band',
        n=top_n,
        columns=['station_name', 'air_temperature', 'rel_humidity',
                'wind_spd_kmh', 'fire_risk_score', 'fire_risk_band']
    )
    
    st.dataframe(top_stations, use_container_width=True, hide_index=True)