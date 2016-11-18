.. _sending:

Sending Metrics
===============

This section describes channels in more detail, including the philosophy behind
them and how they work internally. You won't need to use channels directly;
rather you will configure one when you initialize your 
:class:`~kadabra.Client` and :class:`~kadabra.Agent` (and usually the defaults
are fine). You also don't need to understand this section to use Kadabra; it's
for those who are curious how the internals work.

Why channels?
-------------

You could publish metrics to a database directly from your application.
However, there are problems with this approach:

- It adds performance overhead. Usually the database will be on a different
  server, which means you have to pay the cost for an extra network call
  directly in your application.
- What happens if publishing fails? Should your application fail? Should it
  silently ignore the metrics that failed to publish? Should it retry
  publishing them? How many times should it retry?
- You may have multiple applications running on a single host that publish 
  metrics to the same database but with different cadences. You need to make
  sure your database can handle the load without slowing down and impacting
  your applications.

Channels solve these issues by providing temporary intermediate storage that
allows metrics to be published asynchronously with robust handling of failures.

To use a channel you need to set up the appropriate storage mechanism (e.g.
Redis server) and configure your Client and Agent to use it.

How Channels Work
-----------------

Channels expose four methods:

- **transport()** pushes metrics into the intermediate storage. It is used by
  :class:`~kadabra.Client` to send metrics for publishing.
- **receive()** pulls metrics from the intermediate storage. It is used by the
  :class:`~kadabra.Agent` to fetch metrics for publishing. It also moves the
  metrics into a special "in-progress" queue, indicating that they are in the
  process of being published.
- **complete()** marks metrics as successfully published, removing them from
  intermediate storage. It is called by the Agent once metrics have been
  successfully published.
- **in_progress()** queries metrics from the in-progress queue. It is used by
  the Agent's :class:`~kadabra.agent.Nanny` to retry metrics that have been
  in progress for a long time (e.g. if they failed to publish because the
  backing store experience an outage).

These mechanisms allow your application to efficiently queue metrics for
publishing (the performance of **transport()** is very fast) and enables to
agent to publish metrics asynchronously, and re-attempt publishing failures.

RedisChannel
------------

The :class:`~kadabra.channels.RedisChannel` sends your metrics over a Redis
server at the host, port, and database that you specify. Redis is extremely
simple to set up, and provides great performance. The configuration values are:

- **host**: The host of the Redis server. I recommend just using localhost.
  (Defaults to `localhost`)
- **port**: The port of the Redis server. (Defaults to `6379`)
- **db**: The database on the Redis server to store the metrics before they are
  published. I highly recommend using a dedicated database for Kadabra to
  prevent collision with your application keys (if your application uses
  Redis).

You can overwrite any or none of these values in the ``CLIENT_CHANNEL_ARGS``
and ``AGENT_CHANNEL_ARGS`` configuration keys. For more information on how to
configure the Client and Agent see :doc:`configuration`.

.. note:: Make sure your agent and client use the same channel type and
          arguments. Otherwise your metrics will not get published!

Generally I recommend just running the Redis server locally on the host that is
running the application(s) from which you want to get metrics. In fact, you
should probably run it as part of your deployment stack. For more information
see :doc:`runninginprod`.
