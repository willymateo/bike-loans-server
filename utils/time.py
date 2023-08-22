from datetime import datetime, timedelta

def create_time_intervals(start_time, end_time, date_range):
    intervals = []

    for date in date_range:
        # cuando  starttime hour es mayor que endtime hour se cae
        for hour in range(start_time.hour, end_time.hour):
            time = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
            intervals.append(time)

    return intervals
