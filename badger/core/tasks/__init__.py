__all__ = ["TASKS", "Task", "execute_tasks"]

from badger.core.tasks.blood_pressure import BloodPressure
from badger.core.tasks.core import Task, execute_tasks

TASKS: list[Task] = [BloodPressure()]
