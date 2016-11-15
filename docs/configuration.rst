.. _configuration:

Configuration
=============

Kadabra has a default set of configuration values. You can override the default
configuration by specifying a dictionary when you initialize the
:class:`~kadabra.Client` and :class:`~kadabra.Agent` whose keys are the
configuration you want to override and whose values are the values you want to
use.

For exampe, configuring the Client to use a different Redis port might look
like this::

    my_config = {
        'CLIENT_CHANNEL_ARGS': {
            'port': 6500
    }
    client = kadabra.Client(configuration=my_config)

Note that for configuration values that are dictionaries (like arguments for
initializing the channel), you only need to specify the keys/values that you
are overriding - the defaults will be used for the other arguments.

Configuring the Agent to write to a local InfluxDB server (using the default
arguments) might look like this::

    my_config = {
        'AGENT_CHANNEL_ARGS': {
            'port': 6500
        },
        'AGENT_PUBLISHER_TYPE': 'influxdb'
    }
    agent = kadabra.Agent(configuration=my_config)

A full list of the recognized configuration keys, descriptions of each, and
their default values for the Client and the Agent are provided below.

Client
------

=========================== ==================================================
`CLIENT_DEFAULT_DIMENSIONS` If specified, any collectors instantiated from the
                            client will have these dimensions upon
                            instantiation. Should be dictionary of strings to
                            strings. **Default:** ``{}``
`CLIENT_TIMESTAMP_FORMAT`   The (Python-style) format to use for timestamps
                            when serializing metrics to be sent over the
                            channel. Must match the format of the agent that is
                            publishing those metrics.
                            **Default:** ``%Y-%m-%dT%H:%M:%S.%fZ``
`CLIENT_CHANNEL_TYPE`       The type of the channel to use for transporting
                            metrics. Currently the only accepted value is
                            'redis'. **Default:** ``redis``
`CLIENT_CHANNEL_ARGS`       Dictionary of overrides for the default channel
                            arguments. Keys should match the argument names for
                            the channel constructor. You can specify any, all,
                            or none of the arguments to override; the defaults
                            will be used for any arguments that are not
                            overridden. **Default:** `None`
=========================== ==================================================

Agent
-----

================================ =============================================
`AGENT_LOGGER_NAME`              The name of the logger that the agent will use
                                 to log messages. **Default:**
                                 ``kadabra.agent``
`AGENT_CHANNEL_TYPE`             The type of the channel to use for receiving
                                 metrics. Currently the only accepted value is
                                 'redis'. **Default:** ``redis``
`AGENT_CHANNEL_ARGS`             Dictionary of overrides for the default channel
                                 arguments. Keys should match the argument names
                                 for the channel constructor. You can specify
                                 any, all, or none of the arguments to override;
                                 the defaults will be used for any arguments
                                 that are not overridden. **Default:** `None`
`AGENT_PUBLISHER_TYPE`           The type of the publisher to use for
                                 publishing metrics. The acceptable values are
                                 'debug' and 'influxdb'. **Default:** ``debug``
`AGENT_PUBLISHER_ARGS`           Dictionary of overrides for the default
                                 publisher arguments. Keys should match the
                                 argument names for the publisher constructor.
                                 You can specify any, all, or none of the
                                 arguments to override; the defaults will be
                                 used for any arguments that are not
                                 overridden. **Default:** None
`AGENT_RECEIVER_THREADS`         The number of threads the agent will use for
                                 publishing metrics from the channel.
                                 **Default:** `3`
`AGENT_NANNY_FREQUENCY_SECONDS`  How often the agent will check for metrics
                                 that have been in-progress for a long time so
                                 that they can be republished. **Default:**
                                 `30`
`AGENT_NANNY_THRESHOLD_SECONDS`  How many seconds metrics must be in-progress
                                 before they are considered in-progress for a
                                 "long time" (and will be retried by the
                                 nanny). **Default:** `60`
`AGENT_NANNY_QUERY_LIMIT`        The maximum number of in-progress metrics that
                                 the nanny will process at once. This is
                                 necessary because the in-progress queue is
                                 always changing, so the nanny must take a
                                 "snapshot" of the currently in-progress
                                 metrics. **Default:** `5000`
`AGENT_NANNY_THREADS`            The number of threads the agent will use for
                                 re-publishing metrics that have been
                                 in-progress for a long time. **Default:** `3`
================================ =============================================
