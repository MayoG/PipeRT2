import pytest
from collections import deque
from pipert2 import MiddleRoutine
from pytest_mock import MockerFixture

from pipert2.core.base.routine_logic_runners.fps_logic_runner import FPSLogicRunner
from pipert2.utils.dummy_object import Dummy
from tests.unit.pipert.core.utils.dummy_routines.dummy_middle_routine import DummyMiddleRoutine


@pytest.fixture()
def fps_logic_runner_with_dummy_notifier(mocker: MockerFixture):
    fps_logic_runner_with_dummy_notifier = FPSLogicRunner("dummy", mocker.MagicMock())
    fps_logic_runner_with_dummy_notifier.notifier = mocker.MagicMock()

    return fps_logic_runner_with_dummy_notifier


def test_run_with_delay_time(mocker: MockerFixture, fps_logic_runner_with_dummy_notifier):
    time_sleep_mock = mocker.patch("time.sleep")
    fps_logic_runner_with_dummy_notifier.last_main_logic_duration = 0.25
    fps_logic_runner_with_dummy_notifier._fps = 2

    fps_logic_runner_with_dummy_notifier.run(mocker.MagicMock())

    time_sleep_mock.assert_called_with(0.25)
    assert fps_logic_runner_with_dummy_notifier.last_main_logic_duration is None


def test_run_without_delay_time(mocker: MockerFixture, fps_logic_runner_with_dummy_notifier):
    time_sleep_mock = mocker.patch("time.sleep")
    fps_logic_runner_with_dummy_notifier.last_main_logic_duration = 1
    fps_logic_runner_with_dummy_notifier._fps = 2

    fps_logic_runner_with_dummy_notifier.run(mocker.MagicMock())

    time_sleep_mock.assert_not_called()
    assert fps_logic_runner_with_dummy_notifier.last_main_logic_duration is None


def test_run_main_logic(mocker: MockerFixture, fps_logic_runner_with_dummy_notifier):
    time_mock = mocker.patch("time.time")
    time_mock.side_effect = [1, 2]

    main_logic_mock = mocker.MagicMock()
    main_logic_mock.return_value = "test"

    notifier_mock = fps_logic_runner_with_dummy_notifier.notifier
    notifier_mock.data = mocker.MagicMock()

    run_main_logic_result = fps_logic_runner_with_dummy_notifier.run_main_logic(main_logic_mock)

    notifier_mock.data.append.assert_called_with(1)
    assert fps_logic_runner_with_dummy_notifier.last_main_logic_duration == 1
    assert run_main_logic_result == "test"
