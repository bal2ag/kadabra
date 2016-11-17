.. _usingwithinfluxdb:

Using with InfluxDB
===================

`InfluxDB <https://www.influxdata.com/time-series-platform/influxdb/>`_ is a
great open-source time-series database that works very well for storing
metrics. It is scalable, simple to use, and has an active developer
community. Plus, open-source dashboarding software such as `Graphana
<http://grafana.org/>`_ includes plugins for InfluxDB, making it very easy to
create dashboards from your Kadabra metrics.

This section of the docs will help you set up Kadabra with a locally-running
instance of InfluxDB from scratch.

Install Kadabra and Redis
-------------------------

First, make sure you have installed Kadabra and have a locally running Redis
server by following the directions from :doc:`gettingstarted`. Make sure you
can connect to Redis using the CLI::

    => redis-cli
    127.0.0.1:6379> ping
    PONG

Install and Run InfluxDB
------------------------

Now you need to install the InfluxDB server by following the directions `here
<https://docs.influxdata.com/influxdb/latest/introduction/installation>`_. Make
sure the InfluxDB server is running and that you can connect to it using the
CLI::

    ⇒  influx
    Visit https://enterprise.influxdata.com to register for updates, InfluxDB
    server management, and monitoring.
    Connected to http://localhost:8086 version 0.9.6.1
    InfluxDB shell 0.9.6.1
    >

Note that your InfluxDB might be a later version.

Create the Metrics Database
---------------------------

You will create the database that Kadabra will use to store metrics. The
easiest way to do this is through the command line::

    > create database kadabra;
    >

Make sure the database exists by switching to it (we will use this to see the
metrics we send shortly)::

    > use kadabra;
    Using database kadabra
    >

Configure and Run the Agent
---------------------------

Save the following into a file called **run_agent.py**::

    import logging, sys, kadabra

    handler = logging.StreamHandler(sys.stdout)

    agent_logger = logging.getLogger("kadabra.agent")
    agent_logger.setLevel("INFO")
    agent_logger.addHandler(handler)

    publisher_logger = logging.getLogger("kadabra.publisher")
    publisher_logger.setLevel("INFO")
    publisher_logger.addHandler(handler)

    agent = kadabra.Agent(configuration={"AGENT_PUBLISHER_TYPE": "influxdb"})
    agent.start()

The default arguments for the :class:`~kadabra.publishers.InfluxDBPublisher`
target the InfluxDB server running locally on port 8086, using the `kadabra`
database.

Run the agent in its own terminal window::

    python run_agent.py

Send Some Metrics
-----------------

Let's write a simple program that calculates the Nth fibonacci number, and
records some metrics. We'll call it fib.py::

    import kadabra, sys, datetime

    client = kadabra.Client()
    metrics = client.get_collector()
    metrics.set_dimension("program", "fibonacci")
    
    n = int(sys.argv[1])
    
    start = datetime.datetime.utcnow()
    a, b = 0, 1
    for i in range(n):
        metrics.add_count("iterations", 1)
        a, b = b, a + b
    end = datetime.datetime.utcnow()
    
    metrics.set_timer("runTime", end - start, kadabra.Units.MILLISECONDS)
    client.send(metrics.close())
    
    print a

This program will take a single command line integer argument, calculate that
fibonacci number, and print it. But, it will also time how long this takes and
count the number of loop iterations (admittedly a silly metric, since it will
always be equal to N), and send these to InfluxDB.

Make sure the agent is running in a seperate terminal, and run the fibonacci
program with a reasonable number (like 30)::

    => python fib.py 30
    832040

See the Metrics in InfluxDB
---------------------------

Now let's take a look at what ended up in InfluxDB. Using the CLI, let's view
what measurements are available in our `kadabra` database::

    > show measurements;
    name: measurements
    ------------------
    name
    iterations
    runTime

There are two measurements available, **iterations** and **runTime**
corresponding to the counter and timer we set in our application.

Let's look at **runTime**::

    > select * from runTime;
    name: runTime
    ----------
    time                   program      unit            value
    1479333981920492032    fibonacci    milliseconds    0.828

`time` is the Unix epoch timestamp when the metric was created. `program` is
the dimension we set. It's actually an indexed tag in InfluxDB, meaning we
could efficiently query for all the metrics that share the same `program`. The
`unit` tells us how to interpret the `value`: on my machine the fibonacci
program calculated the value in 0.828 milliseconds.

Now let's take a look at **iterations**::

    > select * from iterations;
    name: iterations
    ----------------
    time                   program        value
    1479333981919803904    fibonacci      30

This counter looks mostly the same as our timer, although there is only a
`value` field which is, as expected, equal to the value we passed in for N.

Next Steps
----------

You've now used Kadabra to publish metrics into a real database suitable for
storing and querying! But the database is running locally, which isn't
particularly helpful as your infrastructure starts to grow and incorporate
additional hosts. For deployment in a real production environment you'll want
to host the InfluxDB server separately from your application hosts. It's easy
to use any InfluxDB host with Kadabra; you just need to change the "host"
argument to the IP or DNS of the remote InfluxDB host.

