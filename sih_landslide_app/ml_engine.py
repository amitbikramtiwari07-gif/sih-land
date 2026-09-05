import numpy as np

def calculate_landslide_risk(slope, live_rain, past_3d_rain, base_moisture):
    """
    Computes scientific Landslide Susceptibility Index (LSI) based on:
    - Terrain Steepness (GSI Slope factor)
    - Antecedent Rainfall (Past 72h accumulation)
    - Active Precipitation & Soil Moisture
    """
    # 1. Slope hazard weight (slopes > 40 deg are critical)
    slope_weight = (slope / 60.0) * 35.0
    
    # 2. Cumulative Antecedent Moisture Saturation (GSI Rainfall Threshold)
    total_effective_rain = past_3d_rain + (live_rain * 24.0)
    rain_weight = min((total_effective_rain / 200.0) * 45.0, 45.0)
    
    # 3. Moisture Factor
    moisture_weight = (base_moisture / 100.0) * 20.0
    
    # Total Composite Index (0 to 100)
    threat_index = round(min(slope_weight + rain_weight + moisture_weight, 99.0), 1)

    if threat_index >= 70.0:
        return threat_index, "Critical", "#ef233c", "error", "Severe risk of slope failure detected. Immediate alert issued. Traffic diverted."
    elif threat_index >= 45.0:
        return threat_index, "Moderate", "#f77f00", "warning", "Elevated saturation levels. Precautionary monitoring active along roadsides."
    else:
        return threat_index, "Low", "#06d6a0", "success", "Stable slope and precipitation metrics. Normal corridor operations."