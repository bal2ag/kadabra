from .metrics import Metrics

import logging, json, base64

class RedisChannel(object):
    """A channel for transporting metrics using Redis.

    :type host: string
    :param host: The host of the Redis server.

    :type port: int
    :param port: The port of the Redis server.

    :type db: int
    :param db: The database to use on the Redis server. This should be used
               exclusively for Kadabra to prevent collisions with keys that
               might be used by your application.

    :type logger: string
    :param logger: The name of the logger to use.
    """

    #: Default arguments for the Redis channel. These will be used by the
    #: client and agent to initialize this channel if custom configuration
    #: values are not provided.
    DEFAULT_ARGS = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "logger": "kadabra.channel",
            "queue_key": "kadabra_queue",
            "inprogress_key": "kadabra_inprogress"
    }

    def __init__(self, host, port, db, logger, queue_key, inprogress_key):
        from redis import StrictRedis
        self.client = StrictRedis(host=host, port=port, db=db)
        self.logger = logging.getLogger(logger)
        self.queue_key = queue_key
        self.inprogress_key = inprogress_key

    def send(self, metrics):
        """Send metrics to a Redis list, which will act as queue for pending
        metrics to be received and published.

        :type metrics: ~kadabra.Metrics
        :param metrics: The metrics to be sent.
        """
        to_push = metrics.serialize()
        self.logger.debug("Sending %s" % to_push)
        self.client.lpush(self.queue_key,\
                base64.b64encode(json.dumps(to_push)))
        self.logger.debug("Successfully sent %s" % to_push)

    def receive(self):
        """Receive metrics from the queue so they can be published. Once
        received, the metrics will be moved into a temporary "in progress"
        queue until they have been acknowledged as published (by calling
        :meth:`~kadabra.channels.RedisChannel.complete`). This method will
        block until there are metrics available on the queue or after 10
        seconds.

        :rtype: ~kadabra.Metrics
        :returns: The metrics to be published, or None if there were no metrics
                  received after the timeout.
        """
        self.logger.debug("Receiving metrics")
        raw = self.client.brpoplpush(self.queue_key, self.inprogress_key,
                timeout=10)
        if raw:
            rv = json.loads(base64.b64decode(raw))
            self.logger.debug("Got metrics: %s" % rv)
            return Metrics.deserialize(rv)
        self.logger.debug("No metrics received")
        return None

    def complete(self, metrics):
        """Mark metrics as completed by removing them from the in-progress
        queue.

        :type metrics: ~kadabra.Metrics
        :param metrics: The metris to mark as complete.
        """
        to_complete = metrics.serialize()
        self.logger.debug("Marking %s as complete" % str(to_complete))
        rv = self.client.lrem(self.inprogress_key, 1,\
                base64.b64encode(json.dumps(to_complete)))
        if rv > 0:
            self.logger.debug("Successfully marked %s as complete" %\
                    str(to_complete))
        else:
            self.logger.debug("Failed to mark %s as complete" %\
                    str(to_complete))

    def in_progress(self, query_limit):
        """Return a list of the metrics that are in_progress.

        :type query_limit: int
        :param query_limit: The maximum number of items to get from the in
                            progress queue.

        :rtype: list
        :returns: A list of :class:`Metric`\s that are in progress.
        """
        in_progress = self.client.lrange(self.inprogress_key, 0,\
                query_limit - 1)
        self.logger.debug("Found %s in progress metrics" % len(in_progress))
        return [Metrics.deserialize(json.loads(base64.b64decode(m)))\
                for m in in_progress]

