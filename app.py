from flask import Flask, request, render_template, send_file, jsonify
from datetime import datetime
import os
import pandas as pd

from data_loader.loader import load_tempo_data, load_ground_data, load_weather_data
from data_processor.processor import process_data
from forecast_engine.model import generate_forecast
from visualizer.plots import visualize_data
from alerts.checker import check_alerts, DEFAULT_THRESHOLDS

# Configure Flask to use the ui/ folders
app = Flask(__name__, template_folder="ui/templates", static_folder="ui/static")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/api/aqi', methods=['GET'])
def api_aqi():
    location = request.args.get('location', 'Boston')
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

    tempo = load_tempo_data(location, date)
    ground = load_ground_data(location, date)
    weather = load_weather_data(location, date)
    processed = process_data(tempo, ground, weather)
    forecast_df = generate_forecast(processed)
    alerts = check_alerts(forecast_df, DEFAULT_THRESHOLDS)

    def to_jsonable(df: pd.DataFrame):
        if df is None or df.empty:
            return []
        out = df.copy()
        if 'date' in out.columns:
            out['date'] = out['date'].astype(str)
        return out.replace({pd.NA: None}).to_dict(orient='records')

    current = processed.tail(1).copy()
    if not current.empty and 'date' in current.columns:
        current['date'] = current['date'].astype(str)
    current_rec = current.replace({pd.NA: None}).to_dict(orient='records')[0] if not current.empty else {}

    return jsonify({
        'location': location,
        'date': str(date),
        'current': current_rec,
        'forecast': to_jsonable(forecast_df),
        'alerts': alerts
    })


@app.route('/plot.png', methods=['GET'])
def plot_png():
    location = request.args.get('location', 'Boston')
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

    tempo = load_tempo_data(location, date)
    ground = load_ground_data(location, date)
    weather = load_weather_data(location, date)
    processed = process_data(tempo, ground, weather)
    forecast_df = generate_forecast(processed)

    out_path = os.path.join('ui', 'static', 'plot.png')
    visualize_data(processed, forecast_df, out_path)
    return send_file(out_path, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
