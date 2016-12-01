import datetime, threading, json

from .channels import RedisChannel
from .config import DEFAULT_CONFIG
from .metrics import Dimension, Counter, Timer, Metrics
from .utils import get_now

class Kadabra(object):
    """Main client API for Kadabra. In conjunction with the
    :class:`~kadabra.client.MetricsCollector`, allows you to collect metrics
    from your application and queue them for publishing via a channel.

    Typically you will use like so::

        kadabra = Kadabra()
        metrics = kadabra.metrics()
        ...
        metrics.add_count("myCount", 1.0)
        ...
        metrics.set_timer("myTimer", datetime.timedelta(seconds=5))
        ...
        metrics.add_count("myCount", 1.0)
        ...
        kadabra.send(metrics.close())

    :type configuration: dict
    :param configuration: Dictionary of configuration to use in place of the
                          defaults.
    """
    def __init__(self, configuration=None):
        config = DEFAULT_CONFIG.copy()
        if configuration:
            config.update(configuration)

        default_dimensions = config.get("CLIENT_DEFAULT_DIMENSIONS", {})
        self.default_dimensions = default_dimensions

        channel_type = config["CLIENT_CHANNEL_TYPE"]
        custom_channel_args = config["CLIENT_CHANNEL_ARGS"]
        if channel_type == 'redis':
            channel_type = RedisChannel
        else:
            raise Exception("Unrecognized channel type: '%s'" % channel_type)

        channel_args = channel_type.DEFAULT_ARGS.copy()
        if custom_channel_args:
            for k,v in custom_channel_args.items():
                channel_args[k] = v

        self.channel = channel_type(**channel_args)

        self.timestamp_format = config["CLIENT_TIMESTAMP_FORMAT"]

    def metrics(self):
        """Return a :class:`~kadabra.client.MetricsCollector` initialized with
        any dimensions as specified by the default dimensions. The collector
        can be used to gather metrics from your application code.
        
        :rtype: ~kadabra.client.MetricsCollector
        :returns: A :class:`~kadabra.client.MetricsCollector` instance.
        """
        return MetricsCollector(self.timestamp_format,
                **self.default_dimensions)

    def send(self, metrics):
        """Send a :class:`Metrics` instance to this client's configured channel
        so that it can be received and published by the agent. Note that a
        Metrics instance can be retrieved from a collector by calling its
        :meth:`~kadabra.client.MetricsCollector.close` method.

        :type metrics: ~kadabra.Metrics
        :param metrics: The :class:`Metrics` instance to be published.
        """
        self.channel.send(metrics)

