import pandas as pd
import numpy as np
#risk bands
RISK_BANDS = [
    (float('-inf'), 0.0, 'Low'),
    (0.0, 0.8, 'Moderate'),
    (0.8, 1.6, 'High'),
    (1.6, float('inf'), 'Extreme'),
]
#weather icons

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

VISIBILITY_ALERT_THRESHOLD = 10  # km
PRESSURE_ALERT_DEVIATION = -3.0  # hPa below mean
RAINFALL_THRESHOLD = 0.0  # mm


def get_weather_emoji(icon_code):
    """
    https://reg.bom.gov.au/info/forecast_icons.shtml
    
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

    if series.isna().all():
        return pd.Series(np.nan, index=series.index)
    
    mean = series.mean()
    std = series.std()
    
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    
    return (series - mean) / std

def calculate_zscore(series):

    if series.isna().all():
        return pd.Series(np.nan, index=series.index)
    
    mean = series.mean()
    std = series.std()
    
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    
    return (series - mean) / std


def assign_risk_band(score):

    if pd.isna(score):
        return 'Unknown'
    
    for lower, upper, band in RISK_BANDS:
        if lower <= score < upper:
            return band
    
    return 'Unknown'


def calculate_risk_score(df, score_col, band_col, formula_fn):

    df = df.copy()
    df[score_col] = formula_fn(df)
    df[band_col] = df[score_col].apply(assign_risk_band)
    return df

def calculate_fire_risk(df):

    def fire_formula(df):
        z_temp = calculate_zscore(df['air_temperature'])
        z_humidity = calculate_zscore(df['rel_humidity'])
        z_wind = calculate_zscore(df['wind_spd_kmh'])
        return z_temp - z_humidity + 0.5 * z_wind
    
    return calculate_risk_score(df, 'fire_risk_score', 'fire_risk_band', fire_formula)


def calculate_rainfall_metrics(df):
    df = df.copy()
    
    # Assume rainfall is over ~10 min = 1/6 hour
    df['rain_intensity_mmh'] = df['rainfall'] * 6.0
    df['rain_1h_est'] = df['rainfall']
    df['rain_24h'] = df['rainfall']
    
    return df


def detect_pressure_drops(df, threshold_hpa=-3.0):

    df = df.copy()
    
    mean_pressure = df['msl_pres'].mean()
    df['pressure_alert'] = df['msl_pres'] < (mean_pressure + threshold_hpa)
    df.loc[df['msl_pres'].isna(), 'pressure_alert'] = False
    
    return df

def calculate_coastal_exposure(df):

    def exposure_formula(df):
        z_wind = calculate_zscore(df['wind_spd_kmh'])
        z_gust = calculate_zscore(df['gust_kmh'])
        return z_wind + 0.7 * z_gust
    
    return calculate_risk_score(df, 'exposure_score', 'exposure_band', exposure_formula)

def apply_all_transforms(df):

    df = df.copy()
    
    df = calculate_fire_risk(df)
    df = calculate_rainfall_metrics(df)
    df = detect_pressure_drops(df)
    df = calculate_coastal_exposure(df)
    
    return df


def get_summary_for_score(df, score_col, band_col, station_col='station_name'):

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

    summary = get_summary_for_score(df, 'fire_risk_score', 'fire_risk_band')
    
    # Rename keys for backward compatibility
    if 'highest_station' in summary:
        summary['highest_risk_station'] = summary.pop('highest_station')
        summary['highest_risk_score'] = summary.pop('highest_score')
        summary['highest_risk_band'] = summary.pop('highest_band')
    
    return summary


def get_rainfall_summary(df):

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