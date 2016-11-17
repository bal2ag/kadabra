.. _publishing:

Publishing Metrics
==================

Metrics are published by receiving them over the channel and calling the
publisher's **publish()** method. This functionality is handled entirely by
the :class:`~kadabra.Agent`. All you need to do is configure it and call
:meth:`~kadabra.Agent.start` from a dedicated process. This section describes
the Agent in more detail as well as the different publishers that are available
to you.

Agent
-----

The agent is a program that runs in a dedicated process. It reads metrics from
the configured channel and publishes them into the configured backing store,
completely independent of the application(s) that is/are sending metrics over
the channel.

The agent basically manages a :class:`~kadabra.agent.Receiver` and a
:class:`~kadabra.agent.Nanny`. The receiver manages a list of
:class:`~kadabra.agent.ReceiverThread`\s which poll the channel for any metrics
that need to be published. The nanny periodically queries the the channel for
any metrics that are in the process of being published, and attempts to publish
any that have been in that state for a long time (over a certain threshold of
seconds) using :class:`~kadabra.agent.NannyThread`\s.

This allows the agent to be robust to publishing failures, and be scaled
indepedently from your application (by increasing the number of receiver and
nanny threads as appropriate, depending on how often your application publishes
metrics).

One important implication from this design is that publishers should be
idempotent, meaning publishing the exact same metrics multiple times should not
impact your underlying database. For example, InfluxDB will not create a new
measurement if you publish metrics with the same timestamp, dimensions, names,
metadata, and values. This means that you will not end up with duplicated
metrics from the agent retrying to publish the same metrics multiple times.

DebugPublisher
--------------

The :class:`~kadabra.publishers.DebugPublisher` simply takes a logger name, and
will log metrics (as serialized JSON) to the logger at the INFO level. This is
useful for ensuring that your metrics are being properly calculated and
reported by your application during development, before you use a publisher
that goes to a database.

InfluxDBPublisher
-----------------

The :class:`~kadabra.publishers.InfluxDBPublisher` sends metrics to `InfluxDB
<https://www.influxdata.com/time-series-platform/influxdb/>`_, a powerful
open-source time series database. Each counter and timer will result in a
seperate measurement which has the name of the counter or timer.

For each measurement:

- Dimensions will become tags (which are indexed, making queries
  for specific dimension values extremely fast)
- Counters will have a single field called `value` with the counter value
- Timers will have two fields: `value` which contains the timer value (as the
  :class:`~datetime.timedelta` seconds multiplied by the unit's seconds offset)
  and `unit` which is the name of the unit.
- Metadata will become additional fields (each key becomes a field's name, and 
  each value becomes the field's value).

The configuration values for this publisher are:

- **host**: The host of the InfluxDB server. (Defaults to `localhost`)
- **port**: The port of the InfluxDB server. (Defaults to `8086`)
- **database**: The name of the InfluxDB database to use. Make sure you create
  this database on the server before you start sending metrics to it! (Defaults
  to `kadabra`)
- **timeout**: The timeout in seconds to wait for the InfluxDB server to respond
  before failing to publish. (Defaults to `5`)

You can overwrite any or none of these values in the ``AGENT_PUBLISHER_ARGS``
configuration key. For more information on how to configure the Agent see
:doc:`configuration`.

For a guide to use Kadabra with InfluxDB see :doc:`usingwithinfluxdb`.
