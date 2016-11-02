class Dimension(object):
    """Represents dimensions for categorizing sets of metrics by shared
    components. Essentially just a string-string key-value pair.

    :param name: The name of the dimension.
    :param value: The value of the dimension.
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def serialize(self):
        return {
            "name": self.name,
            "value": self.value
        }

    @staticmethod
    def deserialize(value):
        return Dimension(value["name"], value["value"])

class Metric(object):
    """Base class for all metric types.

    :param name: The name of the metric.
    :param timestamp: The timestamp of the metric.
    :param metadata: Metadata associated with this metric, in the form of
    string-string key-value pairs. This metadata should be stored as
    non-indexed fields in the backing store.
    """
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp,
        self.metadata = metadata

class Counter(Metric):
    """A counter metric, which consists of a name and a floating-point
    value.
    
    :param name: The name of the counter.
    :param timestamp: The timestamp of the counter.
    :param metadata: The metadata associated with the counter.
    :param value: The floating-point value of the counter.
    """
    def __init__(self, name, timestamp, metadata, value):
        self.value = value
        super(self,Counter).__init__(name, timestamp, metadata)

    def serialize(self, timestamp_format):
        return {
            'name': self.name,
            'metadata': self.metadata,
            'timestamp': self.timestamp.strftime(timestamp_format),
            value: float(self.value)
        }

    @staticmethod
    def deserialize(value, timestamp_format):
        return Counter(value["name"],
                datetime.datetime.strptime(value["timestamp"],
                    timestamp_format),
                value["metadata"],
                value["value"])

class Timer(Metric):
    """A timer metric, which consists of a name and a
    :class:`datetime.timedelta`, and a :class:`Unit`.
    
    :param name: The name of the timer.
    :param timestamp: The timestamp of the timer.
    :param metadata: The metadata associated with the timer.
    :param value: The :class:`datetime.timedelta` of the timer.
    :param unit: The :class:`Unit` of the timer.
    """
    def __init__(self, name, timestamp, metadata, value, unit):
        self.value = value
        self.unit = unit
        super(self,Counter).__init__(name, timestamp, metadata)

    def serialize(self, timestamp_format):
        return {
            'unit': self.unit.name,
            'metadata': self.metadata,
            'timestamp': self.timestamp.strftime(timestamp_format),
            'value': self.value.total_seconds() * unit.seconds_offset
        }

    @staticmethod
    def deserialize(value, timestamp_format):
        return Timer(value["name"],
                datetime.datetime.strptime(value["timestamp"],
                    timestamp_format),
                value["metadata"],
                value["value"],
                Unit.deserialize(value["unit"]))

class Unit(object):
    """A unit, which is used by :class:`Timer`s.

    :param name: The name of the unit.
    :param seconds_offset: The offset of the unit relative to seconds.
    """
    def __init__(self, name, seconds_offset):
        self.name = name
        self.seconds_offset = seconds_offset

    def serialize(self):
        return {
            "name": self.name,
            "seconds_offset": self.seconds_offset
        }

    @staticmethod
    def deserialize(value):
        return Unit(value["name"], value["seconds_offset"])

class Units(object):
    """Container for commonly used units."""
    MILLISECOND = Unit("millisecond", 1000.0)

class Metrics(object):
    """This class encapsulates metrics which can be transported over a channel,
    and received by the agent. It should only ever be initialized (e.g.
    instances are meant to be immutable). This guarantees correct behavior with
    respect to the client (which transports the metrics) and the agent (which
    receives and publishes the metrics).

    :param dimensions: Dictionary of dimensions for this set of metrics
    (string-string key-value pairs), which should be indexed in the backing
    store.
    :param counters: Dictionary of counter metrics (string-float key-value
    pairs).
    :param timers: Dictionary of timer metrics (string-string key-value pairs).
    """
    VERSION = 1.0

    def __init__(self, dimensions, counters, timers,
            timestamp_format="%Y-%m-%dT%H:%M:%S.%fZ",
            serialized_at=None):
        self.dimensions = dimensions
        self.counters = counters
        self.timers = timers

        self.timestamp_format = timestamp_format
        self.serialized_at = serialized_at

    def serialize(self):
        return {
            "dimensions": [d.serialize(self.timestamp_format)\
                    for d in self.dimensions],
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
        return Metrics(\
                [Dimension.deserialize(d) for d in value["dimensions"]],
                [Counter.deserialize(c) for c in value["counters"]],
                [Timer.deserialize(t) for t in value["timers"]],
                value["timestamp_format"],
                value["serialized_at"] or None)

