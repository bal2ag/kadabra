import datetime

def get_now():
    return datetime.datetime.utcnow()

def get_datetime_from_timestamp_string(timestamp_string, timestamp_format):
    return datetime.datetime.strptime(timestamp_string, timestamp_format)

def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) /\
            10.0**6
