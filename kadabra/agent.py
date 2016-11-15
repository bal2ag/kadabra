import threading, logging, datetime, json, Queue, time

from threading import Timer

from .channels import RedisChannel
from .publishers import DebugPublisher, InfluxDBPublisher

from .config import DEFAULT_CONFIG

class Agent(object):
    """Reads metrics from a channel and publishes them (see
    :ref:`api-publishers`). The agent will spin up threads which listen
    to the configured channel and attempt to publish the metrics using the
    configured publisher. The agent will also periodically monitor the metrics
    that have been in progress for a while and attempt to republish them.
    Because the agent is meant to run indefinitely, side by side with your
    application, it should be configured and started in a separate, dedicated
    process.

    Internally this object just manages a :class:`~kadabra.agent.Receiver` and
    :class:`~kadabra.agent.Nanny`.

    :type configuration: dict
    :param configuration: Dictionary of configuration to use in place of the
                          defaults.
    """
    def __init__(self, configuration=None):
        config = DEFAULT_CONFIG.copy()
        if configuration:
            config.update(configuration)

        self.logger = logging.getLogger(config["AGENT_LOGGER_NAME"])
        self.logger.info("Initializing Agent with config: %s" % str(config))

        channel_type = config["AGENT_CHANNEL_TYPE"]
        custom_channel_args = config["AGENT_CHANNEL_ARGS"]
        if channel_type == 'redis':
            channel_type = RedisChannel
        else:
            raise Exception("Unrecognized channel type: '%s'" % channel_type)

        channel_args = channel_type.DEFAULT_ARGS.copy()
        if custom_channel_args:
            for k,v in custom_channel_args.iteritems():
                channel_args[k] = v
        channel = channel_type(**channel_args)

        publisher_type = config["AGENT_PUBLISHER_TYPE"]
        custom_publisher_args = config["AGENT_PUBLISHER_ARGS"]
        if publisher_type == 'debug':
            publisher_type = DebugPublisher
        elif publisher_type == 'influxdb':
            publisher_type = InfluxDBPublisher
        else:
            raise Exception("Unrecognized publisher type: '%s'" %\
                    publisher_type)

        publisher_args = publisher_type.DEFAULT_ARGS.copy()
        if custom_publisher_args:
            for k,v in custom_publisher_args.iteritems():
                publisher_args[k] = v
        publisher = publisher_type(**publisher_args)

        receiver_threads = config["AGENT_RECEIVER_THREADS"]

        nanny_frequency_seconds = config["AGENT_NANNY_FREQUENCY_SECONDS"]
        nanny_threshold_seconds = config["AGENT_NANNY_THRESHOLD_SECONDS"]
        nanny_query_limit = config["AGENT_NANNY_QUERY_LIMIT"]
        nanny_num_threads = config["AGENT_NANNY_THREADS"]

        self.receiver = Receiver(channel, publisher, self.logger,
                receiver_threads)
        self.nanny = Nanny(channel, publisher, self.logger,
                nanny_frequency_seconds, nanny_threshold_seconds,
                nanny_query_limit, nanny_num_threads)

        self.stopped = False

    def start(self):
        """Start the agent. It will receive metrics from the channel, publish
        them, and attempt to republish metrics that have been pending for a
        long time (in the case of publishing failures). The agent runs until
        stopped; thus, you should call this method from a dedicated Python
        process, as it will block until the process is killed, a keyboard
        interrupt is detected, or the :meth:`~kadabra.Agent.stop` method is
        called."""
        self.logger.info("Starting agent...")
        self.receiver.start()
        self.nanny.start()

        try:
            while not self._is_stopped():
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()

    def stop(self, *args, **kwargs):
        """Stop the Agent gracefully, ensuring that any pending publish
        attempts are finished. This method accepts arbitrary arguments so that
        it can be called from any context (such as a signal handler)."""
        self.logger.info("Gracefully stopping the agent... "
                         "This may take up to 10 seconds.")
        self.stopped = True
        self.nanny.stop()
        self.receiver.stop()

    def _is_stopped(self):
        """Determines if the agent has been stopped. This is used internally to
        run the Agent continuously until stopped.

        :rtype: bool
        :returns: True if the Agent has been stopped, False otherwise.
        """
        return self.stopped

