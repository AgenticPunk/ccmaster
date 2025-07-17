# CCMaster 实现指南

本文档详细说明了 CCMaster 的内部实现原理、架构设计和技术方案。

## 📐 架构概述

CCMaster 采用基于事件驱动的架构，通过 Claude Code 的钩子系统实现对会话的实时监控：

```
┌──────────────────────────────────────────────────────────────┐
│                         用户界面层                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  命令解析   │  │   状态显示   │  │   键盘交互(w)   │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────┐
│                         核心逻辑层                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ 会话管理器  │  │  监视模式    │  │   轮次控制器    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────┐
│                         监控系统层                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ 进程监控器  │  │  状态监控器  │  │   日志收集器    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────┐
│                          钩子系统                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │PreToolUse   │  │UserPromptSubmit│ │    Stop Hook    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 🔧 核心实现原理

### 1. 会话管理 (Session Management)

每个会话都有唯一的 ID（格式：`YYYYMMDD_HHMMSS`），用于：
- 隔离不同会话的钩子配置
- 跟踪会话状态和日志
- 管理会话生命周期

```python
def start_session_and_monitor(self, working_dir=None, watch_mode=False, max_turns=None):
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 创建会话级钩子配置
    settings_file, backup_file = self.create_hooks_config(session_id)
    
    # 启动 Claude Code
    applescript = f'''
    tell application "Terminal"
        activate
        set newWindow to do script "cd {working_dir} && {claude_cmd}"
        return id of window 1
    end tell
    '''
```

### 2. 钩子系统 (Hooks System)

CCMaster 使用三种钩子来监控 Claude Code 的状态：

#### PreToolUse Hook
- **触发时机**：Claude 即将使用工具时
- **获取信息**：工具名称
- **状态更新**：设置为 "working"

```python
def main():
    session_id = sys.argv[1]
    utils = HookUtils(session_id)
    data = utils.read_hook_input()
    tool_name = data.get('tool_name', 'unknown')
    utils.update_status('working', tool=tool_name, action=f'Using {tool_name}')
```

#### UserPromptSubmit Hook
- **触发时机**：用户提交新提示词时
- **获取信息**：用户输入的完整提示词
- **状态更新**：设置为 "processing"

```python
def main():
    session_id = sys.argv[1]
    utils = HookUtils(session_id)
    data = utils.read_hook_input()
    user_prompt = data.get('prompt', '')
    
    # 保存提示词到专门的日志文件
    with open(prompt_log_file, 'a') as f:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt': user_prompt
        }
        f.write(json.dumps(log_entry) + '\n')
```

#### Stop Hook
- **触发时机**：Claude 完成响应时
- **获取信息**：响应完成信号
- **状态更新**：设置为 "idle"

### 3. 进程监控 (Process Monitoring)

使用改进的进程检测机制：

```python
def find_claude_pid(self, max_attempts=10):
    our_pid = os.getpid()
    
    for attempt in range(max_attempts):
        time.sleep(1)
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        for line in result.stdout.strip().split('\n'):
            # 排除 ccmaster 自身和 python 进程
            if self.config['claude_code_command'] in line \
               and 'ccmaster' not in line \
               and 'python' not in line:
                pid = int(line.split()[1])
                if pid != our_pid:
                    return pid
```

### 4. 监视模式 (Watch Mode)

监视模式的核心逻辑：

```python
# 检测到空闲状态时
if 'Idle' in message:
    if watch_mode and has_seen_first_prompt:
        # 检查是否达到最大轮次
        if max_turns is None or auto_continue_count < max_turns:
            auto_continue_pending = True
            continue_countdown = 1
        else:
            # 达到最大轮次，自动关闭监视模式
            print(f"🛑 Max auto-continue turns ({max_turns}) reached")
            watch_mode = False

# 发送自动续写命令
if continue_countdown == 0:
    self.send_prompt_to_terminal(terminal_window_id, "continue")
    auto_continue_count += 1
```

### 5. 键盘交互 (Keyboard Interaction)

使用非阻塞输入检测：

```python
def check_keyboard_input(self):
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

# 在主循环中
key = self.check_keyboard_input()
if key == 'w':
    was_at_max_turns = max_turns and auto_continue_count >= max_turns
    watch_mode = not watch_mode
    
    if watch_mode and was_at_max_turns:
        # 重置计数器
        auto_continue_count = 0
        # 如果当前空闲，立即续写
        if self.current_status == 'idle':
            self.send_prompt_to_terminal(terminal_window_id, "continue")
