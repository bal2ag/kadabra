import sys, json, datetime

class DebugPublisher(object):
    """Publish metrics to a logger using the given logger name. Useful for
    debugging.

    :type logger_name: string
    :param logger_name: The name of the logger to use.
    """

    #: Default arguments for this publisher. These will be used by the
    #: agent to initialize this publisher if custom configuration values are
    #: not provided.
    DEFAULT_ARGS = {"logger_name": "kadabra.publisher"}

    def __init__(self, logger_name):
        import logging
        self.logger = logging.getLogger(logger_name)

    def publish(self, metrics):
        """Publish the metrics by logging them (in serialized JSON format) to
        the publisher's logger at the INFO level.

        :type metrics: ~kadabra.Metrics
        :param metrics: The metrics to publish.
        """
        self.logger.info(metrics.serialize())

class InfluxDBPublisher(object):
    """Publish metrics by persisting them into an InfluxDB database. Series
    will be created for each metric. Each metric name becomes a measurement
    and dimensions become the tag set. A single field will be created called
    'value' which contains the value of the counter or timer. Timers will have
    an additional field called 'unit' which contains the name of the unit. Any
    metadata will become additional fields, although note that 'value' is a
    reserved name that will be overwritten for both metric types, and 'unit'
    will be overwritten for timers. For more information about InfluxDB see
    the `docs <https://docs.influxdata.com/influxdb>`.

    :type host: string
    :param host: The hostname of the InfluxDB database.

    :type port: int
    :param port: The port of the InfluxDB database.

    :type database: string
    :param database: The name of the database to use for publishing metrics
                     with this publisher. Note that this database must exist
                     prior to publishing metrics with this publisher - make
                     sure you set it up beforehand!

    :type timeout: int
    :param timeout: The timeout to wait for when calling the InfluxDB database
                    before failing.
    """

    #: Default arguments for this publisher. These will be used by the
    #: agent to initialize this publisher if custom configuration values are
    #: not provided.
    DEFAULT_ARGS = {"host": "localhost", "port": 8086,\
            "database": "kadabra", "timeout": 5}

    def __init__(self, host, port, database, timeout):
        from influxdb import InfluxDBClient
        self.client = InfluxDBClient(host=host, port=port, database=database,\
                timeout=timeout)

    def publish(self, metrics):
        """Publish the metrics by writing them to InfluxDB.

        :type metrics: ~kadabra.Metrics
        :param metrics: The metrics to publish.
        """
        data = []
        tags = {d.name: d.value for d in metrics.dimensions}

        for timer in metrics.timers:
            fields = {k: v for k,v in timer.metadata.iteritems()}
            fields["value"] = timer.value.total_seconds() *\
                    timer.unit.seconds_offset
            fields["unit"] = timer.unit.name
            datum = {
                "measurement": timer.name,
                "tags": tags,
                "time": datetime.datetime.strftime(timer.timestamp,
                    metrics.timestamp_format),
                "fields": fields
            }
            data.append(datum)

        for counter in metrics.counters:
            fields = {k: v for k,v in counter.metadata.iteritems()}
            fields["value"] = counter.value
            datum = {
                "measurement": counter.name,
                "tags": tags,
                "time": datetime.datetime.strftime(counter.timestamp,
                    metrics.timestamp_format),
                "fields": fields
            }
            data.append(datum)

        if len(data) > 0:
            self.client.write_points(data)