class MetricsCollector(object):
    """A class for collecting metrics. Once initialized, instances of this
    class collect metrics by aggregating counts and keeping track of dimensions
    and timers. Typically you won't instantiate this class directly, but rather
    retrieve an instance from the client's :meth:`~Kadabra.metrics` method.

    :class:`Counter`\s are floating point values aggregated over the lifetime
    of this object, and published as a single value (per counter name).

    :class:`Timer`\s will be a floating point value along with a unit.

    A collector instance can be used to collect metrics until it is closed by
    calling its :meth:`~kadabra.client.MetricsCollector.close` method. After
    close() has been called, this object can be safely published without the
    possibility of "losing" additional metrics between the time it is closed
    and the time it is published.

    Although collector objects are thread-safe (meaning the same object can be
    used by multiple threads), note that any threads that attempt to use a
    collector instance after it has been closed will throw an exception.

    :type timestamp_format: string
    :param timestamp_format: The format for timestamps when serializing into a
                             :class:`Metrics` instance.

    :type dimensions: dict
    :param dimensions: Any dimensions that this object should be initialized
                       with.
    """
    def __init__(self, timestamp_format, **dimensions):
        self.counters = {}
        self.timers = {}
        self.dimensions = dimensions if dimensions else {}
        self.timestamp_format = timestamp_format

        self.closed = False
        self.lock = threading.Lock()

    def set_dimension(self, name, value):
        """Set a dimension for this collector object. If it already exists, it
        will be overwritten with the new value.

        :type name: string
        :param name: The name of the dimension to set.

        :type value: string
        :param value: The value of the dimension to be set.

        :raises CollectorClosedError: If this collector object has
                                      already been closed.
        """
        self.lock.acquire()
        try:
            if self.closed:
                raise CollectorClosedError()

            self.dimensions[name] = value
        finally:
            self.lock.release()

    def add_count(self, name, value, timestamp=None, metadata=None,
            replace_timestamp=False):
        """Add a new counter to this collector object, or add the value to an
        existing counter if it already exists.

        :type name: string
        :param name: The name of the counter.

        :type value: float
        :param value: The floating point value to either initialize a new
                      counter with, or add to an existing one.

        :type timestamp: ~datetime.datetime
        :param timestamp: The timestamp to use for when this count was
                          recorded. If unspecified, defaults to now (in UTC).

        :type metadata: dict
        :param metadata: Any metadata to include with this counter as a
                        dictionary of strings to strings. These will be
                        included as unindexed fields for this counter in
                        certain metrics databases. Note that if you specify
                        this for an existing counter, it will completely
                        overwrite the existing metadata. However if you do not
                        specify it, the previous metadata for the counter will
                        remain unchanged.

        :type replace_timestamp: bool
        :param replace_timestamp: Whether to replace the exisiting timestamp
                                  for a counter if it already exists. This can
                                  be set to True if you want to update the
                                  timestamp when you add to an existing
                                  counter.

        :raises CollectorClosedError: If this collector object has
                                      already been closed.
        """
        self.lock.acquire()
        try:
            if self.closed:
                raise CollectorClosedError()

            if timestamp is None:
                timestamp = get_now()
            
            md = metadata if metadata else {}
            if name not in self.counters:
                self.counters[name] = {
                        "metadata": md,
                        "timestamp": timestamp,
                        "value": float(value)
                }
            else:
                self.counters[name]["value"] = self.counters[name]["value"] +\
                        float(value)
                if md:
                    self.counters[name]["metadata"] = md
                if replace_timestamp:
                    self.counters[name]["timestamp"] = timestamp
        finally:
            self.lock.release()

    def set_timer(self, name, value, unit, timestamp=None, metadata=None):
        """Set a timer value for this collector object using a
        :class:`~datetime.timedelta`. If it already exists, it will be
        overwritten with the new value.

        :type name: string
        :param name: The name of the timer to set.

        :type value: ~datetime.timedelta
        :param value: The value to use for the timer.

        :type unit: ~kadabra.Unit
        :param unit: The unit to use for this timer. Common units are specified
                     in :class:`kadabra.Units`.

        :type timestamp: ~datetime.datetime
        :param timestamp: The timestamp to use for when this timer was
                          recorded. If unspecified, defaults to now (in UTC).

        :type metadata: dict
        :param metadata: Any metadata to include with this timer as a
                        dictionary of strings to strings. These will be
                        included as unindexed fields for this timer in
                        certain metrics databases. Note that if you specify
                        this for an existing timer, it will completely
                        overwrite the existing metadata. However if you do not
                        specify it, the previous metadata for the timer will
                        remain unchanged.

        :raises CollectorClosedError: If this collector object has
                                      already been closed.
        """
        self.lock.acquire()
        try:
            if self.closed:
                raise CollectorClosedError()

            if timestamp is None:
                timestamp = get_now()
            md = metadata if metadata else {}

            if name not in self.timers:
                self.timers[name] = {
                        "unit": unit,
                        "metadata": md,
                        "timestamp": timestamp,
                        "value": value
                }
            else:
                self.timers[name]["unit"] = unit
                self.timers[name]["timestamp"] = timestamp
                self.timers[name]["value"] = value
                if md:
                    self.timers[name]["metadata"] = md
        finally:
            self.lock.release()

    def close(self):
        """Close this collector object and return an equivalent
        :class:`Metrics` object. After this method is called, you can no longer
        set dimensions, set timers, or add counts to this object.

        :rtype: ~kadabra.Metrics
        :returns: A :class:`Metrics` instance from the collector's dimensions,
                  counters, and timers.

        :raises CollectorClosedError: Raised if this collector object
                                      has already been closed.
        """
        self.lock.acquire()
        try:
            if self.closed:
                raise CollectorClosedError()
            self.closed = True

            dimensions = [Dimension(n, v)\
                    for n,v in self.dimensions.items()]
            counters = [Counter(n, c["timestamp"], c["metadata"], c["value"])\
                    for n,c in self.counters.items()]
            timers = [Timer(n, t["timestamp"], t["metadata"], t["value"],\
                    t["unit"]) for n,t in self.timers.items()]
            return Metrics(dimensions, counters, timers, self.timestamp_format)
        finally:
            self.lock.release()

class CollectorClosedError(BaseException):
    """Raised if you try to add metrics to or close a
    :class:`~kadabra.client.MetricsCollector` object that has already been
    closed."""
    def __init__(self):
        super(CollectorClosedError, self).__init__(\
                "MetricsCollector object has been closed")