class Receiver(object):
    """Manages :class:`~kadabra.agent.ReceiverThread`\s which receive metrics
    from the channel, move them from the queue to in-progress, and attempt to
    publish them. Publishing failures will result in the metrics remaining
    in-progress and getting picked up by the :class:`~kadabra.agent.Nanny`
    which will attempt to republish them.

    :type channel: :ref:`api-channels`
    :param channel: The channel to read metrics from. See
                    :ref:`api-channels`.

    :type publisher: :ref:`api-publishers`
    :param publisher: The publisher to use for publishing metrics. See
                      :ref:`api-publishers`.

    :type logger: ~logging.Logger
    :param logger: The logger to use.

    :type num_threads: integer
    :param num_threads: The number of threads to use for publishing metrics.
    """
    def __init__(self, channel, publisher, logger, num_threads):
        self.channel = channel
        self.publisher = publisher
        self.logger = logger
        self.num_threads = num_threads

        self.threads = []
        for i in range(self.num_threads):
            name = "KadabraReceiver-%s" % str(i)
            receiver_thread = ReceiverThread(self.channel, self.publisher,\
                    self.logger)
            receiver_thread.name = name
            self.threads.append(receiver_thread)

    def start(self):
        """Start the receiver by starting up each
        :class:`~kadabra.agent.ReceiverThread`."""
        for thread in self.threads:
            self.logger.info("Starting %s" % thread.name)
            thread.start()

    def stop(self):
        """Stop the receiver by stopping each
        :class:`~kadabra.agent.ReceiverThread`."""
        self.logger.info("Stopping Receiver...")
        for thread in self.threads:
            thread.stop()

class ReceiverThread(threading.Thread):
    """Listens to a channel for metrics and publishes them.

    :type channel: :ref:`api-channels`
    :param channel: The channel to read metrics from. See
                    :ref:`api-channels`.

    :type publisher: :ref:`api-publishers`
    :param publisher: The publisher to use for publishing metrics. See
                      :ref:`api-publishers`.

    :type logger: ~logging.Logger
    :param logger: The logger to use.
    """
    def __init__(self, channel, publisher, logger):
        super(ReceiverThread, self).__init__()
        self.channel = channel
        self.publisher = publisher
        self.logger = logger

        self.stopped = False

    def stop(self):
        """Stops this this thread, ensuring that the current run will be the
        last one."""
        self.logger.info("Stopping %s..." % self.name)
        self.stopped = True

    def run(self):
        """Run this thread until stopped."""
        while not self._is_stopped():
            self._run_once()
        self.logger.info("Stopped %s." % self.name)

    def _run_once(self):
        """Runs this thread once. It will receive a message from the channel
        containing the metrics, publish them using the publisher, and mark the
        metrics as complete in the channel."""
        try:
            metrics = self.channel.receive() # This could be blocking
            if metrics is not None:
                self.logger.debug("Publishing metrics: %s" %
                        metrics.serialize())
                self.publisher.publish(metrics)
                self.channel.complete(metrics)
        except:
            self.logger.warn("Receiver thread encountered exception",\
                    exc_info=1)

    def _is_stopped(self):
        """Determines if this thread has been stopped. This is used internally
        to run the thread continuously until stopped.

        :rtype: bool
        :returns: True if the thread has been stopped, False otherwise.
        """
        return self.stopped

