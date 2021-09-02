from abc import ABC, abstractmethod
from src.pipert2.core.base.method import Method


class EventExecutorInterface(ABC):  # TODO - Maybe add a logger abstract class for each class with logger.

    @abstractmethod
    def execute_event(self, event: Method) -> None:
        mapped_events = self.get_events()

        if event.name in mapped_events:
            self._logger.info(f"Running event '{event.name}'")
            for callback in mapped_events[event.name]:
                callback(self, **event.params)

    @classmethod
    @abstractmethod
    def get_events(cls):
        raise NotImplementedError
