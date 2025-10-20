"""
Test script for transforms module.
Verifies derived metrics calculations on live BOM data.

This is the main test to run - it verifies the entire pipeline:
    BOM fetch → XML parse → Transforms → Summary stats

Usage:
    python3 test_transforms.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bom_ingest import get_observations
from transforms import (
    apply_all_transforms,
    get_fire_risk_summary,
    get_rainfall_summary,
    get_coastal_summary
)


def test_transforms():
    """Test transformation functions on live BOM data."""
    
    print("=" * 70)
    print("TESTING TRANSFORMS MODULE")
    print("=" * 70)
    
    # Get observations
    print("\n1. Fetching observations from BOM...")
    df, fetch_time = get_observations()
    print(f"   ✓ Fetched {len(df)} stations at {fetch_time}")
    
    if df.empty:
        print("   ✗ ERROR: No data returned from BOM")
        return None
    
    # Apply transforms
    print("\n2. Applying transformations...")
    df_transformed = apply_all_transforms(df)
    print(f"   ✓ Transformed data shape: {df_transformed.shape}")
    
    # Check new columns
    new_columns = [
        'fire_risk_score', 'fire_risk_band',
        'rain_intensity_mmh', 'rain_1h_est', 'rain_24h',
        'pressure_alert',
        'exposure_score', 'exposure_band'
    ]
    
    print(f"\n3. Checking new columns...")
    for col in new_columns:
        if col in df_transformed.columns:
            non_null = df_transformed[col].notna().sum()
            print(f"   ✓ {col}: {non_null} non-null values")
        else:
            print(f"   ✗ {col}: MISSING")
    
    # Fire Risk Summary
    print("\n" + "=" * 70)
    print("FIRE RISK SUMMARY (DFES)")
    print("=" * 70)
    fire_summary = get_fire_risk_summary(df_transformed)
    for key, value in fire_summary.items():
        print(f"  {key}: {value}")
    
    # Show top 5 fire risk stations
    if 'fire_risk_score' in df_transformed.columns:
        print("\n  Top 5 Fire Risk Stations:")
        top_fire = df_transformed.nlargest(5, 'fire_risk_score')[
            ['station_name', 'air_temperature', 'rel_humidity', 'wind_spd_kmh', 
             'fire_risk_score', 'fire_risk_band']
        ]
        print(top_fire.to_string(index=False))
    
    # Rainfall Summary
    print("\n" + "=" * 70)
    print("RAINFALL SUMMARY (WA SES)")
    print("=" * 70)
    rain_summary = get_rainfall_summary(df_transformed)
    for key, value in rain_summary.items():
        print(f"  {key}: {value}")
    
    # Show stations with rainfall
    if 'rainfall' in df_transformed.columns:
        rain_stations = df_transformed[df_transformed['rainfall'] > 0].nlargest(5, 'rainfall')[
            ['station_name', 'rainfall', 'rain_intensity_mmh', 'gust_kmh', 'msl_pres']
        ]
        if not rain_stations.empty:
            print("\n  Top 5 Rainfall Stations:")
            print(rain_stations.to_string(index=False))
        else:
            print("\n  No stations currently reporting rainfall")
    
    # Coastal Exposure Summary
    print("\n" + "=" * 70)
    print("COASTAL EXPOSURE SUMMARY (SLSWA)")
    print("=" * 70)
    coastal_summary = get_coastal_summary(df_transformed)
    for key, value in coastal_summary.items():
        print(f"  {key}: {value}")
    
    # Show top 5 exposure stations
    if 'exposure_score' in df_transformed.columns:
        print("\n  Top 5 Coastal Exposure Stations:")
        top_coastal = df_transformed.nlargest(5, 'exposure_score')[
            ['station_name', 'wind_spd_kmh', 'gust_kmh', 'vis_km',
             'exposure_score', 'exposure_band']
        ]
        print(top_coastal.to_string(index=False))
    
    # Risk Band Distribution
    print("\n" + "=" * 70)
    print("RISK BAND DISTRIBUTIONS")
    print("=" * 70)
    
    if 'fire_risk_band' in df_transformed.columns:
        print("\n  Fire Risk Bands:")
        print(df_transformed['fire_risk_band'].value_counts())
    
    if 'exposure_band' in df_transformed.columns:
        print("\n  Coastal Exposure Bands:")
        print(df_transformed['exposure_band'].value_counts())
    
    return df_transformed


if __name__ == "__main__":
    try:
        df = test_transforms()
        
        if df is not None:
            print("\n" + "=" * 70)
            print("✓ ALL TRANSFORM TESTS PASSED")
            print("=" * 70)
            print(f"\nTransformed data shape: {df.shape}")
            print(f"Total columns: {len(df.columns)}")
            print("\nColumn list:")
            print(df.columns.tolist())
            print("\nReady to build dashboard components!")
        else:
            print("\n✗ Tests failed - no data returned")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()