class Nanny(object):
    """Monitors metrics that have been in-progress for a long time and attemps
    to republish them. This object will periodically query objects in the
    in-progress queue, and try to republish them if the time between now and
    when they were serialized is greater than a threshold (indicating the first
    attempt to publish the metrics failed). It will grab the first X elements
    from the in-progress queue (where X is a configured value) and add them to
    a queue, which :class:`~kadabra.agent.NannyThread`\s will read from and
    attempt to republish. If metrics are successfully published they will be
    marked as complete.

    :type channel: :ref:`api-channels`
    :param channel: The channel to monitor.

    :type publisher: :ref:`api-publishers`
    :param publisher: The publisher to use for republishing metrics.

    :type logger: ~logging.Logger
    :param logger: The logger to use.

    :type frequency_seconds: integer
    :param frequency_seconds: How often the Nanny should query the in_progress
                              queue.

    :type threshold_seconds: integer
    :param threshold_seconds: The threshold seconds to determine if metrics
                              should be attempted to be republished.

    :type query_limit: integer
    :param query_limit: The maximum number of elements to query from the
                        in-progress queue for any given Nanny run. This is
                        necessary because the in-progress queue will constantly
                        be changing. Thus nanny needs to take a "snapshot"
                        rather than iterate through the queue.

    :type num_threads: integer
    :param num_threads: The number of :class:`~kadabra.agent.NannyThread`\s to
                        use for republishing.
    """
    def __init__(self, channel, publisher, logger, frequency_seconds,
            threshold_seconds, query_limit, num_threads):
        self.channel = channel
        self.publisher = publisher
        self.logger = logger
        self.frequency_seconds = frequency_seconds
        self.threshold_seconds = threshold_seconds
        self.query_limit = query_limit
        self.num_threads = num_threads

        self.queue = Queue.Queue()
        self.threads = []
        self.timer = None

    def start(self):
        """Start the nanny by starting up each
        :class:`~kadabra.agent.NannyThread`."""
        self.threads = []
        for i in range(self.num_threads):
            name = "KadabraNannyThread-%s" % str(i)
            nanny_thread = NannyThread(self.channel, self.publisher,
                    self.queue, self.logger)
            nanny_thread.name = name
            self.threads.append(nanny_thread)
            nanny_thread.start()

        timer = Timer(self.frequency_seconds, self._run_nanny)
        timer.name = "KadabraNanny"
        self.timer = timer
        timer.start()

    def stop(self):
        """Stop the nanny by stopping the Nanny from listening to the channela
        nd by stopping each :class:`~kadabra.agent.NannyThread`."""
        self.logger.info("Stopping Nanny...")
        if self.timer is not None:
            self.timer.cancel()
        for thread in self.threads:
            thread.stop()

    def _run_nanny(self):
        """Runs the nanny. It will check the channel's in-progress queue at the
        configured frequency, and add any in-progress items to an internal
        queue, which the :class:`~kadabra.agent.NannyThread`\s will listen to
        and attempt to republish metrics from."""
        try:
            self.logger.debug("Running nanny")
            in_progress = self.channel.in_progress(self.query_limit)

            if len(in_progress) == 0:
                self.logger.debug("No metrics found in progress.")

            for metrics in in_progress:
                should_republish = False
                if metrics.serialized_at is not None:
                    now = datetime.datetime.utcnow()
                    serialized_at =\
                            datetime.datetime.strptime(metrics.serialized_at,
                                    metrics.timestamp_format)
                    delta = (now - serialized_at).total_seconds()
                    self.logger.debug(\
                            "serialized_at: %s, now: %s, delta: %s" %\
                        (str(metrics.serialized_at), str(now), delta))
                    should_republish = delta > self.threshold_seconds
                else:
                    self.logger.warn("Metrics is missing serialized_at, "
                            "something is wrong with the channel. "
                            "Attempting to republish anyway")
                    should_republish = True
                if should_republish:
                    self.queue.put(metrics)
        except:
            self.logger.warn("Encountered exception trying to get "
                    "in-progress metrics", exc_info=1)
        finally:
            timer = Timer(self.frequency_seconds, self._run_nanny)
            timer.name = "KadabraNanny"
            self.timer = timer
            timer.start()

class NannyThread(threading.Thread):
    """Listens to a queue for metrics that have been in progress for a long
    time and attempts to republish them. If the publishing is successful,
    marks the metrics as complete.

    :type channel: :ref:`api-channels`
    :param channel: The channel to mark the metrics as complete upon successful
                    publishing.

    :type publisher: :ref:`api-publishers`
    :param publisher: The publisher to be used to publish the metrics object.

    :type queue: ~Queue.Queue
    :param queue: The queue to monitor for metrics to republish.

    :type logger: ~logging.Logger
    :param logger: The :class:`Logger` to log messages to.
    """
    def __init__(self, channel, publisher, queue, logger):
        super(NannyThread, self).__init__()
        self.channel = channel
        self.publisher = publisher
        self.queue = queue
        self.logger = logger

        self.stopped = False

    def stop(self):
        """Stops this this thread, ensuring that the current run will be the
        last one."""
        self.logger.info("Stopping %s..." % self.name)
        self.stopped = True

    def run(self):
        """Run this thread until stopped."""
        while not self._is_stopped():
            self._run_once()
        self.logger.info("Stopped %s." % self.name)

    def _run_once(self):
        """Listen to the queue for metrics to publish and attempt to publish
        them and mark them as complete."""
        try:
            metrics = self.queue.get(timeout=10)
            if metrics is not None:
                self.logger.debug("Publishing metrics: %s" %\
                        metrics.serialize())
                self.publisher.publish(metrics)
                self.channel.complete(metrics)
        except Queue.Empty:
            pass
        except:
            self.logger.warn("Nanny thread encountered exception",\
                    exc_info=1)

    def _is_stopped(self):
        """Determines if this thread has been stopped. This is used internally
        to run the thread continuously until stopped.

        :rtype: bool
        :returns: True if the thread has been stopped, False otherwise.
        """
        return self.stopped
