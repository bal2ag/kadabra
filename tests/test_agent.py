import kadabra
import pytest

from mock import MagicMock, mock, call

def test_ctor_unrecognized_agent_type():
    with pytest.raises(Exception):
        kadabra.Agent(configuration={"AGENT_TYPE": "ehjgrhjehe"})

def test_ctor_unrecognized_channel():
    with pytest.raises(Exception):
        kadabra.Agent(configuration={"AGENT_CHANNEL_TYPE": "ehjgrhjehe"})

def test_ctor_unrecognized_publisher():
    with pytest.raises(Exception):
        kadabra.Agent(configuration={"AGENT_PUBLISHER_TYPE": "ehjgrhjehe"})

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
def test_ctor_defaults(mock_nanny, mock_receiver, mock_redis_channel,
        mock_debug_publisher):
    channel = "testChannel"
    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    publisher = "testPublisher"
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}
    mock_debug_publisher.return_value = publisher
    mock_debug_publisher.DEFAULT_ARGS = publisher_default_args

    receiver = "testReceiver"
    mock_receiver.return_value = receiver

    nanny = "testNanny"
    mock_nanny.return_value = nanny

    agent = kadabra.Agent()

    expected_receiver_args = {
        "channel": channel,
        "publisher": publisher,
        "logger": agent.logger,
        "receiver_threads":
                kadabra.config.DEFAULT_CONFIG["AGENT_RECEIVER_THREADS"]
    }
    expected_nanny_args = {
        "channel": channel,
        "publisher": publisher,
        "logger": agent.logger,
        "frequency_seconds": 
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_FREQUENCY_SECONDS"],
        "threshold_seconds":
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_THRESHOLD_SECONDS"],
        "query_limit": 
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_QUERY_LIMIT"],
        "num_threads": 
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_THREADS"]
    }

    mock_redis_channel.assert_called_with(**channel_default_args)
    mock_debug_publisher.assert_called_with(**publisher_default_args)
    mock_receiver.assert_called_with(**expected_receiver_args)
    mock_nanny.assert_called_with(**expected_nanny_args)
    assert agent.receiver == receiver
    assert agent.nanny == nanny

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.BatchedReceiver')
@mock.patch('kadabra.agent.BatchedNanny')
def test_ctor_batched_defaults(mock_nanny, mock_receiver, mock_redis_channel,
        mock_debug_publisher):
    channel = "testChannel"
    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    publisher = "testPublisher"
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}
    mock_debug_publisher.return_value = publisher
    mock_debug_publisher.DEFAULT_ARGS = publisher_default_args

    receiver = "testReceiver"
    mock_receiver.return_value = receiver

    nanny = "testNanny"
    mock_nanny.return_value = nanny

    agent = kadabra.Agent(configuration={"AGENT_TYPE": "batched"})

    expected_receiver_args = {
        "channel": channel,
        "publisher": publisher,
        "logger": agent.logger,
        "publishing_interval":
            kadabra.config.DEFAULT_CONFIG["BATCHED_AGENT_INTERVAL_SECONDS"],
        "max_batch_size":
            kadabra.config.DEFAULT_CONFIG["BATCHED_AGENT_MAX_BATCH_SIZE"]
    }
    expected_nanny_args = {
        "channel": channel,
        "publisher": publisher,
        "logger": agent.logger,
        "frequency_seconds": 
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_FREQUENCY_SECONDS"],
        "threshold_seconds":
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_THRESHOLD_SECONDS"],
        "max_batch_size": 
            kadabra.config.DEFAULT_CONFIG["BATCHED_AGENT_NANNY_MAX_BATCH_SIZE"]
    }

    mock_redis_channel.assert_called_with(**channel_default_args)
    mock_debug_publisher.assert_called_with(**publisher_default_args)
    mock_receiver.assert_called_with(**expected_receiver_args)
    mock_nanny.assert_called_with(**expected_nanny_args)
    assert agent.receiver == receiver
    assert agent.nanny == nanny

