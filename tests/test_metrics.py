"""
    tests.metrics
    ~~~~~~~~~~~
    Definitions of basic metric classes and serialization/deserialization.

    :copyright: (c) 2016 by Alex Landau.
    :license: BSD, see LICENSE for more details.
"""

import datetime
import kadabra

from mock import MagicMock, mock

def test_dimension():
    name = "dimensionName"
    value = "dimensionValue"
    expected_serialized = {
        "name": name,
        "value": value
    }

    dimension = kadabra.Dimension(name, value)

    assert dimension.name == name
    assert dimension.value == value
    assert dimension.serialize() == expected_serialized

    deserialized = kadabra.Dimension.deserialize(expected_serialized)
    assert deserialized.name == name
    assert deserialized.value == value

def test_counter():
    name = "myCounter"
    timestamp = datetime.datetime.utcnow()
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    metadata = {"mdName": "mdValue"}
    value = 15.0

    expected_serialized = {
        "name": name,
        "timestamp": timestamp.strftime(timestamp_format),
        "metadata": metadata,
        "value": value
    }

    counter = kadabra.Counter(name, timestamp, metadata, value)

    assert counter.name == name
    assert counter.timestamp == timestamp
    assert counter.metadata == metadata
    assert counter.value == value
    assert counter.serialize(timestamp_format) == expected_serialized

    deserialized = kadabra.Counter.deserialize(expected_serialized,
            timestamp_format)
    assert deserialized.name == name
    assert deserialized.timestamp == timestamp
    assert deserialized.metadata == metadata
    assert deserialized.value == value

def test_unit():
    name = "unitName"
    seconds_offset = 25.0
    expected_serialized = {
        "name": name,
        "seconds_offset": seconds_offset
    }

    unit = kadabra.Unit(name, seconds_offset)

    assert unit.name == name
    assert unit.seconds_offset == seconds_offset
    assert unit.serialize() == expected_serialized

    deserialized = kadabra.Unit.deserialize(expected_serialized)
    assert deserialized.name == name
    assert deserialized.seconds_offset == seconds_offset

@mock.patch('kadabra.Unit.deserialize')
def test_timer(mock_deserialize):
    name = "timerName"
    timestamp = datetime.datetime.utcnow()
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    metadata = {"mdName": "mdValue"}
    value = datetime.timedelta(seconds=5)
    unit_seconds_offset = 25.0
    unit = kadabra.Unit("unitName", unit_seconds_offset)

    unit.serialize = MagicMock(return_value="unit")
    mock_deserialize.return_value = unit

    expected_serialized = {
        "name": name,
        "metadata": metadata,
        "timestamp": timestamp.strftime(timestamp_format),
        "unit": "unit",
        "value": value.total_seconds() * unit_seconds_offset
    }

    timer = kadabra.Timer(name, timestamp, metadata, value, unit)

    assert timer.name == name
    assert timer.timestamp == timestamp
    assert timer.metadata == metadata
    assert timer.value == value
    assert timer.unit == unit
    assert timer.serialize(timestamp_format) == expected_serialized

    deserialized = kadabra.Timer.deserialize(expected_serialized,
            timestamp_format)

    mock_deserialize.assert_called_with("unit")

    assert deserialized.name == name
    assert deserialized.timestamp == timestamp
    assert deserialized.metadata == metadata
    assert deserialized.value == value
    assert deserialized.unit == unit

