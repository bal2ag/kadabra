import kadabra

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
    nanny_thread.run_once()

    queue.get.assert_called_with()
    publisher.publish.assert_has_calls([])
    channel.complete.assert_has_calls([])


def test_run_once_no_metrics():
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
    nanny_thread.run_once()

    queue.get.assert_called_with()
    publisher.publish.assert_called_with(metrics)
    channel.complete.assert_called_with(metrics)

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
    nanny_thread.run_once()

    queue.get.assert_called_with()
    publisher.publish.assert_called_with(metrics)
    channel.complete.assert_has_calls([])
