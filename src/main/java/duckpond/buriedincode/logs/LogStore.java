package duckpond.buriedincode.logs;

import static duckpond.buriedincode.Utils.getStateHome;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import org.jspecify.annotations.NullMarked;

@NullMarked
public class LogStore {
  private static final Gson GSON = new Gson();
  private static final Path LOG_FILE = getStateHome().resolve("logs.jsonl");

  private LogStore() {
  }

  public static void addLog(LogEntry log) {
    var entry = new LinkedHashMap<String, String>();
    entry.put("timestamp", log.timestamp().toString());
    entry.put("level", log.level().name());
    entry.put("message", log.message());

    try (var writer = Files.newBufferedWriter(LOG_FILE, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
      writer.write(GSON.toJson(entry));
      writer.newLine();
    } catch (IOException ioe) {
      throw new UncheckedIOException(ioe);
    }
  }

  public static List<LogEntry> readLogs() {
    var logs = new ArrayList<LogEntry>();
    if (!Files.exists(LOG_FILE)) {
      return logs;
    }
    try (var reader = Files.newBufferedReader(LOG_FILE)) {
      String line;
      while ((line = reader.readLine()) != null) {
        line = line.strip();
        if (line.isEmpty()) {
          continue;
        }
        var obj = GSON.fromJson(line, JsonObject.class);
        logs.add(
            new LogEntry(
                LocalDateTime.parse(obj.get("timestamp").getAsString()),
                LogLevel.valueOf(obj.get("level").getAsString()),
                obj.get("message").getAsString()
            )
        );
      }
    } catch (IOException ioe) {
      throw new UncheckedIOException(ioe);
    }
    return logs;
  }
}