```

### 6. 自动续写控制 (Auto-Continue Control)

通过 AppleScript 发送命令到终端：

```python
def send_prompt_to_terminal(self, window_id, prompt):
    clear_script = f'''
    tell application "Terminal"
        activate
        set frontmost of window id {window_id} to true
    end tell
    
    tell application "System Events"
        tell process "Terminal"
            keystroke return  -- 清除任何中断状态
            delay 0.2
            keystroke "{prompt}"
            keystroke return
        end tell
    end tell
    '''
```

## 📊 数据流程

### 状态更新流程

```
Claude Code ──(Hook Event)──> Hook Script ──(Update)──> Status File
                                    │
                                    └──(Log)──> Log File
                                    
CCMaster ──(Monitor)──> Status File ──(Parse)──> Display Update
                              │
                              └──(Queue)──> Real-time Display
```

### 自动续写流程

```
1. Stop Hook 触发 ──> 状态设为 "idle"
2. CCMaster 检测到 idle 状态
3. 检查条件：
   - 是否在监视模式
   - 是否已看到第一个提示词
   - 是否未达到最大轮次
4. 如果满足条件 ──> 1秒倒计时
5. 倒计时结束 ──> AppleScript 发送 "continue"
6. 更新计数器
```

## 🛠 技术细节

### 文件结构

```
~/.ccmaster/
├── config.json              # 全局配置
├── sessions.json            # 会话元数据
├── status/                  # 实时状态
│   └── {session_id}.json    # 单个会话状态
└── logs/                    # 日志文件
    ├── {session_id}.log     # 会话事件日志
    └── {session_id}_prompts.log  # 用户提示词日志
```

### 状态文件格式

```json
{
    "state": "working",
    "last_tool": "Edit",
    "current_action": "Using Edit",
    "timestamp": "2024-01-24T14:30:24.123456",
    "session_id": "20240124_143022"
}
```

### 会话元数据格式

```json
{
    "20240124_143022": {
        "id": "20240124_143022",
        "started_at": "2024-01-24T14:30:22.123456",
        "working_dir": "/Users/name/project",
        "status": "running",
        "pid": 12345,
        "last_activity": "2024-01-24T14:35:45.123456"
    }
}
```

## 🔍 关键技术决策

### 1. 为什么使用会话级钩子？

- **隔离性**：每个会话独立，互不干扰
- **安全性**：会话结束后自动恢复原始设置
- **灵活性**：可以同时运行多个 CCMaster 会话

### 2. 为什么使用 AppleScript？

- macOS 原生支持，无需额外依赖
- 可以精确控制终端窗口
- 支持键盘输入模拟

### 3. 为什么使用轮询而非事件推送？

- Claude Code 钩子系统的限制
- 简化实现，避免复杂的 IPC
- 0.2秒的轮询间隔足够响应

### 4. 轮次限制的设计考虑

- 防止无限循环消耗资源
- 给用户明确的控制权
- 支持手动重置，平衡自动化和控制

## 🚀 性能优化

1. **简化的进程检测**
   - 使用基础的 `pgrep` 和 `ps` 命令确保可靠性
   - 无复杂的 PID 跟踪或重试机制
   - 容错监控（5 次失败后才声明结束）

2. **流畅的自动续写**
   - 使用 AppleScript 直接检测终端标签页
   - 双层回退系统确保最大可靠性
   - 清晰的成功/失败反馈，无复杂时机控制

3. **高效监控**
   - 简单的后台线程每 2 秒检查一次
   - 无复杂的进程验证或多种方法
   - 直观逻辑，最小资源使用

## 🔒 错误处理

1. **会话监控**
   - 等待 3 秒让 Claude 启动后再开始监控
   - 需要连续 5 次失败才声明会话结束
   - 会话真正结束时提供清晰反馈

2. **自动续写可靠性**
   - 主要方法：查找 Claude 标签页并发送 continue
   - 回退方法：发送到最前面的终端窗口
   - 自动续写失败时显示清晰错误消息

3. **优雅降级**
   - 如果自动续写失败，用户获得清晰指示
   - 即使自动续写出错，会话监控继续工作
   - 无可能引入错误的复杂回退链

## 📝 总结

CCMaster 通过巧妙利用 Claude Code 的钩子系统，实现了对会话的完整监控和自动化控制。其设计强调：

- **用户体验**：美观的输出，直观的交互
- **可靠性**：健壮的错误处理，多重保障
- **灵活性**：可配置的参数，交互式控制
- **性能**：优化的轮询，最小的资源占用

这种设计使 CCMaster 成为提升 Claude Code 使用体验的强大工具。