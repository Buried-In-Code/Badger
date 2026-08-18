package duckpond.buriedincode.tasks.impl;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import duckpond.buriedincode.tasks.Task;
import java.util.function.Consumer;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class BloodPressureTask implements Task {
  @Override
  public String getId() {
    return "blood-pressure";
  }

  @Override
  public String getName() {
    return "Blood Pressure";
  }

  @Override
  public boolean matches(String entry) {
    return getName().equals(entry);
  }

  @Override
  public void run(Page page, Consumer<String> log) {
    log.accept("Performing Blood Pressure recall");
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Complete")).click();
  }
}
