from typing import List
import pandas as pd

# --- Public API ---

def process_data(tempo: pd.DataFrame, ground: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, validate and merge datasets on date and location.
    Produces a daily table with pollutant metrics and weather covariates.
    """
    # Basic sanity: ensure expected columns exist
    def ensure_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA
        return df

    tempo = ensure_cols(tempo.copy(), ['date','location','NO2','PM25','O3'])
    ground = ensure_cols(ground.copy(), ['date','location','PM25','PM10','NO2','O3'])
    weather = ensure_cols(weather.copy(), ['date','location','temp_c','wind_kph','humidity','pressure_hpa'])

    # Coerce date to date type if needed
    for df in (tempo, ground, weather):
        if pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = df['date'].dt.date

    # Merge with preference: ground > tempo
    merged = pd.merge(tempo, ground, on=['date','location'], how='outer', suffixes=('_tempo','_ground'))

    # Resolve PM25, NO2, O3 by preferring ground measurements when available
    def prefer_ground(row, pollutant):
        g = row.get(f"{pollutant}_ground")
        t = row.get(f"{pollutant}_tempo")
        return g if pd.notna(g) else t

    for pollutant in ['PM25','NO2','O3']:
        merged[pollutant] = merged.apply(lambda r: prefer_ground(r, pollutant), axis=1)

    # Attach weather
    merged = pd.merge(merged, weather, on=['date','location'], how='left')

    # Compute simple AQI-like index (not official): scaled sum
    def compute_simple_aqi(row):
        pm25 = row.get('PM25')
        no2 = row.get('NO2')
        o3 = row.get('O3')
        pm25 = 0 if pd.isna(pm25) else float(pm25)
        no2 = 0 if pd.isna(no2) else float(no2)
        o3 = 0 if pd.isna(o3) else float(o3)
        # Rough scaling to 0-500 domain (hackathon-grade)
        aqi = min(500.0, (pm25*4) + (no2*2) + (o3*2))
        return aqi

    merged['AQI'] = merged.apply(compute_simple_aqi, axis=1)
    merged = merged.sort_values(['date']).reset_index(drop=True)

    # Keep relevant columns
    keep = ['date','location','PM25','NO2','O3','PM10','temp_c','wind_kph','humidity','pressure_hpa','AQI']
    for col in keep:
        if col not in merged.columns:
            merged[col] = pd.NA
    return merged[keep]