def test_metrics_serialize():
    dimension_one = kadabra.Dimension("name", "value")
    dimension_two = kadabra.Dimension("name", "value")
    dimension_three = kadabra.Dimension("name", "value")

    dimension_one.serialize = MagicMock(return_value='dimensionOne')
    dimension_two.serialize = MagicMock(return_value='dimensionTwo')
    dimension_three.serialize = MagicMock(return_value='dimensionThree')

    counter_one = kadabra.Counter("name", "time", {}, 1.0)
    counter_two = kadabra.Counter("name", "time", {}, 1.0)
    counter_three = kadabra.Counter("name", "time", {}, 1.0)

    counter_one.serialize = MagicMock(return_value='counterOne')
    counter_two.serialize = MagicMock(return_value='counterTwo')
    counter_three.serialize = MagicMock(return_value='counterThree')

    timer_one = kadabra.Timer("name", "time", {}, "value", "unit")
    timer_two = kadabra.Timer("name", "time", {}, "value", "unit")
    timer_three = kadabra.Timer("name", "time", {}, "value", "unit")

    timer_one.serialize = MagicMock(return_value='timerOne')
    timer_two.serialize = MagicMock(return_value='timerTwo')
    timer_three.serialize = MagicMock(return_value='timerThree')

    dimensions = [dimension_one, dimension_two, dimension_three]
    counters = [counter_one, counter_two, counter_three]
    timers = [timer_one, timer_two, timer_three]

    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    serialized_at = "now"

    expected_serialized = {
        "dimensions": ['dimensionOne', 'dimensionTwo', 'dimensionThree'],
        "counters": ['counterOne', 'counterTwo', 'counterThree'],
        "timers": ['timerOne', 'timerTwo', 'timerThree'],
        "timestamp_format": timestamp_format,
        "serialized_at": serialized_at
    }

    metrics = kadabra.Metrics(dimensions, counters, timers, timestamp_format)
    assert metrics.dimensions == dimensions
    assert metrics.counters == counters
    assert metrics.timers == timers
    assert metrics.timestamp_format == timestamp_format
    assert metrics.serialized_at == None

    serialized = metrics.serialize()
    assert serialized["dimensions"] == expected_serialized["dimensions"]
    assert serialized["counters"] == expected_serialized["counters"]
    assert serialized["timers"] == expected_serialized["timers"]
    assert serialized["timestamp_format"] ==\
            expected_serialized["timestamp_format"]

    # Can't figure out how to mock utcnow() cleanly, so just make sure it
    # parses to a valid date w.r.t. the timestamp format.
    datetime.datetime.strptime(serialized["serialized_at"], timestamp_format)

    # Make sure if we specify a serialized_at we get it back
    metrics = kadabra.Metrics(dimensions, counters, timers, timestamp_format,
            "test")
    assert metrics.serialize()["serialized_at"] == "test"

# Note: multiple mock patches apply to the function args in reverse order.
@mock.patch("kadabra.Dimension.deserialize")
@mock.patch("kadabra.Counter.deserialize")
@mock.patch("kadabra.Timer.deserialize")
def test_metrics_deserialize(mock_timer_deserialize,
        mock_counter_deserialize, mock_dimension_deserialize):
    dimensions = ['dimensionOne', 'dimensionTwo', 'dimensionThree']
    counters = ['counterOne', 'counterTwo', 'counterThree']
    timers = ['timerOne', 'timerTwo', 'timerThree']

    mock_dimension_deserialize.side_effect = dimensions
    mock_counter_deserialize.side_effect = counters
    mock_timer_deserialize.side_effect = timers

    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    serialized_at = datetime.datetime.utcnow().strftime(timestamp_format)

    metrics_serialized = {
        "dimensions": dimensions,
        "counters": counters,
        "timers": timers,
        "timestamp_format": timestamp_format,
        "serialized_at": serialized_at
    }

    metrics = kadabra.Metrics.deserialize(metrics_serialized)
    assert metrics.dimensions == dimensions
    assert metrics.counters == counters
    assert metrics.timers == timers
    assert metrics.timestamp_format == timestamp_format
    assert metrics.serialized_at == serialized_at

@mock.patch("kadabra.Dimension.deserialize")
@mock.patch("kadabra.Counter.deserialize")
@mock.patch("kadabra.Timer.deserialize")
def test_metrics_deserialize_no_serialized_at(mock_timer_deserialize,
        mock_counter_deserialize, mock_dimension_deserialize):
    dimensions = ['dimensionOne', 'dimensionTwo', 'dimensionThree']
    counters = ['counterOne', 'counterTwo', 'counterThree']
    timers = ['timerOne', 'timerTwo', 'timerThree']

    mock_dimension_deserialize.side_effect = dimensions
    mock_counter_deserialize.side_effect = counters
    mock_timer_deserialize.side_effect = timers

    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    metrics_serialized = {
        "dimensions": dimensions,
        "counters": counters,
        "timers": timers,
        "timestamp_format": timestamp_format
    }

    metrics = kadabra.Metrics.deserialize(metrics_serialized)
    assert metrics.dimensions == dimensions
    assert metrics.counters == counters
    assert metrics.timers == timers
    assert metrics.timestamp_format == timestamp_format
    assert metrics.serialized_at == None
