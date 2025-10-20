"""
Transforms Module
Calculates derived metrics and risk scores from BOM observation data.

Metrics:
1. Fire Risk Score (DFES) - temperature, humidity, wind-based
2. Rainfall Accumulations (WA SES) - intensity and rolling sums
3. Coastal Exposure Score (SLSWA) - wind and gust-based
"""

import pandas as pd
import numpy as np


# =============================================================================
# CONFIGURATION: RISK BANDS
# =============================================================================

RISK_BANDS = [
    (float('-inf'), 0.0, 'Low'),
    (0.0, 0.8, 'Moderate'),
    (0.8, 1.6, 'High'),
    (1.6, float('inf'), 'Extreme'),
]

# =============================================================================
# CONFIGURATION: WEATHER ICONS
# =============================================================================

WEATHER_ICON_MAP = {
    # Sunny/Clear
    1: '☀️',    # Sunny
    2: '🌤️',   # Clear
    3: '⛅',    # Partly cloudy
    4: '☁️',    # Cloudy
    
    # Overcast
    6: '☁️',    # Overcast
    
    # Showers/Rain
    8: '🌦️',   # Light shower
    9: '🌦️',   # Shower
    10: '🌧️',  # Light rain
    11: '🌧️',  # Rain
    12: '🌧️',  # Heavy rain
    13: '⛈️',  # Storm
    14: '⛈️',  # Light shower (thunderstorm)
    15: '⛈️',  # Shower (thunderstorm)
    16: '⛈️',  # Storm (heavy)
    17: '⛈️',  # Heavy shower (thunderstorm)
    18: '🧊',  # Hail
    19: '💨',  # Windy
    20: '🌫️',  # Fog
    21: '🌫️',  # Haze
    22: '🌫️',  # Smoke
    23: '🌫️',  # Dust
    24: '❄️',  # Frost
    25: '🌨️',  # Snow
    26: '🌀',  # Tropical cyclone
}

DEFAULT_WEATHER_ICON = '🌡️'


# =============================================================================
# CONFIGURATION: ALERT THRESHOLDS
# =============================================================================

VISIBILITY_ALERT_THRESHOLD = 10  # km
PRESSURE_ALERT_DEVIATION = -3.0  # hPa below mean
RAINFALL_THRESHOLD = 0.0  # mm


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_weather_emoji(icon_code):
    """
    Convert BOM icon code to weather emoji.
    
    Uses official BOM icon codes from:
    https://reg.bom.gov.au/info/forecast_icons.shtml
    
    Args:
        icon_code: BOM weather icon code (numeric, can be None/NaN)
        
    Returns:
        str: Weather emoji
    """
    if pd.isna(icon_code):
        return "❓"
    
    # Convert to integer
    try:
        numeric_code = int(float(icon_code))
        return WEATHER_ICON_MAP.get(numeric_code, DEFAULT_WEATHER_ICON)
    except (ValueError, TypeError):
        # If conversion fails, return default
        return DEFAULT_WEATHER_ICON


def calculate_zscore(series):
    """
    Calculate z-scores for a pandas Series, handling missing values.
    
    Z-score = (value - mean) / std_dev
    
    Args:
        series (pd.Series): Input values
        
    Returns:
        pd.Series: Z-scores (same length, NaN where input is NaN)
    """
    if series.isna().all():
        return pd.Series(np.nan, index=series.index)
    
    mean = series.mean()
    std = series.std()
    
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    
    return (series - mean) / std


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def calculate_zscore(series):
    """
    Calculate z-scores for a pandas Series, handling missing values.
    
    Z-score = (value - mean) / std_dev
    
    Args:
        series (pd.Series): Input values
        
    Returns:
        pd.Series: Z-scores (same length, NaN where input is NaN)
    """
    if series.isna().all():
        return pd.Series(np.nan, index=series.index)
    
    mean = series.mean()
    std = series.std()
    
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    
    return (series - mean) / std


def assign_risk_band(score):
    """
    Assign risk band based on score value.
    
    Uses global RISK_BANDS configuration.
    
    Args:
        score (float): Risk score value
        
    Returns:
        str: Risk band name ('Low', 'Moderate', 'High', 'Extreme', or 'Unknown')
    """
    if pd.isna(score):
        return 'Unknown'
    
    for lower, upper, band in RISK_BANDS:
        if lower <= score < upper:
            return band
    
    return 'Unknown'


