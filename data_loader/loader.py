import os
from datetime import date, timedelta
from typing import Optional
import pandas as pd
import requests

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data')

# --- Public API ---

def load_tempo_data(location: str, target_date: date) -> pd.DataFrame:
    """
    Load TEMPO satellite data for a given location and date.
    Uses sample CSV fallback for hackathon demo if API unavailable.
    Columns: date, location, NO2, PM25, O3
    """
    sample_path = os.path.join(SAMPLE_DIR, 'tempo_sample.csv')
    try:
        df = pd.read_csv(sample_path, parse_dates=['date'])
        df['date'] = df['date'].dt.date
        df = df[df['location'].str.lower() == location.lower()]
        df = df[df['date'] <= target_date]
        return df.reset_index(drop=True)
    except Exception as exc:
        print(f'[load_tempo_data] Fallback error: {exc}')
        return pd.DataFrame(columns=['date','location','NO2','PM25','O3'])


def load_ground_data(location: str, target_date: date) -> pd.DataFrame:
    """
    Load ground measurements (OpenAQ) for a given location and date.
    Uses sample CSV fallback for demo.
    Columns: date, location, PM25, PM10, NO2, O3
    """
    sample_path = os.path.join(SAMPLE_DIR, 'openaq_sample.csv')
    try:
        df = pd.read_csv(sample_path, parse_dates=['date'])
        df['date'] = df['date'].dt.date
        df = df[df['location'].str.lower() == location.lower()]
        df = df[df['date'] <= target_date]
        return df.reset_index(drop=True)
    except Exception as exc:
        print(f'[load_ground_data] Fallback error: {exc}')
        return pd.DataFrame(columns=['date','location','PM25','PM10','NO2','O3'])


def load_weather_data(location: str, target_date: date) -> pd.DataFrame:
    """
    Load weather data from a public API (or fallback CSV).
    Columns: date, location, temp_c, wind_kph, humidity, pressure_hpa
    """
    sample_path = os.path.join(SAMPLE_DIR, 'weather_sample.csv')
    try:
        df = pd.read_csv(sample_path, parse_dates=['date'])
        df['date'] = df['date'].dt.date
        df = df[df['location'].str.lower() == location.lower()]
        df = df[df['date'] <= target_date]
        return df.reset_index(drop=True)
    except Exception as exc:
        print(f'[load_weather_data] Fallback error: {exc}')
        return pd.DataFrame(columns=['date','location','temp_c','wind_kph','humidity','pressure_hpa'])
