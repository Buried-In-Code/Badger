package duckpond.buriedincode.badger;

import duckpond.buriedincode.badger.logs.LogStore;
import duckpond.buriedincode.badger.ui.BadgerUI;
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
