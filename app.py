from flask import Flask, request, jsonify
from keras.models import load_model
from datetime import datetime
import pathlib
import os

from constants import ALLOWED_STATIONS, DATETIME_FORMAT
from utils import generate_sequences

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
        start_datetime = data.get("start_datetime")
        station_ids = data.get("station_ids", [])
        end_datetime = data.get("end_datetime")

        if not start_datetime:
            return jsonify({"error": "start_datetime is required"})

        if not station_ids:
            return jsonify({"error": "station_ids is required"})

        if not end_datetime:
            return jsonify({"error": "end_datetime is required"})

        are_valid_station_ids = all(
            station_id in ALLOWED_STATIONS for station_id in station_ids
        )

        if not are_valid_station_ids:
            return jsonify({"error": f"station_ids must be {ALLOWED_STATIONS}"})

        preprocessed_data = genereate_sequences(
            {
                "start_datetime": datetime.strptime(start_datetime, DATETIME_FORMAT),
                "end_datetime": datetime.strptime(end_datetime, DATETIME_FORMAT),
                "station_ids": station_ids,
            }
        )

        prediction = model.predict(preprocessed_data)
        loans = prediction[0]

        return jsonify(loans)
    except Exception as e:
        return jsonify({"error": str(e)})
