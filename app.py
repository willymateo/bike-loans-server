from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import pandas as pd
import numpy as np
import pathlib
import os

from constants import ALLOWED_STATIONS, DATETIME_FORMAT
from utils.sequence import generate_sequence, scaler
from utils.predict import predict_by_stations
from utils.time import create_time_intervals

app = Flask("ESPOL Bike Loans")
CORS(app)


@app.get("/")
def home():
    return {"app": "ESPOL bike loans", "version": "1.0.0"}


@app.post("/predict")
def predict_loans():
    try:
        data = request.get_json()
        station_ids = data.get("station_ids", ALLOWED_STATIONS)
        start_datetime = data.get("start_datetime")
        end_datetime = data.get("end_datetime")

        if not start_datetime:
            return jsonify({"error": "start_datetime is required"})

        if not end_datetime:
            return jsonify({"error": "end_datetime is required"})

        if start_datetime > end_datetime:
            return jsonify({"error": "start_datetime must be less than end_datetime"})

        are_valid_station_ids = all(
            station_id in ALLOWED_STATIONS for station_id in station_ids
        )

        if not are_valid_station_ids:
            return jsonify({"error": f"station_ids must be {ALLOWED_STATIONS}"})

        start_datetime = datetime.strptime(start_datetime, DATETIME_FORMAT)
        end_datetime = datetime.strptime(end_datetime, DATETIME_FORMAT)

        date_range_business_days = pd.date_range(
            start=start_datetime, end=end_datetime, freq="B"
        ).to_frame(index=False, name="loan_datetime")

        time_intervals = create_time_intervals(
            start_datetime,
            end_datetime,
            date_range_business_days["loan_datetime"],
        )
        df_range_allowed_time = pd.DataFrame({"loan_datetime": time_intervals})
        
        stations = {}
        for station_id in station_ids:
            prediction = predict_by_stations(station_id, df_range_allowed_time)
            stations[station_id] = prediction.to_dict().get("loans")

        return jsonify({"stations": stations})
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "Unexpected error"})
