__version__ = "2.1.2"

try:
    from dataclasses import dataclass, field, fields
except ImportError:
    from .utils.data_class.dataclasses import dataclass, field, fields


# User interaction classes
from .core import Pipe, Wire

# Interfaces for user implementations
from .core import SourceRoutine, MiddleRoutine, DestinationRoutine, Network, MessageHandler, DataTransmitter

# Given implementations
from .core import QueueNetwork, QueueHandler, SharedMemoryTransmitter, BasicTransmitter

# Event names.
from .utils import START_EVENT_NAME, STOP_EVENT_NAME, KILL_EVENT_NAME
