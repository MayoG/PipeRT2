import time
import threading
from typing import Dict
from logging import Logger
import multiprocessing as mp
from statistics import median
from pipert2.utils.base_event_executor import BaseEventExecutor
from pipert2.utils.annotations import class_functions_dictionary
from pipert2.utils.consts import START_EVENT_NAME, KILL_EVENT_NAME, FINISH_ROUTINE_LOGIC_NAME
from pipert2.core.base.routines.source_routine import SourceRoutine
from pipert2.core.base.synchronize_routines.synchronizer_node import SynchronizerNode


class RoutinesSynchronizer(BaseEventExecutor):

    events = class_functions_dictionary()

    def __init__(self, event_board: any, logger: Logger, wires: Dict,
                 notify_callback: callable):

        super().__init__(event_board, logger)
        self.max_queue_size = 200
        self.wires = wires
        self._logger = logger
        self.notify_callback = notify_callback
        self.updating_interval = 1

        self._stop_event = mp.Event()

        mp_manager = mp.Manager()
        mp_manager.register('SynchronizerNode', SynchronizerNode)

        self.mp_manager = mp_manager
        self.routines_graph: Dict[str, SynchronizerNode] = mp_manager.dict()

        self.notify_delay_thread: threading.Thread = threading.Thread(target=self.update_delay_iteration)

        self.routines_measurements: Dict[str, list] = self.mp_manager.dict()

    def before_build(self) -> None:
        """Start the queue listener process.

        """

        self.routines_graph = self.create_routines_graph()
        self._stop_event.set()

    def create_routines_graph(self):
        """Build the routine's graph.

        Returns:
            Multiprocess dictionary of { "routine name", synchronized_node }
        """

        synchronize_graph = {}
        synchronizer_nodes = {}

        for wire in self.wires.values():
            for wire_destination_routine in wire.destinations:
                if wire_destination_routine.name not in synchronizer_nodes:
                    synchronizer_nodes[wire_destination_routine.name] = SynchronizerNode(
                        wire_destination_routine.name,
                        wire_destination_routine.flow_name,
                        [],
                        self.mp_manager
                    )

            destinations_synchronizer_nodes = [synchronizer_nodes[wire_destination_routine.name]
                                               for wire_destination_routine
                                               in wire.destinations]

            if wire.source.name in synchronizer_nodes:
                synchronizer_nodes[wire.source.name].nodes = destinations_synchronizer_nodes
            else:
                source_node = SynchronizerNode(
                    wire.source.name,
                    wire.source.flow_name,
                    destinations_synchronizer_nodes,
                    self.mp_manager
                )

                if isinstance(wire.source, SourceRoutine):
                    synchronize_graph[source_node.name] = source_node

        return self.mp_manager.dict(synchronize_graph)

    def get_routine_fps(self, routine_name):
        """Get the median fps by routine name.

        Args:
            routine_name: The routine name.

        Returns:
            The median fps for the required fps.
        """

        if routine_name in self.routines_measurements:
            routine_fps_list = self.routines_measurements[routine_name]

            if len(routine_fps_list) > 0:
                return 1 / median(routine_fps_list)

        return 0

    def update_delay_iteration(self):
        """One iteration of updating fps for all graph's routines.

        """

        while not self._stop_event.is_set():
            self._execute_function_for_sources(SynchronizerNode.update_original_fps_by_real_time.__name__, self.get_routine_fps)
            self._execute_function_for_sources(SynchronizerNode.update_fps_by_nodes.__name__)
            self._execute_function_for_sources(SynchronizerNode.update_fps_by_fathers.__name__)
            self._execute_function_for_sources(SynchronizerNode.notify_fps.__name__, self.notify_callback)
            self._execute_function_for_sources(SynchronizerNode.reset.__name__)

            time.sleep(self.updating_interval)

    def join_external(self) -> None:
        """Block until the notify delay thread stops.

        """

        if self.notify_delay_thread.is_alive():
            self.notify_delay_thread.join(timeout=1)

    @events(START_EVENT_NAME)
    def start_notify_process(self):
        """Start the notify process.

        """

        if self._stop_event.is_set():
            self._stop_event.clear()
            self.notify_delay_thread.start()

    @events(KILL_EVENT_NAME)
    def kill_synchronized_process(self):
        """Kill the listening the queue process.

        """

        if not self._stop_event.is_set():
            self._stop_event.set()

    @events(FINISH_ROUTINE_LOGIC_NAME)
    def update_finish_routine_logic_time(self, **params):
        """Updating the duration of routine.

        Args:
            **params: Dictionary contained the routine name.
        """

        routine_name = params['routine_name']
        durations: [] = params['durations']

        if routine_name not in self.routines_measurements:
            self.routines_measurements[routine_name] = self.mp_manager.list()

        self.routines_measurements[routine_name] = durations

    def _execute_function_for_sources(self, callback: callable, param=None):
        """Execute the callback function for all the graph's sources.

        Args:
            callback: Function in synchronize node to activate

        """

        for value in self.routines_graph.values():
            if param is not None:
                value.__getattribute__(callback)(param)
            else:
                value.__getattribute__(callback)()
