package duckpond.buriedincode.badger;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class PageUtils {
  private PageUtils() {
  }

  public static String getText(Locator locator) {
    return locator.innerText().strip();
  }

  public static List<Locator> iterTableRows(Page page, String tableId) {
    var table = page.locator("table[id=\"%s\"]".formatted(tableId));
    var rows = table.locator("tbody tr");
    var cells = new ArrayList<Locator>();
    var count = rows.count();
    for (var index = 0; index < count; index++) {
      cells.add(rows.nth(index).locator("td"));
    }
    return cells;
  }
}
