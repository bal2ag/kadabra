from .metrics import Metrics

import logging, json

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
        self.client.lpush(self.queue_key, json.dumps(to_push))
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
            rv = json.loads(raw)
            self.logger.debug("Got metrics: %s" % rv)
            return Metrics.deserialize(rv)
        self.logger.debug("No metrics received")
        return None

    def receive_batch(self, max_batch_size):
        """Receive a list of metrics from the queue so they can be published.
        Once received, all metrics will be moved into a temporary "in progress"
        queue until they have been acknowledged as published (by calling
        :meth:`~kadabra.channels.RedisChannel.complete`). The number of metrics
        that are received is less than or equal to the ``max_batch_size``, and
        possibly empty.

        :type max_batch_size: int
        :param max_batch_size: The maximum number of metrics to receive in the
                               batch.

        :rtype: list
        :returns: The list of metrics to be published. The size of the list is
                  less than or equal to the ``max_batch_size``, and possibly
                  empty if there are no metrics in the queue.
        """
        self.logger.debug("Receiving batch of metrics")
        pipeline = self.client.pipeline()
        for i in range(max_batch_size):
            pipeline.rpoplpush(self.queue_key, self.inprogress_key)
        return [Metrics.deserialize(json.loads(m)) for m in pipeline.execute()
                if m is not None]

    def complete(self, metrics):
        """Mark a list of metrics as completed by removing them from the
        in-progress queue.

        :type metrics: list
        :param metrics: The list of :class:`~kadabra.Metrics` to mark as
                        complete.
        """
        if len(metrics) > 0:
            pipeline = self.client.pipeline()
            for m in metrics:
                pipeline.lrem(self.inprogress_key, 1,
                        json.dumps(m.serialize()))
            pipeline.execute()

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
        return [Metrics.deserialize(json.loads(m))\
                for m in in_progress]

