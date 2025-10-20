"""
Test script for components module.
Creates sample visualizations to verify Plotly functions work.

Usage:
    python3 test_components.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bom_ingest import get_observations
from transforms import apply_all_transforms
from components import (
    create_risk_map,
    create_band_distribution,
    create_top_stations_table,
    create_metric_scatter,
    create_rainfall_bar
)


def test_components():
    """Test visualization components."""
    
    print("=" * 70)
    print("TESTING COMPONENTS MODULE")
    print("=" * 70)
    
    # Get and transform data
    print("\n1. Fetching and transforming data...")
    df, _ = get_observations()
    df = apply_all_transforms(df)
    print(f"   ✓ Data ready: {len(df)} stations")
    
    # Test fire risk map
    print("\n2. Creating fire risk map...")
    fig_map = create_risk_map(
        df, 
        score_col='fire_risk_score',
        band_col='fire_risk_band',
        title='Fire Risk Map',
        size_col='wind_spd_kmh'
    )
    print(f"   ✓ Map created with {len(fig_map.data)} traces")
    
    # Test band distribution
    print("\n3. Creating band distribution chart...")
    fig_dist = create_band_distribution(
        df,
        band_col='fire_risk_band',
        title='Fire Risk Distribution'
    )
    print(f"   ✓ Distribution chart created")
    
    # Test top stations table
    print("\n4. Creating top stations table...")
    df_top = create_top_stations_table(
        df,
        score_col='fire_risk_score',
        band_col='fire_risk_band',
        n=5,
        columns=['station_name', 'fire_risk_score', 'fire_risk_band', 'air_temperature']
    )
    print(f"   ✓ Table created with {len(df_top)} rows")
    print("\n   Preview:")
    print(df_top.to_string(index=False))
    
    # Test scatter plot
    print("\n5. Creating metric scatter plot...")
    fig_scatter = create_metric_scatter(
        df,
        x_col='air_temperature',
        y_col='wind_spd_kmh',
        color_col='fire_risk_band',
        title='Temperature vs Wind Speed'
    )
    print(f"   ✓ Scatter plot created with {len(fig_scatter.data)} traces")
    
    # Test rainfall bar chart
    print("\n6. Creating rainfall bar chart...")
    fig_rain = create_rainfall_bar(df, n=10)
    print(f"   ✓ Rainfall chart created")
    
    print("\n" + "=" * 70)
    print("✓ ALL COMPONENT TESTS PASSED")
    print("=" * 70)
    print("\nAll visualization functions working correctly.")
    print("Ready to build the main Streamlit app!")
    
    return True


if __name__ == "__main__":
    try:
        test_components()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()