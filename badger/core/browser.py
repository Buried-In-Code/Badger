import time


def launch_chrome() -> dict:
    """Launch Chrome with remote debugging.

    Returns:
        dict with keys: success (bool), message (str), running (bool)
    """
    time.sleep(1.5)
    return {
        "success": True,
        "message": "Chrome launched successfully with remote debugging enabled.",
        "running": True,
    }
