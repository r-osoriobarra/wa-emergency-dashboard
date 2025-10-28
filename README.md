# WA Emergency Services Interactive Dashboard

### ICT605 - Interactive Data Visualisation and Simulation
### Authors:
Rodrigo Osorio
Saif Qureshi
Mimansha D. Ramcharn
Xuehua Song
Akriti Simkhada


## Introduction

This guide shows how to access the WA Emergency Services Interactive Dashboard, which contains three main panels dedicated to the three stakeholder groups within the project's scope:

- DFES (Department of Fire and Emergency Services)
- WA SES (State Emergency Service)
- SLSWA (Surf Life Saving WA)

---

## How to Access

### Option 1: Accessing the Streamlit Web Platform

The dashboard is hosted on Streamlit, a free platform used for uploading and sharing data science projects.

1. Access the URL: **https://wa-emergency-services-project-ict605.streamlit.app/**
2. Navigate directly through the panel - no login or authentication required

### Option 2: Run the Project Locally

1. Download the ZIP file from the GitHub repository: **https://github.com/r-osoriobarra/wa-emergency-dashboard**
2. Open Terminal (macOS/Linux) or cmd/PowerShell (Windows) and navigate to the project folder
3. Install dependencies by running: `pip install -r requirements.txt`
4. After installation, start the application: `streamlit run app.py`
5. Open your web browser and go to: `http://localhost:8501`
6. The dashboard will automatically open and be ready for navigation

---

## Project Structure

```
bom_dashboard/
│
├── app.py                           # Main application entry point
├── requirements.txt                 # Project dependencies
├── README.md                        # Documentation
│
├── test_transforms.py               # Data pipeline tests
├── test_components.py               # Visualization tests
│
└── src/                             # Source code
    │
    ├── __init__.py
    ├── bom_ingest.py                # Connection with BOM services
    ├── xml_parsers.py               # Data preprocessing
    ├── utils.py
    ├── transforms.py                # Risk level calculation rules
    ├── components.py
    │
    └── dashboards/                  # All dashboard modules
        ├── __init__.py
        ├── summary.py               # Project overview
        ├── dfes_dashboard.py        # Fire risk monitoring
        ├── ses_dashboard.py         # Storm and rainfall alerts
        └── slswa_dashboard.py       # Coastal safety monitoring
```

### Libraries and Dependencies

| Library | Version | Usage |
|---------|---------|-------|
| Streamlit | ≥ 1.28.0 | Interactive interface, widgets, caching |
| Pandas | ≥ 2.0.0 | DataFrame manipulation |
| NumPy | ≥ 1.24.0 | Numerical operations |
| Plotly | ≥ 5.17.0 | Interactive maps, scatter plots with hover |
| Matplotlib | ≥ 3.7.0 | Histograms, bar charts |
| Seaborn | ≥ 0.12.0 | Boxplots, visual statistical analysis |
| Requests | ≥ 2.31.0 | Downloading XML files from BOM |
| lxml | ≥ 4.9.0 | XML parsing |
| statsmodels | ≥ 0.14.0 | Trendlines in Plotly |

---

## How to Navigate Dashboards

### Navigation Structure

The platform contains dashboards accessible from the sidebar navigation menu on the left:

**Summary Dashboard**
- Project overview and context

**DFES Fire Risk Dashboard**
- Fire risk map
- Score by station
- Temperature vs humidity analysis
- Factors analysis

**SES Storm Dashboard**
- Rainfall activity map
- Rainfall distribution statistics
- Wind analysis
- Atmospheric pressure analysis

**SLSWA Coastal Safety Dashboard**
- Coastal exposure map
- Exposure level distribution
- Wind conditions
- Visibility alerts

**7-Days Forecasting Dashboard**
- Extended weather forecast

### Navigation Instructions

1. All dashboards are accessible from the sidebar navigation menu
2. Each dashboard displays real-time data visualizations from BOM data feeds
3. Each dashboard is dedicated to a specific emergency service
4. Use the interactive filters and maps available on each dashboard
5. Press the "Refresh Data" button to update the data manually
6. Press the "Summary" button to return to the main panel
7. Navigate between dashboards using the sidebar links

---

## Real-Time Data

The dashboard automatically updates data every 10 minutes from the Bureau of Meteorology (BOM) data feeds. No manual refresh is required for regular updates, though you can use the "Refresh Data" button for immediate updates if needed.