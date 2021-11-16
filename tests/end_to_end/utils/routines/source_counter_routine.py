import time
import multiprocessing as mp
from typing import Callable

from pipert2 import SourceRoutine, MessageHandler
from pipert2.utils.consts import NULL_FPS


class SourceCounterRoutine(SourceRoutine):
    def __init__(self, fps, name, const_fps=NULL_FPS):
        super().__init__(name, const_fps=const_fps)
        self.routine_fps = fps
        self.counter = mp.Value('i', 0)

        self.prev_run_time = None
        self.estimate_fps = mp.Value('f', NULL_FPS)

        self._const_fps = 0

    def main_logic(self) -> dict:

        fps = self.routine_logic_runner._const_fps if not self.routine_logic_runner._const_fps == NULL_FPS else self.routine_logic_runner._fps

        if fps is not None:
            self.estimate_fps.value = fps

        self.counter.value = self.counter.value + 1
        time.sleep(1 / self.routine_fps)

        return {
            'test': 'test'
        }

    def initialize(self, message_handler: MessageHandler, event_notifier: Callable, auto_pacing_mechanism: bool = False, *args, **kwargs):
        super().initialize(message_handler, event_notifier, auto_pacing_mechanism)

        if self._const_fps > 0:
            self.routine_logic_runner.set_const_fps(self._const_fps)
