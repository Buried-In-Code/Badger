from badger.core.tasks.core import TaskResult


def test_task_result_retains_outcome() -> None:
    result = TaskResult(
        entry_index=2,
        task_id="blood-pressure",
        task_name="Blood Pressure",
        success=False,
        message="Unable to complete task",
    )

    assert result.entry_index == 2
    assert result.task_id == "blood-pressure"
    assert result.task_name == "Blood Pressure"
    assert result.success is False
    assert result.message == "Unable to complete task"


def test_task_results_use_value_equality() -> None:
    first = TaskResult(
        entry_index=0,
        task_id="blood-pressure",
        task_name="Blood Pressure",
        success=True,
        message="Blood Pressure completed.",
    )
    second = TaskResult(
        entry_index=0,
        task_id="blood-pressure",
        task_name="Blood Pressure",
        success=True,
        message="Blood Pressure completed.",
    )

    assert first == second