def calculate_risk_score(df, score_col, band_col, formula_fn):
    """
    Generic function to calculate risk score and assign bands.
    
    This reduces code duplication between fire risk and coastal exposure.
    
    Args:
        df (pd.DataFrame): Input data
        score_col (str): Name for score column
        band_col (str): Name for band column
        formula_fn (callable): Function that takes df and returns score series
        
    Returns:
        pd.DataFrame: df with added score and band columns
    """
    df = df.copy()
    df[score_col] = formula_fn(df)
    df[band_col] = df[score_col].apply(assign_risk_band)
    return df


# =============================================================================
# 1. FIRE RISK SCORE (DFES)
# =============================================================================

def calculate_fire_risk(df):
    """
    Calculate fire risk score based on temperature, humidity, and wind.
    
    Formula:
        fire_risk_score = z(temp) - z(humidity) + 0.5 * z(wind)
    
    Higher temps, lower humidity, and stronger winds increase fire risk.
    
    Risk Bands: Low < 0.0, Moderate 0.0-0.8, High 0.8-1.6, Extreme > 1.6
    
    Args:
        df (pd.DataFrame): Observations with air_temperature, rel_humidity, wind_spd_kmh
        
    Returns:
        pd.DataFrame: Original df with fire_risk_score and fire_risk_band columns
    """
    def fire_formula(df):
        z_temp = calculate_zscore(df['air_temperature'])
        z_humidity = calculate_zscore(df['rel_humidity'])
        z_wind = calculate_zscore(df['wind_spd_kmh'])
        return z_temp - z_humidity + 0.5 * z_wind
    
    return calculate_risk_score(df, 'fire_risk_score', 'fire_risk_band', fire_formula)


# =============================================================================
# 2. RAINFALL METRICS (WA SES)
# =============================================================================

def calculate_rainfall_metrics(df):
    """
    Calculate rainfall intensity and estimated accumulations.
    
    Since we only have snapshot data (not time-series), we estimate:
    - rain_intensity_mmh: mm/hour (assumes 10-min period)
    - rain_1h_est: 1-hour accumulation estimate
    - rain_24h: 24-hour accumulation (from rainfall column)
    
    Args:
        df (pd.DataFrame): Observations with rainfall column
        
    Returns:
        pd.DataFrame: Original df with rainfall metrics
    """
    df = df.copy()
    
    # Assume rainfall is over ~10 min = 1/6 hour
    df['rain_intensity_mmh'] = df['rainfall'] * 6.0
    df['rain_1h_est'] = df['rainfall']
    df['rain_24h'] = df['rainfall']
    
    return df


def detect_pressure_drops(df, threshold_hpa=-3.0):
    """
    Flag stations with low pressure (storm indicator).
    
    Note: With snapshot data only, we flag based on absolute low pressure
    relative to mean. Ideally needs historical data for pressure change rate.
    
    Args:
        df (pd.DataFrame): Observations with msl_pres
        threshold_hpa (float): Pressure below mean + threshold triggers alert
        
    Returns:
        pd.DataFrame: Original df with pressure_alert column (bool)
    """
    df = df.copy()
    
    mean_pressure = df['msl_pres'].mean()
    df['pressure_alert'] = df['msl_pres'] < (mean_pressure + threshold_hpa)
    df.loc[df['msl_pres'].isna(), 'pressure_alert'] = False
    
    return df


# =============================================================================
# 3. COASTAL EXPOSURE SCORE (SLSWA)
# =============================================================================

def calculate_coastal_exposure(df):
    """
    Calculate coastal exposure score based on wind and gusts.
    
    Formula:
        exposure_score = z(wind_speed) + 0.7 * z(gust_speed)
    
    Higher winds and gusts indicate more hazardous coastal conditions.
    
    Risk Bands: Low < 0.0, Moderate 0.0-0.8, High 0.8-1.6, Extreme > 1.6
    
    Args:
        df (pd.DataFrame): Observations with wind_spd_kmh, gust_kmh
        
    Returns:
        pd.DataFrame: Original df with exposure_score and exposure_band columns
    """
    def exposure_formula(df):
        z_wind = calculate_zscore(df['wind_spd_kmh'])
        z_gust = calculate_zscore(df['gust_kmh'])
        return z_wind + 0.7 * z_gust
    
    return calculate_risk_score(df, 'exposure_score', 'exposure_band', exposure_formula)


