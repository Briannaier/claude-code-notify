#!/usr/bin/env python3
"""
Claude Code Notify - Desktop notifications for Claude Code.

Supported platforms:
- macOS: Uses osascript (native)
- Windows: Uses PowerShell MessageBox (native, non-blocking background process)
- Linux: Uses notify-send (requires libnotify)
"""

import base64
import json
import locale
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ============================================================================
# Internationalization (i18n) Support
# ============================================================================

MSG_PERMISSION_PROMPT = "permission_prompt"
MSG_IDLE_PROMPT = "idle_prompt"
MSG_AUTH_SUCCESS = "auth_success"
MSG_AUTH_REQUIRED = "auth_required"
MSG_ELICITATION = "elicitation"
MSG_QUESTION = "question"
MSG_ATTENTION = "attention"
MSG_TASK_COMPLETED = "task_completed"

TRANSLATIONS = {
    "en": {
        MSG_PERMISSION_PROMPT: "\U0001f510 Needs your permission",
        MSG_IDLE_PROMPT: "⏳ Waiting for your input",
        MSG_AUTH_SUCCESS: "✅ Authentication successful",
        MSG_AUTH_REQUIRED: "\U0001f511 Authentication required",
        MSG_ELICITATION: "\U0001f4ac MCP tool needs your input",
        MSG_QUESTION: "❓ Claude has a question for you",
        MSG_ATTENTION: "\U0001f514 Needs your attention",
        MSG_TASK_COMPLETED: "Task Completed",
    },
    "zh": {
        MSG_PERMISSION_PROMPT: "\U0001f510 需要您的授权",
        MSG_IDLE_PROMPT: "⏳ 等待您的输入",
        MSG_AUTH_SUCCESS: "✅ 认证成功",
        MSG_AUTH_REQUIRED: "\U0001f511 需要认证",
        MSG_ELICITATION: "\U0001f4ac MCP 工具需要您的输入",
        MSG_QUESTION: "❓ Claude 有问题想问您",
        MSG_ATTENTION: "\U0001f514 需要您的关注",
        MSG_TASK_COMPLETED: "任务已完成",
    },
    "ja": {
        MSG_PERMISSION_PROMPT: "\U0001f510 許可が必要です",
        MSG_IDLE_PROMPT: "⏳ 入力をお待ちしています",
        MSG_AUTH_SUCCESS: "✅ 認証成功",
        MSG_AUTH_REQUIRED: "\U0001f511 認証が必要です",
        MSG_ELICITATION: "\U0001f4ac MCPツールの入力が必要です",
        MSG_QUESTION: "❓ Claudeから質問があります",
        MSG_ATTENTION: "\U0001f514 注意が必要です",
        MSG_TASK_COMPLETED: "タスク完了",
    },
    "ko": {
        MSG_PERMISSION_PROMPT: "\U0001f510 권한이 필요합니다",
        MSG_IDLE_PROMPT: "⏳ 입력을 기다리고 있습니다",
        MSG_AUTH_SUCCESS: "✅ 인증 성공",
        MSG_AUTH_REQUIRED: "\U0001f511 인증이 필요합니다",
        MSG_ELICITATION: "\U0001f4ac MCP 도구 입력이 필요합니다",
        MSG_QUESTION: "❓ Claude가 질문이 있습니다",
        MSG_ATTENTION: "\U0001f514 주의가 필요합니다",
        MSG_TASK_COMPLETED: "작업 완료",
    },
    "de": {
        MSG_PERMISSION_PROMPT: "\U0001f510 Berechtigung erforderlich",
        MSG_IDLE_PROMPT: "⏳ Warte auf Ihre Eingabe",
        MSG_AUTH_SUCCESS: "✅ Authentifizierung erfolgreich",
        MSG_AUTH_REQUIRED: "\U0001f511 Authentifizierung erforderlich",
        MSG_ELICITATION: "\U0001f4ac MCP-Tool benötigt Eingabe",
        MSG_QUESTION: "❓ Claude hat eine Frage",
        MSG_ATTENTION: "\U0001f514 Aufmerksamkeit erforderlich",
        MSG_TASK_COMPLETED: "Aufgabe abgeschlossen",
    },
    "fr": {
        MSG_PERMISSION_PROMPT: "\U0001f510 Permission requise",
        MSG_IDLE_PROMPT: "⏳ En attente de votre saisie",
        MSG_AUTH_SUCCESS: "✅ Authentification réussie",
        MSG_AUTH_REQUIRED: "\U0001f511 Authentification requise",
        MSG_ELICITATION: "\U0001f4ac L'outil MCP nécessite une entrée",
        MSG_QUESTION: "❓ Claude a une question",
        MSG_ATTENTION: "\U0001f514 Attention requise",
        MSG_TASK_COMPLETED: "Tâche terminée",
    },
    "es": {
        MSG_PERMISSION_PROMPT: "\U0001f510 Se necesita permiso",
        MSG_IDLE_PROMPT: "⏳ Esperando su entrada",
        MSG_AUTH_SUCCESS: "✅ Autenticación exitosa",
        MSG_AUTH_REQUIRED: "\U0001f511 Autenticación requerida",
        MSG_ELICITATION: "\U0001f4ac La herramienta MCP necesita entrada",
        MSG_QUESTION: "❓ Claude tiene una pregunta",
        MSG_ATTENTION: "\U0001f514 Se requiere atención",
        MSG_TASK_COMPLETED: "Tarea completada",
    },
}


