#!/usr/bin/env python3
"""Desktop Agent — an AI assistant that watches your screen and gives advice.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python main.py [--interval 30] [--monitor 0] [--once]

Environment variables:
    ANTHROPIC_API_KEY              Required. Your Anthropic API key.
    DESKTOP_AGENT_MODEL            Model to use (default: claude-sonnet-4-20250514).
    DESKTOP_AGENT_INTERVAL         Capture interval in seconds (default: 30).
    DESKTOP_AGENT_PROMPT           Custom system prompt for the advisor.
"""

import argparse
import signal
import sys
import time
from datetime import datetime

from capture import take_screenshot, list_monitors
from analyzer import analyze_screenshot
from notifier import notify
import config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI desktop agent that watches your screen and advises you."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=config.CAPTURE_INTERVAL_SECONDS,
        help=f"Seconds between captures (default: {config.CAPTURE_INTERVAL_SECONDS})",
    )
    parser.add_argument(
        "--monitor",
        type=int,
        default=0,
        help="Monitor index to capture (0 = all, 1 = first, etc.)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single capture-analyze cycle and exit.",
    )
    parser.add_argument(
        "--list-monitors",
        action="store_true",
        help="List available monitors and exit.",
    )
    return parser.parse_args()


def run_cycle(monitor_index: int) -> None:
    """Capture screen, analyze, and notify if there's advice."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Capturing screen...")

    try:
        image_b64 = take_screenshot(monitor_index)
    except Exception as e:
        print(f"[{timestamp}] Screen capture failed: {e}")
        return

    print(f"[{timestamp}] Analyzing with Claude...")

    try:
        advice = analyze_screenshot(image_b64)
    except Exception as e:
        print(f"[{timestamp}] Analysis failed: {e}")
        return

    if advice:
        print(f"[{timestamp}] Advice: {advice}")
        notify("Desktop Advice", advice)
    else:
        print(f"[{timestamp}] Nothing noteworthy detected.")


def main() -> None:
    args = parse_args()

    if args.list_monitors:
        monitors = list_monitors()
        print("Available monitors:")
        for m in monitors:
            label = "all combined" if m["index"] == 0 else f"monitor {m['index']}"
            print(f"  [{m['index']}] {label}: {m['width']}x{m['height']}")
        return

    if not config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    print("=" * 50)
    print("  Desktop Agent — AI Screen Advisor")
    print("=" * 50)
    print(f"  Model:    {config.MODEL}")
    print(f"  Interval: {args.interval}s")
    print(f"  Monitor:  {args.monitor}")
    print("  Press Ctrl+C to stop.")
    print("=" * 50)
    print()

    # Graceful shutdown
    running = True

    def handle_signal(sig, frame):
        nonlocal running
        print("\nShutting down...")
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if args.once:
        run_cycle(args.monitor)
        return

    while running:
        run_cycle(args.monitor)
        # Sleep in small increments so Ctrl+C is responsive
        for _ in range(args.interval * 10):
            if not running:
                break
            time.sleep(0.1)

    print("Desktop Agent stopped.")


if __name__ == "__main__":
    main()
