import os

# Claude API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("DESKTOP_AGENT_MODEL", "claude-sonnet-4-20250514")

# Screen capture
CAPTURE_INTERVAL_SECONDS = int(os.environ.get("DESKTOP_AGENT_INTERVAL", "30"))
SCREENSHOT_MAX_WIDTH = 1280  # downscale to save tokens

# Agent behavior
SYSTEM_PROMPT = os.environ.get("DESKTOP_AGENT_PROMPT", (
    "You are a helpful desktop assistant watching the user's screen. "
    "Analyze the screenshot and provide brief, actionable advice. "
    "Focus on: productivity tips, potential errors or issues visible on screen, "
    "workflow improvements, or anything noteworthy. "
    "Keep your response to 1-3 short sentences. "
    "If nothing noteworthy is happening, respond with exactly: NOTHING_TO_REPORT"
))

# Display
NOTIFICATION_DURATION_SECONDS = 10
