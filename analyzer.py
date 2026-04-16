"""OpenAI GPT-4o vision analyzer — sends screenshots to the API and returns advice."""

from openai import OpenAI

from config import OPENAI_API_KEY, MODEL, SYSTEM_PROMPT

_NOTHING_TAG = "NOTHING_TO_REPORT"


def _build_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set. "
            "Export it before running the agent."
        )
    return OpenAI(api_key=OPENAI_API_KEY)


def analyze_screenshot(image_b64: str, context: str = "") -> str | None:
    """Send a base64 screenshot to GPT-4o and get advice back.

    Args:
        image_b64: Base64-encoded JPEG screenshot.
        context: Optional extra context to include.

    Returns:
        Advice string, or None if nothing noteworthy was found.
    """
    client = _build_client()

    user_content = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_b64}",
                "detail": "low",
            },
        },
        {
            "type": "text",
            "text": context if context else "What do you see on my screen? Any advice?",
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    text = response.choices[0].message.content.strip()
    if _NOTHING_TAG in text:
        return None
    return text
