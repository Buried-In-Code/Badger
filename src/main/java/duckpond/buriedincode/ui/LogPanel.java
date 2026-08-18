package duckpond.buriedincode.ui;

import duckpond.buriedincode.logs.LogEntry;
import duckpond.buriedincode.logs.LogLevel;
import java.awt.BorderLayout;
import java.awt.Color;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import javax.swing.BorderFactory;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextPane;
import javax.swing.text.BadLocationException;
import javax.swing.text.SimpleAttributeSet;
import javax.swing.text.StyleConstants;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class LogPanel extends JPanel {
  private static final Color TIMESTAMP_COLOUR = new Color(0x75, 0x75, 0x75);
  private static final DateTimeFormatter TS_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private final JTextPane textPane;
  private final List<LogEntry> entries = new ArrayList<>();
  private final Map<LogLevel, Color> colours = new EnumMap<>(LogLevel.class);
  private boolean debugVisible = false;

  public LogPanel() {
    super(new BorderLayout());
    setBorder(BorderFactory.createTitledBorder("Activity Log"));

    colours.put(LogLevel.DEBUG, new Color(0x9c, 0xdc, 0xfe));
    colours.put(LogLevel.INFO, new Color(0xcc, 0xcc, 0xcc));
    colours.put(LogLevel.WARN, new Color(230, 230, 30));
    colours.put(LogLevel.ERROR, new Color(0xf4, 0x47, 0x47));

    textPane = new JTextPane();
    textPane.setEditable(false);
    textPane.setBackground(new Color(0x1e, 0x1e, 0x1e));
    textPane.setForeground(new Color(0xcc, 0xcc, 0xcc));

    add(new JScrollPane(textPane), BorderLayout.CENTER);
  }

  public void append(LogEntry log) {
    entries.add(log);
    if (log.level() != LogLevel.DEBUG || debugVisible) {
      appendLine(log);
    }
  }

  public void setDebugVisible(boolean visible) {
    this.debugVisible = visible;
    rerender();
  }

  private void appendLine(LogEntry log) {
    var doc = textPane.getStyledDocument();

    var tsAttrs = new SimpleAttributeSet();
    StyleConstants.setForeground(tsAttrs, TIMESTAMP_COLOUR);

    var msgAttrs = new SimpleAttributeSet();
    StyleConstants.setForeground(msgAttrs, colours.get(log.level()));

    try {
      doc.insertString(doc.getLength(), "[%s] ".formatted(TS_FORMAT.format(log.timestamp())), tsAttrs);
      doc.insertString(doc.getLength(), String.format("[%-5s] %s%n", log.level().name(), log.message()), msgAttrs);
    } catch (BadLocationException ble) {
      throw new IllegalStateException(ble);
    }
    textPane.setCaretPosition(doc.getLength());
  }

  private void rerender() {
    textPane.setText("");
    for (var entry : entries) {
      if (entry.level() != LogLevel.DEBUG || debugVisible) {
        appendLine(entry);
      }
    }
  }
}
