"""
Components Module
Reusable Plotly visualization components for the dashboard.

Functions create interactive maps, charts, and tables that can be
used across all three dashboards (DFES, WA SES, SLSWA).
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# =============================================================================
# CONFIGURATION: COLORS
# =============================================================================

# Color scheme for risk bands (consistent across all dashboards)
RISK_COLORS = {
    'Low': '#2ecc71',       # Green
    'Moderate': '#f39c12',  # Orange
    'High': '#e67e22',      # Dark orange
    'Extreme': '#e74c3c',   # Red
    'Unknown': '#95a5a6'    # Gray
}

# Map styling
MAP_STYLE = 'open-street-map'  # Options: 'open-street-map', 'carto-positron', 'carto-darkmatter'
MAP_CENTER = {'lat': -26.0, 'lon': 121.0}  # Center of WA
MAP_ZOOM = 4.5


# =============================================================================
# 1. INTERACTIVE RISK MAP
# =============================================================================

def create_risk_map(df, score_col, band_col, title, size_col=None):
    """
    Create an interactive map showing stations colored by risk band.
    
    Args:
        df (pd.DataFrame): Data with lat, lon, station_name, and risk columns
        score_col (str): Name of score column (e.g., 'fire_risk_score')
        band_col (str): Name of band column (e.g., 'fire_risk_band')
        title (str): Map title
        size_col (str, optional): Column to use for marker size (e.g., 'wind_spd_kmh')
        
    Returns:
        plotly.graph_objects.Figure: Interactive map
    """
    # Filter out stations without coordinates or risk data
    df_map = df[df['lat'].notna() & df['lon'].notna() & df[band_col].notna()].copy()
    
    if df_map.empty:
        # Return empty map with message
        fig = go.Figure()
        fig.add_annotation(
            text="No valid location data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create hover text
    df_map['hover_text'] = df_map.apply(
        lambda row: f"<b>{row['station_name']}</b><br>" +
                    f"Risk: {row[band_col]}<br>" +
                    f"Score: {row[score_col]:.2f}" if pd.notna(row[score_col]) else 
                    f"<b>{row['station_name']}</b><br>Risk: {row[band_col]}",
        axis=1
    )
    
    # Determine marker size
    if size_col and size_col in df_map.columns:
        df_map['marker_size'] = df_map[size_col].fillna(0) / 2 + 5  # Scale for visibility
    else:
        df_map['marker_size'] = 8
    
    # Create figure
    fig = go.Figure()
    
    # Add a trace for each risk band
    for band in ['Low', 'Moderate', 'High', 'Extreme', 'Unknown']:
        df_band = df_map[df_map[band_col] == band]
        if not df_band.empty:
            fig.add_trace(go.Scattermapbox(
                lat=df_band['lat'],
                lon=df_band['lon'],
                mode='markers',
                marker=dict(
                    size=df_band['marker_size'],
                    color=RISK_COLORS[band],
                    opacity=0.8
                ),
                text=df_band['hover_text'],
                hovertemplate='%{text}<extra></extra>',
                name=band,
                showlegend=True
            ))
    
    # Update layout
    fig.update_layout(
        title=title,
        mapbox=dict(
            style=MAP_STYLE,
            center=MAP_CENTER,
            zoom=MAP_ZOOM
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )
    
    return fig


# =============================================================================
# 2. RISK BAND DISTRIBUTION CHART
# =============================================================================

def create_band_distribution(df, band_col, title):
    """
    Create a bar chart showing distribution of risk bands.
    
    Args:
        df (pd.DataFrame): Data with risk band column
        band_col (str): Name of band column
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    # Count stations per band
    band_counts = df[band_col].value_counts()
    
    # Ensure all bands are present (even if count is 0)
    all_bands = ['Low', 'Moderate', 'High', 'Extreme', 'Unknown']
    band_counts = band_counts.reindex(all_bands, fill_value=0)
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=band_counts.index,
            y=band_counts.values,
            marker_color=[RISK_COLORS[band] for band in band_counts.index],
            text=band_counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title="Risk Band",
        yaxis_title="Number of Stations",
        height=400,
        showlegend=False
    )
    
    return fig


# =============================================================================
# 3. TOP STATIONS TABLE
# =============================================================================

