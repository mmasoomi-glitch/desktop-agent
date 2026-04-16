"""Screen capture module using mss for fast, cross-platform screenshots."""

import base64
import io

import mss
from PIL import Image

from config import SCREENSHOT_MAX_WIDTH


def take_screenshot(monitor_index: int = 0) -> str:
    """Capture the screen and return a base64-encoded JPEG string.

    Args:
        monitor_index: Which monitor to capture. 0 = all monitors combined,
                       1 = first monitor, 2 = second, etc.

    Returns:
        Base64-encoded JPEG image string.
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_index >= len(monitors):
            monitor_index = 0
        monitor = monitors[monitor_index]
        raw = sct.grab(monitor)

    img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    # Downscale if wider than max to save API tokens
    if img.width > SCREENSHOT_MAX_WIDTH:
        ratio = SCREENSHOT_MAX_WIDTH / img.width
        new_size = (SCREENSHOT_MAX_WIDTH, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def list_monitors() -> list[dict]:
    """Return available monitor geometries."""
    with mss.mss() as sct:
        return [
            {"index": i, "width": m["width"], "height": m["height"]}
            for i, m in enumerate(sct.monitors)
        ]
