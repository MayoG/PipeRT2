from src.pipert2.core.base.routine import Routine

DUMMY_ROUTINE_EVENT_NAME = "Change"


class DummyRoutine(Routine):

    def __init__(self, counter=0, **kwargs):
        super().__init__(**kwargs)
        self.counter = counter
        self.inc = True

    def main_logic(self, data):
        if self.inc:
            self.counter += 1
        else:
            self.counter -= 1

    def setup(self) -> None:
        self.counter = 0

    def cleanup(self) -> None:
        pass

    @Routine.events(DUMMY_ROUTINE_EVENT_NAME)
    def change_logic(self):
        self.inc = not self.inc
