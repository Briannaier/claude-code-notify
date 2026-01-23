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
import locale
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# Internationalization (i18n) Support
# ============================================================================

# Message keys
MSG_PERMISSION_PROMPT = "permission_prompt"
MSG_IDLE_PROMPT = "idle_prompt"
MSG_AUTH_SUCCESS = "auth_success"
MSG_AUTH_REQUIRED = "auth_required"
MSG_ELICITATION = "elicitation"
MSG_QUESTION = "question"
MSG_ATTENTION = "attention"
MSG_TASK_COMPLETED = "task_completed"

# Translations dictionary
TRANSLATIONS = {
    "en": {
        MSG_PERMISSION_PROMPT: "🔐 Needs your permission",
        MSG_IDLE_PROMPT: "⏳ Waiting for your input",
        MSG_AUTH_SUCCESS: "✅ Authentication successful",
        MSG_AUTH_REQUIRED: "🔑 Authentication required",
        MSG_ELICITATION: "💬 MCP tool needs your input",
        MSG_QUESTION: "❓ Claude has a question for you",
        MSG_ATTENTION: "🔔 Needs your attention",
        MSG_TASK_COMPLETED: "Task Completed",
    },
    "zh": {
        MSG_PERMISSION_PROMPT: "🔐 需要您的授权",
        MSG_IDLE_PROMPT: "⏳ 等待您的输入",
        MSG_AUTH_SUCCESS: "✅ 认证成功",
        MSG_AUTH_REQUIRED: "🔑 需要认证",
        MSG_ELICITATION: "💬 MCP 工具需要您的输入",
        MSG_QUESTION: "❓ Claude 有问题想问您",
        MSG_ATTENTION: "🔔 需要您的关注",
        MSG_TASK_COMPLETED: "任务已完成",
    },
    "ja": {
        MSG_PERMISSION_PROMPT: "🔐 許可が必要です",
        MSG_IDLE_PROMPT: "⏳ 入力をお待ちしています",
        MSG_AUTH_SUCCESS: "✅ 認証成功",
        MSG_AUTH_REQUIRED: "🔑 認証が必要です",
        MSG_ELICITATION: "💬 MCPツールの入力が必要です",
        MSG_QUESTION: "❓ Claudeから質問があります",
        MSG_ATTENTION: "🔔 注意が必要です",
        MSG_TASK_COMPLETED: "タスク完了",
    },
    "ko": {
        MSG_PERMISSION_PROMPT: "🔐 권한이 필요합니다",
        MSG_IDLE_PROMPT: "⏳ 입력을 기다리고 있습니다",
        MSG_AUTH_SUCCESS: "✅ 인증 성공",
        MSG_AUTH_REQUIRED: "🔑 인증이 필요합니다",
        MSG_ELICITATION: "💬 MCP 도구 입력이 필요합니다",
        MSG_QUESTION: "❓ Claude가 질문이 있습니다",
        MSG_ATTENTION: "🔔 주의가 필요합니다",
        MSG_TASK_COMPLETED: "작업 완료",
    },
    "de": {
        MSG_PERMISSION_PROMPT: "🔐 Berechtigung erforderlich",
        MSG_IDLE_PROMPT: "⏳ Warte auf Ihre Eingabe",
        MSG_AUTH_SUCCESS: "✅ Authentifizierung erfolgreich",
        MSG_AUTH_REQUIRED: "🔑 Authentifizierung erforderlich",
        MSG_ELICITATION: "💬 MCP-Tool benötigt Eingabe",
        MSG_QUESTION: "❓ Claude hat eine Frage",
        MSG_ATTENTION: "🔔 Aufmerksamkeit erforderlich",
        MSG_TASK_COMPLETED: "Aufgabe abgeschlossen",
    },
    "fr": {
        MSG_PERMISSION_PROMPT: "🔐 Permission requise",
        MSG_IDLE_PROMPT: "⏳ En attente de votre saisie",
        MSG_AUTH_SUCCESS: "✅ Authentification réussie",
        MSG_AUTH_REQUIRED: "🔑 Authentification requise",
        MSG_ELICITATION: "💬 L'outil MCP nécessite une entrée",
        MSG_QUESTION: "❓ Claude a une question",
        MSG_ATTENTION: "🔔 Attention requise",
        MSG_TASK_COMPLETED: "Tâche terminée",
    },
    "es": {
        MSG_PERMISSION_PROMPT: "🔐 Se necesita permiso",
        MSG_IDLE_PROMPT: "⏳ Esperando su entrada",
        MSG_AUTH_SUCCESS: "✅ Autenticación exitosa",
        MSG_AUTH_REQUIRED: "🔑 Autenticación requerida",
        MSG_ELICITATION: "💬 La herramienta MCP necesita entrada",
        MSG_QUESTION: "❓ Claude tiene una pregunta",
        MSG_ATTENTION: "🔔 Se requiere atención",
        MSG_TASK_COMPLETED: "Tarea completada",
    },
}


