from src.pipert2.core.base.flow import Flow

from pytest_mock import MockerFixture
from unittest.mock import call

import pytest


ROUTINE_NAME = "R1"
KILL_EVENT = "kill"
EVENT1 = "event1"
START_EVENT = "start"
STOP_EVENT = "stop"


@pytest.fixture()
def dummy_flow_with_two_routines(mocker: MockerFixture):
    event_board_mocker = mocker.MagicMock()
    event_handler_mocker = mocker.MagicMock()
    event_handler_mocker.get_names.side_effect = [[START_EVENT], [EVENT1], [KILL_EVENT]]
    event_board_mocker.get_event_handler.return_value = event_handler_mocker

    routine_mocker = mocker.MagicMock()
    routine_mocker.name = ROUTINE_NAME

    logger_mocker = mocker.MagicMock()
    logger_mocker.get_child.return_value = mocker.MagicMock()

    dummy_flow = Flow(name="Flow1",
                      event_board=event_board_mocker,
                      logger=logger_mocker,
                      routines=[routine_mocker])

    return dummy_flow


def test_run(mocker, dummy_flow_with_two_routines: Flow):
    start_event_callback_mock = mocker.MagicMock()
    dummy_flow_with_two_routines.get_events()[START_EVENT] = {start_event_callback_mock}

    stop_event_callback_mock = mocker.MagicMock()
    dummy_flow_with_two_routines.get_events()[STOP_EVENT] = {stop_event_callback_mock}

    routine = dummy_flow_with_two_routines.routines[ROUTINE_NAME]

    dummy_flow_with_two_routines.run()

    assert routine.execute_event.call_count == 4
    assert routine.execute_event.call_args_list == [call(START_EVENT), call(EVENT1), call(KILL_EVENT), call("stop")]

    start_event_callback_mock.assert_called_once()
    stop_event_callback_mock.assert_called_once()


def test_execute_event(dummy_flow_with_two_routines: Flow):
    EVENT_NAME = "MAYO"

    dummy_flow_with_two_routines.execute_event(EVENT_NAME)
    routine_mocker = dummy_flow_with_two_routines.routines[ROUTINE_NAME]

    routine_mocker.execute_event.assert_called_with(EVENT_NAME)