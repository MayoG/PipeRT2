import time
from pipert2.utils.method_data import Method
from pipert2.utils.batch_notifier import BatchNotifier
from pipert2.utils.interfaces import EventExecutorInterface
from pipert2.utils.annotations import class_functions_dictionary
from pipert2.core.base.routine_logic_runner import RoutineLogicRunner
from pipert2.utils.consts import NOTIFY_ROUTINE_DURATIONS_NAME, UPDATE_FPS_NAME, START_EVENT_NAME, STOP_EVENT_NAME
from pipert2.utils.consts.synchronise_routines import FPS_MULTIPLIER, ROUTINE_NOTIFY_DURATIONS_INTERVAL, NULL_FPS, \
    DURATIONS_MAX_SIZE


class FPSLogicRunner(RoutineLogicRunner):

    events = class_functions_dictionary()

    def __init__(self, name: str, logger):

        self.name = name
        self._logger = logger

        self.notifier = None

        self.last_main_logic_duration = None
        self._fps = NULL_FPS
        self._const_fps = NULL_FPS

    def execute_event(self, event: Method) -> None:
        EventExecutorInterface.execute_event(self, event)

    def initialize(self, event_notifier):
        """Initialize FPSRoutine and initialize the base class.

        Args:
            event_notifier: The callback for event notifying.

        """

        self.notifier = BatchNotifier(ROUTINE_NOTIFY_DURATIONS_INTERVAL,
                                      NOTIFY_ROUTINE_DURATIONS_NAME,
                                      event_notifier, self.name, DURATIONS_MAX_SIZE)

    def set_const_fps(self, fps):
        """Set const fps for routine.

        Args:
            fps: The require fps.

        """

        self._const_fps = fps

    def run(self, extended_run):
        """Run the routine logic with delaying by required fps.

        Returns:

        """

        extended_run()
        self._delay_routine()
        self.last_main_logic_duration = None

    def _delay_routine(self):
        """Delay the routine by required fps.

        """

        if self.last_main_logic_duration is not None and (self._fps > NULL_FPS or self._const_fps > NULL_FPS):
            required_fps = self._const_fps if self._const_fps > NULL_FPS else self._fps

            if (required_fps > 0) and self.last_main_logic_duration < (1 / required_fps):
                time.sleep((1 / required_fps) - self.last_main_logic_duration)

    def run_main_logic(self, main_logic):
        """Run main logic with updating durations queue.

        Args:
            main_logic: Main logic to run.

        Returns:
            (main logic result, the duration time of main logic)

        """

        start_time = time.time()

        result = main_logic()

        duration: float = time.time() - start_time

        if self._const_fps is not NULL_FPS:
            duration = 1 / self._const_fps

        self.notifier.data.append(duration)
        self.last_main_logic_duration = duration

        return result

    @events(UPDATE_FPS_NAME)
    def update_delay_time(self, fps) -> None:
        """Update the routine's fps.

        """

        if fps != NULL_FPS and fps > 0:
            self._fps = fps * FPS_MULTIPLIER

        print(f"Current fps of {self.name} is: {self._fps}")

    @events(START_EVENT_NAME)
    def start_notifier(self) -> None:
        """Start the batch notifier.

        """

        self.notifier.start()

    @events(STOP_EVENT_NAME)
    def stop_notifier(self) -> None:
        """Stop the batch notifier.

        """

        self.notifier.stop()

    @classmethod
    def get_events(cls):
        """Get the events of the routine

        Returns:
            dict[str, list[Callback]]: The events callbacks mapped by their events

        """

        return cls.events.all[cls.__name__]
