from pipert2.core import Routine

from pipert2 import Pipe
from pipert2.core.base.synchronise_routines.routines_synchroniser import RoutinesSynchroniser


class AutoPacingPipe(Pipe):
    def __init__(self):
        super().__init__()

        self.routine_synchroniser = RoutinesSynchroniser(event_board=self.event_board,
                                                         logger=self.logger,
                                                         notify_callback=self.event_board.get_event_notifier())

    def build(self):
        super(AutoPacingPipe, self).build()
        self.routine_synchroniser.wires = self.wires
        self.routine_synchroniser.build()

    def join(self, to_kill=False):
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
