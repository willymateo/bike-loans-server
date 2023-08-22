from .sequence import generate_sequence, scaler
from keras.models import load_model
import pandas as pd
import numpy as np
import pathlib
import os

from constants import ALLOWED_STATIONS, DATETIME_FORMAT

#  Load models
station_1_model = load_model(os.path.join("models", "station_1.h5"))
station_2_model = load_model(os.path.join("models", "station_2.h5"))


def predict_by_stations(station_id, df_range_allowed_time):
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

        prediction = None
        if station_id == 1:
            prediction = station_1_model.predict(sequence)
        else:
            prediction = station_2_model.predict(sequence)
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

    return df_result

