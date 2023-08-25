from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from constants import ALLOWED_STATIONS, DATETIME_FORMAT
from utils.predict import predict_loan

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


        stations = {}
        for station_id in station_ids:
            prediction = predict_loan(station_id, start_datetime, end_datetime)
            prediction.set_index('loan_datetime', inplace=True)  # Establecer la columna como índice
            prediction.index = prediction.index.strftime(DATETIME_FORMAT)
            stations[station_id] = prediction['loans'].to_dict()  # Obtener el diccionario de predicciones de préstamos

        return jsonify({"stations": stations})
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "Unexpected error"})
