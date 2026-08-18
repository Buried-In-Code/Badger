__all__ = ["get_text", "iter_table"]

from collections.abc import Iterator

from playwright.sync_api import Locator, Page


def iter_table(page: Page, table_id: str) -> Iterator[Locator]:
    table = page.locator(f'table[id="{table_id}"]')
    rows = table.locator("tbody tr")
    for idx in range(rows.count()):
        yield rows.nth(idx).locator("td")


def get_text(obj: Locator) -> str:
    return obj.inner_text().strip()
