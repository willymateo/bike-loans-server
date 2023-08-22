from datetime import datetime, timedelta
import pandas as pd

from constants import (
    BICIESPOL_WORK_START_TIME,
    BICIESPOL_WORK_END_TIME,
    ADMISSIONS_DATASET_PATH,
    ESPOL_DATASET_PATH,
    START_CUT_DATE,
)

df_admissions = pd.read_excel(
    ADMISSIONS_DATASET_PATH, usecols=["ZONA PRESTAMO", "FECHA_PRESTAMO"]
)
df_espol = pd.read_excel(
    ESPOL_DATASET_PATH, usecols=["ZONA PRESTAMO", "FECHA_PRESTAMO"]
)

# Merge datasets
new_column_names = {
    "FECHA_PRESTAMO": "loan_datetime",
    "ZONA PRESTAMO": "station",
}
df_merged = pd.concat([df_espol, df_admissions], ignore_index=True)
df_merged.rename(columns=new_column_names, inplace=True)

#  Group loans by hour and station
df_station_1 = df_merged[df_merged["station"] == 1]
df_station_2 = df_merged[df_merged["station"] == 2]

df_station_1.loc[:, "loan_datetime"] = df_station_1["loan_datetime"].dt.floor("H")
df_grouped_1 = df_station_1.groupby("loan_datetime").size().reset_index(name="loans")

df_station_2.loc[:, "loan_datetime"] = df_station_2["loan_datetime"].dt.floor("H")
df_grouped_2 = df_station_2.groupby("loan_datetime").size().reset_index(name="loans")


# Keep only business days
def create_time_intervals(start_time, end_time, date_range):
    intervals = []
    for date in date_range:
        for hour in range(start_time.hour, end_time.hour):
            time = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
            intervals.append(time)
    return intervals


start_time = datetime.strptime(BICIESPOL_WORK_START_TIME, "%H:%M:%S").time()
end_time = datetime.strptime(BICIESPOL_WORK_END_TIME, "%H:%M:%S").time()
date_range = pd.date_range(
    start=START_CUT_DATE,
    end=df_grouped_1["loan_datetime"].max().strftime("%Y-%m-%d"),
    freq="B",
)
time_intervals = create_time_intervals(start_time, end_time, date_range)
df_station_1_filled = pd.DataFrame({"loan_datetime": time_intervals})
df_station_2_filled = pd.DataFrame({"loan_datetime": time_intervals})

df_station_1_merged = df_station_1_filled.merge(
    df_grouped_1, on="loan_datetime", how="left"
).fillna(0)
df_station_2_merged = df_station_2_filled.merge(
    df_grouped_2, on="loan_datetime", how="left"
).fillna(0)
