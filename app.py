from flask import Flask, jsonify
from earthquake_tracker import EarthquakeTracker
from datetime import datetime
import threading
import time
import pandas as pd

app = Flask(__name__)
tracker = EarthquakeTracker()

def background_update():
    """Background task to update earthquake data periodically"""
    while True:
        try:
            print(f"[{datetime.now()}] Updating earthquake data...")
            tracker.update_historical_data()
            print(f"[{datetime.now()}] Update complete")
        except Exception as e:
            print(f"[{datetime.now()}] Error in background update: {e}")
        time.sleep(3600)  # Update every hour

@app.route('/')
def home():
    """Home page with basic info"""
    return jsonify({
        'status': 'running',
        'endpoints': {
            '/recent-earthquakes': 'Get 10 most recent earthquakes',
            '/prediction': 'Get earthquake prediction for next day'
        }
    })

@app.route('/recent-earthquakes')
def recent_earthquakes():
    """Get recent earthquake data"""
    if tracker.historical_data is None or tracker.historical_data.empty:
        return jsonify({'error': 'No data available'}), 404
    
    try:
        recent_quakes = tracker.historical_data.sort_values('time', ascending=False).head(10)
        return jsonify([{
            'time': str(row['time']),
            'magnitude': float(row['magnitude']) if pd.notna(row['magnitude']) else None,
            'location': row['place'],
            'coordinates': [float(row['latitude']), float(row['longitude'])]
        } for _, row in recent_quakes.iterrows()])
    except Exception as e:
        return jsonify({'error': f'Error processing earthquake data: {str(e)}'}), 500

@app.route('/prediction')
def get_prediction():
    """Get earthquake prediction for next day"""
    try:
        prediction = tracker.predict_next_earthquake()
        return jsonify({
            'prediction_date': str(datetime.now().date()),
            'predicted_earthquakes': prediction['predicted_earthquakes'],
            'confidence': prediction['confidence']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=background_update, daemon=True)
    update_thread.start()
    
    # Initialize data
    tracker.update_historical_data()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
