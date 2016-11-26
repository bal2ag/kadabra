import kadabra
import datetime

def test_get_datetime_from_timestamp_string():
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    assert kadabra.utils.get_datetime_from_timestamp_string(
            now.strftime(timestamp_format), timestamp_format) == now
