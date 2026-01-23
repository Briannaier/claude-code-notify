# claude-code-notify

Desktop notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - get notified when tasks complete, when permission is needed, or when Claude is waiting for input.

## Features

- **Task Completion Notifications**: Get notified when Claude finishes a task, with a preview of the response
- **Permission Prompts**: Know immediately when Claude needs your approval
- **Idle Prompts**: Get alerted when Claude is waiting for your input
- **Cross-Platform**: Works on macOS, Windows, and Linux

## Installation

### Option 1: Claude Code Plugin (Recommended)

Add the marketplace in Claude Code:

```bash
claude /plugin:marketplace:add https://github.com/starpipi/claude-code-notify
```

Then install the plugin:

```bash
claude /plugin:install notify
```

### Option 2: pip/uv install

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
# If installed via plugin
python3 ~/.claude/plugins/cache/claude-code-notify/notify/*/plugin/hooks/notify.py "Test" "Hello"

# If installed via pip/uv
claude-code-notify "Test Title" "Test message body"
```

## Debug Logs

Debug logs are written to `/tmp/claude_code_notify_debug.log` for troubleshooting.

## License

Apache-2.0