# =============================================================================
# MASTER TRANSFORM FUNCTION
# =============================================================================

def apply_all_transforms(df):
    """
    Apply all transformations to observation data.
    
    This is the main function to call - it applies all metrics needed
    for DFES, WA SES, and SLSWA dashboards.
    
    Args:
        df (pd.DataFrame): Raw observations from bom_ingest.get_observations()
        
    Returns:
        pd.DataFrame: Transformed data with all derived metrics
    """
    df = df.copy()
    
    df = calculate_fire_risk(df)
    df = calculate_rainfall_metrics(df)
    df = detect_pressure_drops(df)
    df = calculate_coastal_exposure(df)
    
    return df


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

def get_summary_for_score(df, score_col, band_col, station_col='station_name'):
    """
    Generic summary statistics for a risk score.
    
    Reduces code duplication across fire risk and coastal exposure summaries.
    
    Args:
        df (pd.DataFrame): Transformed data
        score_col (str): Name of score column
        band_col (str): Name of band column
        station_col (str): Name of station column
        
    Returns:
        dict: Summary statistics
    """
    if df.empty or score_col not in df.columns:
        return {}
    
    valid = df[df[score_col].notna()].copy()
    
    if valid.empty:
        return {'error': f'No valid {score_col} data'}
    
    max_idx = valid[score_col].idxmax()
    highest = valid.loc[max_idx]
    band_counts = valid[band_col].value_counts().to_dict()
    
    return {
        'highest_station': highest[station_col],
        'highest_score': highest[score_col],
        'highest_band': highest[band_col],
        'mean_score': valid[score_col].mean(),
        'band_counts': band_counts,
        'stations_with_data': len(valid)
    }


def get_fire_risk_summary(df):
    """
    Get summary statistics for fire risk.
    
    Returns:
        dict: Summary with highest risk station, mean score, band counts
    """
    summary = get_summary_for_score(df, 'fire_risk_score', 'fire_risk_band')
    
    # Rename keys for backward compatibility
    if 'highest_station' in summary:
        summary['highest_risk_station'] = summary.pop('highest_station')
        summary['highest_risk_score'] = summary.pop('highest_score')
        summary['highest_risk_band'] = summary.pop('highest_band')
    
    return summary


def get_rainfall_summary(df):
    """
    Get summary statistics for rainfall.
    
    Returns:
        dict: Summary with heaviest rain, max gust, pressure alerts
    """
    if df.empty or 'rainfall' not in df.columns:
        return {}
    
    rain_stations = df[df['rainfall'] > 0].copy()
    
    summary = {
        'stations_with_rain': len(rain_stations),
        'max_rainfall': df['rainfall'].max() if not df['rainfall'].isna().all() else 0,
        'max_gust': df['gust_kmh'].max() if not df['gust_kmh'].isna().all() else 0,
    }
    
    if not rain_stations.empty:
        max_rain_idx = rain_stations['rainfall'].idxmax()
        summary['heaviest_rain_station'] = rain_stations.loc[max_rain_idx, 'station_name']
        summary['heaviest_rain_amount'] = rain_stations.loc[max_rain_idx, 'rainfall']
    
    if 'pressure_alert' in df.columns:
        summary['pressure_alerts'] = df['pressure_alert'].sum()
    
    return summary


def get_coastal_summary(df):
    """
    Get summary statistics for coastal exposure.
    
    Returns:
        dict: Summary with highest exposure, visibility issues, band counts
    """
    summary = get_summary_for_score(df, 'exposure_score', 'exposure_band')
    
    # Rename keys for backward compatibility
    if 'highest_station' in summary:
        summary['highest_exposure_station'] = summary.pop('highest_station')
        summary['highest_exposure_score'] = summary.pop('highest_score')
        summary['highest_exposure_band'] = summary.pop('highest_band')
    
    # Add visibility count
    if not df.empty and 'vis_km' in df.columns:
        summary['low_visibility_count'] = len(df[(df['vis_km'] < 10) & (df['vis_km'].notna())])
    
    return summary