from logging import Logger

from pipert2.utils.logging_module_modifiers import get_default_print_logger

from pipert2 import Pipe, Network, QueueNetwork, DataTransmitter, BasicTransmitter
from pipert2.core import Routine
from pipert2.core.base.synchronise_routines.routines_synchroniser import RoutinesSynchroniser


class AutoPacingPipe(Pipe):
    def __init__(self, network: Network = QueueNetwork(),
                 logger: Logger = get_default_print_logger("Pipe"),
                 data_transmitter: DataTransmitter = BasicTransmitter()):

        super().__init__(network, logger, data_transmitter)

        self.routine_synchroniser = RoutinesSynchroniser(event_board=self.event_board,
                                                         logger=self.logger,
                                                         notify_callback=self.event_board.get_event_notifier())

    def build(self):
        """Build the pipe to be ready to start working, and build the routine synchroniser.

        """

        super(AutoPacingPipe, self).build()
        self.routine_synchroniser.wires = self.wires
        self.routine_synchroniser.build()

    def join(self, to_kill=False):
        """Block the execution until all of the processes of base pipe have been killed and the synchroniser.

        """

        super(AutoPacingPipe, self).join()
        self.routine_synchroniser.join()
        self.logger.plog("Joined synchroniser")

    def _initialize_routines(self, *routines: Routine):
        """Initialize routines with auto pacing.

            Args:
                *routines: The routines to initialized.

            Returns:
                Initialized routines with auto pacing.
            """

        for routine in routines:
            routine.initialize(message_handler=self.network.get_message_handler(routine.name),
                               event_notifier=self.event_board.get_event_notifier(),
                               auto_pacing_mechanism=True)
