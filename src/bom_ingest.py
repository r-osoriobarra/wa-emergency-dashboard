"""
BOM Data Ingest Module
Main entry point for fetching BOM data with Streamlit caching.

This module coordinates data fetching but delegates XML parsing
to xml_parsers.py for better code organization.

Data Sources:
- Observations: http://www.bom.gov.au/fwo/IDW60920.xml (10-min updates)
- Forecasts: http://www.bom.gov.au/fwo/IDW14199.xml (hourly updates)
"""

import streamlit as st
from xml_parsers import fetch_and_parse_observations, fetch_and_parse_forecasts


# =============================================================================
# CACHED DATA FETCHERS
# =============================================================================

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_observations():
    """
    Fetch and parse current WA observations.
    
    Cached for 10 minutes to match BOM update frequency.
    Data includes: temperature, humidity, wind, rainfall, pressure, etc.
    
    Returns:
        tuple: (pd.DataFrame, datetime)
            - DataFrame with observation data for ~145 WA stations
            - Timestamp of when data was fetched
            
    Raises:
        Exception: If fetch or parse fails (caught and displayed by Streamlit)
    """
    url = "http://www.bom.gov.au/fwo/IDW60920.xml"
    
    try:
        return fetch_and_parse_observations(url)
    except Exception as e:
        st.error(f"Error fetching observations: {str(e)}")
        # Return empty data on error
        import pandas as pd
        return pd.DataFrame(), None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_forecasts():
    """
    Fetch and parse WA town forecasts.
    
    Cached for 1 hour as forecasts update less frequently than observations.
    Data includes: min/max temps, rain probability, weather description.
    
    Returns:
        tuple: (pd.DataFrame, datetime)
            - DataFrame with forecast data for ~116 WA localities
            - Timestamp of when data was fetched
            
    Raises:
        Exception: If fetch or parse fails (caught and displayed by Streamlit)
    """
    url = "http://www.bom.gov.au/fwo/IDW14199.xml"
    
    try:
        return fetch_and_parse_forecasts(url)
    except Exception as e:
        st.error(f"Error fetching forecasts: {str(e)}")
        # Return empty data on error
        import pandas as pd
        return pd.DataFrame(), None