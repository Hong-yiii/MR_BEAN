from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
from backend_logic import *

app = Flask(__name__)
CORS(app)

# Initialize an empty DataFrame to store lat/lon data
df = pd.DataFrame(columns=['latitude', 'longitude'])

@app.route('/data', methods=['POST'])
def handle_data():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()
        if not json_data or 'latitude' not in json_data or 'longitude' not in json_data:
            return jsonify({"error": "Latitude and Longitude data required"}), 400

        # Extract latitude and longitude from the request
        latitude = float(json_data['latitude'])
        longitude = float(json_data['longitude'])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    response_data = best_gmo_strain(latitude, longitude)

    return jsonify(response_data), 200



if __name__ == '__main__':
    app.run(debug=True, port = 5002) 

