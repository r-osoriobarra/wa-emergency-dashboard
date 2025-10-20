"""
XML Parsing Module
Handles fetching and parsing BOM XML feeds.

This module contains all XML-specific logic isolated from the main application.
If BOM changes their XML structure, modifications are needed only here.
"""

import requests
import pandas as pd
from lxml import etree
from datetime import datetime
from utils import to_float


# =============================================================================
# HTTP REQUEST CONFIGURATION
# =============================================================================

# Headers to mimic browser requests (BOM blocks requests without User-Agent)
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


# =============================================================================
# LOW-LEVEL: FETCH XML
# =============================================================================

def fetch_xml(url, timeout=10):
    """
    Fetch XML content from a URL and return parsed tree.
    
    Args:
        url (str): URL to fetch
        timeout (int): Request timeout in seconds
        
    Returns:
        lxml.etree.Element: Parsed XML root element
        
    Raises:
        Exception: If fetch fails or XML is malformed
    """
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=timeout)
        response.raise_for_status()
        
        # Parse XML with lxml
        root = etree.fromstring(response.content)
        return root
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data from {url}: {str(e)}")
    except etree.XMLSyntaxError as e:
        raise Exception(f"Failed to parse XML from {url}: {str(e)}")


# =============================================================================
# PARSE OBSERVATIONS
# =============================================================================

