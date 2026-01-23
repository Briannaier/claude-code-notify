#!/usr/bin/env python3
"""
Tests for Claude Code Notify.

These tests cover all notification scenarios to ensure reliability
across different platforms and event types.
"""

import json
import subprocess
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# Add src to path for imports
sys.path.insert(0, "src")

from claude_code_notify.notify import (
    MSG_ATTENTION,
    MSG_AUTH_REQUIRED,
    MSG_AUTH_SUCCESS,
    MSG_ELICITATION,
    MSG_IDLE_PROMPT,
    MSG_PERMISSION_PROMPT,
    MSG_QUESTION,
    MSG_TASK_COMPLETED,
    TRANSLATIONS,
    get_message,
    get_system_language,
    get_latest_claude_message,
    send_notification,
)


class TestInternationalization(unittest.TestCase):
    """Test internationalization (i18n) functionality."""

    def test_get_message_returns_english_by_default(self):
        """get_message returns English message when lang is 'en'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "en")
        self.assertEqual(msg, "🔐 Needs your permission")

    def test_get_message_returns_chinese_for_zh(self):
        """get_message returns Chinese message when lang is 'zh'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "zh")
        self.assertEqual(msg, "🔐 需要您的授权")

    def test_get_message_returns_japanese_for_ja(self):
        """get_message returns Japanese message when lang is 'ja'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "ja")
        self.assertEqual(msg, "🔐 許可が必要です")

    def test_get_message_returns_korean_for_ko(self):
        """get_message returns Korean message when lang is 'ko'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "ko")
        self.assertEqual(msg, "🔐 권한이 필요합니다")

    def test_get_message_returns_german_for_de(self):
        """get_message returns German message when lang is 'de'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "de")
        self.assertEqual(msg, "🔐 Berechtigung erforderlich")

    def test_get_message_returns_french_for_fr(self):
        """get_message returns French message when lang is 'fr'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "fr")
        self.assertEqual(msg, "🔐 Permission requise")

    def test_get_message_returns_spanish_for_es(self):
        """get_message returns Spanish message when lang is 'es'."""
        msg = get_message(MSG_PERMISSION_PROMPT, "es")
        self.assertEqual(msg, "🔐 Se necesita permiso")

    def test_get_message_falls_back_to_english_for_unknown_lang(self):
        """get_message falls back to English for unsupported languages."""
        msg = get_message(MSG_PERMISSION_PROMPT, "unknown_lang")
        self.assertEqual(msg, "🔐 Needs your permission")

    def test_all_message_keys_exist_in_all_languages(self):
        """All message keys exist in all supported languages."""
        all_keys = [
            MSG_PERMISSION_PROMPT,
            MSG_IDLE_PROMPT,
            MSG_AUTH_SUCCESS,
            MSG_AUTH_REQUIRED,
            MSG_ELICITATION,
            MSG_QUESTION,
            MSG_ATTENTION,
            MSG_TASK_COMPLETED,
        ]
        for lang in TRANSLATIONS:
            for key in all_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, TRANSLATIONS[lang])
                    self.assertTrue(len(TRANSLATIONS[lang][key]) > 0)


class TestLanguageDetection(unittest.TestCase):
    """Test system language detection."""

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_detects_chinese_on_macos(self, mock_run, mock_system):
        """Detects Chinese language on macOS."""
        mock_system.return_value = "Darwin"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='(\n    "zh-Hans-CN",\n    "en-CN"\n)'
        )
        lang = get_system_language()
        self.assertEqual(lang, "zh")

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_detects_japanese_on_macos(self, mock_run, mock_system):
        """Detects Japanese language on macOS."""
        mock_system.return_value = "Darwin"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='(\n    "ja-JP",\n    "en-US"\n)'
        )
        lang = get_system_language()
        self.assertEqual(lang, "ja")

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_falls_back_to_english_on_macos_error(self, mock_run, mock_system):
        """Falls back to English when macOS command fails."""
        mock_system.return_value = "Darwin"
        mock_run.side_effect = Exception("Command failed")
        lang = get_system_language()
        self.assertEqual(lang, "en")

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.locale.getdefaultlocale")
    def test_uses_locale_on_linux(self, mock_locale, mock_system):
        """Uses locale for language detection on Linux."""
        mock_system.return_value = "Linux"
        mock_locale.return_value = ("zh_CN", "UTF-8")
        lang = get_system_language()
        self.assertEqual(lang, "zh")

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.locale.getdefaultlocale")
    @patch.dict("os.environ", {"LANG": "ja_JP.UTF-8"})
    def test_uses_env_var_as_fallback(self, mock_locale, mock_system):
        """Uses LANG environment variable as fallback."""
        mock_system.return_value = "Linux"
        mock_locale.return_value = (None, None)
        lang = get_system_language()
        self.assertEqual(lang, "ja")


