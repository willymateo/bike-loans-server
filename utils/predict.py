from sklearn.preprocessing import RobustScaler
from keras.models import load_model
import pandas as pd
import numpy as np
import os

from constants import DATETIME_FORMAT, SEQUENCE_LENGTH
from utils.sequence import create_sequences
from utils.data import df_station_1_merged

scaler = RobustScaler()

#  Load models
station_1_model = load_model(os.path.join("models", "station_1.h5"))
station_2_model = load_model(os.path.join("models", "station_2.h5"))


def predict_by_stations(station_id, df_range_allowed_time):
    df_result = pd.DataFrame(columns=["loans", "loan_datetime"])

    start_datetime = df_range_allowed_time["loan_datetime"][0]
    start_index = df_station_1_merged[df_station_1_merged["loan_datetime"] == start_datetime].index[0]
    df_sequence_range = df_station_1_merged[start_index - SEQUENCE_LENGTH : start_index +1]
    df_scaled_loans = scaler.fit_transform(pd.DataFrame(df_sequence_range["loans"]))
    sequence = create_sequences(df_scaled_loans)

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
    df_result["loan_datetime"] = df_result["loan_datetime"].dt.strftime(DATETIME_FORMAT)
    df_result.set_index("loan_datetime", inplace=True)

    return df_result
