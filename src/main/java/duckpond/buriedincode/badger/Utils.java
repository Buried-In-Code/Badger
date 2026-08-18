package duckpond.buriedincode.badger;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.jspecify.annotations.NullMarked;

@NullMarked
public final class Utils {
  public static final String PROJECT = "badger";
  public static final String VERSION = "2026.2.0";

  private Utils() {
  }

  public static Path getCacheHome() {
    return home("cache");
  }

  public static Path getConfigHome() {
    return home("config");
  }

  public static Path getDataHome() {
    return home("data");
  }

  public static Path getStateHome() {
    return home("state");
  }

  private static Path home(String leaf) {
    var folder = Path.of(System.getProperty("user.home"), "." + PROJECT, leaf);
    try {
      Files.createDirectories(folder);
    } catch (IOException ioe) {
      throw new UncheckedIOException(ioe);
    }
    return folder;
  }
}
