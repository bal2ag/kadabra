import kadabra
import Queue

from mock import MagicMock

def test_ctor():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)

    assert nanny_thread.channel == channel
    assert nanny_thread.publisher == publisher
    assert nanny_thread.queue == queue
    assert nanny_thread.logger == logger

def test_run_once_no_metrics():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    queue.get = MagicMock(return_value=None)
    publisher.publish = MagicMock()
    channel.complete = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    nanny_thread._run_once()

    queue.get.assert_called_with(timeout=10)
    publisher.publish.assert_has_calls([])
    channel.complete.assert_has_calls([])

def test_run_once():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    queue.get = MagicMock()
    metrics = queue.get.return_value
    metrics.serialize = MagicMock()
    publisher.publish = MagicMock()
    channel.complete = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    nanny_thread._run_once()

    queue.get.assert_called_with(timeout=10)
    publisher.publish.assert_called_with(metrics)
    channel.complete.assert_called_with(metrics)

def test_run_once_empty_queue():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    queue.get = MagicMock()
    queue.get.side_effect = Queue.Empty()
    publisher.publish = MagicMock()
    channel.complete = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    nanny_thread._run_once()

    queue.get.assert_called_with(timeout=10)
    publisher.publish.assert_has_calls([])
    channel.complete.assert_has_calls([])

def test_run_once_exception():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    queue.get = MagicMock()
    metrics = queue.get.return_value
    metrics.serialize = MagicMock()
    publisher.publish = MagicMock()
    publisher.publish.side_effect = Exception()
    channel.complete = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    nanny_thread._run_once()

    queue.get.assert_called_with(timeout=10)
    publisher.publish.assert_called_with(metrics)
    channel.complete.assert_has_calls([])

def test_stop():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    nanny_thread.stopped = False
    nanny_thread.stop()

    assert nanny_thread.stopped == True

def test_is_stopped():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    assert nanny_thread._is_stopped() == False
    nanny_thread.stopped = True
    assert nanny_thread._is_stopped() == True

def test_run():
    channel = MagicMock()
    publisher = MagicMock()
    queue = MagicMock()
    logger = MagicMock()

    nanny_thread = kadabra.agent.NannyThread(channel, publisher, queue, logger)
    nanny_thread._run_once = MagicMock()
    nanny_thread._is_stopped = MagicMock()
    nanny_thread._is_stopped.side_effect = [False, True]

    nanny_thread.run()

    assert nanny_thread._is_stopped.call_count == 2
    assert nanny_thread._run_once.call_count == 1
