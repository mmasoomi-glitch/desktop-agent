#!/usr/bin/env python3
"""Desktop Agent — an AI assistant that watches your screen and gives advice.

Usage:
    export OPENAI_API_KEY="sk-..."
    python main.py [--interval 30] [--monitor 0] [--once]

Environment variables:
    OPENAI_API_KEY                 Required. Your OpenAI API key.
    DESKTOP_AGENT_MODEL            Model to use (default: gpt-4o).
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
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (no API calls, simulated advice).",
    )
    return parser.parse_args()


def run_cycle(monitor_index: int, demo: bool = False) -> None:
    """Capture screen, analyze, and notify if there's advice."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Capturing screen...")

    try:
        image_b64 = take_screenshot(monitor_index)
    except Exception as e:
        print(f"[{timestamp}] Screen capture failed: {e}")
        return

    size_kb = len(image_b64) * 3 // 4 // 1024
    print(f"[{timestamp}] Screenshot captured ({size_kb} KB)")

    if demo:
        advice = "Demo mode: Your screen was captured successfully! In live mode, GPT-4o would analyze this and give real advice."
    else:
        print(f"[{timestamp}] Analyzing with GPT-4o...")
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

    if not args.demo and not config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  Or run with --demo to test without an API key.")
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
        run_cycle(args.monitor, demo=args.demo)
        return

    while running:
        run_cycle(args.monitor, demo=args.demo)
        # Sleep in small increments so Ctrl+C is responsive
        for _ in range(args.interval * 10):
            if not running:
                break
            time.sleep(0.1)

    print("Desktop Agent stopped.")


if __name__ == "__main__":
    main()
