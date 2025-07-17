# CCMaster 实现原理文档

本文档详细介绍 CCMaster 的内部实现原理和核心逻辑，帮助开发者理解项目的技术架构。

## 项目架构概述

CCMaster 是一个基于 Python 的 CLI 工具，通过以下几个核心组件实现对 Claude Code 会话的管理和监控：

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   CCMaster CLI  │────▶│  AppleScript │────▶│  Terminal   │
│   (Python)      │     │              │     │  + Claude   │
└────────┬────────┘     └──────────────┘     └──────┬──────┘
         │                                            │
         │ 监控状态文件                                │
         │                                            │
         ▼                                            ▼
┌─────────────────┐                          ┌──────────────┐
│  Status Files   │◀─────────────────────────│    Hooks     │
│ ~/.ccmaster/    │      更新状态             │  (Python)    │
└─────────────────┘                          └──────────────┘
```

## 核心实现原理

### 1. 会话启动机制

当用户运行 `ccmaster start` 时，程序执行以下步骤：

```python
def start_session_and_monitor(self, working_dir=None):
    # 1. 生成唯一的会话 ID（基于时间戳）
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 2. 创建钩子配置文件
    settings_file, backup_file = self.create_hooks_config(session_id)
    
    # 3. 使用 AppleScript 打开新终端窗口
    applescript = f'''
    tell application "Terminal"
        activate
        set newWindow to do script "cd {working_dir} && {claude_cmd}"
        return id of window 1
    end tell
    '''
    
    # 4. 查找 Claude 进程 PID
    pid = self.find_claude_pid()
    
    # 5. 启动监控线程
    process_thread = threading.Thread(target=self.monitor_process)
    status_thread = threading.Thread(target=self.monitor_status)
```

**关键点**：
- 使用 AppleScript 实现 macOS 终端自动化
- 通过时间戳生成唯一会话 ID，避免冲突
- 多线程并行监控进程状态和钩子状态

### 2. 钩子（Hooks）集成机制

CCMaster 的核心监控能力依赖于 Claude Code 的钩子系统：

#### 2.1 钩子配置结构

```python
hooks_config = {
    "hooks": {
        "PreToolUse": [{
            "matcher": ".*",  # 匹配所有工具
            "hooks": [{
                "type": "command",
                "command": f"python3 {hooks_dir}/pre_tool_use.py {session_id}"
            }]
        }],
        "UserPromptSubmit": [{
            "hooks": [{
                "type": "command",
                "command": f"python3 {hooks_dir}/user_prompt_submit.py {session_id}"
            }]
        }]
    }
}
```

#### 2.2 钩子工作流程

1. **用户提交提示词** → `UserPromptSubmit` 钩子触发 → 状态更新为 "processing"
2. **Claude 使用工具** → `PreToolUse` 钩子触发 → 状态更新为 "working"
3. **工具使用完成** → `PostToolUse` 钩子触发 → 不更新状态（避免重复）
4. **无活动 2 秒** → 自动检测 → 状态更新为 "idle"

### 3. 状态管理系统

#### 3.1 会话隔离设计

每个会话使用独立的状态文件，避免多会话冲突：

```python
# 原设计（有冲突）
self.status_file = ~/.ccmaster/status.json  # 所有会话共享

# 改进设计（无冲突）
self.status_file = ~/.ccmaster/status/{session_id}.json  # 每个会话独立
```

#### 3.2 状态文件结构

```json
{
    "state": "working",           // 当前状态
    "timestamp": "2025-01-18...", // 更新时间
    "last_tool": "Read",          // 最后使用的工具
    "current_action": "Using Read" // 当前动作描述
}
```

### 4. 防止重复空闲消息的核心逻辑

这是项目中最复杂的部分，通过以下机制实现：

```python
def monitor_status(self, session_id):
    has_shown_idle_for_cycle = False  # 周期内是否已显示空闲
    
    while True:
        if current_state != last_status:
            if current_state == 'processing':
                has_shown_idle_for_cycle = False  # 新周期开始，重置标志
                
            elif current_state == 'idle':
                if not has_shown_idle_for_cycle:  # 仅在未显示时显示
                    self.log_event('STATUS', 'Idle')
                    has_shown_idle_for_cycle = True
