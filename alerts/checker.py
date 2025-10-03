from typing import Dict, List
import pandas as pd

DEFAULT_THRESHOLDS = {
    'AQI': 100,  # rough threshold
    'PM25': 25,  # ug/m3 (24h WHO guideline)
    'NO2': 40,   # ug/m3 annual guideline, used as proxy
    'O3': 100    # ug/m3 8h, simplified
}

# --- Public API ---

def check_alerts(forecast: pd.DataFrame, thresholds: Dict[str, float] = DEFAULT_THRESHOLDS) -> List[dict]:
    """
    Evaluate forecast against thresholds and return list of alerts with severity.
    """
    if forecast is None or forecast.empty:
        return []
    alerts: List[dict] = []
    for _, row in forecast.iterrows():
        day_alerts = []
        for key, limit in thresholds.items():
            value = row.get(key)
            if value is not None and pd.notna(value) and float(value) > float(limit):
                day_alerts.append({
                    'metric': key,
                    'value': float(value),
                    'limit': float(limit),
                    'date': str(row.get('date'))
                })
        if day_alerts:
            alerts.extend(day_alerts)
    return alerts
