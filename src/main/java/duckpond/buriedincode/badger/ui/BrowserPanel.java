package duckpond.buriedincode.badger.ui;

import duckpond.buriedincode.badger.browser.BrowserUtils;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.FlowLayout;
import java.util.function.Consumer;
import java.util.function.IntConsumer;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSeparator;
import javax.swing.JSpinner;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingConstants;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class BrowserPanel extends JPanel {
  private final JButton launchBtn;
  private final JLabel statusLabel;
  private final JPanel advancedPanel;
  private boolean advancedOpen = false;
  private final JSpinner portSpinner;
  private final JTextField browserPathField;

  public BrowserPanel(Runnable onLaunch, IntConsumer onPortChange, Consumer<Boolean> onDebugVisibilityChange) {
    super(new BorderLayout());
    setBorder(BorderFactory.createTitledBorder("Step 1  -  Open Browser"));

    var topRow = new JPanel(new BorderLayout());

    var launchRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 6));
    launchBtn = new JButton("Open Browser");
    launchBtn.addActionListener(e -> onLaunch.run());
    launchRow.add(launchBtn);

    statusLabel = new JLabel("Not running");
    launchRow.add(statusLabel);
    topRow.add(launchRow, BorderLayout.WEST);

    var advBtn = new JButton("Advanced");
    advBtn.addActionListener(e -> toggleAdvanced());
    var advBtnRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 6));
    advBtnRow.add(advBtn);
    topRow.add(advBtnRow, BorderLayout.EAST);

    add(topRow, BorderLayout.NORTH);

    advancedPanel = new JPanel(new BorderLayout());

    var optionsRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 4));
    optionsRow.add(new JLabel("Debug port:"));
    portSpinner = new JSpinner(new SpinnerNumberModel(9222, 1024, 65535, 1));
    ((JSpinner.DefaultEditor) portSpinner.getEditor()).getTextField().setColumns(6);
    portSpinner.addChangeListener(e -> onPortChange.accept(getPort()));
    optionsRow.add(portSpinner);

    optionsRow.add(new JSeparator(SwingConstants.VERTICAL));

    var showDebugCheck = new JCheckBox("Show debug output");
    showDebugCheck.addActionListener(e -> onDebugVisibilityChange.accept(showDebugCheck.isSelected()));
    optionsRow.add(showDebugCheck);
    advancedPanel.add(optionsRow, BorderLayout.NORTH);

    var pathRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 4));
    pathRow.add(new JLabel("Browser path:"));
    browserPathField = new JTextField(BrowserUtils.defaultBrowserPath(), 40);
    pathRow.add(browserPathField);
    advancedPanel.add(pathRow, BorderLayout.SOUTH);

    advancedPanel.setVisible(false);
    add(advancedPanel, BorderLayout.SOUTH);
  }

  public String getBrowserPath() {
    return browserPathField.getText();
  }

  public int getPort() {
    return (Integer) portSpinner.getValue();
  }

  public void setState(BrowserState state) {
    var launchLocked = state == BrowserState.OPEN || state == BrowserState.LAUNCHING;
    launchBtn.setEnabled(!launchLocked);
    portSpinner.setEnabled(!launchLocked);
    browserPathField.setEnabled(!launchLocked);

    String text;
    Color colour;
    switch (state) {
      case OPEN -> {
        text = "Ready";
        colour = new Color(0x4c, 0xaf, 0x50);
      }
      case LAUNCHING -> {
        text = "Launching";
        colour = new Color(0xff, 0x98, 0x00);
      }
      case FAILED -> {
        text = "Failed";
        colour = new Color(0xf4, 0x47, 0x47);
      }
      default -> {
        text = "Not running";
        colour = new Color(0x9e, 0x9e, 0x9e);
      }
    }
    statusLabel.setText(text);
    statusLabel.setForeground(colour);
  }

  private void toggleAdvanced() {
    advancedOpen = !advancedOpen;
    advancedPanel.setVisible(advancedOpen);
    revalidate();
    repaint();
  }
}
