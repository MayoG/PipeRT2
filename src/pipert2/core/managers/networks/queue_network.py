from typing import Tuple
from src.pipert2.core import Routine, Network, QueueHandler, DataTransmitter
from src.pipert2.utils.publish_queue import PublishQueue


class QueueNetwork(Network):
    """The queue network generates queue handlers to manage communication using multiprocessing queues within the pipe.

    """

    def get_message_handler(self, routine_name: str) -> QueueHandler:
        """Generate/Retrieve a queue handler.

        Args:
            routine_name: The name of the routine to retrieve the queue handler for.

        Returns:
            A QueueHandler object relevant to the routine.

        """

        if routine_name in self.message_handlers:
            message_handler = self.message_handlers[routine_name]
        else:
            message_handler = QueueHandler(routine_name)
            self.message_handlers[routine_name] = message_handler

        return message_handler

    def link(self, source: Routine, destinations: Tuple[Routine], data_transmitter: DataTransmitter):
        """Links between two QueueHandlers of the given routines.

        Args:
            source: The source routine that generates data.
            destinations: Destination routines that receive the data.
            data_transmitter: The data transmitter that indicates how to transfer the data.

        """
        publish_queue = PublishQueue()

        for destination_routine in destinations:
            destination_routine.message_handler.input_queue = \
                publish_queue.register(destination_routine.message_handler.input_queue)
            destination_routine.message_handler.receive = data_transmitter.receive()

        source.message_handler.output_queue = publish_queue
        source.message_handler.transmit = data_transmitter.transmit()
