import kadabra
import pytest
import datetime

from mock import MagicMock, mock, call

NOW = datetime.datetime.utcnow()

class MockDatetime(datetime.datetime):
    "A fake replacement for date that can be mocked for testing."
    def __new__(cls, *args, **kwargs):
        return datetime.datetime.__new__(date, *args, **kwargs)

    @classmethod
    def utcnow(cls):
        return NOW

def test_client_ctor_unrecognized_channel():
    with pytest.raises(Exception):
        kadabra.Client(configuration={"CLIENT_CHANNEL_TYPE": "grenjiweroni"})

# http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
@mock.patch('kadabra.client.RedisChannel')
def test_client_ctor_defaults(mock_redis_channel):
    channel = "test"
    channel_default_args = {"arg1": "1", "arg2": 2}

    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    client = kadabra.Client()

    mock_redis_channel.assert_called_with(**channel_default_args)
    assert client.default_dimensions == {}
    assert client.channel == channel

@mock.patch('kadabra.client.RedisChannel')
def test_client_ctor_custom_channel_args(mock_redis_channel):
    channel = "test"
    channel_default_args = {"arg1": "1", "arg2": 2}
    channel_custom_args = {"arg2": 3}
    combined_args = channel_default_args.copy()
    combined_args.update(channel_custom_args)

    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    client = kadabra.Client(\
            configuration={"CLIENT_CHANNEL_ARGS": combined_args})

    mock_redis_channel.assert_called_with(**combined_args)
    assert client.channel == channel

@mock.patch('kadabra.client.Collector')
@mock.patch('kadabra.client.RedisChannel')
def test_client_get_collector_no_default_dimensions(mock_redis_channel,
        mock_collector):
    timestamp_format = "timestamp_format"
    expected_collector = "test_collector"
    channel = "test"
    channel_default_args = {"arg1": "1", "arg2": 2}

    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    mock_collector.return_value = expected_collector

    client = kadabra.Client(\
            configuration={"CLIENT_TIMESTAMP_FORMAT": timestamp_format})
    collector = client.get_collector()

    mock_collector.assert_called_with(timestamp_format)
    assert collector == expected_collector

@mock.patch('kadabra.client.Collector')
@mock.patch('kadabra.client.RedisChannel')
def test_client_get_collector_default_dimensions(mock_redis_channel,
        mock_collector):
    timestamp_format = "timestamp_format"
    default_dimensions = {"one": "o", "two": "t"}
    expected_collector = "test_collector"
    channel = "test"
    channel_default_args = {"arg1": "1", "arg2": 2}

    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    mock_collector.return_value = expected_collector

    client = kadabra.Client(\
            configuration={"CLIENT_DEFAULT_DIMENSIONS": default_dimensions,
                "CLIENT_TIMESTAMP_FORMAT": timestamp_format})
    collector = client.get_collector()

    mock_collector.assert_called_with(timestamp_format, **default_dimensions)
    assert collector == expected_collector

@mock.patch('kadabra.client.RedisChannel')
def test_client_send(mock_redis_channel):
    to_send = "to_send"
    channel_default_args = {"arg1": "1", "arg2": 2}

    mock_redis_channel.DEFAULT_ARGS = channel_default_args
    mock_redis_channel.send = MagicMock()
    mock_channel_instance = mock_redis_channel.return_value

    client = kadabra.Client()
    client.send(to_send)

    mock_channel_instance.send.assert_called_with(to_send)

def test_collector_ctor_no_dimensions():
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format)

    assert collector.counters == {}
    assert collector.timers == {}
    assert collector.dimensions == {}
    assert collector.closed == False
    assert hasattr(collector, "lock")

def test_collector_ctor_dimensions():
    timestamp_format = "timestamp_format"
    dimensions = {"dimensionOne": "d1", "dimensionTwo": "d2"}
    collector = kadabra.client.Collector(timestamp_format, **dimensions)

    assert collector.counters == {}
    assert collector.timers == {}
    assert collector.dimensions == dimensions
    assert collector.closed == False
    assert hasattr(collector, "lock")

