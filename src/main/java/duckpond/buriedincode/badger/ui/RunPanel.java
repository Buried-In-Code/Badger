package duckpond.buriedincode.badger.ui;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class RunPanel extends JPanel {
  private final JButton runBtn;
  private final JButton stopBtn;
  private final JLabel statusLabel;

  public RunPanel(Runnable onRun, Runnable onStop) {
    super(new BorderLayout());
    setBorder(BorderFactory.createTitledBorder("Step 3  -  Run"));

    var row = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 6));
    runBtn = new JButton("Start");
    runBtn.addActionListener(e -> onRun.run());
    row.add(runBtn);

    stopBtn = new JButton("Stop");
    stopBtn.addActionListener(e -> onStop.run());
    row.add(stopBtn);
    add(row, BorderLayout.WEST);

    statusLabel = new JLabel("");
    var statusRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 6));
    statusRow.add(statusLabel);
    add(statusRow, BorderLayout.EAST);
  }

  public void setState(RunState state, boolean canStart) {
    var isRunning = state == RunState.RUNNING;
    runBtn.setEnabled(canStart);
    runBtn.setText(isRunning ? "Running" : "Start");
    stopBtn.setEnabled(isRunning);
    statusLabel.setText(
        switch (state) {
          case RUNNING -> "Running";
          case COMPLETE -> "Complete";
          case IDLE -> "";
        }
    );
  }
}