def parse_observations_xml(xml_root):
    """
    Parse BOM observations XML into a structured DataFrame.
    
    The BOM observations XML has a nested structure:
    <product>
      <observations>
        <station stn-id="..." stn-name="..." lat="..." lon="...">
          <period time-local="..." time-utc="...">
            <level type="surface">
              <element type="air_temperature">15.0</element>
              <element type="rel-humidity">96</element>
              ...
    
    Note: Values are in element.text, not in a 'value' attribute.
    
    Args:
        xml_root (lxml.etree.Element): Parsed XML root
        
    Returns:
        pd.DataFrame: Normalized observations with columns:
            station_id, station_name, lat, lon, time_utc, time_local,
            air_temperature, rel_humidity, wind_spd_kmh, gust_kmh,
            vis_km, msl_pres, rainfall
    """
    records = []
    
    # Navigate XML structure
    observations = xml_root.find('.//observations')
    if observations is None:
        return pd.DataFrame()
    
    for station in observations.findall('station'):
        # Extract station metadata
        station_id = station.get('bom-id', 'unknown')
        station_name = station.get('stn-name', 'Unknown')
        lat = station.get('lat', None)
        lon = station.get('lon', None)
        
        # Convert lat/lon to float, handle missing values
        try:
            lat = float(lat) if lat else None
            lon = float(lon) if lon else None
        except ValueError:
            lat, lon = None, None
        
        # Extract most recent period (typically the first one)
        period = station.find('period')
        if period is None:
            continue
            
        time_local = period.get('time-local', None)
        time_utc = period.get('time-utc', None)
        
        # Initialize record with station metadata
        record = {
            'station_id': station_id,
            'station_name': station_name,
            'lat': lat,
            'lon': lon,
            'time_local': time_local,
            'time_utc': time_utc,
        }
        
        # Extract weather elements from <level>
        level = period.find('level')
        if level is not None:
            for element in level.findall('element'):
                element_type = element.get('type', '')
                element_value = element.text  # Values are in text content, not 'value' attribute
                
                # Map element types to our column names
                if element_type == 'air_temperature':
                    record['air_temperature'] = to_float(element_value)
                elif element_type == 'rel-humidity':
                    record['rel_humidity'] = to_float(element_value)
                elif element_type == 'wind_spd_kmh':
                    record['wind_spd_kmh'] = to_float(element_value)
                elif element_type == 'gust_kmh':
                    record['gust_kmh'] = to_float(element_value)
                elif element_type == 'vis_km':
                    record['vis_km'] = to_float(element_value)
                elif element_type == 'msl_pres':
                    record['msl_pres'] = to_float(element_value)
                elif element_type == 'rainfall':
                    record['rainfall'] = to_float(element_value)
        
        records.append(record)
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Ensure all expected columns exist (fill missing with NaN)
    expected_cols = [
        'station_id', 'station_name', 'lat', 'lon', 'time_local', 'time_utc',
        'air_temperature', 'rel_humidity', 'wind_spd_kmh', 'gust_kmh',
        'vis_km', 'msl_pres', 'rainfall'
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    
    return df[expected_cols]


# =============================================================================
# PARSE FORECASTS
# =============================================================================

def parse_forecasts_xml(xml_root):
    """
    Parse BOM town forecasts XML into a structured DataFrame.
    
    Now extracts ALL forecast periods (7-8 days) instead of just the first.
    
    Args:
        xml_root (lxml.etree.Element): Parsed XML root
        
    Returns:
        pd.DataFrame: Normalized forecasts with columns:
            locality_name, area_code, fcst_time, period_index, min_temp, max_temp,
            rain_probability, precis_text, icon_code
    """
    records = []
    
    forecast_root = xml_root.find('.//forecast')
    if forecast_root is None:
        return pd.DataFrame()
    
    for area in forecast_root.findall('area'):
        locality_name = area.get('description', 'Unknown')
        area_code = area.get('aac', 'unknown')
        area_type = area.get('type', '')
        
        # We want location-type areas (towns), not districts
        if area_type != 'location':
            continue
        
        # Get ALL forecast periods (not just the first)
        periods = area.findall('forecast-period')
        
        for period in periods:
            period_index_str = period.get('index', None)
            fcst_time = period.get('start-time-local', None)
            
            # Convert period_index to int immediately
            try:
                period_index = int(period_index_str) if period_index_str is not None else None
            except (ValueError, TypeError):
                period_index = None
            
            # Initialize record
            record = {
                'locality_name': locality_name,
                'area_code': area_code,
                'fcst_time': fcst_time,
                'period_index': period_index,
            }
            
            # Extract forecast elements
            for element in period.findall('element'):
                element_type = element.get('type', '')
                
                if element_type == 'air_temperature_minimum':
                    record['min_temp'] = to_float(element.text)
                elif element_type == 'air_temperature_maximum':
                    record['max_temp'] = to_float(element.text)
                elif element_type == 'probability_of_precipitation':
                    record['rain_probability'] = to_float(element.text)
                elif element_type == 'forecast_icon_code':
                    record['icon_code'] = to_float(element.text)
            
            # Extract precis text (short weather description)
            text_elem = period.find("text[@type='precis']")
            if text_elem is not None:
                record['precis_text'] = text_elem.text
            else:
                record['precis_text'] = None
            
            records.append(record)
    
    df = pd.DataFrame(records)
    
    # Ensure all expected columns exist
    expected_cols = [
        'locality_name', 'area_code', 'fcst_time', 'period_index',
        'min_temp', 'max_temp', 'rain_probability',
        'precis_text', 'icon_code'
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    
    # Sort by locality and period
    df = df.sort_values(['locality_name', 'period_index']).reset_index(drop=True)
    
    return df[expected_cols]


# =============================================================================
# HIGH-LEVEL: FETCH AND PARSE (Public API)
# =============================================================================

def fetch_and_parse_observations(url):
    """
    Fetch and parse observations feed in one step.
    
    This is the main function called by bom_ingest.py
    
    Args:
        url (str): BOM observations feed URL
        
    Returns:
        tuple: (DataFrame, datetime) - parsed data and fetch timestamp
        
    Raises:
        Exception: If fetch or parse fails
    """
    xml_root = fetch_xml(url)
    df = parse_observations_xml(xml_root)
    fetch_time = datetime.now()
    
    return df, fetch_time


def fetch_and_parse_forecasts(url):
    """
    Fetch and parse forecasts feed in one step.
    
    This is the main function called by bom_ingest.py
    
    Args:
        url (str): BOM forecasts feed URL
        
    Returns:
        tuple: (DataFrame, datetime) - parsed data and fetch timestamp
        
    Raises:
        Exception: If fetch or parse fails
    """
    xml_root = fetch_xml(url)
    df = parse_forecasts_xml(xml_root)
    fetch_time = datetime.now()
    
    return df, fetch_time