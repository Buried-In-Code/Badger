package duckpond.buriedincode.badger.browser;

import org.jspecify.annotations.NullMarked;

@NullMarked
public record LaunchResult(boolean running, String message) {}