class MockLock(object):
    def __init__(self):
        self.acquire = MagicMock(return_value=True)
        self.release = MagicMock(return_value=True)

def test_collector_close_closed():
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()
    collector.close()
    with pytest.raises(kadabra.client.CollectorClosedError):
        collector.close()
    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2

def test_collector_set_dimension_closed():
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()
    collector.close()
    with pytest.raises(kadabra.client.CollectorClosedError):
        collector.set_dimension("name", "value")
    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2

def test_collector_add_count_closed():
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()
    collector.close()
    with pytest.raises(kadabra.client.CollectorClosedError):
        collector.add_count("name", 1.0)
    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2

def test_collector_set_timer_closed():
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()
    collector.close()
    with pytest.raises(kadabra.client.CollectorClosedError):
        collector.set_timer("name", datetime.timedelta(seconds=5),
                kadabra.Units.MILLISECONDS)
    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2

def test_collector_set_dimension():
    dimension_name = "name"
    dimension_value = "value"
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.set_dimension(dimension_name, dimension_value)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.dimensions[dimension_name] == dimension_value

def test_collector_set_dimension_override():
    dimension_name = "name"
    dimension_value = "newValue"
    timestamp_format = "timestamp_format"
    collector = kadabra.client.Collector(timestamp_format, name="oldValue")
    collector.lock = MockLock()

    collector.set_dimension(dimension_name, dimension_value)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.dimensions[dimension_name] == dimension_value

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_add_count():
    count_name = "name"
    count_value = 1.0
    timestamp_format = "timestamp_format"

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.add_count(count_name, count_value)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.counters[count_name]["value"] == count_value
    assert collector.counters[count_name]["metadata"] == {}
    assert collector.counters[count_name]["timestamp"] == NOW

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_add_count_timestamp():
    count_name = "name"
    count_value = 1.0
    timestamp_format = "timestamp_format"
    timestamp = NOW + datetime.timedelta(seconds=30)

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.add_count(count_name, count_value, timestamp=timestamp)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.counters[count_name]["value"] == count_value
    assert collector.counters[count_name]["metadata"] == {}
    assert collector.counters[count_name]["timestamp"] == timestamp

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_add_count_metadata():
    count_name = "name"
    count_value = 1.0
    count_metadata = {"name": "value"}
    timestamp_format = "timestamp_format"

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.add_count(count_name, count_value, metadata=count_metadata)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.counters[count_name]["value"] == count_value
    assert collector.counters[count_name]["metadata"] == count_metadata
    assert collector.counters[count_name]["timestamp"] == NOW

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_add_count_existing():
    count_name = "name"
    count_value = 1.0
    timestamp_format = "timestamp_format"

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.add_count(count_name, count_value)
    collector.add_count(count_name, count_value)

    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2
    assert collector.counters[count_name]["value"] == count_value + count_value
    assert collector.counters[count_name]["metadata"] == {}
    assert collector.counters[count_name]["timestamp"] == NOW

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_add_count_existing_replace_metadata():
    count_name = "name"
    count_value = 1.0
    count_metadata = {"name": "value"}
    timestamp_format = "timestamp_format"

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.add_count(count_name, count_value, metadata=count_metadata)
    assert collector.counters[count_name]["metadata"] == count_metadata
    count_metadata_replacement = {"newName": "newValue"}
    collector.add_count(count_name, count_value,
            metadata=count_metadata_replacement)

    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2
    assert collector.counters[count_name]["value"] == count_value + count_value
    assert collector.counters[count_name]["metadata"] ==\
        count_metadata_replacement
    assert collector.counters[count_name]["timestamp"] == NOW

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_add_count_existing_replace_timestamp():
    count_name = "name"
    count_value = 1.0
    count_metadata = {"name": "value"}
    timestamp_format = "timestamp_format"
    timestamp = NOW + datetime.timedelta(seconds=30)

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.add_count(count_name, count_value)
    collector.add_count(count_name, count_value, timestamp=timestamp,
            replace_timestamp=True)

    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2
    assert collector.counters[count_name]["value"] == count_value + count_value
    assert collector.counters[count_name]["metadata"] == {}
    assert collector.counters[count_name]["timestamp"] == timestamp


