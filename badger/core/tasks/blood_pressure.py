__all__ = ["BloodPressure"]

from collections.abc import Callable
from typing import Any

from playwright.sync_api import Page

from badger.core.tasks.core import Task


class BloodPressure(Task):
    id = "blood-pressure"
    name = "Blood Pressure"

    def matches(self, entry: str) -> bool:
        return self.name == entry

    def run(self, page: Page, log: Callable[[str], None], **kwargs: Any) -> None:
        log("Performing Blood Pressure recall")
        page.get_by_role("button", name="Complete").click()
