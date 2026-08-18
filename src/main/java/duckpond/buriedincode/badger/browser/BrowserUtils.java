package duckpond.buriedincode.badger.browser;

import static duckpond.buriedincode.badger.Utils.PROJECT;
import static duckpond.buriedincode.badger.Utils.getCacheHome;
import static duckpond.buriedincode.badger.Utils.getStateHome;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.Tracing;
import duckpond.buriedincode.badger.logs.LogLevel;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.function.BiConsumer;
import java.util.function.Consumer;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class BrowserUtils {
  private BrowserUtils() {
  }

  public static String defaultBrowserPath() {
    var os = System.getProperty("os.name", "").toLowerCase();
    if (os.contains("win")) {
      return "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
    }
    if (os.contains("nux") || os.contains("nix")) {
      return "microsoft-edge-stable";
    }
    if (os.contains("mac")) {
      return "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge";
    }
    return "";
  }

  public static boolean isBrowserRunning(int port) {
    try {
      var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(1)).build();
      var request = HttpRequest
        .newBuilder()
        .uri(URI.create("http://localhost:%d/json/version".formatted(port)))
        .timeout(Duration.ofSeconds(1))
        .GET()
        .build();
      var response = client.send(request, HttpResponse.BodyHandlers.discarding());
      return response.statusCode() >= 200 && response.statusCode() < 300;
    } catch (IOException | InterruptedException e) {
      if (e instanceof InterruptedException) {
        Thread.currentThread().interrupt();
      }
      return false;
    }
  }

  public static LaunchResult launchEdge(BiConsumer<String, LogLevel> logMessage, int port, String browserPath) {
    var dataPath = getCacheHome().resolve("remote-debug-profile");
    var edgePath = browserPath == null ? "" : browserPath.strip();
    if (edgePath.isEmpty()) {
      edgePath = defaultBrowserPath();
    }
    if (edgePath.isEmpty()) {
      return new LaunchResult(false, "Unsupported platform: %s".formatted(System.getProperty("os.name", "unknown")));
    }

    var cmd = List.of(edgePath, "--remote-debugging-port=%d".formatted(port), "--user-data-dir=%s".formatted(dataPath));

    try {
      logMessage.accept("Starting Edge with CDP...", LogLevel.DEBUG);
      new ProcessBuilder(cmd).start();
      return new LaunchResult(true, "Edge launched successfully");
    } catch (IOException err) {
      return new LaunchResult(false, err.getMessage());
    }
  }

  public static void recordSession(Page page, Runnable action) {
    var context = page.context();
    context.tracing().start(new Tracing.StartOptions().setScreenshots(true).setSnapshots(true).setSources(true));
    try {
      action.run();
    } finally {
      var stamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss"));
      try {
        context
          .tracing()
          .stop(new Tracing.StopOptions().setPath(getStateHome().resolve("%s_%s.zip".formatted(PROJECT, stamp))));
      } catch (RuntimeException ignored) {
      }
    }
  }

  public static boolean waitForBrowser(int port, double timeoutSeconds) {
    var deadlineNanos = System.nanoTime() + (long) (timeoutSeconds * 1_000_000_000L);
    while (System.nanoTime() < deadlineNanos) {
      if (isBrowserRunning(port)) {
        return true;
      }
      try {
        Thread.sleep(500);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        return false;
      }
    }
    return false;
  }

  public static void withBrowser(int port, Consumer<Page> action) {
    try (var playwright = Playwright.create()) {
      var browser = playwright.chromium().connectOverCDP("http://localhost:%d".formatted(port));
      var page = browser
        .contexts()
        .stream()
        .flatMap(context -> context.pages().stream())
        .findFirst()
        .orElseThrow(() -> new RuntimeException("No open pages found; navigate to the list first."));
      action.accept(page);
    }
  }
}
