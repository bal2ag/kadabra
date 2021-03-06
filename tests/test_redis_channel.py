import redis
import kadabra
import json

from mock import MagicMock, mock, call

host = "host"
port = 1234
db = 0
logger = "testlogger"
queue_key = 'queue_key'
inprogress_key = 'inprogress_key'

def get_unit():
    return kadabra.channels.RedisChannel(host, port, db, logger, queue_key,
            inprogress_key)

@mock.patch('redis.StrictRedis')
def test_ctor(mock_redis):
    mock_redis.return_value = "test"

    channel = get_unit()

    mock_redis.assert_called_with(host=host, port=port, db=db)

    assert channel.client == "test"
    assert channel.logger.name == logger
    assert channel.queue_key == queue_key
    assert channel.inprogress_key == inprogress_key

def test_send():
    serialized = {"name": "value"}

    channel = get_unit()
    metrics = kadabra.Metrics([], [], [])

    metrics.serialize = MagicMock(return_value=serialized)
    channel.client.lpush = MagicMock()

    channel.send(metrics)

    metrics.serialize.assert_called_with()
    channel.client.lpush.assert_called_with(queue_key, json.dumps(serialized))

@mock.patch('kadabra.Metrics.deserialize')
def test_receive_metrics(mock_deserialize):
    deserialized = "test"
    mock_deserialize.return_value = deserialized
    raw_metrics = {"name": "value"}
    encoded = json.dumps(raw_metrics)

    channel = get_unit()
    channel.client.brpoplpush = MagicMock(return_value=encoded)

    metrics = channel.receive()

    channel.client.brpoplpush.assert_called_with(queue_key, inprogress_key,
            timeout=10)
    mock_deserialize.assert_called_with(raw_metrics)
    assert metrics == deserialized

def test_receive_nometrics():
    raw_metrics = None

    channel = get_unit()
    channel.client.brpoplpush = MagicMock(return_value=raw_metrics)

    metrics = channel.receive()

    channel.client.brpoplpush.assert_called_with(queue_key, inprogress_key,
            timeout=10)
    assert metrics == None

@mock.patch('kadabra.channels.Metrics.deserialize')
def test_receive_batch(mock_deserialize):
    channel = get_unit()

    max_batch_size = 3

    m1 = '{"m1_name": "m1_value"}'
    m2 = '{"m2_name": "m2_value"}'
    metrics = [m1, m2, None]
    expected_batch = [MagicMock(), MagicMock()]
    mock_deserialize.side_effect = expected_batch

    pipeline = MagicMock()
    pipeline.rpoplpush = MagicMock()
    pipeline.execute = MagicMock(return_value=metrics)
    channel.client.pipeline = MagicMock(return_value=pipeline)

    batch = channel.receive_batch(max_batch_size)

    pipeline.rpoplpush.assert_has_calls(
            [call(queue_key, inprogress_key) for i in range(max_batch_size)])
    mock_deserialize.assert_has_calls([
            call(json.loads(m1)),
            call(json.loads(m2))])
    assert batch == expected_batch

def test_complete_successful():
    serialized = {"name": "value"}

    channel = get_unit()
    metrics = kadabra.Metrics([], [], [])

    metrics.serialize = MagicMock(return_value=serialized)

    pipeline = MagicMock()
    pipeline.lrem = MagicMock(return_value=1)
    channel.client.pipeline = MagicMock(return_value=pipeline)

    channel.complete([metrics])

    metrics.serialize.assert_called_with()
    pipeline.lrem.assert_called_with(inprogress_key, 1,\
            json.dumps(serialized))

def test_complete_unsuccessful():
    serialized = {"name": "value"}

    channel = get_unit()
    metrics = kadabra.Metrics([], [], [])

    metrics.serialize = MagicMock(return_value=serialized)

    pipeline = MagicMock()
    pipeline.lrem = MagicMock(return_value=0)
    channel.client.pipeline = MagicMock(return_value=pipeline)

    channel.complete([metrics])

    metrics.serialize.assert_called_with()
    pipeline.lrem.assert_called_with(inprogress_key, 1,\
            json.dumps(serialized))

@mock.patch('kadabra.Metrics.deserialize')
def test_in_progress(mock_deserialize):
    query_limit = 3
    raw = [json.dumps({"nameOne": "valueOne"}),
           json.dumps({"nameTwo": "valueTwo"}),
           json.dumps({"nameThree": "valueThree"})]
    deserialized = ['one', 'two', 'three']
    mock_deserialize.side_effect = deserialized

    channel = get_unit()
    channel.client.lrange = MagicMock(return_value=raw)

    in_progress = channel.in_progress(query_limit)

    channel.client.lrange.assert_called_with(inprogress_key, 0,\
            query_limit - 1)

    for r in raw:
        mock_deserialize.assert_any_call(json.loads(r))
    assert in_progress == deserialized
