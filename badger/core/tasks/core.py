__all__ = ["Task", "TaskResult", "execute_tasks"]

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar

from playwright.sync_api import Locator, Page

from badger.core.utils import get_text, iter_table


class Task(ABC):
    id: ClassVar[str]
    name: ClassVar[str]

    @abstractmethod
    def matches(self, entry: str) -> bool: ...

    @abstractmethod
    def run(self, page: Page, log: Callable[[str], None], **kwargs: Any) -> None: ...


@dataclass
class TaskResult:
    entry_index: int
    task_id: str
    task_name: str
    success: bool
    message: str


def _open_entry(list_page: Page, entry: Locator) -> Page:
    with list_page.context.expect_page() as new_page:
        entry.nth(0).locator("a").click()
    page = new_page.value
    page.wait_for_load_state()
    return page


def _process_entry(
    list_page: Page,
    entry: Locator,
    *,
    index: int,
    label: str,
    tasks: list[Task],
    log: Callable[[str], None],
) -> TaskResult | None:
    task: Task | None = None
    try:
        type_ = get_text(entry.nth(1))
        task = next((it for it in tasks if it.matches(type_)), None)
        if task is None:
            log(f"{label}: no selected task matches, skipping.")
            return None

        log(f"{label}: running {task.name}")
        page = _open_entry(list_page, entry)
        try:
            task.run(page, lambda msg: log(f"{label}: {msg}"))
        finally:
            page.close()
    except Exception as err:  # noqa: BLE001
        message = f"{type(err).__name__}: {err}"
        log(f"{label}: failed - {message}")
        return TaskResult(
            entry_index=index,
            task_id=task.id if task else "",
            task_name=task.name if task else "",
            success=False,
            message=message,
        )

    log(f"{label}: {task.name} completed.")
    return TaskResult(
        entry_index=index,
        task_id=task.id,
        task_name=task.name,
        success=True,
        message=f"{task.name} completed.",
    )


def execute_tasks(
    list_page: Page, tasks: list[Task], log: Callable[[str], None], is_cancelled: Callable[[], bool]
) -> list[TaskResult]:
    entries = list(iter_table(page=list_page, table_id="ListGrid"))
    total = len(entries)
    log(f"Found {total} entries.")

    results: list[TaskResult] = []
    for index, entry in enumerate(entries):
        if is_cancelled():
            log("Cancelled, stopping.")
            break
        label = f"Entry {index + 1}/{total}"
        result = _process_entry(list_page, entry, index=index, label=label, tasks=tasks, log=log)
        if result is not None:
            results.append(result)
    return results
