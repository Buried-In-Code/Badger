package duckpond.buriedincode.ui;

import duckpond.buriedincode.tasks.Task;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.FlowLayout;
import java.util.ArrayList;
import java.util.List;
import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class TaskPanel extends JPanel {
  private final List<Task> tasks;
  private final Runnable onSelectionChange;
  private final List<JCheckBox> checkboxes = new ArrayList<>();
  private final JButton selectAllBtn;
  private final JButton clearAllBtn;

  public TaskPanel(List<Task> tasks, Runnable onSelectionChange) {
    super(new BorderLayout());
    this.tasks = tasks;
    this.onSelectionChange = onSelectionChange;
    setBorder(BorderFactory.createTitledBorder("Step 2  -  Choose Tasks"));

    var btnRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 4));
    selectAllBtn = new JButton("Select All");
    selectAllBtn.addActionListener(e -> selectAll());
    btnRow.add(selectAllBtn);

    clearAllBtn = new JButton("Clear All");
    clearAllBtn.addActionListener(e -> clearAll());
    btnRow.add(clearAllBtn);
    add(btnRow, BorderLayout.NORTH);

    var listPanel = new JPanel();
    listPanel.setLayout(new BoxLayout(listPanel, BoxLayout.Y_AXIS));
    for (var task : tasks) {
      var checkbox = new JCheckBox(task.getName());
      checkbox.setAlignmentX(Component.LEFT_ALIGNMENT);
      checkbox.addActionListener(e -> onSelectionChange.run());
      checkboxes.add(checkbox);
      listPanel.add(checkbox);
    }

    var scrollPane = new JScrollPane(listPanel);
    scrollPane.setBorder(BorderFactory.createEmptyBorder());
    add(scrollPane, BorderLayout.CENTER);
  }

  public boolean hasSelection() {
    return checkboxes.stream().anyMatch(JCheckBox::isSelected);
  }

  public List<Task> selectedTasks() {
    var selected = new ArrayList<Task>();
    for (var i = 0; i < tasks.size(); i++) {
      if (checkboxes.get(i).isSelected()) {
        selected.add(tasks.get(i));
      }
    }
    return selected;
  }

  public void setTasksEnabled(boolean enabled) {
    for (var checkbox : checkboxes) {
      checkbox.setEnabled(enabled);
    }
    selectAllBtn.setEnabled(enabled);
    clearAllBtn.setEnabled(enabled);
  }

  private void clearAll() {
    checkboxes.forEach(cb -> cb.setSelected(false));
    onSelectionChange.run();
  }

  private void selectAll() {
    checkboxes.forEach(cb -> cb.setSelected(true));
    onSelectionChange.run();
  }
}
