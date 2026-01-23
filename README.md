# claude-code-notify

English | [中文](./README_CN.md)

Desktop notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - get notified when tasks complete, when permission is needed, or when Claude is waiting for input.

## Features

- **Task Completion Notifications**: Get notified when Claude finishes a task, with a preview of the response
- **Permission Prompts**: Know immediately when Claude needs your approval
- **Idle Prompts**: Get alerted when Claude is waiting for your input
- **Cross-Platform**: Works on macOS, Windows, and Linux
- **Multi-Language Support**: Auto-detects system language (EN, ZH, JA, KO, DE, FR, ES)

## Changelog

### v1.0.2 (2026-01-23)

**New Features**
- 🌍 Add i18n support for 7 languages: English, 简体中文, 日本語, 한국어, Deutsch, Français, Español
- 🔔 Add new notification types: `auth_success`, `elicitation_dialog`
- 🛡️ Add fallback message detection for missing `notification_type` (workaround for Claude Code bug)

**Improvements**
- ✨ Add emoji indicators for all notification types
- 🧪 Add comprehensive test suite (51 tests)

### v1.0.0 (2026-01-23)

- Initial release
- Support for Stop and Notification hooks
- Cross-platform support (macOS, Windows, Linux)

## Installation

### Option 1: pip/uv install (Recommended)

```bash
pip install git+https://github.com/starpipi/claude-code-notify.git
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv tool install git+https://github.com/starpipi/claude-code-notify.git
```

Then add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "claude-code-notify"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "claude-code-notify"
          }
        ]
      }
    ]
  }
}
```

### Option 2: Claude Code Plugin

Clone the repository to the plugins marketplace directory:

```bash
git clone https://github.com/starpipi/claude-code-notify.git ~/.claude/plugins/marketplaces/claude-code-notify
```

Then enable the plugin in `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "notify@claude-code-notify": true
  }
}
```

## Platform Requirements

### macOS
No additional setup needed. Uses native `osascript`.

### Windows
No additional setup needed. Uses PowerShell with Windows Forms.

### Linux
Requires `libnotify`:

```bash
# Debian/Ubuntu
sudo apt install libnotify-bin

# Fedora
sudo dnf install libnotify

# Arch
sudo pacman -S libnotify
```

## Manual Testing

Test notifications directly from the command line:

```bash
# If installed via pip/uv
claude-code-notify "Test Title" "Test message body"

# If installed via plugin
python3 ~/.claude/plugins/marketplaces/claude-code-notify/plugin/hooks/notify.py "Test" "Hello"
```

## Debug Logs

Debug logs are written to `/tmp/claude_code_notify_debug.log` for troubleshooting.

## License

Apache-2.0
