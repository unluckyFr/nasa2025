from datetime import timedelta
import numpy as np
import pandas as pd

# --- Public API ---

def generate_forecast(processed: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a 48-hour (2-day) daily forecast using a simple baseline:
    - If history exists, use last value + small drift informed by weather
    - Otherwise, default to mean of available data or zeros
    Returns a DataFrame with rows for D+1 and D+2 and columns including AQI and pollutants.
    """
    if processed.empty:
        return pd.DataFrame([])

    last_row = processed.tail(1).iloc[0]
    base_pm25 = float(last_row.get('PM25') or 0)
    base_no2 = float(last_row.get('NO2') or 0)
    base_o3 = float(last_row.get('O3') or 0)
    base_aqi = float(last_row.get('AQI') or 0)
    wind = float(last_row.get('wind_kph') or 0)

    # Simple heuristic: higher wind reduces pollutants slightly
    wind_factor = max(0.8, 1.0 - min(wind, 30) / 200.0)

    forecasts = []
    last_date = pd.to_datetime(last_row['date']).date()
    for i in range(1, 3):
        pm25 = max(0.0, base_pm25 * wind_factor**i)
        no2 = max(0.0, base_no2 * (0.98**i))
        o3 = max(0.0, base_o3 * (1.01**i))
        aqi = min(500.0, (pm25*4) + (no2*2) + (o3*2))
        forecasts.append({
            'date': last_date + timedelta(days=i),
            'location': last_row['location'],
            'PM25': round(pm25, 2),
            'NO2': round(no2, 2),
            'O3': round(o3, 2),
            'AQI': round(aqi, 1)
        })

    return pd.DataFrame(forecasts)
