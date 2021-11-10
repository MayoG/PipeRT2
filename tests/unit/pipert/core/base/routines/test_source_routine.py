import time

from pytest_mock import MockerFixture
from pipert2.utils.dummy_object import Dummy
from tests.unit.pipert.core.utils.dummy_routines.dummy_source_routine import DummySourceRoutine, DummySourceRoutineException
from tests.unit.pipert.core.utils.functions_test_utils import message_generator

MAX_TIMEOUT_WAITING = 3


def test_routine_execution(mocker: MockerFixture):
    dummy_routine = DummySourceRoutine()
    mock_message_handler = mocker.MagicMock()
    mock_message_handler.get.side_effect = message_generator
    dummy_routine.initialize(mock_message_handler, event_notifier=Dummy())

    dummy_routine.start()

    assert not dummy_routine.stop_event.is_set()

    dummy_routine.stop()

    assert dummy_routine.stop_event.is_set()

    number_of_main_logic_calls = dummy_routine.counter
    message_handler = dummy_routine.message_handler

    assert message_handler.put.call_count == number_of_main_logic_calls
    assert message_handler.get.call_count == 0


def test_throws_exception(mocker: MockerFixture):
    dummy_routine = DummySourceRoutineException()
    mock_message_handler = mocker.MagicMock()
    mock_message_handler.get.get_data.side_effect = Exception()
    dummy_routine.initialize(mock_message_handler, event_notifier=Dummy())

    dummy_routine.start()

    assert not dummy_routine.stop_event.is_set()

    dummy_routine.stop()

    assert dummy_routine.stop_event.is_set()

    message_handler = dummy_routine.message_handler

    assert message_handler.put.call_count == 0
    assert message_handler.get.call_count == 0
