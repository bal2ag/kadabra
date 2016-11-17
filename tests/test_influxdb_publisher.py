import kadabra
import influxdb
import datetime

from mock import MagicMock, mock

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

@mock.patch('influxdb.InfluxDBClient')
def test_ctor(mock_influxdb):
    mocked = "test"
    host = "host"
    port = 1234
    database = "db"
    timeout = 3
    mock_influxdb.return_value = mocked

    publisher = kadabra.publishers.InfluxDBPublisher(host, port, database,
            timeout)

    mock_influxdb.assert_called_with(host=host, port=port, database=database,
            timeout=timeout)
    assert publisher.client == mocked

@mock.patch('influxdb.InfluxDBClient')
def test_publish_no_points(mock_influxdb):
    mocked = "test"
    host = "host"
    port = 1234
    database = "db"
    timeout = 3
    mocked = mock_influxdb.return_value
    mocked.write_points = MagicMock()

    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    metrics = MagicMock()

    dimensionOne = MagicMock()
    dimensionOne.name = "dimensionOneName"
    dimensionOne.value = "dimensionOneValue"

    dimensionTwo = MagicMock()
    dimensionTwo.name = "dimensionTwoName"
    dimensionTwo.value = "dimensionTwoValue"

    metrics.dimensions = [dimensionOne, dimensionTwo]
    metrics.counters = []
    metrics.timers = []

    publisher = kadabra.publishers.InfluxDBPublisher(host, port, database,
            timeout)
    publisher.publish(metrics)

    publisher.client.write_points.assert_has_calls([])

@mock.patch('influxdb.InfluxDBClient')
def test_publish(mock_influxdb):
    mocked = "test"
    host = "host"
    port = 1234
    database = "db"
    timeout = 3
    mocked = mock_influxdb.return_value
    mocked.write_points = MagicMock()

    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    metrics = MagicMock()
    metrics.timestamp_format = timestamp_format

    dimensionOne = MagicMock()
    dimensionOne.name = "dimensionOneName"
    dimensionOne.value = "dimensionOneValue"

    dimensionTwo = MagicMock()
    dimensionTwo.name = "dimensionTwoName"
    dimensionTwo.value = "dimensionTwoValue"

    timerOne = MagicMock()
    timerOne.name = "timerOne"
    timerOne.value = datetime.timedelta(seconds=10);
    timerOne.timestamp = datetime.datetime.utcnow()
    timerOne.metadata = {"timerOneMdName": "timerOneMdValue"}
    timerOne.unit = MagicMock()
    timerOne.unit.name = "timerOneUnit"
    timerOne.unit.seconds_offset = 10

    timerTwo = MagicMock()
    timerTwo.name = "timerTwo"
    timerTwo.value = datetime.timedelta(seconds=20)
    timerTwo.timestamp = datetime.datetime.utcnow() +\
            datetime.timedelta(seconds=5)
    timerTwo.metadata = {"timerTwoMdName": "timerTwoMdValue"}
    timerTwo.unit = MagicMock()
    timerTwo.unit.name = "timerTwoUnit"
    timerTwo.unit.seconds_offset = 20

    counterOne = MagicMock()
    counterOne.name = "counterOne"
    counterOne.value = 1.0;
    counterOne.timestamp = datetime.datetime.utcnow()
    counterOne.metadata = {"counterOneMdName": "counterOneMdValue"}

    counterTwo = MagicMock()
    counterTwo.name = "counterTwo"
    counterTwo.value = 2.0;
    counterTwo.timestamp = datetime.datetime.utcnow() +\
            datetime.timedelta(seconds=10)
    counterTwo.metadata = {"counterTwoMdName": "counterTwoMdValue"}

    metrics.dimensions = [dimensionOne, dimensionTwo]
    metrics.counters = [counterOne, counterTwo]
    metrics.timers = [timerOne, timerTwo]

    tags = {
        dimensionOne.name: dimensionOne.value,
        dimensionTwo.name: dimensionTwo.value
    }
    expected_points = [
        {
            "measurement": timerOne.name,
            "tags": tags,
            "time": datetime.datetime.strftime(timerOne.timestamp,
                timestamp_format),
            "fields": merge_dicts(timerOne.metadata, {\
                "value": timerOne.value.total_seconds() *\
                timerOne.unit.seconds_offset,
                "unit": timerOne.unit.name})
        },
        {
            "measurement": timerTwo.name,
            "tags": tags,
            "time": datetime.datetime.strftime(timerTwo.timestamp,
                timestamp_format),
            "fields": merge_dicts(timerTwo.metadata, {\
                "value": timerTwo.value.total_seconds() *\
                timerTwo.unit.seconds_offset,
                "unit": timerTwo.unit.name})
        },
        {
            "measurement": counterOne.name,
            "tags": tags,
            "time": datetime.datetime.strftime(counterOne.timestamp,
                timestamp_format),
            "fields": merge_dicts(counterOne.metadata, {"value":
                counterOne.value})
        },
        {
            "measurement": counterTwo.name,
            "tags": tags,
            "time": datetime.datetime.strftime(counterTwo.timestamp,
                timestamp_format),
            "fields": merge_dicts(counterTwo.metadata, {"value":
                counterTwo.value})
        }
    ]

    publisher = kadabra.publishers.InfluxDBPublisher(host, port, database,
            timeout)
    publisher.publish(metrics)

    publisher.client.write_points.assert_called_with(expected_points)

