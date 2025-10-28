"""
Data Sources:
- Observations: http://www.bom.gov.au/fwo/IDW60920.xml (10-min updates)
- Forecasts: http://www.bom.gov.au/fwo/IDW14199.xml (hourly updates)
"""

import streamlit as st
from xml_parsers import fetch_and_parse_observations, fetch_and_parse_forecasts

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_observations():
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

    url = "http://www.bom.gov.au/fwo/IDW14199.xml"
    
    try:
        return fetch_and_parse_forecasts(url)
    except Exception as e:
        st.error(f"Error fetching forecasts: {str(e)}")
        # Return empty data on error
        import pandas as pd
        return pd.DataFrame(), None