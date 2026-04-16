"""Cross-platform desktop notification module.

Uses native notification commands where available, with a terminal fallback.
"""

import platform
import subprocess
import shutil
import textwrap

APP_NAME = "Desktop Agent"


def notify(title: str, message: str) -> None:
    """Show a desktop notification. Falls back to terminal output."""
    system = platform.system()

    try:
        if system == "Linux":
            _notify_linux(title, message)
        elif system == "Darwin":
            _notify_macos(title, message)
        elif system == "Windows":
            _notify_windows(title, message)
        else:
            _notify_terminal(title, message)
    except Exception:
        _notify_terminal(title, message)


def _notify_linux(title: str, message: str) -> None:
    if shutil.which("notify-send"):
        subprocess.run(
            ["notify-send", "-a", APP_NAME, title, message],
            timeout=5,
            check=False,
        )
    else:
        _notify_terminal(title, message)


def _notify_macos(title: str, message: str) -> None:
    escaped_msg = message.replace('"', '\\"')
    escaped_title = title.replace('"', '\\"')
    script = (
        f'display notification "{escaped_msg}" '
        f'with title "{escaped_title}"'
    )
    subprocess.run(
        ["osascript", "-e", script],
        timeout=5,
        check=False,
    )


def _notify_windows(title: str, message: str) -> None:
    # PowerShell toast notification
    ps_script = (
        "[Windows.UI.Notifications.ToastNotificationManager, "
        "Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
        "$template = [Windows.UI.Notifications.ToastNotificationManager]::"
        "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::"
        "ToastText02); "
        "$textNodes = $template.GetElementsByTagName('text'); "
        f"$textNodes.Item(0).AppendChild($template.CreateTextNode('{title}')); "
        f"$textNodes.Item(1).AppendChild($template.CreateTextNode('{message}')); "
        "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
        "[Windows.UI.Notifications.ToastNotificationManager]::"
        f"CreateToastNotifier('{APP_NAME}').Show($toast)"
    )
    subprocess.run(
        ["powershell", "-Command", ps_script],
        timeout=10,
        check=False,
    )


def _notify_terminal(title: str, message: str) -> None:
    width = 60
    border = "=" * width
    wrapped = textwrap.fill(message, width=width - 4)
    indented = "\n".join(f"  {line}" for line in wrapped.splitlines())
    print(f"\n{border}")
    print(f"  {APP_NAME} | {title}")
    print(f"{'-' * width}")
    print(indented)
    print(f"{border}\n")
