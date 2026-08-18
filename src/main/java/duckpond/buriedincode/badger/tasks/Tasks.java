package duckpond.buriedincode.badger.tasks;

import duckpond.buriedincode.badger.tasks.impl.BloodPressureTask;
import java.util.List;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class Tasks {
  public static final List<Task> ALL = List.of(new BloodPressureTask());

  private Tasks() {
  }
}