def get_system_language() -> str:
    try:
        system_type = platform.system()

        if system_type == "Darwin":
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleLanguages"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
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

        lang = locale.getdefaultlocale()[0] or os.environ.get("LANG", "en")
        lang_code = lang.split("_")[0].lower()

        if lang_code in TRANSLATIONS:
            return lang_code

        return "en"
    except Exception:
        return "en"


def get_message(key: str, lang: str = None) -> str:
    if lang is None:
        lang = get_system_language()

    messages = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return messages.get(key, TRANSLATIONS["en"].get(key, ""))


def debug_log(msg: str) -> None:
    log_path = Path(tempfile.gettempdir()) / "claude_code_notify_debug.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except Exception:
        pass


def send_notification(title: str, message: str) -> bool:
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

    # --- Windows (WPF card-style popup) ---
    elif system_type == "Windows":
        try:
            # XAML-escape: encode emoji as XML char refs, escape & < > "
            def _xml_escape(s):
                result = []
                for ch in s:
                    cp = ord(ch)
                    if cp > 0xFFFF:
                        result.append(f'&#x{cp:X};')
                    elif ch == '&':
                        result.append('&amp;')
                    elif ch == '<':
                        result.append('&lt;')
                    elif ch == '>':
                        result.append('&gt;')
                    elif ch == '"':
                        result.append('&quot;')
                    else:
                        result.append(ch)
                return ''.join(result)

            x_title = _xml_escape(title)
            x_message = _xml_escape(message)

            ps_script = f"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {{
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
}}
"@

$termClasses = @('ConsoleWindowClass','CASCADIA_HOSTING_WINDOW_CLASS')
$termProcs = @('powershell','cmd','conhost','WindowsTerminal','wsl','bash')
$hwnd = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder(256)
[Win32]::GetClassName($hwnd, $sb, 256) | Out-Null
$fgClass = $sb.ToString()
$fgPid = 0
[Win32]::GetWindowThreadProcessId($hwnd, [ref]$fgPid) | Out-Null
try {{ $fgProc = (Get-Process -Id $fgPid -ErrorAction Stop).ProcessName }} catch {{ $fgProc = '' }}
if ($fgClass -in $termClasses -or $fgProc -in $termProcs) {{ exit 0 }}

Add-Type -AssemblyName PresentationFramework,PresentationCore,WindowsBase

[xml]$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        Title="" Width="380" Height="195"
        WindowStyle="None" AllowsTransparency="True"
        Background="Transparent" Topmost="True"
        WindowStartupLocation="CenterScreen"
        ShowInTaskbar="True" ResizeMode="NoResize">
    <Border CornerRadius="16" Background="#FAFAFA" BorderBrush="#E8E8EC" BorderThickness="1">
        <Border.Effect>
            <DropShadowEffect BlurRadius="40" ShadowDepth="2" Opacity="0.08" Color="Black"/>
        </Border.Effect>
        <Grid Margin="28,26">
            <Grid.RowDefinitions>
                <RowDefinition Height="Auto"/>
                <RowDefinition Height="*"/>
                <RowDefinition Height="Auto"/>
            </Grid.RowDefinitions>
            <TextBlock Grid.Row="0" Text="{x_title}"
                       FontFamily="Microsoft YaHei UI" FontSize="15" FontWeight="SemiBold"
                       Foreground="#1D1D1F" Margin="0,0,0,12"/>
            <TextBlock Grid.Row="1" Text="{x_message}"
                       FontFamily="Microsoft YaHei UI" FontSize="13"
                       Foreground="#6E6E73" TextWrapping="Wrap"
                       LineHeight="20" VerticalAlignment="Top"/>
            <Button Grid.Row="2" Content="OK" Width="72" Height="30"
                    HorizontalAlignment="Right" Margin="0,16,0,0" IsDefault="True"
                    FontFamily="Microsoft YaHei UI" FontSize="12" FontWeight="SemiBold"
                    Foreground="White" Cursor="Hand">
                <Button.Template>
                    <ControlTemplate TargetType="Button">
                        <Border Background="#0071E3" CornerRadius="15">
                            <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
                        </Border>
                    </ControlTemplate>
                </Button.Template>
            </Button>
        </Grid>
    </Border>
</Window>
"@

