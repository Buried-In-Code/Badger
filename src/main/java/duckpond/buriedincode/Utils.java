package duckpond.buriedincode;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class Utils {
  public static final String PROJECT = "badger";
  public static final String VERSION = "2026.2.0";

  private Utils() {
  }

  public static Path getCacheHome() {
    return home("cache");
  }

  public static Path getConfigHome() {
    return home("config");
  }

  public static Path getDataHome() {
    return home("data");
  }

  public static Path getStateHome() {
    return home("state");
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

  private static Path home(String leaf) {
    var folder = Path.of(System.getProperty("user.home"), ".%s".formatted(PROJECT), leaf);
    try {
      Files.createDirectories(folder);
    } catch (IOException ioe) {
      throw new UncheckedIOException(ioe);
    }
    return folder;
  }
}
