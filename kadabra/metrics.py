import datetime

class Dimension(object):
    """Dimensions are used for grouping sets of metrics by shared components.
    They are key-value string pairs which are meant to be indexed in the
    metrics storage for ease of querying metrics.

    :type name: string
    :param name: The name of the dimension.

    :type value: string
    :param value: The value of the dimension.
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def serialize(self):
        """Serializes this dimension to a dictionary.

        :rtype: dict
        :returns: The dimension as a dictionary.
        """
        return {
            "name": self.name,
            "value": self.value
        }

    @staticmethod
    def deserialize(value):
        """Deserializes a dictionary into a :class:`~kadabra.Dimension`
        instance.

        :type value: dict
        :param value: The dictionary to deserialize into a
                      :class:`~kadabra.Dimension` instance.

        :rtype: ~kadabra.Dimension
        :returns: A dimension that the dictionary represents.
        """
        return Dimension(value["name"], value["value"])

class Metric(object):
    """Base class for all metric types. Should not be instantiated directly.

    :type name: string
    :param name: The name of the metric.

    :type timestamp: ~datetime.datetime
    :param timestamp: The timestamp of the metric.

    :type metadata: dict
    :param metadata: Metadata associated with this metric, in the form of
                     string-string key-value pairs. This metadata is meant to
                     be stored as non-indexed fields in the metrics storage.
    """
    def __init__(self, name, timestamp, metadata):
        self.name = name
        self.timestamp = timestamp
        self.metadata = metadata

class Counter(Metric):
    """A counter metric, which consists of a name and a floating-point
    value.

    :type name: string
    :param name: The name of the metric.

    :type timestamp: ~datetime.datetime
    :param timestamp: The timestamp of the metric.

    :type metadata: dict
    :param metadata: Metadata associated with this metric, in the form of
                     string-string key-value pairs. This metadata is meant to
                     be stored as non-indexed fields in the metrics storage.

    :type value: float
    :param value: The floating-point value of this counter.
    """
    def __init__(self, name, timestamp, metadata, value):
        super(Counter, self).__init__(name, timestamp, metadata)
        self.value = value

    def serialize(self, timestamp_format):
        """Serializes this counter to a dictionary.

        :type timestamp_format: string
        :param timestamp_format: The format string for this counter's timestamp.

        :rtype: dict
        :returns: The counter as a dictionary.
        """
        return {
            "name": self.name,
            "metadata": self.metadata,
            "timestamp": self.timestamp.strftime(timestamp_format),
            "value": float(self.value)
        }

    @staticmethod
    def deserialize(value, timestamp_format):
        """Deserializes a dictionary into a :class:`~kadabra.Counter`
        instance.

        :type value: dict
        :param value: The dictionary to deserialize into a
                      :class:`~kadabra.Counter` instance.

        :rtype: ~kadabra.Counter
        :returns: A counter that the dictionary represents.
        """
        return Counter(value["name"],
                datetime.datetime.strptime(value["timestamp"],
                    timestamp_format),
                value["metadata"],
                value["value"])

class Timer(Metric):
    """A timer metric representing an elapsed period of time, identified by a
    :class:`datetime.timedelta` and a :class:`~kadabra.Unit`.

    :type name: string
    :param name: The name of the timer.

    :type timestamp: ~datetime.datetime
    :param timestamp: The timestamp of the timer.

    :type metadata: dict
    :param metadata: The metadata associated with the timer.

    :type value: ~datetime.timedelta
    :param value: The value of the timer.

    :type unit: kadabra.Unit
    :param unit: The unit of the timer value.
    """
    def __init__(self, name, timestamp, metadata, value, unit):
        self.value = value
        self.unit = unit
        super(Timer, self).__init__(name, timestamp, metadata)

    def serialize(self, timestamp_format):
        """Serializes this timer to a dictionary.

        :type timestamp_format: string
        :param timestamp_format: The format string for this timer's timestamp.

        :rtype: dict
        :returns: The timer as a dictionary.
        """
        return {
            'name': self.name,
            'unit': self.unit.serialize(),
            'metadata': self.metadata,
            'timestamp': self.timestamp.strftime(timestamp_format),
            'value': self.value.total_seconds() * self.unit.seconds_offset
        }

    @staticmethod
    def deserialize(value, timestamp_format):
        """Deserializes a dictionary into a :class:`~kadabra.Timer` instance.

        :type value: dict
        :param value: The dictionary to deserialize into a
                      :class:`~kadabra.Timer` instance.

        :rtype: ~kadabra.Timer
        :returns: A timer that the dictionary represents.
        """
        unit = Unit.deserialize(value["unit"])
        seconds = value["value"] / unit.seconds_offset
        timer_value = datetime.timedelta(seconds=seconds)
        return Timer(value["name"],
                datetime.datetime.strptime(value["timestamp"],
                    timestamp_format),
                value["metadata"],
                timer_value,
                unit)

class Unit(object):
    """A unit, representing an offset from seconds. This is used by by
    :class:`kadabra.Timer`\s for unambiguous reporting of the timer's value.

    :type name: string
    :param name: The name of the unit.

    :type seconds_offset: integer
    :param seconds_offset: The offset of the unit relative to seconds.
    """
    def __init__(self, name, seconds_offset):
        self.name = name
        self.seconds_offset = seconds_offset

    def serialize(self):
        """Serializes this unit to a dictionary.

        :rtype: dict
        :returns: The unit as a dictionary.
        """
        return {
            "name": self.name,
            "seconds_offset": self.seconds_offset
        }

    @staticmethod
    def deserialize(value):
        """Deserializes a dictionary into a :class:`~kadabra.Unit` instance.

        :type value: dict
        :param value: The dictionary to deserialize into a
                      :class:`~kadabra.Unit` instance.

        :rtype: ~kadabra.Unit
        :returns: A unit that the dictionary represents.
        """
        return Unit(value["name"], value["seconds_offset"])

class Units(object):
    """Container for commonly used units."""
    #: Unit representing seconds.
    SECONDS = Unit("seconds", 1.0)

    #: Unit representing milliseconds.
    MILLISECONDS = Unit("milliseconds", 1000.0)

class Metrics(object):
    """This class encapsulates metrics which can be transported over a channel,
    and received by the agent. It should only ever be initialized (e.g.
    instances are meant to be immutable). This guarantees correct behavior with
    respect to the client (which transports the metrics) and the agent (which
    receives and publishes the metrics).

    :type dimensions: list
    :param dimensions: :class:`~kadabra.Dimension`\s for this set of metrics.

    :type counters: list
    :param counters: :class:`~kadabra.Counter`\s for this set of metrics.

    :type timers: list
    :param timers: :class:`~kadabra.Timer`\s for this set of metrics.

    :type timestamp_format: string
    :param timestamp_format: The format string for timestamps.

    :type serialized_at: string
    :param serialized_at: The timestamp string for when the metrics were
                          serialized, if they were previously serialized.
    """
    def __init__(self, dimensions, counters, timers,
            timestamp_format="%Y-%m-%dT%H:%M:%S.%fZ",
            serialized_at=None):
        self.dimensions = dimensions
        self.counters = counters
        self.timers = timers

        self.timestamp_format = timestamp_format
        self.serialized_at = serialized_at

    def serialize(self):
        """Serializes this set of metrics into a dictionary.

        :rtype: dict
        :returns: The metrics as a dictionary.
        """
        return {
            "dimensions": [d.serialize() for d in self.dimensions],
            "counters": [c.serialize(self.timestamp_format)\
                    for c in self.counters],
            "timers": [t.serialize(self.timestamp_format)\
                    for t in self.timers],
            "timestamp_format": self.timestamp_format,
            "serialized_at":  datetime.datetime.utcnow().strftime(\
                    self.timestamp_format) if self.serialized_at is None\
                    else self.serialized_at
        }

    @staticmethod
    def deserialize(value):
        """Deserializes a dictionary into a :class:`~kadabra.Metrics`
        instance.

        :type value: dict
        :param value: The dictionary to deserialize into a
                      :class:`~kadabra.Metrics` instance.

        :rtype: ~kadabra.Metrics
        :returns: A metrics that the dictionary represents.
        """
        timestamp_format = value["timestamp_format"]
        serialized_at = value["serialized_at"]\
                if "serialized_at" in value else None
        return Metrics(\
                [Dimension.deserialize(d) for d in value["dimensions"]],
                [Counter.deserialize(c, timestamp_format)\
                        for c in value["counters"]],
                [Timer.deserialize(t, timestamp_format)\
                        for t in value["timers"]],
                timestamp_format,
                serialized_at)