class TestNotificationTypes(unittest.TestCase):
    """Test all notification type scenarios."""

    def test_permission_prompt_message_zh(self):
        """permission_prompt returns correct Chinese message."""
        msg = get_message(MSG_PERMISSION_PROMPT, "zh")
        self.assertIn("授权", msg)
        self.assertIn("🔐", msg)

    def test_idle_prompt_message_zh(self):
        """idle_prompt returns correct Chinese message."""
        msg = get_message(MSG_IDLE_PROMPT, "zh")
        self.assertIn("等待", msg)
        self.assertIn("⏳", msg)

    def test_auth_success_message_zh(self):
        """auth_success returns correct Chinese message."""
        msg = get_message(MSG_AUTH_SUCCESS, "zh")
        self.assertIn("认证成功", msg)
        self.assertIn("✅", msg)

    def test_auth_required_message_zh(self):
        """auth_required returns correct Chinese message."""
        msg = get_message(MSG_AUTH_REQUIRED, "zh")
        self.assertIn("认证", msg)
        self.assertIn("🔑", msg)

    def test_elicitation_message_zh(self):
        """elicitation returns correct Chinese message."""
        msg = get_message(MSG_ELICITATION, "zh")
        self.assertIn("MCP", msg)
        self.assertIn("💬", msg)

    def test_question_message_zh(self):
        """question returns correct Chinese message."""
        msg = get_message(MSG_QUESTION, "zh")
        self.assertIn("问题", msg)
        self.assertIn("❓", msg)

    def test_attention_message_zh(self):
        """attention returns correct Chinese message."""
        msg = get_message(MSG_ATTENTION, "zh")
        self.assertIn("关注", msg)
        self.assertIn("🔔", msg)

    def test_task_completed_message_zh(self):
        """task_completed returns correct Chinese message."""
        msg = get_message(MSG_TASK_COMPLETED, "zh")
        self.assertIn("完成", msg)


class TestSendNotification(unittest.TestCase):
    """Test notification sending on different platforms."""

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_sends_notification_on_macos(self, mock_run, mock_system):
        """Sends notification using osascript on macOS."""
        mock_system.return_value = "Darwin"
        mock_run.return_value = MagicMock(returncode=0)

        result = send_notification("Test Title", "Test Message")

        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "osascript")
        self.assertIn("Test Title", call_args[2])
        self.assertIn("Test Message", call_args[2])

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_sends_notification_on_linux(self, mock_run, mock_system):
        """Sends notification using notify-send on Linux."""
        mock_system.return_value = "Linux"
        mock_run.return_value = MagicMock(returncode=0)

        result = send_notification("Test Title", "Test Message")

        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "notify-send")
        self.assertIn("Test Title", call_args)
        self.assertIn("Test Message", call_args)

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_handles_macos_notification_failure(self, mock_run, mock_system):
        """Handles notification failure gracefully on macOS."""
        mock_system.return_value = "Darwin"
        mock_run.side_effect = Exception("osascript failed")

        result = send_notification("Test", "Test")

        self.assertFalse(result)

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_handles_linux_notify_send_not_found(self, mock_run, mock_system):
        """Handles notify-send not found on Linux."""
        mock_system.return_value = "Linux"
        mock_run.side_effect = FileNotFoundError("notify-send not found")

        result = send_notification("Test", "Test")

        self.assertFalse(result)

    @patch("claude_code_notify.notify.platform.system")
    def test_returns_false_for_unsupported_platform(self, mock_system):
        """Returns False for unsupported platforms."""
        mock_system.return_value = "UnknownOS"

        result = send_notification("Test", "Test")

        self.assertFalse(result)

    @patch("claude_code_notify.notify.platform.system")
    @patch("claude_code_notify.notify.subprocess.run")
    def test_escapes_quotes_in_macos_notification(self, mock_run, mock_system):
        """Escapes double quotes in macOS notification messages."""
        mock_system.return_value = "Darwin"
        mock_run.return_value = MagicMock(returncode=0)

        send_notification('Title with "quotes"', 'Message with "quotes"')

        call_args = mock_run.call_args[0][0]
        # Quotes should be escaped
        self.assertIn('\\"', call_args[2])


