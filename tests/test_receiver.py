import kadabra
import pytest

from mock import MagicMock, mock, call

@mock.patch('kadabra.agent.ReceiverThread')
def test_ctor(mock_receiver_thread):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    num_threads = 3

    receiver_threads = [MagicMock(), MagicMock(), MagicMock()]
    mock_receiver_thread.side_effect = receiver_threads

    receiver = kadabra.agent.Receiver(channel, publisher, logger, num_threads)

    assert receiver.channel == channel
    assert receiver.publisher == publisher
    assert receiver.logger == logger
    assert receiver.num_threads == num_threads

    mock_receiver_thread.assert_has_calls(
            [call(channel, publisher, logger) for x in receiver_threads])
    for i in range(len(receiver_threads)):
        expected_name = "KadabraReceiver-%s" % str(i)
        assert receiver.threads[i].name == expected_name

@mock.patch('kadabra.agent.ReceiverThread')
def test_start(mock_receiver_thread):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    num_threads = 3

    thread_one = MagicMock()
    thread_one.start = MagicMock()
    thread_one.name = "threadOne"
    thread_two = MagicMock()
    thread_two.start = MagicMock()
    thread_two.name = "threadTwo"
    thread_three = MagicMock()
    thread_three.start = MagicMock()
    thread_three.name = "threadThree"
    threads = [thread_one, thread_two, thread_three]
    mock_receiver_thread.side_effect = threads

    receiver = kadabra.agent.Receiver(channel, publisher, logger, num_threads)
    receiver.start()

    for thread in threads:
        thread.start.assert_called_with()

@mock.patch('kadabra.agent.ReceiverThread')
def test_stop(mock_receiver_thread):
    channel = MagicMock()
    publisher = MagicMock()
    logger = MagicMock()
    num_threads = 3

    thread_one = MagicMock()
    thread_one.stop = MagicMock()
    thread_one.name = "threadOne"
    thread_two = MagicMock()
    thread_two.stop = MagicMock()
    thread_two.name = "threadTwo"
    thread_three = MagicMock()
    thread_three.stop = MagicMock()
    thread_three.name = "threadThree"
    threads = [thread_one, thread_two, thread_three]
    mock_receiver_thread.side_effect = threads

    receiver = kadabra.agent.Receiver(channel, publisher, logger, num_threads)
    receiver.stop()

    for thread in threads:
        thread.stop.assert_called_with()
