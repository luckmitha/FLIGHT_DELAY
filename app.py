from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'flight_delay_lgbm_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, 'feature_columns.json'), 'r') as f:
    feature_columns = json.load(f)

CARRIERS = ['AA','DL','UA','WN','B6','AS','NK','F9','HA','G4','OO','YX','MQ','OH','YV','VX','EV']
AIRPORTS = ['ATL','DFW','CLT','SFO','IAH','LAS','DTW','SEA','ORD','OTHER']

CARRIER_NAMES = {
    'AA': 'American Airlines', 'DL': 'Delta Air Lines', 'UA': 'United Airlines',
    'WN': 'Southwest Airlines', 'B6': 'JetBlue', 'AS': 'Alaska Airlines',
    'NK': 'Spirit Airlines', 'F9': 'Frontier Airlines', 'HA': 'Hawaiian Airlines',
    'G4': 'Allegiant Air', 'OO': 'SkyWest Airlines', 'YX': 'Republic Airways',
    'MQ': 'Envoy Air', 'OH': 'PSA Airlines', 'YV': 'Mesa Airlines',
    'VX': 'Virgin America', 'EV': 'ExpressJet'
}

AIRPORT_NAMES = {
    'ATL': 'Atlanta', 'DFW': 'Dallas–Fort Worth', 'CLT': 'Charlotte',
    'SFO': 'San Francisco', 'IAH': 'Houston', 'LAS': 'Las Vegas',
    'DTW': 'Detroit', 'SEA': 'Seattle', 'ORD': 'Chicago O\'Hare', 'OTHER': 'Other airport'
}


@app.route('/')
def home():
    return render_template(
        'index.html',
        carriers=CARRIERS,
        airports=AIRPORTS,
        carrier_names=CARRIER_NAMES,
        airport_names=AIRPORT_NAMES
    )


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    month = int(data['month'])
    day_of_week = int(data['day_of_week'])
    hour = int(data['hour'])
    distance = float(data['distance'])
    carrier = data['carrier']
    origin = data['origin']
    dest = data['dest']

    row = pd.DataFrame([[0] * len(feature_columns)], columns=feature_columns)
    row['month'] = month
    row['day_of_week'] = day_of_week
    row['hour'] = hour
    row['DISTANCE'] = distance

    for prefix, val in [('OP_CARRIER_', carrier), ('ORIGIN_', origin), ('DEST_', dest)]:
        col = f'{prefix}{val}'
        if col in row.columns:
            row[col] = 1

    prob = float(model.predict_proba(row)[:, 1][0])
    is_delayed = prob > 0.20

    return jsonify({
        'probability': round(prob * 100, 1),
        'is_delayed': is_delayed,
        'status': 'Likely Delayed' if is_delayed else 'Likely On Time'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
