package duckpond.buriedincode.badger.tasks;

import com.microsoft.playwright.Page;
import java.util.function.Consumer;
import org.jspecify.annotations.NullMarked;

@NullMarked
public interface Task {
  String getId();

  String getName();

  boolean matches(String entry);

  void run(Page page, Consumer<String> log);
}
