from unittest.mock import patch
from _pytest.fixtures import fixture
from pytest_mock import MockerFixture
from pipert2.core.base.pipes.auto_pacing_pipe import AutoPacingPipe


@fixture()
def auto_pacing_pipe(mocker: MockerFixture):
    auto_pacing_pipe = AutoPacingPipe(mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock())

    auto_pacing_pipe.routine_synchroniser = mocker.MagicMock()
    auto_pacing_pipe.event_board = mocker.MagicMock()

    return auto_pacing_pipe


def test_build(auto_pacing_pipe):
    with patch("pipert2.core.base.pipes.pipe.flow_validator.validate_flow"):
        with patch("pipert2.core.base.pipes.pipe.wires_validator.validate_wires"):
            synchroniser = auto_pacing_pipe.routine_synchroniser
            auto_pacing_pipe.build()
            synchroniser.build.assert_called()


def test_join(auto_pacing_pipe):
    synchroniser = auto_pacing_pipe.routine_synchroniser
    auto_pacing_pipe.join()
    synchroniser.join.assert_called()


def test_create_flow_(auto_pacing_pipe, mocker):
    dummy_routine = mocker.MagicMock()
    auto_pacing_pipe.create_flow("test", False, dummy_routine)

    assert dummy_routine.initialize.call_args[1].get('auto_pacing_mechanism')
