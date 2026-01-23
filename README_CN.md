# claude-code-notify

[English](./README.md) | 中文

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) 桌面通知插件 - 任务完成、需要权限或等待输入时自动通知你。

## 功能特性

- **任务完成通知**：Claude 完成任务时通知你，并预览回复内容
- **权限请求提醒**：Claude 需要授权时立即提醒
- **等待输入提醒**：Claude 等待你输入时发出通知
- **跨平台支持**：支持 macOS、Windows 和 Linux

## 安装方式

### 方式一：Claude Code 插件安装（推荐）

在 Claude Code 中添加插件市场：

```bash
claude /plugin:marketplace:add https://github.com/starpipi/claude-code-notify
```

然后安装插件：

```bash
claude /plugin:install notify
```

### 方式二：pip/uv 安装

```bash
pip install git+https://github.com/starpipi/claude-code-notify.git
```

或使用 [uv](https://github.com/astral-sh/uv)：

```bash
uv tool install git+https://github.com/starpipi/claude-code-notify.git
```

然后在 `~/.claude/settings.json` 中添加配置：

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

## 平台要求

### macOS
无需额外设置，使用系统原生 `osascript`。

### Windows
无需额外设置，使用 PowerShell 和 Windows Forms。

### Linux
需要安装 `libnotify`：

```bash
# Debian/Ubuntu
sudo apt install libnotify-bin

# Fedora
sudo dnf install libnotify

# Arch
sudo pacman -S libnotify
```

## 手动测试

通过命令行直接测试通知：

```bash
# 插件安装方式
python3 ~/.claude/plugins/cache/claude-code-notify/notify/*/plugin/hooks/notify.py "测试" "你好"

# pip/uv 安装方式
claude-code-notify "测试标题" "测试消息内容"
```

## 调试日志

调试日志保存在 `/tmp/claude_code_notify_debug.log`，可用于问题排查。

## 开源协议

Apache-2.0
