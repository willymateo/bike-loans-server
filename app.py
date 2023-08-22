from flask import Flask, request, jsonify
from keras.models import load_model
from datetime import datetime
import pandas as pd
import pathlib
import os

from constants import ALLOWED_STATIONS, DATETIME_FORMAT
from utils.sequence import generate_sequence

#  Load models
station_1_model = load_model(os.path.join("models", "station_1.h5"))
station_2_model = load_model(os.path.join("models", "station_2.h5"))

app = Flask("ESPOL Bike Loans")


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
            return jsonify(
                {"error": "start_datetime must be less than end_datetime"}
            )

        are_valid_station_ids = all(
            station_id in ALLOWED_STATIONS for station_id in station_ids
        )

        if not are_valid_station_ids:
            return jsonify({"error": f"station_ids must be {ALLOWED_STATIONS}"})
        
        df_range_business_days = pd.date_range(
            start=start_datetime, end=end_datetime, freq="B"
        ).to_frame(index=False, name="loans_datetime")
        print("======================")
        print("======================")
        print(df_range_business_days)
        print("======================")
        print("======================")

        sequence, df_to_predict = generate_sequence(
            {
                "start_datetime": datetime.strptime(start_datetime, DATETIME_FORMAT),
                "end_datetime": datetime.strptime(end_datetime, DATETIME_FORMAT),
            }
        )
        print(df_to_predict)
        print(sequence)

        prediction = station_1_model.predict(sequence)
        df_prediction = pd.DataFrame(prediction)
        print(df_prediction)

        return jsonify(prediction)
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "Unexpected error"})