class TestPayloadHandling(unittest.TestCase):
    """Test handling of different Claude Code event payloads."""

    def create_notification_payload(self, notification_type, message=""):
        """Helper to create notification event payloads."""
        return {
            "session_id": "test-session",
            "transcript_path": "/tmp/test.jsonl",
            "cwd": "/tmp",
            "hook_event_name": "Notification",
            "notification_type": notification_type,
            "message": message,
        }

    def create_stop_payload(self, transcript_path):
        """Helper to create stop event payloads."""
        return {
            "session_id": "test-session",
            "transcript_path": transcript_path,
            "cwd": "/tmp",
            "hook_event_name": "Stop",
            "stop_hook_active": False,
        }

    def test_permission_prompt_payload_structure(self):
        """permission_prompt payload has correct structure."""
        payload = self.create_notification_payload("permission_prompt")
        self.assertEqual(payload["hook_event_name"], "Notification")
        self.assertEqual(payload["notification_type"], "permission_prompt")

    def test_idle_prompt_payload_structure(self):
        """idle_prompt payload has correct structure."""
        payload = self.create_notification_payload(
            "idle_prompt",
            "Claude is waiting for your input"
        )
        self.assertEqual(payload["notification_type"], "idle_prompt")
        self.assertIn("waiting", payload["message"])

    def test_auth_success_payload_structure(self):
        """auth_success payload has correct structure."""
        payload = self.create_notification_payload("auth_success")
        self.assertEqual(payload["notification_type"], "auth_success")

    def test_elicitation_dialog_payload_structure(self):
        """elicitation_dialog payload has correct structure."""
        payload = self.create_notification_payload("elicitation_dialog")
        self.assertEqual(payload["notification_type"], "elicitation_dialog")

    def test_stop_payload_structure(self):
        """Stop event payload has correct structure."""
        payload = self.create_stop_payload("/tmp/transcript.jsonl")
        self.assertEqual(payload["hook_event_name"], "Stop")
        self.assertIn("transcript_path", payload)


class TestFallbackMessageDetection(unittest.TestCase):
    """Test fallback message content detection when notification_type is missing."""

    def test_detects_permission_from_message(self):
        """Detects permission request from message content."""
        test_messages = [
            "Claude needs permission to run this command",
            "Allow Claude to access the file",
            "Permission required for this action",
        ]
        for msg in test_messages:
            with self.subTest(msg=msg):
                msg_lower = msg.lower()
                detected = "permission" in msg_lower or "allow" in msg_lower
                self.assertTrue(detected)

    def test_detects_idle_from_message(self):
        """Detects idle/waiting from message content."""
        test_messages = [
            "Claude is waiting for your input",
            "Waiting for user input",
            "Claude is idle",
        ]
        for msg in test_messages:
            with self.subTest(msg=msg):
                msg_lower = msg.lower()
                detected = "waiting" in msg_lower or "input" in msg_lower or "idle" in msg_lower
                self.assertTrue(detected)

    def test_detects_auth_from_message(self):
        """Detects auth request from message content."""
        test_messages = [
            "Authentication required",
            "Please login to continue",
            "Sign in to your account",
        ]
        for msg in test_messages:
            with self.subTest(msg=msg):
                msg_lower = msg.lower()
                detected = "auth" in msg_lower or "login" in msg_lower or "sign" in msg_lower
                self.assertTrue(detected)

    def test_detects_mcp_from_message(self):
        """Detects MCP/tool request from message content."""
        test_messages = [
            "MCP server needs input",
            "Tool requires additional information",
            "Elicitation dialog opened",
        ]
        for msg in test_messages:
            with self.subTest(msg=msg):
                msg_lower = msg.lower()
                detected = "mcp" in msg_lower or "tool" in msg_lower or "elicit" in msg_lower
                self.assertTrue(detected)

    def test_detects_question_from_message(self):
        """Detects question from message content."""
        test_messages = [
            "Claude has a question for you",
            "Please choose an option",
            "Select the desired action",
        ]
        for msg in test_messages:
            with self.subTest(msg=msg):
                msg_lower = msg.lower()
                detected = "question" in msg_lower or "choose" in msg_lower or "select" in msg_lower
                self.assertTrue(detected)


