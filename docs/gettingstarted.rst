.. _gettingstarted:

Getting Started
===============

In this section we will demonstrate the basic functionality of Kadabra by
publishing some metrics using the :class:`~kadabra.publishers.DebugPublisher`,
which just outputs the metrics to a logger.

Make sure you have installed Kadabra following the directions in the
:doc:`installation` section.

Install and Run Redis Server
----------------------------

First, we need to have an instance of Redis server running locally. Redis is
very easy to setup and run. If you haven't used it before,
follow the docs `here <http://redis.io/download#installation>`_
to get your Redis server up and running. We will assume the Redis server is
running locally on port **6379** (the default port).

Run the Agent
-------------

Next, we will run the agent, which will watch for metrics and publish them (in
this case, to a logger setup to write to stdout). Put the following code into a
file called **run_agent.py**::

    import logging, sys, kadabra

    handler = logging.StreamHandler(sys.stdout)

    agent_logger = logging.getLogger("kadabra.agent")
    agent_logger.setLevel("INFO")
    agent_logger.addHandler(handler)

    publisher_logger = logging.getLogger("kadabra.publisher")
    publisher_logger.setLevel("INFO")
    publisher_logger.addHandler(handler)

    agent = kadabra.Agent()
    agent.start()

This code sets up the agent's logger (so we can see what it's doing) and the
publisher's logger (so we can see the metrics get printed).

Now we can run the agent::

    python run_agent.py

You should see some output indicating that the agent has started running,
meaning it is listening to Redis for metrics. If you see some output about
connection errors, ensure that the Redis server is actually running and that
you can connect to it.

Publish Some Metrics
--------------------

Now, in a separate terminal, open up a Python interpreter. We'll record some
metrics and publish them. First, let's initialize the Kadabra client::

    >>> import kadabra
    >>> client = kadabra.Client()

Now let's get a :class:`~kadabra.client.Collector` object from our client. This
is the API we use to record metrics in our application. It is thread-safe and
can be shared throughout our application::

    >>> metrics = client.get_collector()

In a real application, the metrics code would be located in places where we
care about recording important information, such as customer sales, user
signups, or application failures. But since we are just demonstrating
basic functionality, let's record a few counters and a timer::

    >>> import datetime
    >>> metrics.add_count("myCount", 1.0)
    >>> metrics.add_count("myOtherCount", 1.0)
    >>> metrics.add_count("myOtherCount", 1.0)
    >>> metrics.set_timer("myTimer", datetime.timedelta(seconds=30), kadabra.Units.MILLISECONDS)

.. note:: Timers record a :class:`datetime.timedelta`, but you can report the actual
   value in any of the units from :class:`kadabra.Units`.

Now we're ready to send our metrics for publishing::

    >>> client.send(metrics.close())

Go over to the terminal where your agent is running. You should see the metrics
output as serialized JSON. Lastly, hit CTRL+C to gracefully shut down the
agent.

Configuration
-------------

You can configure the Client and the Agent using a dictionary when you
instantiate them to control various aspects of their functionality. For more
information see the :doc:`configuration` section.

Publishing to Storage
---------------------

The :class:`~kadabra.publishers.DebugPublisher` just serializes the metrics
into JSON and outputs them to a logger. You could pipe this output into another
program which writes the metrics into more permanant storage. But it would be
best to publish the metrics directly into a database that is designed for
metrics.
`Time-series databases <https://en.wikipedia.org/wiki/Time_series_database>`_
are ideal for storing metrics data.

One such database engine is
`InfluxDB <https://www.influxdata.com/time-series-platform/influxdb/>`_, which
is capable of storing metrics with indexed tags and provides mechanisms for
querying those metrics in useful ways. Kadabra ships with an
:class:`~kadabra.publishers.InfluxDBPublisher` that can publish metrics
straight to an InfluxDB server - you just provide the host, port, and database
name.

For a guide on how to set up Kadabra to publish metrics using InfluxDB, see
:doc:`usingwithinfluxdb`.

Learning More
-------------

You now have everything you need to use Kadabra in your application. You can
find out more about :doc:`collecting`, :doc:`sending`, and :doc:`publishing` in
the corresponding sections. For a complete look at the API, see :doc:`api`.
