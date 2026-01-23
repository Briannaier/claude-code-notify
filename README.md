# claude-code-notify

Desktop notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - get notified when tasks complete, when permission is needed, or when Claude is waiting for input.

## Features

- **Task Completion Notifications**: Get notified when Claude finishes a task, with a preview of the response
- **Permission Prompts**: Know immediately when Claude needs your approval
- **Idle Prompts**: Get alerted when Claude is waiting for your input
- **Cross-Platform**: Works on macOS, Windows, and Linux

## Installation

```bash
pip install claude-code-notify
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv tool install claude-code-notify
```

## Setup

After installation, configure Claude Code to use this notification hook.

### Option 1: Add to your Claude settings

Add to `~/.claude/settings.json`:

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

### Option 2: Project-level configuration

Add to your project's `.claude/settings.json`:

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
    ]
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
claude-code-notify "Test Title" "Test message body"
```

## Debug Logs

Debug logs are written to `/tmp/claude_code_notify_debug.log` for troubleshooting.

## License

MIT