@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_set_timer():
    timer_name = "name"
    timer_value = datetime.timedelta(seconds=10)
    unit = kadabra.Units.MILLISECONDS
    timestamp_format = "timestamp_format"

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.set_timer(timer_name, timer_value, unit)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.timers[timer_name]["value"] == timer_value
    assert collector.timers[timer_name]["unit"] == unit
    assert collector.timers[timer_name]["metadata"] == {}
    assert collector.timers[timer_name]["timestamp"] == NOW

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_set_timer_timestamp():
    timer_name = "name"
    timer_value = datetime.timedelta(seconds=10)
    unit = kadabra.Units.MILLISECONDS
    timestamp_format = "timestamp_format"
    timestamp = NOW + datetime.timedelta(seconds=30)

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.set_timer(timer_name, timer_value, unit, timestamp=timestamp)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.timers[timer_name]["value"] == timer_value
    assert collector.timers[timer_name]["unit"] == unit
    assert collector.timers[timer_name]["metadata"] == {}
    assert collector.timers[timer_name]["timestamp"] == timestamp

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_set_timer_metadata():
    timer_name = "name"
    timer_value = datetime.timedelta(seconds=10)
    unit = kadabra.Units.MILLISECONDS
    timestamp_format = "timestamp_format"
    metadata = {"name": "value"}

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.set_timer(timer_name, timer_value, unit, metadata=metadata)

    assert len(collector.lock.acquire.mock_calls) == 1
    assert len(collector.lock.release.mock_calls) == 1
    assert collector.timers[timer_name]["value"] == timer_value
    assert collector.timers[timer_name]["unit"] == unit
    assert collector.timers[timer_name]["metadata"] == metadata
    assert collector.timers[timer_name]["timestamp"] == NOW

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_set_timer_existing():
    timer_name = "name"
    timer_value = datetime.timedelta(seconds=10)
    unit = kadabra.Units.MILLISECONDS
    timestamp_format = "timestamp_format"
    timestamp = NOW + datetime.timedelta(seconds=30)

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.set_timer(timer_name, timer_value, unit)
    unit_replacement = kadabra.Units.SECONDS
    timer_value_replacement = datetime.timedelta(seconds=20)
    collector.set_timer(timer_name, timer_value_replacement, unit_replacement,
            timestamp=timestamp)

    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2
    assert collector.timers[timer_name]["value"] == timer_value_replacement
    assert collector.timers[timer_name]["unit"] == unit_replacement
    assert collector.timers[timer_name]["metadata"] == {}
    assert collector.timers[timer_name]["timestamp"] == timestamp

@mock.patch('kadabra.client.datetime.datetime', MockDatetime)
def test_collector_set_timer_existing_replace_metadata():
    timer_name = "name"
    timer_value = datetime.timedelta(seconds=10)
    unit = kadabra.Units.MILLISECONDS
    metadata = {"name": "value"}
    timestamp_format = "timestamp_format"
    timestamp = NOW + datetime.timedelta(seconds=30)

    collector = kadabra.client.Collector(timestamp_format)
    collector.lock = MockLock()

    collector.set_timer(timer_name, timer_value, unit, metadata=metadata)
    unit_replacement = kadabra.Units.SECONDS
    timer_value_replacement = datetime.timedelta(seconds=20)
    metadata_replacement = {"newName": "newValue"}
    collector.set_timer(timer_name, timer_value_replacement, unit_replacement,
            timestamp=timestamp, metadata=metadata_replacement)

    assert len(collector.lock.acquire.mock_calls) == 2
    assert len(collector.lock.release.mock_calls) == 2
    assert collector.timers[timer_name]["value"] == timer_value_replacement
    assert collector.timers[timer_name]["unit"] == unit_replacement
    assert collector.timers[timer_name]["metadata"] == metadata_replacement
    assert collector.timers[timer_name]["timestamp"] == timestamp

# TODO: Test close() with mocked counters, timers, dimensions.
