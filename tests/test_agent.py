import kadabra
import pytest

from mock import MagicMock, mock, call

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

    expected_receiver_threads =\
            kadabra.config.DEFAULT_CONFIG["AGENT_RECEIVER_THREADS"]
    expected_nanny_frequency_seconds =\
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_FREQUENCY_SECONDS"]
    expected_nanny_threshold_seconds =\
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_THRESHOLD_SECONDS"]
    expected_nanny_query_limit =\
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_QUERY_LIMIT"]
    expected_nanny_num_threads =\
            kadabra.config.DEFAULT_CONFIG["AGENT_NANNY_THREADS"]

    agent = kadabra.Agent()

    mock_redis_channel.assert_called_with(**channel_default_args)
    mock_debug_publisher.assert_called_with(**publisher_default_args)
    mock_receiver.assert_called_with(
            channel,
            publisher,
            agent.logger,
            expected_receiver_threads)
    mock_nanny.assert_called_with(
            channel,
            publisher,
            agent.logger,
            expected_nanny_frequency_seconds,
            expected_nanny_threshold_seconds,
            expected_nanny_query_limit,
            expected_nanny_num_threads)
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
    agent._is_stopped = MagicMock()
    agent._is_stopped.side_effect = [False, True]
    agent.start()

    agent.receiver.start.assert_called_with()
    agent.nanny.start.assert_called_with()
    assert agent._is_stopped.call_count == 2
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
    agent._is_stopped = MagicMock()
    agent._is_stopped.return_value = False
    agent.stop = MagicMock()
    agent.start()

    agent.receiver.start.assert_called_with()
    agent.nanny.start.assert_called_with()
    assert agent._is_stopped.call_count == 1
    agent.stop.assert_called_with()

@mock.patch('kadabra.agent.DebugPublisher')
@mock.patch('kadabra.agent.RedisChannel')
@mock.patch('kadabra.agent.Receiver')
@mock.patch('kadabra.agent.Nanny')
@mock.patch('kadabra.agent.time.sleep')
def test_is_stopped(mock_sleep, mock_nanny, mock_receiver, mock_redis_channel,
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
    agent._is_stopped() == False

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
    assert agent._is_stopped() == False
    agent.stop()
    assert agent._is_stopped() == True
    nanny.stop.assert_called_with()
    receiver.stop.assert_called_with()