def get_system_language() -> str:
    """Detect system language and return language code (e.g., 'en', 'zh', 'ja')."""
    try:
        system_type = platform.system()

        # macOS: Use AppleScript to get system language
        if system_type == "Darwin":
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleLanguages"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    # Parse output like: (\n    "zh-Hans-CN",\n    "en-CN"\n)
                    output = result.stdout
                    if '"zh' in output.lower():
                        return "zh"
                    elif '"ja' in output.lower():
                        return "ja"
                    elif '"ko' in output.lower():
                        return "ko"
                    elif '"de' in output.lower():
                        return "de"
                    elif '"fr' in output.lower():
                        return "fr"
                    elif '"es' in output.lower():
                        return "es"
            except Exception:
                pass

        # Fallback: Use locale
        lang = locale.getdefaultlocale()[0] or os.environ.get("LANG", "en")
        lang_code = lang.split("_")[0].lower()

        if lang_code in TRANSLATIONS:
            return lang_code

        return "en"
    except Exception:
        return "en"


def get_message(key: str, lang: str = None) -> str:
    """Get localized message by key."""
    if lang is None:
        lang = get_system_language()

    messages = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return messages.get(key, TRANSLATIONS["en"].get(key, ""))


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

    # Detect system language once
    lang = get_system_language()
    debug_log(f"Detected language: {lang}")

    title = "Claude Code"
    message = get_message(MSG_TASK_COMPLETED, lang)

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
                        event_message = payload.get("message", "")
                        debug_log(f"Notification type: {notification_type}")
                        debug_log(f"Event message: {event_message}")

                        # 1. 根据 notification_type 处理（优先）
                        if notification_type == "permission_prompt":
                            message = get_message(MSG_PERMISSION_PROMPT, lang)
                        elif notification_type == "idle_prompt":
                            message = get_message(MSG_IDLE_PROMPT, lang)
                        elif notification_type == "auth_success":
                            message = get_message(MSG_AUTH_SUCCESS, lang)
                        elif notification_type == "elicitation_dialog":
                            message = get_message(MSG_ELICITATION, lang)
                        # 2. 兜底：根据 message 内容推断类型（解决 notification_type 缺失的 bug）
                        elif event_message:
                            msg_lower = event_message.lower()
                            if "permission" in msg_lower or "allow" in msg_lower:
                                message = get_message(MSG_PERMISSION_PROMPT, lang)
                            elif "waiting" in msg_lower or "input" in msg_lower or "idle" in msg_lower:
                                message = get_message(MSG_IDLE_PROMPT, lang)
                            elif "auth" in msg_lower or "login" in msg_lower or "sign" in msg_lower:
                                message = get_message(MSG_AUTH_REQUIRED, lang)
                            elif "mcp" in msg_lower or "tool" in msg_lower or "elicit" in msg_lower:
                                message = get_message(MSG_ELICITATION, lang)
                            elif "question" in msg_lower or "choose" in msg_lower or "select" in msg_lower:
                                message = get_message(MSG_QUESTION, lang)
                            else:
                                # 使用原始消息（截断）
                                message = event_message[:100] + "..." if len(event_message) > 100 else event_message
                        else:
                            message = get_message(MSG_ATTENTION, lang)

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
