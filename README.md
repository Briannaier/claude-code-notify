# Claude Code Notify — Apple-Style Windows Popup

> Forked from [starpipi/claude-code-notify](https://github.com/starpipi/claude-code-notify) · Windows 端重写

当你切到浏览器、编辑器等非终端窗口时，Claude Code 需要你关注（权限请求 / 回复完成 / 等待输入）会自动弹出置顶提醒窗口。

**纯弹窗，无提示音，不打扰。**

---

## 适用环境

| 项目 | 说明 |
|------|------|
| 操作系统 | Windows 10 / 11 |
| Claude Code 版本 | 2.x（CLI 终端模式） |
| 终端 | PowerShell / CMD / Windows Terminal / Git Bash |
| Python | 3.8+ |

macOS / Linux 用户请使用[原项目](https://github.com/starpipi/claude-code-notify)。

---

## 弹窗类型

Claude Code 触发的事件共 8 类：

| 事件 | 弹窗内容 | 触发场景 |
|------|----------|----------|
| `permission_prompt` | 🔐 需要您的授权 | Claude 需要你批准执行命令 |
| `idle_prompt` | ⏳ 等待您的输入 | Claude 在等你回答问题 |
| **Stop 事件** | **Claude Code需要您回复** | Claude 回复完成，等你下一轮输入 |
| `auth_success` | ✅ 认证成功 | 认证通过 |
| `auth_required` | 🔑 需要认证 | 需要登录认证 |
| `elicitation` | 💬 MCP 工具需要您的输入 | MCP 插件需要交互 |
| `question` | ❓ Claude 有问题想问您 | Claude 主动提问 |
| `attention` | 🔔 需要您的关注 | 其他需要关注的事件 |

---

## 弹窗风格

苹果极简风格（Apple Minimalist）：

- 白色卡片 + 16px 圆角
- 柔和阴影
- 深灰色标题 / 浅灰色正文（`#1D1D1F` / `#6E6E73`）
- 苹果蓝圆角按钮（`#0071E3`）
- WPF 渲染，屏幕居中，始终置顶
- **无提示音**，纯视觉提醒

---

## 安装

```bash
pip install git+https://github.com/Briannaier/claude-code-notify.git
```

## 配置

在 `~/.claude/settings.json` 中添加 hooks：

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -m claude_code_notify"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -m claude_code_notify"
          }
        ]
      }
    ]
  }
}
```

## 行为逻辑

- **终端焦点时**：自动跳过，不弹窗（你已经在看了）
- **切到其他窗口时**：置顶弹窗提醒你回来
- 按 `ESC` 或点击 `OK` 关闭弹窗

---

## 致谢

基于 [starpipi/claude-code-notify](https://github.com/starpipi/claude-code-notify) 改进，Windows 端以下部分完全重写：

- JSON 解析容错（Windows 中文路径兼容）
- MessageBox → WPF 置顶弹窗
- 前景窗口焦点检测
- XAML 安全转义
- Stop 事件从截取回复改为直白提醒
