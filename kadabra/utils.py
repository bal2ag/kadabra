def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) /\
            10.0**6