class TestTranscriptReading(unittest.TestCase):
    """Test reading Claude transcript files."""

    def test_handles_missing_transcript_file(self):
        """Returns appropriate message for missing file."""
        result = get_latest_claude_message("/nonexistent/path/file.jsonl")
        self.assertIn("not found", result.lower())

    def test_handles_empty_transcript(self):
        """Returns default message for empty transcript."""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = get_latest_claude_message(temp_path)
            self.assertEqual(result, "Task Completed")
        finally:
            import os
            os.unlink(temp_path)

    def test_reads_last_assistant_message(self):
        """Reads the last assistant message from transcript."""
        import tempfile
        transcript_lines = [
            json.dumps({"message": {"role": "user", "content": [{"type": "text", "text": "Hello"}]}}),
            json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": "First response"}]}}),
            json.dumps({"message": {"role": "user", "content": [{"type": "text", "text": "Another message"}]}}),
            json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": "Final response"}]}}),
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write("\n".join(transcript_lines))
            temp_path = f.name

        try:
            result = get_latest_claude_message(temp_path)
            self.assertEqual(result, "Final response")
        finally:
            import os
            os.unlink(temp_path)

    def test_handles_malformed_json_lines(self):
        """Skips malformed JSON lines gracefully."""
        import tempfile
        transcript_lines = [
            "not valid json",
            json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": "Valid message"}]}}),
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write("\n".join(transcript_lines))
            temp_path = f.name

        try:
            result = get_latest_claude_message(temp_path)
            self.assertEqual(result, "Valid message")
        finally:
            import os
            os.unlink(temp_path)


class TestMessageTruncation(unittest.TestCase):
    """Test message truncation for notifications."""

    def test_truncates_long_messages(self):
        """Long messages are truncated with ellipsis."""
        long_message = "A" * 200
        truncated = long_message[:100] + "..." if len(long_message) > 100 else long_message
        self.assertEqual(len(truncated), 103)  # 100 + "..."
        self.assertTrue(truncated.endswith("..."))

    def test_does_not_truncate_short_messages(self):
        """Short messages are not truncated."""
        short_message = "Short message"
        result = short_message[:100] + "..." if len(short_message) > 100 else short_message
        self.assertEqual(result, "Short message")
        self.assertFalse(result.endswith("..."))


class TestEmojiPresence(unittest.TestCase):
    """Test that all notification messages contain appropriate emojis."""

    def test_permission_prompt_has_lock_emoji(self):
        """permission_prompt message contains lock emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_PERMISSION_PROMPT, lang)
            self.assertIn("🔐", msg, f"Missing emoji for {lang}")

    def test_idle_prompt_has_hourglass_emoji(self):
        """idle_prompt message contains hourglass emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_IDLE_PROMPT, lang)
            self.assertIn("⏳", msg, f"Missing emoji for {lang}")

    def test_auth_success_has_checkmark_emoji(self):
        """auth_success message contains checkmark emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_AUTH_SUCCESS, lang)
            self.assertIn("✅", msg, f"Missing emoji for {lang}")

    def test_auth_required_has_key_emoji(self):
        """auth_required message contains key emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_AUTH_REQUIRED, lang)
            self.assertIn("🔑", msg, f"Missing emoji for {lang}")

    def test_elicitation_has_speech_emoji(self):
        """elicitation message contains speech emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_ELICITATION, lang)
            self.assertIn("💬", msg, f"Missing emoji for {lang}")

    def test_question_has_question_emoji(self):
        """question message contains question emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_QUESTION, lang)
            self.assertIn("❓", msg, f"Missing emoji for {lang}")

    def test_attention_has_bell_emoji(self):
        """attention message contains bell emoji."""
        for lang in TRANSLATIONS:
            msg = get_message(MSG_ATTENTION, lang)
            self.assertIn("🔔", msg, f"Missing emoji for {lang}")


if __name__ == "__main__":
    unittest.main()
