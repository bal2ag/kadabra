import kadabra
import logging

from mock import MagicMock, mock

@mock.patch('logging.getLogger')
def test_ctor(mock_get_logger):
    logger = "test"
    logger_name = "loggerName"
    mock_get_logger.return_value = logger

    publisher = kadabra.publishers.DebugPublisher(logger_name)
    mock_get_logger.assert_called_with(logger_name)
    assert publisher.logger == logger

@mock.patch('logging.getLogger')
def test_ctor(mock_get_logger):
    serialized = "test"
    logger_name = "loggerName"
    mocked_logger = mock_get_logger.return_value
    mocked_logger.info = MagicMock()
    mocked_metrics = MagicMock()
    mocked_metrics.serialize = MagicMock(return_value=serialized)

    publisher = kadabra.publishers.DebugPublisher(logger_name)
    publisher.publish(mocked_metrics)

    mocked_metrics.serialize.assert_called_with()
    mocked_logger.info.assert_called_with(serialized)
