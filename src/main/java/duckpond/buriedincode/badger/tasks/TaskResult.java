package duckpond.buriedincode.badger.tasks;

import org.jspecify.annotations.NullMarked;

@NullMarked
public record TaskResult(int entryIndex, String taskId, String taskName, boolean success, String message) {}
