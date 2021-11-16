from abc import abstractmethod, ABCMeta
from pipert2.utils.interfaces import EventExecutorInterface


class RoutineLogicRunner(EventExecutorInterface, metaclass=ABCMeta):
    @abstractmethod
    def run(self, extended_run: callable):
        pass

    @abstractmethod
    def run_main_logic(self, main_logic):
        pass

    @classmethod
    def get_events(cls):
        pass

    @abstractmethod
    def initialize(self, *args, **kwargs):
        pass