@mock.patch('kadabra.agent.InfluxDBPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
def test_ctor_custom_args(mock_nanny, mock_receiver, mock_redis_channel,
        mock_influxdb_publisher):
    channel = "testChannel"
    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    channel_custom_args = {"channelArg2": 7}
    combined_channel_args = channel_default_args.copy()
    combined_channel_args.update(channel_custom_args)

    mock_redis_channel.return_value = channel
    mock_redis_channel.DEFAULT_ARGS = channel_default_args

    publisher = "testPublisher"
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}
    publisher_custom_args = {"publisherArg2": 9}
    combined_publisher_args = publisher_default_args.copy()
    combined_publisher_args.update(publisher_custom_args)

    mock_influxdb_publisher.return_value = publisher
    mock_influxdb_publisher.DEFAULT_ARGS = publisher_default_args

    receiver = "testReceiver"
    mock_receiver.return_value = receiver

    nanny = "testNanny"
    mock_nanny.return_value = nanny

    agent = kadabra.Agent(configuration={
        "AGENT_CHANNEL_ARGS": combined_channel_args,
        "AGENT_PUBLISHER_TYPE": 'influxdb',
        "AGENT_PUBLISHER_ARGS": combined_publisher_args
        })

    mock_redis_channel.assert_called_with(**combined_channel_args)
    mock_influxdb_publisher.assert_called_with(**combined_publisher_args)

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
@mock.patch('kadabra.agent.time.sleep')
def test_start(mock_sleep, mock_nanny, mock_receiver, mock_redis_channel,
        mock_debug_publisher):
    nanny = mock_nanny.return_value
    nanny.start = MagicMock()
    receiver = mock_receiver.return_value
    receiver.start = MagicMock()

    mock_thread_one = MagicMock()
    mock_thread_one.join = MagicMock()
    mock_thread_two = MagicMock()
    mock_thread_two.join = MagicMock()
    mock_thread_three = MagicMock()
    mock_thread_three.join = MagicMock()
    receiver.threads = [mock_thread_one, mock_thread_two,
            mock_thread_three]

    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}

    mock_redis_channel.DEFAULT_ARGS = channel_default_args
    mock_debug_publisher.DEFAULT_ARGS = publisher_default_args

    agent = kadabra.Agent()
    agent._check_stopped = MagicMock()
    agent._check_stopped.side_effect = [False, True]
    agent.start()

    agent.receiver.start.assert_called_with()
    agent.nanny.start.assert_called_with()
    assert agent._check_stopped.call_count == 2
    mock_sleep.assert_has_calls([call(10)])

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
@mock.patch('kadabra.agent.time.sleep')
def test_start(mock_sleep, mock_nanny, mock_receiver, mock_redis_channel,
        mock_debug_publisher):
    mock_sleep.side_effect = KeyboardInterrupt()

    nanny = mock_nanny.return_value
    nanny.start = MagicMock()
    receiver = mock_receiver.return_value
    receiver.start = MagicMock()

    mock_thread_one = MagicMock()
    mock_thread_one.join = MagicMock()
    mock_thread_two = MagicMock()
    mock_thread_two.join = MagicMock()
    mock_thread_three = MagicMock()
    mock_thread_three.join = MagicMock()
    receiver.threads = [mock_thread_one, mock_thread_two,
            mock_thread_three]

    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}

    mock_redis_channel.DEFAULT_ARGS = channel_default_args
    mock_debug_publisher.DEFAULT_ARGS = publisher_default_args

    agent = kadabra.Agent()
    agent._check_stopped = MagicMock()
    agent._check_stopped.return_value = False
    agent.stop = MagicMock()
    agent.start()

    agent.receiver.start.assert_called_with()
    agent.nanny.start.assert_called_with()
    assert agent._check_stopped.call_count == 1
    agent.stop.assert_called_with()

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
@mock.patch('kadabra.agent.time.sleep')
def test_check_stopped(mock_sleep, mock_nanny, mock_receiver, mock_redis_channel,
        mock_debug_publisher):
    mock_sleep.side_effect = KeyboardInterrupt()

    nanny = mock_nanny.return_value
    receiver = mock_receiver.return_value

    mock_thread_one = MagicMock()
    mock_thread_one.join = MagicMock()
    mock_thread_two = MagicMock()
    mock_thread_two.join = MagicMock()
    mock_thread_three = MagicMock()
    mock_thread_three.join = MagicMock()
    receiver.threads = [mock_thread_one, mock_thread_two,
            mock_thread_three]

    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}

    mock_redis_channel.DEFAULT_ARGS = channel_default_args
    mock_debug_publisher.DEFAULT_ARGS = publisher_default_args

    agent = kadabra.Agent()
    agent._check_stopped() == False

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
@mock.patch('kadabra.agent.time.sleep')
def test_stop(mock_sleep, mock_nanny, mock_receiver, mock_redis_channel,
        mock_debug_publisher):
    mock_sleep.side_effect = KeyboardInterrupt()

    nanny = mock_nanny.return_value
    nanny.stop = MagicMock()
    receiver = mock_receiver.return_value
    receiver.stop = MagicMock()

    mock_thread_one = MagicMock()
    mock_thread_one.join = MagicMock()
    mock_thread_two = MagicMock()
    mock_thread_two.join = MagicMock()
    mock_thread_three = MagicMock()
    mock_thread_three.join = MagicMock()
    receiver.threads = [mock_thread_one, mock_thread_two,
            mock_thread_three]

    channel_default_args = {"channelArg1": "1", "channelArg2": 2}
    publisher_default_args = {"publisherArg1": "5", "publisherArg2": 6}

    mock_redis_channel.DEFAULT_ARGS = channel_default_args
    mock_debug_publisher.DEFAULT_ARGS = publisher_default_args

    agent = kadabra.Agent()
    assert agent._check_stopped() == False
    agent.stop()
    assert agent._check_stopped() == True
    nanny.stop.assert_called_with()
    receiver.stop.assert_called_with()
