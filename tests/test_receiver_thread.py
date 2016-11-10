import kadabra

from mock import MagicMock

def test_ctor():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()

    receiver_thread = kadabra.agent.ReceiverThread(channel, publisher, logger)

    assert receiver_thread.channel == channel
    assert receiver_thread.publisher == publisher
    assert receiver_thread.logger == logger

def test_run_once_no_metrics():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()

    channel.receive = MagicMock(return_value=None)
    publisher.publish = MagicMock()
    channel.complete = MagicMock()

    receiver_thread = kadabra.agent.ReceiverThread(channel, publisher, logger)
    receiver_thread.run_once()

    channel.receive.assert_called_with()
    publisher.publish.assert_has_calls([])
    channel.complete.assert_has_calls([])

def test_run_once_metrics():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()

    channel.receive = MagicMock()
    metrics = channel.receive.return_value
    metrics.serialize = MagicMock()
    publisher.publish = MagicMock()
    channel.complete = MagicMock()

    receiver_thread = kadabra.agent.ReceiverThread(channel, publisher, logger)
    receiver_thread.run_once()

    channel.receive.assert_called_with()
    metrics.serialize.assert_called_with()
    publisher.publish.assert_called_with(metrics)
    channel.complete.assert_called_with(metrics)

def test_run_once_exception():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()

    channel.receive = MagicMock()
    metrics = channel.receive.return_value
    metrics.serialize = MagicMock()
    publisher.publish = MagicMock()
    publisher.publish.side_effect = Exception()
    channel.complete = MagicMock()

    receiver_thread = kadabra.agent.ReceiverThread(channel, publisher, logger)
    receiver_thread.run_once()

    channel.receive.assert_called_with()
    metrics.serialize.assert_called_with()
    publisher.publish.assert_called_with(metrics)
    channel.complete.assert_has_calls([])
