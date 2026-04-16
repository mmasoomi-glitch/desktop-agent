"""Claude vision analyzer — sends screenshots to the API and returns advice."""

import anthropic

from config import ANTHROPIC_API_KEY, MODEL, SYSTEM_PROMPT

_NOTHING_TAG = "NOTHING_TO_REPORT"


def _build_client() -> anthropic.Anthropic:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Export it before running the agent."
        )
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def analyze_screenshot(image_b64: str, context: str = "") -> str | None:
    """Send a base64 screenshot to Claude and get advice back.

    Args:
        image_b64: Base64-encoded JPEG screenshot.
        context: Optional extra context to include (e.g. recent advice history).

    Returns:
        Advice string, or None if nothing noteworthy was found.
    """
    client = _build_client()

    user_content: list[dict] = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_b64,
            },
        },
    ]

    if context:
        user_content.append({"type": "text", "text": context})
    else:
        user_content.append({
            "type": "text",
            "text": "What do you see on my screen? Any advice?",
        })

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    text = response.content[0].text.strip()
    if _NOTHING_TAG in text:
        return None
    return text
