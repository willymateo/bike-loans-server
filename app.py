from flask import Flask, request, jsonify
from keras.models import load_model
from datetime import datetime
from flask_cors import CORS
import pandas as pd
import numpy as np
import pathlib
import os

from constants import ALLOWED_STATIONS, DATETIME_FORMAT
from utils.sequence import generate_sequence, scaler
from utils.time import create_time_intervals


#  Load models
station_1_model = load_model(os.path.join("models", "station_1.h5"))
station_2_model = load_model(os.path.join("models", "station_2.h5"))

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

        df_result = pd.DataFrame(columns=["loans", "loan_datetime"])

        sequence, df_sequence_range = generate_sequence(
            {
                "start_datetime": df_range_allowed_time["loan_datetime"][0],
                "end_datetime": df_range_allowed_time["loan_datetime"][1],
            }
        )

        for index_datetime in df_range_allowed_time.index[:-1]:
            start_datetime_in_sequence = df_range_allowed_time["loan_datetime"][
                index_datetime
            ]

            prediction = station_1_model.predict(sequence)
            inversed_prediction = scaler.inverse_transform(prediction)
            df_result.loc[len(df_result)] = {
                "loans": inversed_prediction[0][0],
                "loan_datetime": start_datetime_in_sequence,
            }
            new_sequence = sequence[0][1:]
            new_sequence = np.append(new_sequence, prediction)
            new_sequence = new_sequence.reshape(10, 1)
            new_sequence = new_sequence.reshape(1, 10, 1)
            sequence = new_sequence

        df_result["loans"] = round(df_result["loans"]).astype(int)
        df_result["loan_datetime"] = df_result["loan_datetime"].dt.strftime(
            DATETIME_FORMAT
        )
        df_result.set_index("loan_datetime", inplace=True)

        return jsonify(
            {
                "stations": {
                    "1": df_result.to_dict().get("loans"),
                }
            }
        )
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "Unexpected error"})
