package duckpond.buriedincode.tasks;

import static duckpond.buriedincode.Utils.getText;
import static duckpond.buriedincode.Utils.iterTableRows;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

@NullMarked
public final class TaskRunner {
  private TaskRunner() {
  }

  public static List<TaskResult> executeTasks(
      Page listPage,
      List<Task> tasks,
      Consumer<String> log,
      BooleanSupplier isCancelled
  ) {
    // TODO: Define table grid
    var entries = iterTableRows(listPage, "ListGrid");
    var total = entries.size();
    log.accept("Found %s entries.".formatted(total));

    var results = new ArrayList<TaskResult>();
    for (var index = 0; index < total; index++) {
      if (isCancelled.getAsBoolean()) {
        log.accept("Cancelled, stopping.");
        break;
      }
      var label = "Entry %d/%d".formatted(index + 1, total);
      var result = processEntry(listPage, entries.get(index), index, label, tasks, log);
      if (result != null) {
        results.add(result);
      }
    }
    return results;
  }

  private static Page openEntry(Page listPage, Locator entry) {
    var context = listPage.context();
    // TODO: Define column idx
    var page = context.waitForPage(() -> entry.nth(0).locator("a").click());
    page.waitForLoadState();
    return page;
  }

  @Nullable
  private static TaskResult processEntry(
      Page listPage,
      Locator entry,
      int index,
      String label,
      List<Task> tasks,
      Consumer<String> log
  ) {
    Task task = null;
    try {
      // TODO: Define column idx
      var type = getText(entry.nth(1));
      task = tasks
        .stream()
        .filter(candidate -> candidate.matches(type))
        .findFirst()
        .orElse(null);
      if (task == null) {
        log.accept("%s: no selected task matches, skipping.".formatted(label));
        return null;
      }

      log.accept(label + ": running " + task.getName());
      try (var page = openEntry(listPage, entry)) {
        task.run(page, msg -> log.accept("%s: %s".formatted(label, msg)));
      }
    } catch (RuntimeException err) {
      var message = "%s: %s".formatted(err.getClass().getSimpleName(), err.getMessage());
      log.accept("%s: failed - %s".formatted(label, message));
      return new TaskResult(index, task != null ? task.getId() : "", task != null ? task.getName() : "", false, message);
    }

    log.accept("%s: %s completed.".formatted(label, task.getName()));
    return new TaskResult(index, task.getId(), task.getName(), true, "%s completed.".formatted(task.getName()));
  }
}
