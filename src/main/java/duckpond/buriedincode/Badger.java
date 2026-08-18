package duckpond.buriedincode;

import duckpond.buriedincode.logs.LogStore;
import duckpond.buriedincode.ui.BadgerUI;
import javax.swing.SwingUtilities;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class Badger {
  private Badger() {
  }

  public static void main(String[] args) {
    SwingUtilities.invokeLater(() -> {
      var ui = new BadgerUI();
      ui.show(LogStore.readLogs());
    });
  }
}
