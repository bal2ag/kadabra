from .metrics import Metrics

import logging

class RedisChannel(object):
    """A channel for transporting metrics using Redis as the transport medium.

    :type host: string
    :param host: The host of the Redis server.

    :type port: integer
    :param port: The port of the Redis server.

    :type db: integer
    :param db: The database to use on the Redis server. This should be used
    exclusively for Kadabra to prevent collisions with keys that might be used
    by your application.

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

    def __init__(self, host, port, db,
            logger='kadabra.channel',
            queue_key='kadabra_queue',
            inprogress_key='kadabra_inprogress'):
        from redis import StrictRedis
        self.client = StrictRedis(host=host, port=port, db=db)
        self.logger = logging.getLogger(logger)
        self.queue_key = queue_key
        self.inprogress_key = inprogress_key

    def send(self, metrics):
        """Send :class:`Metrics` to a Redis list, which will act as queue for
        metrics to be received and published.

        :type metrics: kadabra.Metrics
        :param metrics: The :class:`Metrics` to be sent.
        """
        to_push = metrics.serialize()
        self.logger.debug("Sending %s" % str(to_push))
        self.client.lpush(self.queue_key, to_push)
        self.logger.debug("Successfully sent %s" % str(to_push))

    def receive(self):
        """Receive metrics from the queue so they can be published. Once
        received, the metrics will be moved into a temporary "in progress"
        queue until they have been acknolwedged as completed (by calling
        :meth:`complete`). This method will block until there are metrics
        available on the queue or after a long timeout.

        :rtype: kadabra.Metrics
        :returns: The :class:`Metrics` from the queue.
        """
        self.logger.debug("Receiving metrics")
        rv = self.client.brpoplpush(self.queue_key, self.inprogress_key)
        if rv:
            self.logger.debug("Got metrics: %s" % rv)
            return Metrics.deserialize(rv)
        self.logger.debug("No metrics received")
        return None

    def complete(self, metrics):
        """Mark metrics as completed by removing them from the in progress
        queue.

        :type metrics: kadabra.Metrics
        :param metrics: The :class:`Metrics` to mark as complete.
        """
        to_complete = metrics.serialize()
        self.logger.debug("Marking %s as complete" % str(to_complete))
        rv = self.client.lrem(self.inprogress_key, 1, to_complete)
        if rv > 0:
            self.logger.debug("Successfully marked %s as complete" %\
                    str(to_complete))
        else:
            self.logger.debug("Failed to mark %s as complete" %\
                    str(to_complete))

    def in_progress(self):
        """Return a list of the metrics that are in_progress.

        :rtype: list
        :returns: A list of :class:`Metric`s that are in progress.
        """
        in_progress = self.client.lrange(self.inprogress_key, 0, -1)
        self.logger.debug("Found %s in progress metrics" % len(in_progress))
        return [Metrics.deserialize(m) for m in in_progress]

