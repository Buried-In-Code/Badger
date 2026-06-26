import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Task:
    id: str
    name: str
    description: str


@dataclass
class TaskResult:
    task_id: str
    task_name: str
    success: bool
    message: str


TASKS: list[Task] = [
    Task(id="task_001", name="Task 1: Data Collection", description="Collect data from source"),
    Task(id="task_002", name="Task 2: Validation", description="Validate collected data"),
    Task(id="task_003", name="Task 3: Processing", description="Process collected data"),
    Task(id="task_004", name="Task 4: Reporting", description="Generate report"),
    Task(id="task_005", name="Task 5: Cleanup", description="Cleanup temporary files"),
]

APP_NAME = "Task Automation Manager"


def execute_tasks(
    tasks: list[Task],
    on_progress: Callable[[str], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
) -> list[TaskResult]:
    """Execute a list of tasks, reporting progress via callbacks.

    Args:
        tasks: The tasks to execute.
        on_progress: Optional callback invoked with a status message.
        is_cancelled: Optional callback; execution stops if it returns True.

    Returns:
        List of TaskResult for each task attempted.
    """
    results = []
    for task in tasks:
        if is_cancelled is not None and is_cancelled():
            break
        if on_progress is not None:
            on_progress(f"Running {task.name}...")
        time.sleep(2)
        result = TaskResult(
            task_id=task.id, task_name=task.name, success=True, message=f"{task.name} completed."
        )
        results.append(result)
        if on_progress is not None:
            on_progress(result.message)
    return results