$reader = New-Object System.Xml.XmlNodeReader $xaml
$win = [Windows.Markup.XamlReader]::Load($reader)
$win.Add_Loaded({{
    function FindChild($p, $t) {{
        for ($i=0; $i -lt [Windows.Media.VisualTreeHelper]::GetChildrenCount($p); $i++) {{
            $c = [Windows.Media.VisualTreeHelper]::GetChild($p, $i)
            if ($c -is $t) {{ return $c }}
            $r = FindChild $c $t; if ($r) {{ return $r }}
        }}
        return $null
    }}
    $okBtn = FindChild $win ([System.Windows.Controls.Button])
    if ($okBtn) {{ $okBtn.Add_Click({{ $win.Close() }}) }}
    $win.Activate()
}})
$win.Add_KeyDown({{ if ($_.Key -eq 'Escape') {{ $win.Close() }} }})
$win.ShowDialog() | Out-Null
"""

            encoded_command = base64.b64encode(
                ps_script.encode('utf-16le')
            ).decode('utf-8')

            debug_log(f"Sending Windows notification: title={title}, message={message}")

            # Capture stderr to temp file for debugging
            import tempfile as _tf
            _errfile = os.path.join(_tf.gettempdir(), 'claude_notify_ps_err.txt')
            with open(_errfile, 'w') as _ef:
                pass  # truncate

            proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-EncodedCommand", encoded_command],
                creationflags=0x08000000 if sys.platform == 'win32' else 0,
                stdout=subprocess.DEVNULL,
                stderr=open(_errfile, 'a'),
            )
            debug_log(f"PowerShell process spawned, pid={proc.pid}, stderr->{_errfile}")
            return True
        except Exception as e:
            debug_log(f"Windows notification failed: {str(e)}")
            return False

            encoded_command = base64.b64encode(
                ps_script.encode('utf-16le')
            ).decode('utf-8')

            debug_log(f"Sending Windows notification: title={title}, message={message}")

            # Launch in background via CREATE_NO_WINDOW flag (0x08000000)
            proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-EncodedCommand", encoded_command],
                creationflags=0x08000000 if sys.platform == 'win32' else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            debug_log(f"PowerShell process spawned, pid={proc.pid}")
            return True
        except Exception as e:
            debug_log(f"Windows notification failed: {str(e)}")
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
    debug_log("=== Hook triggered ===")
    debug_log(f"sys.argv: {sys.argv}")
    debug_log(f"stdin.isatty(): {sys.stdin.isatty()}")

    lang = get_system_language()
    debug_log(f"Detected language: {lang}")

    title = "Claude Code"
    message = get_message(MSG_TASK_COMPLETED, lang)

    try:
        # 1. Try reading from stdin (Claude Hook mode)
        if not sys.stdin.isatty():
            try:
                input_data = sys.stdin.read()
                debug_log(f"stdin data: {input_data[:500] if input_data else 'empty'}")

                if input_data.strip():
                    # Detect notification type from raw input (JSON may be malformed
                    # due to unescaped Windows paths from Claude Code)
                    raw = input_data
                    debug_log(f"stdin raw ({len(raw)} bytes)")

                    # Try JSON parse first, fall back to string matching
                    notification_type = ""
                    event_message = ""
                    hook_event = ""
                    try:
                        payload = json.loads(raw)
                        hook_event = payload.get("hook_event_name", "")
                        notification_type = payload.get("notification_type", "")
                        event_message = payload.get("message", "")
                    except json.JSONDecodeError:
                        debug_log("JSON parse failed, using string matching fallback")
                        # Simple string-based detection from raw input
                        if "hook_event_name" in raw and "Notification" in raw:
                            hook_event = "Notification"
                        if '"notification_type":"permission_prompt"' in raw:
                            notification_type = "permission_prompt"
                        elif '"notification_type":"idle_prompt"' in raw:
                            notification_type = "idle_prompt"
                        elif '"notification_type":"auth_success"' in raw:
                            notification_type = "auth_success"
                        elif '"notification_type":"elicitation_dialog"' in raw:
                            notification_type = "elicitation_dialog"
                        # Extract message if possible
                        import re as _re
                        m = _re.search(r'"message"\s*:\s*"([^"]*)"', raw)
                        if m:
                            event_message = m.group(1)

                    debug_log(f"hook_event={hook_event}, type={notification_type}, msg={event_message}")

                    if hook_event == "Notification":
                        if notification_type == "permission_prompt":
                            message = get_message(MSG_PERMISSION_PROMPT, lang)
                        elif notification_type == "idle_prompt":
                            message = get_message(MSG_IDLE_PROMPT, lang)
                        elif notification_type == "auth_success":
                            message = get_message(MSG_AUTH_SUCCESS, lang)
                        elif notification_type == "elicitation_dialog":
                            message = get_message(MSG_ELICITATION, lang)
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
                                message = event_message[:100] + "..." if len(event_message) > 100 else event_message
                        else:
                            message = get_message(MSG_ATTENTION, lang)

                        send_notification(title, message)
                        return 0

                    # Handle Stop events — Claude finished, waiting for user
                    if "transcript_path" in raw and hook_event != "Notification":
                        message = get_message(MSG_IDLE_PROMPT, lang)
                        if lang == 'zh':
                            message = 'Claude Code需要您回复'
                        send_notification(title, message)
                        return 0

            except Exception as e:
                debug_log(f"Exception in stdin handling: {str(e)}")
                pass

        # 2. Manual test mode
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