def create_top_stations_table(df, score_col, band_col, n=10, columns=None):
    """
    Create a formatted table of top N stations by score.
    
    Args:
        df (pd.DataFrame): Data with station and risk columns
        score_col (str): Name of score column to sort by
        band_col (str): Name of band column
        n (int): Number of top stations to show
        columns (list, optional): Specific columns to display
        
    Returns:
        pd.DataFrame: Styled dataframe for display
    """
    # Default columns if not specified
    if columns is None:
        columns = ['station_name', score_col, band_col]
    
    # Get top N stations
    df_top = df.nlargest(n, score_col)[columns].copy()
    
    # Round numeric columns
    for col in df_top.columns:
        if df_top[col].dtype in ['float64', 'float32']:
            df_top[col] = df_top[col].round(2)
    
    return df_top


# =============================================================================
# 4. METRIC COMPARISON CHART
# =============================================================================

def create_metric_scatter(df, x_col, y_col, color_col, title):
    """
    Create a scatter plot comparing two metrics, colored by risk band.
    
    Args:
        df (pd.DataFrame): Data with metrics and risk band
        x_col (str): Column name for x-axis
        y_col (str): Column name for y-axis
        color_col (str): Band column for coloring
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Scatter plot
    """
    # Filter valid data
    df_plot = df[df[x_col].notna() & df[y_col].notna()].copy()
    
    if df_plot.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid data for comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    fig = go.Figure()
    
    # Add trace for each risk band
    for band in ['Low', 'Moderate', 'High', 'Extreme', 'Unknown']:
        df_band = df_plot[df_plot[color_col] == band]
        if not df_band.empty:
            fig.add_trace(go.Scatter(
                x=df_band[x_col],
                y=df_band[y_col],
                mode='markers',
                marker=dict(
                    size=8,
                    color=RISK_COLORS[band],
                    opacity=0.6
                ),
                name=band,
                text=df_band['station_name'],
                hovertemplate='<b>%{text}</b><br>' +
                              f'{x_col}: %{{x:.1f}}<br>' +
                              f'{y_col}: %{{y:.1f}}<extra></extra>'
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    return fig


# =============================================================================
# 5. RAINFALL INTENSITY CHART
# =============================================================================

def create_rainfall_bar(df, n=15):
    """
    Create a bar chart of stations with rainfall, sorted by amount.
    
    Args:
        df (pd.DataFrame): Data with rainfall column
        n (int): Number of stations to show
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    # Filter stations with rainfall
    df_rain = df[df['rainfall'] > 0].copy()
    
    if df_rain.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No rainfall currently reported",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(height=400)
        return fig
    
    # Sort and take top N
    df_rain = df_rain.nlargest(n, 'rainfall')
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=df_rain['rainfall'],
            y=df_rain['station_name'],
            orientation='h',
            marker_color='#3498db',
            text=df_rain['rainfall'].round(1),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Rainfall: %{x:.1f} mm<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=f"Top {min(n, len(df_rain))} Stations by Rainfall",
        xaxis_title="Rainfall (mm)",
        yaxis_title="",
        height=max(400, len(df_rain) * 25),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


# =============================================================================
# 6. KPI METRICS DISPLAY
# =============================================================================

def format_kpi(label, value, unit='', delta=None):
    """
    Format a KPI metric for display.
    
    Args:
        label (str): KPI label
        value (float or int): KPI value
        unit (str): Unit of measurement
        delta (float, optional): Change from previous (for trends)
        
    Returns:
        dict: Formatted KPI data for Streamlit metric display
    """
    return {
        'label': label,
        'value': f"{value:.2f}{unit}" if isinstance(value, float) else f"{value}{unit}",
        'delta': delta
    }


def get_summary_kpis(summary_dict):
    """
    Extract key KPIs from a summary dictionary.
    
    Args:
        summary_dict (dict): Summary from get_*_summary functions
        
    Returns:
        list: List of formatted KPI dictionaries
    """
    kpis = []
    
    if 'highest_risk_station' in summary_dict:
        kpis.append({
            'label': 'Highest Risk Station',
            'value': summary_dict['highest_risk_station']
        })
        kpis.append({
            'label': 'Highest Risk Score',
            'value': f"{summary_dict['highest_risk_score']:.2f}"
        })
    
    if 'highest_exposure_station' in summary_dict:
        kpis.append({
            'label': 'Highest Exposure Station',
            'value': summary_dict['highest_exposure_station']
        })
    
    if 'stations_with_rain' in summary_dict:
        kpis.append({
            'label': 'Stations with Rain',
            'value': str(summary_dict['stations_with_rain'])
        })
    
    if 'max_rainfall' in summary_dict:
        kpis.append({
            'label': 'Max Rainfall',
            'value': f"{summary_dict['max_rainfall']:.1f} mm"
        })
    
    return kpis