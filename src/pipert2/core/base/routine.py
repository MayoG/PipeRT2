import threading
import multiprocessing as mp
from typing import Callable
from functools import partial
from abc import ABCMeta, abstractmethod
from src.pipert2.utils.method_data import Method
from src.pipert2.core.base.logger import PipeLogger
from src.pipert2.core.handlers.message_handler import MessageHandler
from src.pipert2.utils.consts.event_names import START_EVENT_NAME, STOP_EVENT_NAME
from src.pipert2.utils.dummy_object import Dummy
from src.pipert2.utils.annotations import class_functions_dictionary
from src.pipert2.utils.interfaces.event_executor_interface import EventExecutorInterface


class Routine(EventExecutorInterface, metaclass=ABCMeta):
    """A routine is responsible for performing one of the flow’s main tasks.
    It can run as either a thread or a process.
    First it runs a setup function, then it runs its main logic function in a continuous loop, until it is told to terminate.
    Once terminated it runs a cleanup function.

    """

    events = class_functions_dictionary()
    runners = class_functions_dictionary()
    routines_created_counter = 0

    def __init__(self, name: str = None):
        """
        Args:
            name: Name of the routine

        Attributes:
            name (str): Name of the flow
            message_handler (MessageHandler): Message handler of the routine to send and receive messages
            runner_creator (Callback): Callback for running the routine's main logic
            event_notifier (Callback): Callback for notifying an event has occurred
            _logger (PipeLogger): The routines logger object
            stop_event (mp.Event): A multiprocessing event object indicating the routine state (run/stop)

        """

        if name is not None:
            self.name = name
        else:
            self.name = f"{self.__class__.__name__}-{self.routines_created_counter}"
            self.routines_created_counter += 1

        self.message_handler: MessageHandler = None
        self.runner_creator = None
        self.event_notifier: Callable = Dummy()
        self._logger: PipeLogger = Dummy()
        self.stop_event = mp.Event()
        self.stop_event.set()
        self.runner = Dummy()

    def initialize(self, message_handler: MessageHandler, event_notifier: Callable, *args, **kwargs):
        """Initialize the routine to be ready to run

        Args:
            message_handler: The routines message
            event_notifier: A callable object for notifying an event
            kwargs: Additional parameters for setting the routine with certain behaviors

        """

        self.message_handler = message_handler
        self.event_notifier = event_notifier

        self.message_handler.logger = self._logger

        if "runner" in kwargs and kwargs["runner"] in self.runners.all:
            self._get_runners()[kwargs["runner"]](self)
        else:
            self.set_runner_as_thread()

    def set_logger(self, logger: PipeLogger):
        self._logger = logger

    @classmethod
    def get_events(cls):
        """Get the events of the routine

        Returns:
            dict[str, list[Callback]]: The events callbacks mapped by their events

        """

        routine_events = cls.events.all[Routine.__name__]
        for event_name, events_functions in routine_events.items():
            cls.events.all[cls.__name__][event_name].update(events_functions)

        return cls.events.all[cls.__name__]

    @classmethod
    def _get_runners(cls):
        return cls.runners.all[cls.__name__]

    @abstractmethod
    def setup(self) -> None:
        """An initial setup before running

        """

        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        """The final method that ends the routine execution

        """

        raise NotImplementedError

    @abstractmethod
    def _extended_run(self) -> None:
        """Wrapper method for executing the entire routine logic

        """

<<<<<<< HEAD
        raise NotImplementedError
=======
        self.setup()

        while not self.stop_event.is_set():
            message = self.message_handler.get()
            try:
                output_data = self.main_logic(message.get_data())
            except Exception as error:
                self._logger.exception(f"The routine has crashed: {error}")
            else:
                message.update_data(output_data)
                self.message_handler.put(message)

        self.cleanup()
>>>>>>> 7678db007eb4dfe486269ffee27de2781d303adf

    @runners("thread")
    def set_runner_as_thread(self):
        self.runner_creator = partial(threading.Thread, target=self._extended_run)

    @events(START_EVENT_NAME)
    def start(self) -> None:
        """Start running the routine

        (This method will be called when the 'start' event is triggered)

        """

        if self.stop_event.is_set():
            self._logger.info("Starting")  # TODO - Maybe add an infrastructure logg type instead of info
            self.stop_event.clear()
            self.runner = self.runner_creator()
            self.runner.start()

    @events(STOP_EVENT_NAME)
    def stop(self) -> None:
        """Stop the routine from running

        (This method will be called when the 'stop' event is triggered)

        """

        if not self.stop_event.is_set():
            self._logger.info("Stopping")
            self.stop_event.set()
            self.runner.join()

    def execute_event(self, event: Method) -> None:
        """Execute an event to start

        Args:
            event: The event to execute

        """

        EventExecutorInterface.execute_event(self, event)  # TODO - Can be removed but i think it should stay

    def notify_event(self, event_name: str, **event_params) -> None:
        """Notify that an event has happened

        Args:
            event_name: The name of the event to notify

        """

        self.event_notifier(event_name, **event_params)

    def join(self):
        """Block until all routine thread terminates

        """

        if self.stop_event.is_set():
            self.runner.join()
