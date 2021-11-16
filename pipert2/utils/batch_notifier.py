import time
import threading
from collections import deque
from typing import Callable, Deque


class BatchNotifier:
    def __init__(self, interval: float, event_name: str, notify: Callable, source: str, data_maxlen: int):
        self.interval = interval
        self.event_name = event_name
        self.notify = notify
        self.source = source

        self.stop_notify = threading.Event()
        self.data: Deque = deque(maxlen=data_maxlen)

    def start(self):
        """Starts the notify thread.

        """

        self.stop_notify.clear()
        threading.Thread(target=self._run).start()

    def stop(self):
        """Stops the notify thread.

        """

        self.stop_notify.set()

    def add(self, record):
        """Add a record to the data queue to notify.

        Args:
            record:

        Returns:

        """

        self.data.append(record)

    def _run(self):
        """Run the notifier logic, each time interval notify about the current data.

        Returns:

        """

        while not self.stop_notify.is_set():
            self.notify(event_name=self.event_name, source_name=self.source, data=self.data)
            time.sleep(self.interval)
