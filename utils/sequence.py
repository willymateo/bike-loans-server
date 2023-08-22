import pandas as pd
import numpy as np

from .data import df_station_1_merged, df_station_2_merged
from constants import SEQUENCE_LENGTH


def genereate_sequences(data):
    end_datetime = data.get("end_datetime").replace(minute=0, second=0, microsecond=0)
    start_datetime = data.get("start_datetime").replace(
        minute=0, second=0, microsecond=0
    )
    station_ids = data.get("station_ids", [])

    diff_hours = int((end_datetime - start_datetime).total_seconds() / 3600)

    for prediction_num in range(diff_hours):
        current_datetime = start_datetime + timedelta(hours=prediction_num)
        input_sequence = pd.date_range(
            current_datetime - timedelta(hours=10),
            current_datetime - timedelta(hours=1),
            freq="H",
        )

        input_data = df.loc[
            df["loan_datetime"].isin(input_sequence), "loans"
        ].values.reshape(1, 10, 1)

        prediction = model.predict(input_data)

        predictions_df = predictions_df.append(
            {"loan_datetime": current_datetime, "prediction": prediction[0][0]},
            ignore_index=True,
        )


def create_sequences(data):
    x, y = [], []

    for i in range(len(data) - SEQUENCE_LENGTH):
        x.append(data[i : i + SEQUENCE_LENGTH])
        y.append(data[i + SEQUENCE_LENGTH])

    return np.array(x), np.array(y)
