package duckpond.buriedincode.badger.ui;

import static duckpond.buriedincode.badger.Utils.PROJECT;
import static duckpond.buriedincode.badger.Utils.VERSION;
import duckpond.buriedincode.badger.browser.BrowserUtils;
import duckpond.buriedincode.badger.logs.LogEntry;
import duckpond.buriedincode.badger.logs.LogLevel;
import duckpond.buriedincode.badger.logs.LogStore;
import duckpond.buriedincode.badger.tasks.Task;
import duckpond.buriedincode.badger.tasks.TaskResult;
import duckpond.buriedincode.badger.tasks.TaskRunner;
import duckpond.buriedincode.badger.tasks.Tasks;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridLayout;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicReference;
import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class BadgerUI {
  private static final double POLL_INTERVAL_SECS = 2.0;
  private final JFrame frame;
  private volatile BrowserState browserState = BrowserState.CLOSED;
  private volatile RunState runState = RunState.IDLE;
  private final ConcurrentLinkedQueue<LogEntry> logQueue = new ConcurrentLinkedQueue<>();
  private volatile int pollPort = 9222;
  private BrowserPanel browserPanel;
  private TaskPanel taskPanel;
  private LogPanel logPanel;
  private RunPanel runPanel;

  public BadgerUI() {
    frame = new JFrame();
    setupWindow();
    buildUi();
    updateUi();

    new Timer(100, e -> processLogQueue()).start();

    var pollThread = new Thread(this::pollBrowser, "browser-poll");
    pollThread.setDaemon(true);
    pollThread.start();
  }

  public void show(List<LogEntry> initialLogs) {
    logQueue.addAll(initialLogs);
    frame.setVisible(true);
  }

  private void buildUi() {
    var main = new JPanel(new BorderLayout(0, 8));
    main.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
    frame.setContentPane(main);

    browserPanel = new BrowserPanel(this::onLaunchBrowser, this::onPortChange, this::onToggleDebug);
    main.add(browserPanel, BorderLayout.NORTH);

    var middle = new JPanel(new GridLayout(1, 2, 8, 0));
    taskPanel = new TaskPanel(Tasks.ALL, this::updateUi);
    middle.add(taskPanel);

    logPanel = new LogPanel();
    middle.add(logPanel);
    main.add(middle, BorderLayout.CENTER);

    runPanel = new RunPanel(this::onRun, this::onStop);
    main.add(runPanel, BorderLayout.SOUTH);
  }

  private void launchBrowserThread(int port, String browserPath) {
    var result = BrowserUtils.launchEdge((msg, level) -> queueLog("BROWSER", msg, level), port, browserPath);

    String reason;
    if (!result.running()) {
      reason = result.message();
    } else if (BrowserUtils.waitForBrowser(port, 30.0)) {
      SwingUtilities.invokeLater(() -> onLaunchFinished(true, ""));
      return;
    } else {
      reason = "no CDP response on port %d after 30s".formatted(port);
    }
    SwingUtilities.invokeLater(() -> onLaunchFinished(false, reason));
  }

  private void onBrowserPoll(boolean running) {
    if (browserState == BrowserState.LAUNCHING) {
      return;
    }
    if (running && browserState != BrowserState.OPEN) {
      browserState = BrowserState.OPEN;
      queueLog("BROWSER", "Browser detected on port %d.".formatted(pollPort));
    } else if (!running && browserState == BrowserState.OPEN) {
      browserState = BrowserState.CLOSED;
      queueLog("BROWSER", "Browser closed.", LogLevel.WARN);
      if (runState == RunState.RUNNING) {
        runState = RunState.COMPLETE;
        queueLog(
            "RUN",
            "Browser closed mid-run; cancelling remaining entries. Re-open Edge, navigate back to the list and start again.",
            LogLevel.ERROR
        );
      }
    } else {
      return;
    }
    updateUi();
  }

  private void onLaunchBrowser() {
    browserState = BrowserState.LAUNCHING;
    updateUi();
    var port = browserPanel.getPort();
    var browserPath = browserPanel.getBrowserPath();
    queueLog("BROWSER", "Opening Edge on port %d".formatted(port));

    var thread = new Thread(() -> launchBrowserThread(port, browserPath));
    thread.setDaemon(true);
    thread.start();
  }

  private void onLaunchFinished(boolean success, String reason) {
    if (success) {
      browserState = BrowserState.OPEN;
      queueLog("BROWSER", "Edge is ready.");
    } else {
      browserState = BrowserState.FAILED;
      queueLog("BROWSER", "Edge failed to launch: %s".formatted(reason), LogLevel.ERROR);
    }
    updateUi();
  }

  private void onPortChange(int port) {
    this.pollPort = port;
  }

  private void onRun() {
    var selected = taskPanel.selectedTasks();
    if (selected.isEmpty() || browserState != BrowserState.OPEN) {
      return;
    }
    if (runState == RunState.RUNNING) {
      return;
    }
    runState = RunState.RUNNING;
    updateUi();
    var port = browserPanel.getPort();
    queueLog("RUN", "Starting %d task(s)".formatted(selected.size()));

    var thread = new Thread(() -> runTasks(selected, port));
    thread.setDaemon(true);
    thread.start();
  }

  private void onRunComplete() {
    if (runState == RunState.RUNNING) {
      runState = RunState.COMPLETE;
    }
    updateUi();
  }

  private void onStop() {
    runState = RunState.COMPLETE;
    queueLog("RUN", "Stopped by user.", LogLevel.WARN);
    updateUi();
  }

  private void onToggleDebug(boolean visible) {
    logPanel.setDebugVisible(visible);
  }

  private void pollBrowser() {
    while (true) {
      var running = BrowserUtils.isBrowserRunning(pollPort);
      SwingUtilities.invokeLater(() -> onBrowserPoll(running));
      try {
        Thread.sleep((long) (POLL_INTERVAL_SECS * 1000));
      } catch (InterruptedException ie) {
        Thread.currentThread().interrupt();
        return;
      }
    }
  }

  private void processLogQueue() {
    LogEntry log;
    while ((log = logQueue.poll()) != null) {
      logPanel.append(log);
    }
  }

  private void queueLog(String step, String message) {
    queueLog(step, message, LogLevel.INFO);
  }

  private void queueLog(String step, String message, LogLevel level) {
    var log = new LogEntry(level, "[%s] %s".formatted(step, message));
    LogStore.addLog(log);
    logQueue.add(log);
  }

  private void runTasks(List<Task> selected, int port) {
    var resultsRef = new AtomicReference<List<TaskResult>>(List.of());
    try {
      BrowserUtils.withBrowser(port, listPage -> {
        queueLog("RUN", "Attached to %s".formatted(listPage.url()), LogLevel.DEBUG);
        BrowserUtils.recordSession(listPage, () -> {
          var results =
              TaskRunner.executeTasks(listPage, selected, msg -> queueLog("RUN", msg), () -> runState != RunState.RUNNING);
          resultsRef.set(results);
        });
      });

      var results = resultsRef.get();
      var failed = results
        .stream()
        .filter(result -> !result.success())
        .count();
      queueLog(
          "RUN",
          "Finished: %d succeeded, %d failed.".formatted(results.size() - failed, failed),
          failed > 0 ? LogLevel.WARN : LogLevel.INFO
      );
    } catch (RuntimeException exc) {
      queueLog("RUN", "Unexpected error: %s".formatted(exc.getMessage()), LogLevel.ERROR);
    } finally {
      SwingUtilities.invokeLater(this::onRunComplete);
    }
  }

  private void setupWindow() {
    frame.setTitle("%s v%s".formatted(PROJECT, VERSION));
    frame.setSize(1000, 500);
    frame.setMinimumSize(new Dimension(1000, 500));
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
  }

  private void updateUi() {
    var browserOpen = browserState == BrowserState.OPEN;
    var isRunning = runState == RunState.RUNNING;

    browserPanel.setState(browserState);
    taskPanel.setTasksEnabled(browserOpen && !isRunning);
    runPanel.setState(runState, browserOpen && taskPanel.hasSelection() && !isRunning);
  }
}
