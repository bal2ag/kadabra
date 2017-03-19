import datetime

import kadabra

from mock import mock, call, MagicMock

NOW = datetime.datetime.utcnow()

def test_ctor():
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)

    assert nanny.channel == channel
    assert nanny.publisher == publisher
    assert nanny.logger == logger
    assert nanny.frequency_seconds == frequency_seconds
    assert nanny.threshold_seconds == threshold_seconds
    assert nanny.max_batch_size == max_batch_size
    assert nanny.timer == None

@mock.patch('kadabra.agent.Timer')
def test_start(mock_timer):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3
    
    timer = mock_timer.return_value
    timer.start = MagicMock()

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)
    nanny.start()

    mock_timer.assert_called_with(frequency_seconds, nanny._run_nanny)
    assert nanny.timer == timer
    assert timer.name == "KadabraBatchedNanny"
    timer.start.assert_called_with()

@mock.patch('kadabra.agent.Timer')
def test_stop_no_timer(mock_timer):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3
    
    timer = MagicMock()
    timer.cancel = MagicMock()

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)
    nanny.stop()

    assert timer.cancel.call_count == 0

@mock.patch('kadabra.agent.Timer')
def test_stop(mock_timer):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3
    
    timer = MagicMock()
    timer.cancel = MagicMock()

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)
    nanny.timer = timer
    nanny.stop()

    timer.cancel.assert_called_with()

@mock.patch('kadabra.agent.Timer')
def test_run_exception(mock_timer):
    channel = MagicMock()
    channel.complete = MagicMock()
    channel.in_progress = MagicMock()
    channel.in_progress.side_effect = Exception()
    publisher = MagicMock()
    publisher.publish = MagicMock()
    logger = MagicMock()
    logger.warn = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3
    
    timer = MagicMock()
    timer.start = MagicMock()
    mock_timer.return_value = timer

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)
    nanny._run_nanny()

    assert logger.warn.call_count == 1
    mock_timer.assert_called_with(frequency_seconds, nanny._run_nanny)
    assert timer.name == "KadabraBatchedNanny"
    timer.start.assert_called_with()
    assert channel.complete.call_count == 0
    assert publisher.publish.call_count == 0

@mock.patch('kadabra.agent.get_datetime_from_timestamp_string')
@mock.patch('kadabra.agent.get_now', return_value=NOW)
@mock.patch('kadabra.agent.Timer')
def test_run_no_inprogress_metrics(mock_timer, mock_now, mock_get_datetime):
    channel = MagicMock()
    channel.complete = MagicMock()
    channel.in_progress = MagicMock(return_value=[])
    publisher = MagicMock()
    publisher.publish = MagicMock()
    logger = MagicMock()
    logger.debug = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3
    
    timer = MagicMock()
    timer.start = MagicMock()
    mock_timer.return_value = timer

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)
    nanny._run_nanny()

    channel.in_progress.assert_called_with(max_batch_size)
    assert mock_get_datetime.call_count == 0
    assert logger.debug.call_count == 2
    publisher.publish.assert_called_with([])
    channel.complete.assert_called_with([])
    mock_timer.assert_called_with(frequency_seconds, nanny._run_nanny)
    assert timer.name == "KadabraBatchedNanny"
    timer.start.assert_called_with()

@mock.patch('kadabra.agent.get_datetime_from_timestamp_string')
@mock.patch('kadabra.agent.get_now', return_value=NOW)
@mock.patch('kadabra.agent.Timer')
def test_run(mock_timer, mock_now, mock_get_datetime):
    channel = MagicMock()
    channel.complete = MagicMock()
    channel.in_progress = MagicMock()
    publisher = MagicMock()
    publisher.publish = MagicMock()
    logger = MagicMock()
    frequency_seconds = 10.0
    threshold_seconds = 5.0
    max_batch_size = 3
    
    timer = MagicMock()
    timer.start = MagicMock()
    mock_timer.return_value = timer

    m1 = MagicMock()
    m1.serialized_at = MagicMock()
    m1.timestamp_format = MagicMock()
    m2 = MagicMock()
    m2.serialized_at = MagicMock()
    m2.timestamp_format = MagicMock()
    m3 = MagicMock()
    m3.serialized_at = MagicMock()
    m3.timestamp_format = MagicMock()
    m4 = MagicMock()
    m4.serialized_at = None
    metrics = [m1, m2, m3, m4]
    channel.in_progress.return_value = metrics
    mock_get_datetime.side_effect = [
            NOW - datetime.timedelta(seconds=8),
            NOW - datetime.timedelta(seconds=5),
            NOW - datetime.timedelta(seconds=10)]

    nanny = kadabra.agent.BatchedNanny(channel, publisher, logger,
            frequency_seconds, threshold_seconds, max_batch_size)
    nanny._run_nanny()

    channel.in_progress.assert_called_with(max_batch_size)
    
    mock_get_datetime.assert_has_calls([
            call(m1.serialized_at, m1.timestamp_format),
            call(m2.serialized_at, m2.timestamp_format),
            call(m3.serialized_at, m3.timestamp_format)])

    publisher.publish.assert_called_with([m1, m3, m4])
    channel.complete.assert_called_with([m1, m3, m4])
    mock_timer.assert_called_with(frequency_seconds, nanny._run_nanny)
    assert timer.name == "KadabraBatchedNanny"
    timer.start.assert_called_with()
