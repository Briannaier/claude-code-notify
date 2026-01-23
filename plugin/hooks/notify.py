#!/usr/bin/env python3
"""
Claude Code Notify - Desktop notifications for Claude Code.

This script sends desktop notifications when Claude Code tasks complete,
when permission prompts appear, or when Claude is waiting for input.

Supported platforms:
- macOS: Uses osascript (native)
- Windows: Uses PowerShell with Windows Forms
- Linux: Uses notify-send (requires libnotify)
"""

import base64
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def debug_log(msg: str) -> None:
    """Write debug log to temp file."""
    log_path = Path("/tmp/claude_code_notify_debug.log")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except Exception:
        pass


def send_notification(title: str, message: str) -> bool:
    """Send a desktop notification based on the operating system."""
    system_type = platform.system()

    # --- macOS (osascript) ---
    if system_type == "Darwin":
        try:
            safe_msg = message.replace('"', '\\"')
            safe_title = title.replace('"', '\\"')
            subprocess.run(
                [
                    "osascript", "-e",
                    f'display notification "{safe_msg}" with title "{safe_title}" sound name "Glass"'
                ],
                check=True,
                capture_output=True,
            )
            return True
        except Exception:
            return False

    # --- Windows (PowerShell with Windows Forms) ---
    elif system_type == "Windows":
        try:
            ps_title = json.dumps(title, ensure_ascii=False)
            ps_message = json.dumps(message, ensure_ascii=False)

            ps_script = f"""
            $ErrorActionPreference = 'Stop'
            [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
            $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
            $objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information
            $objNotifyIcon.Visible = $True
            $objNotifyIcon.BalloonTipTitle = {ps_title}
            $objNotifyIcon.BalloonTipText = {ps_message}
            $objNotifyIcon.ShowBalloonTip(5000)
            """

            encoded_command = base64.b64encode(
                ps_script.encode('utf-16le')
            ).decode('utf-8')

            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_command],
                check=True,
                capture_output=True,
            )
            return True
        except Exception:
            return False

    # --- Linux (notify-send) ---
    elif system_type == "Linux":
        try:
            subprocess.run(
                ["notify-send", title, message, "-a", "Claude Code"],
                check=True,
                capture_output=True,
            )
            return True
        except FileNotFoundError:
            debug_log("notify-send not found. Install libnotify: sudo apt install libnotify-bin")
            return False
        except Exception:
            return False

    return False


def get_latest_claude_message(transcript_path: str) -> str:
    """Read Claude's transcript file and get the last assistant message."""
    try:
        path = os.path.expanduser(transcript_path)
        if not os.path.exists(path):
            return "Transcript file not found."

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('message', {}).get('role') == 'assistant':
                    content = entry['message']['content']
                    text_parts = [
                        c.get('text', '')
                        for c in content
                        if c.get('type') == 'text'
                    ]
                    return " ".join(text_parts).strip()
            except json.JSONDecodeError:
                continue

        return "Task Completed"
    except Exception as e:
        return f"Error reading log: {str(e)}"


def main() -> int:
    """Main entry point for the notification hook."""
    debug_log("=== Hook triggered ===")
    debug_log(f"sys.argv: {sys.argv}")
    debug_log(f"stdin.isatty(): {sys.stdin.isatty()}")

    title = "Claude Code"
    message = "Task Finished"

    try:
        if not sys.stdin.isatty():
            try:
                input_data = sys.stdin.read()
                debug_log(f"stdin data: {input_data[:500] if input_data else 'empty'}")

                if input_data.strip():
                    payload = json.loads(input_data)
                    debug_log(f"parsed payload keys: {list(payload.keys())}")

                    # Handle Notification events
                    if payload.get("hook_event_name") == "Notification":
                        notification_type = payload.get("notification_type", "")
                        debug_log(f"Notification type: {notification_type}")

                        if notification_type == "permission_prompt":
                            message = "Needs your permission"
                        elif notification_type == "idle_prompt":
                            message = "Waiting for your input"
                        else:
                            message = "Needs your attention"

                        send_notification(title, message)
                        return 0

                    # Handle Stop events
                    if "transcript_path" in payload:
                        transcript_msg = get_latest_claude_message(payload["transcript_path"])
                        if len(transcript_msg) > 150:
                            message = transcript_msg[:150] + "..."
                        else:
                            message = transcript_msg
                        send_notification(title, message)
                        return 0

            except Exception as e:
                debug_log(f"Exception: {str(e)}")
                pass

        # Manual test mode
        if len(sys.argv) > 1:
            title = sys.argv[1]
            if len(sys.argv) > 2:
                message = sys.argv[2]
            send_notification(title, message)

    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
