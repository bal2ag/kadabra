import kadabra
import pytest

from mock import MagicMock, mock, call

def test_ctor():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    publishing_interval = 10.0
    max_batch_size = 5

    receiver = kadabra.agent.BatchedReceiver(channel, publisher, logger,
            publishing_interval, max_batch_size)

    assert receiver.channel == channel
    assert receiver.publisher == publisher
    assert receiver.logger == logger
    assert receiver.publishing_interval == publishing_interval
    assert receiver.max_batch_size == max_batch_size

@mock.patch('kadabra.agent.Timer')
def test_start(mock_timer):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    publishing_interval = 10.0
    max_batch_size = 5

    timer = mock_timer.return_value
    timer.start = MagicMock()

    receiver = kadabra.agent.BatchedReceiver(channel, publisher, logger,
            publishing_interval, max_batch_size)
    receiver.start()

    mock_timer.assert_called_with(publishing_interval,
            receiver._run_batched_receiver)
    assert receiver.timer == timer
    timer.start.assert_called_with()

def test_stop_no_timer():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    publishing_interval = 10.0
    max_batch_size = 5

    receiver = kadabra.agent.BatchedReceiver(channel, publisher, logger,
            publishing_interval, max_batch_size)
    receiver.stop()
   
    assert getattr(receiver, "timer") == None

@mock.patch('kadabra.agent.Timer')
def test_stop(mock_timer):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    publishing_interval = 10.0
    max_batch_size = 5

    timer = mock_timer.return_value
    timer.cancel = MagicMock()

    receiver = kadabra.agent.BatchedReceiver(channel, publisher, logger,
            publishing_interval, max_batch_size)
    receiver.start()
    receiver.stop()

    timer.cancel.assert_called_with()

@mock.patch('kadabra.agent.Timer')
def test_run_exception(mock_timer):
    batch = MagicMock()
    channel = MagicMock()
    channel.receive_batch = MagicMock(return_value=batch)
    channel.complete = MagicMock()
    channel.complete.side_effect = Exception()
    publisher = MagicMock()
    publisher.publish = MagicMock()
    logger = MagicMock()
    logger.warn = MagicMock()
    publishing_interval = 10.0
    max_batch_size = 5

    timer = mock_timer.return_value
    timer.start = MagicMock()

    receiver = kadabra.agent.BatchedReceiver(channel, publisher, logger,
            publishing_interval, max_batch_size)
    receiver._run_batched_receiver()
    
    channel.receive_batch.assert_called_with(max_batch_size)
    publisher.publish.assert_called_with(batch)
    channel.complete.assert_called_with(batch)
    assert logger.warn.call_count == 1

    mock_timer.assert_called_with(publishing_interval,
            receiver._run_batched_receiver)
    assert timer.name == "KadabraBatchedReceiverRunner"
    assert receiver.timer == timer
    timer.start.assert_called_with()

@mock.patch('kadabra.agent.Timer')
def test_run(mock_timer):
    batch = MagicMock()
    channel = MagicMock()
    channel.receive_batch = MagicMock(return_value=batch)
    channel.complete = MagicMock()
    publisher = MagicMock()
    publisher.publish = MagicMock()
    logger = MagicMock()
    logger.warn = MagicMock()
    publishing_interval = 10.0
    max_batch_size = 5

    timer = mock_timer.return_value
    timer.start = MagicMock()

    receiver = kadabra.agent.BatchedReceiver(channel, publisher, logger,
            publishing_interval, max_batch_size)
    receiver._run_batched_receiver()
    
    channel.receive_batch.assert_called_with(max_batch_size)
    publisher.publish.assert_called_with(batch)
    channel.complete.assert_called_with(batch)

    mock_timer.assert_called_with(publishing_interval,
            receiver._run_batched_receiver)
    assert timer.name == "KadabraBatchedReceiverRunner"
    assert receiver.timer == timer
    timer.start.assert_called_with()