```

**关键逻辑**：
1. 使用 `has_shown_idle_for_cycle` 标志跟踪周期
2. "Processing" 状态标志新周期开始
3. 每个周期只允许显示一次 "Idle"

### 5. 实时显示系统

使用队列实现线程安全的日志显示：

```python
# 生产者（监控线程）
self.log_queue.put((timestamp, event_type, message))

# 消费者（主线程）
while True:
    timestamp, event_type, message = self.log_queue.get_nowait()
    
    if event_type == 'STATUS':
        # 显示状态变化（Processing/Idle）
        print(f"[{time_str}] {status_symbol}")
        
    elif event_type == 'TOOL':
        # 显示工具活动
        print(f"[{time_str}] → Using {tool}")  # 绿色箭头
        print(f"[{time_str}] ✓ Completed {tool}")  # 蓝色勾号
```

### 6. 进程生命周期管理

```python
def monitor_process(self, session_id, pid):
    while True:
        # 检查进程是否存在
        result = subprocess.run(['ps', '-p', str(pid)])
        if result.returncode != 0:
            # 进程已结束
            self.log_event('SESSION_END', 'Claude session ended')
            self.sessions[session_id]['status'] = 'ended'
            break
```

## 技术难点与解决方案

### 1. 符号链接路径问题

**问题**：当 ccmaster 通过 `/usr/local/bin/ccmaster` 符号链接运行时，`__file__` 指向符号链接而非实际文件。

**解决方案**：
```python
self.hooks_dir = Path(__file__).resolve().parent.parent / 'hooks'
# .resolve() 会解析符号链接到实际路径
```

### 2. 多重空闲消息问题

**问题**：多个钩子和自动检测都可能触发空闲状态，导致重复消息。

**解决方案**：
1. PostToolUse 钩子不设置空闲状态
2. 使用周期跟踪机制
3. 每个会话独立的状态文件

### 3. 终端窗口控制

**问题**：需要在新终端窗口中启动 Claude，而非当前窗口。

**解决方案**：使用 AppleScript 实现 macOS 终端自动化：
```applescript
tell application "Terminal"
    activate
    do script "cd /path && claude"
end tell
```

## 数据流程图

```
用户输入 "ccmaster start"
    │
    ▼
创建会话 ID 和配置
    │
    ▼
配置 Claude 钩子 ──────────┐
    │                      │
    ▼                      ▼
打开终端运行 Claude    钩子脚本就绪
    │                      │
    ▼                      │
查找进程 PID              │
    │                      │
    ▼                      ▼
启动监控线程 ◀─────────────┘
    │
    ├─→ 进程监控线程（检测 Claude 是否运行）
    │
    ├─→ 状态监控线程（读取状态文件变化）
    │
    └─→ 主线程（显示实时日志）
```

## 性能优化

1. **状态检查频率**：每 0.2 秒检查一次状态文件，平衡响应性和 CPU 使用
2. **自动空闲检测**：2 秒超时，快速响应但避免误判
3. **日志队列**：使用 `queue.Queue` 实现无锁的线程间通信

## 扩展性设计

1. **模块化钩子**：每个钩子是独立的 Python 脚本，易于修改和扩展
2. **配置驱动**：关键参数通过 `config.json` 配置，无需修改代码
3. **会话隔离**：支持同时运行多个独立的 Claude 会话

## 总结

CCMaster 通过巧妙结合以下技术实现了对 Claude Code 的透明监控：

1. **钩子机制**：利用 Claude 的扩展点获取实时状态
2. **多线程架构**：并行处理监控和显示
3. **状态机设计**：精确跟踪会话生命周期
4. **周期跟踪算法**：确保输出的简洁性

这种设计既保证了功能的完整性，又维持了用户体验的简洁性，是一个轻量级但功能强大的开发辅助工具。