import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# --- Public API ---

def visualize_data(processed: pd.DataFrame, forecast: pd.DataFrame, out_path: str) -> None:
    """
    Generate a simple time series plot showing historical PM2.5 and forecasted values, plus AQI.
    Saves to out_path as PNG.
    """
    plt.figure(figsize=(8,4))
    if not processed.empty:
        plt.plot(pd.to_datetime(processed['date']), processed['PM25'], label='PM2.5 (hist)')
        plt.plot(pd.to_datetime(processed['date']), processed['AQI'], label='AQI (hist)', alpha=0.6)
    if forecast is not None and not forecast.empty:
        plt.plot(pd.to_datetime(forecast['date']), forecast['PM25'], '--', label='PM2.5 (fcst)')
        plt.plot(pd.to_datetime(forecast['date']), forecast['AQI'], '--', label='AQI (fcst)', alpha=0.6)
    plt.legend()
    plt.title('Air Quality Overview')
    plt.xlabel('Date')
    plt.ylabel('Value')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
