package duckpond.buriedincode.browser;

import org.jspecify.annotations.NullMarked;

@NullMarked
public record LaunchResult(boolean running, String message) {}
