from datetime import datetime, timedelta
import pandas as pd

from constants import NOT_ALLOWED_HOURS


def create_time_intervals(start_time, end_time, date_range):
    intervals = []

    allowed_hours = pd.DataFrame(
        pd.date_range(
            start=start_time,
            end=end_time,
            freq="H",
        ),
        columns=["range_time"],
    )
    allowed_hours["only_hours"] = allowed_hours["range_time"].dt.hour
    allowed_hours = allowed_hours[~allowed_hours["only_hours"].isin(NOT_ALLOWED_HOURS)]

    for date in date_range:
        # cuando  starttime hour es mayor que endtime hour se cae
        for hour in allowed_hours["only_hours"]:
            time = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
            intervals.append(time)

    return intervals
