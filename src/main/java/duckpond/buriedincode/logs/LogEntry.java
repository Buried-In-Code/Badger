package duckpond.buriedincode.logs;

import java.time.LocalDateTime;
import org.jspecify.annotations.NullMarked;

@NullMarked
public record LogEntry(LocalDateTime timestamp, LogLevel level, String message) {
  public LogEntry(LogLevel level, String message) {
    this(LocalDateTime.now(), level, message);
  }

  public LogEntry(String message) {
    this(LogLevel.INFO, message);
  }
}
