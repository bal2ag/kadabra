.. _collecting:

Collecting Metrics
==================

This section describes in detail the kinds of metrics you can gather in your
application using a :class:`~kadabra.client.Collector` which can be retrieved
via the client's :meth:`~kadabra.Client.get_collector` method, and the
semantics of using the collector. 

Dimensions
----------

:class:`~kadabra.Dimension`\s are simply key-value pairs that allow you to
categorize and label metrics based on shared traits such as "environment"
(e.g. `beta`, `prod`) or "jobType" (e.g. `notifyUsers`, `processData`)::

    >>> metrics.set_dimension("name", "value")

Dimensions will apply to all counters and timers associated with the collector.

When you use a publisher such as the
:class:`~kadabra.publishers.InfluxDBPublisher` you will publish metrics into
a database. For databases that support it, dimensions will become indexed fields
on your data, allowing you to efficiently query and filter on these dimensions.

Note that dimensions should never be tied to an "unbounded" domain of values
(like, for example, user ID). You should keep dimensions to a small domain of
known values to prevent your indexes from exploding in size.

Counters
--------

:class:`~kadabra.Counter`\s track floating point values identified by a key.
The collector's :meth:`~kadabra.client.Collector.add_count` method will create
a counter if it doesn't exist or add a value to an existing counter. Once the
collector is closed and sent, only the final value will be reported for each
counter::

    >>> metrics.add_count("myCount", 1)
    >>> metrics.add_count("myCount", 3)
    >>> closed = metrics.close()
    >>> len(closed.counters)
    1
    >>> closed.counters[0].name
    'myCount'
    >>> closed.counters[0].value
    4.0

This allows you to aggregate counts locally before publishing them as a single
metric.

Timers
------

:class:`~kadabra.Timer`\s associate a key with a :class:`~datetime.timedelta`,
along with a :class:`~kadabra.Unit` representing the offset from seconds that
the time should be reported in::

    >>> metrics.set_timer("myCount", datetime.timedelta(seconds=30),\
            kadabra.Units.MILLISECONDS)

Common units are found in :class:`~kadabra.Units`.

Timers can only be set; if you call :meth:`~kadabra.client.Collector.set_timer`
with an existing key, the timer will be overwritten with the new value.

Metadata
--------

Metadata are also simple key-value pairs, but unlike dimensions they are not
meant to be indexed in a database. They provide a way to associate additional
context with your metrics without having to pay the storage costs associated
with indexing dimensions. Metadata is particularly useful for storing keys
with highly dimensional values (e.g. the user ID associated with a particular
metric), which you wouldn't need to query/filter on later.

Metadata can be associated with individual counters or timers by passing in a
dictionary to the "metadata" argument when you record a counter or timer::

    >>> metrics.add_count("myCount", 1.0, metadata={"name", "value"})
    >>> metrics.set_timer("myCount", datetime.timedelta(seconds=30),\
            kadabra.Units.MILLISECONDS, metadata={"name", "value"})

If you specify metadata for an existing counter or timer, the previous
metadata will be `completely` replaced with the new metadata. If you have
specified previous metadata for a timer or counter and don't specify metadata
on subsequent calls to :meth:`~kadabra.client.Collector.add_count` or
:meth:`~kadabra.client.Collector.set_timer` for the same counter or timer, the
previous metadata will remain.

The way metadata is ultimately handled depends on the publisher. For example,
the :class:`~kadabra.publishers.InfluxDBPublisher` will transform the metadata
into fields for each measurement.

.. note:: Don't use `value` or `unit` for metadata keys; these are reserved and
          will be overwritten.

Timestamps
----------

Because metric data may be published some time after the metric was originally
recorded, you will want to associate the timestamp of the metric with when it
was originally created, not when it gets published/writted to a database.
Otherwise your metric data may appear delayed and inaccurate.

By default, timestamps are associated with counters when they are first
created, and timers each time they are set. You can override this behavior by
passing your own :class:`datetime.datetime` to the ``timestamp`` argument of
:meth:`~kadabra.client.Collector.add_count` or
:meth:`~kadabra.client.Collector.set_timer`, which will associate the metric
with that timestamp.

For example, if you wanted to set the timestamp for a metric to 5 minutes ago::

    >>>  metrics.add_count("myCount", 1, timestamp=\
            datetime.datetime.utcnow() - datetime.timedelta(minutes=5))

For existing timers, any time you set the timestamp it will replace whatever
timestamp already exists. However, if you try to set the timestamp for an
existing counter, it will only replace the current timestamp if you pass the
``replace_timestamp`` parameter with a value of `False`::

    >>>  metrics.add_count("myCount", 1, timestamp=datetime.datetime.utcnow(),\
            replace_timestamp=True)

Because the timestamp defaults to  "now" (in UTC) if unspecified, this allows
you to easily update the timestamp of a counter each time you add to it::

    >>> metrics.add_count("myCount", 1, replace_timestamp=True)

If you don't specify ``replace_timestamp`` the timestamp will remain at whatever
value was set when you first created the counter.
