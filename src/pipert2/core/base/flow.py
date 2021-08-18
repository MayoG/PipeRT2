from multiprocessing import Process
from typing import List
from src.pipert2.core.base.logger import PipeLogger
from src.pipert2.core.base.routine import Routine
from src.pipert2.core.handlers.event_handler import EventHandler
from src.pipert2.core.managers.event_board import EventBoard
from src.pipert2.utils.annotations import class_functions_dictionary
from src.pipert2.utils.consts.event_names import START_EVENT_NAME, STOP_EVENT_NAME, KILL_EVENT_NAME
from src.pipert2.utils.interfaces.event_executor_interface import EventExecutorInterface
from src.pipert2.utils.method_data import Method
from src.pipert2.utils.dummy_object import Dummy


class Flow(EventExecutorInterface):
    """Flow is an entity designed for running a group of routines in a single process.
    It is also responsible to notify his routines when an event is triggered.

    """

    events = class_functions_dictionary()

    def __init__(self, name: str, event_board: EventBoard, logger: PipeLogger, routines: List[Routine]):
        """
        Args:
            name (str): Name of the flow.
            event_board (EventBoard): The EventBoard of the pipe.
            logger (PipeLogger): PipeLogger object for logging the flow actions.
            routines (Routine): The routines that will be in the flow.

        Attributes:
            routines (dict[str, Routine]): Dictionary mapping the routines to their name.
            name (str): Name of the flow.
            logger (PipeLogger): PipeLogger object for logging the flow actions.
            event_handler (EventHandler): EventHandler object for communicating with the
                event system of the pipe.

        """

        self.routines = {}
        self.name = name
        self._logger = logger
        self.flow_process = Dummy()

        flow_events_to_listen = set(self.get_events().keys())

        for routine in routines:
            routine.set_logger(logger=logger.get_child())
            flow_events_to_listen.update(routine.get_events().keys())
            self.routines[routine.name] = routine

        self.event_handler: EventHandler = event_board.get_event_handler(flow_events_to_listen)

    def build(self) -> None:
        """Start the flow process.

        """

        self.flow_process = Process(target=self.run)
        self.flow_process.start()

    def run(self) -> None:
        """The flow process, executing the pipe events that occur.

        """

        event: Method = self.event_handler.wait()
        while event.name != KILL_EVENT_NAME:
            self.execute_event(event)
            event = self.event_handler.wait()

        self.execute_event(Method(STOP_EVENT_NAME))

        for routine in self.routines.values():
            routine.join()

    @events(START_EVENT_NAME)
    def start(self):
        self._logger.info("Starting")

    @events(STOP_EVENT_NAME)
    def stop(self):
        self._logger.info("Stopping")

    def execute_event(self, event: Method) -> None:
        """Execute the event callbacks in the flow and its routines.

        Args:
            event: The event to be executed.

        """

        for routine in self.routines.values():
            routine.execute_event(event)

        EventExecutorInterface.execute_event(self, event)

    def join(self) -> None:
        """Block until the flow process terminates

        """

        self.flow_process.join()

    @classmethod
    def get_events(cls):
        """Get the events of the flow.

        Returns:
            dict[str, set[Callback]]: The events callbacks mapped by their events.

        """

        return cls.events.all[cls.__name__]
