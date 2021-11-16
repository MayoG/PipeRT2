from pipert2.core.base.routine_logic_runner import RoutineLogicRunner
from pipert2.utils.method_data import Method


class BaseRoutineLogicRunner(RoutineLogicRunner):
    def initialize(self, *args, **kwargs):
        pass

    def execute_event(self, event: Method) -> None:
        pass

    def run(self, extended_run: callable):
        extended_run()

    def run_main_logic(self, main_logic):
        return main_logic()
