from sklearn.preprocessing import RobustScaler
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .data import df_station_1_merged, df_station_2_merged
from constants import SEQUENCE_LENGTH


scaler = RobustScaler()


def generate_sequence(data):
    end_datetime = data.get("end_datetime").replace(minute=0, second=0, microsecond=0)
    start_datetime = data.get("start_datetime").replace(
        minute=0, second=0, microsecond=0
    )

    start_index = df_station_1_merged[
        df_station_1_merged["loan_datetime"] == start_datetime
    ].index[0]
    end_index = df_station_1_merged[
        df_station_1_merged["loan_datetime"] == end_datetime
    ].index[0]

    df_sequence_range = df_station_1_merged[
        start_index - SEQUENCE_LENGTH : end_index
    ]
    df_to_predict = df_station_1_merged[start_index:end_index]

    df_scaled_loans = scaler.fit_transform(pd.DataFrame(df_sequence_range["loans"]))
    sequence = create_sequences(df_scaled_loans)

    return sequence, df_to_predict


def create_sequences(data):
    x, y = [], []

    for i in range(len(data) - SEQUENCE_LENGTH):
        x.append(data[i : i + SEQUENCE_LENGTH])
        y.append(data[i + SEQUENCE_LENGTH])

    return np.array(x)
