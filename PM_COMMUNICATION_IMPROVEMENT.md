# PM Mode 通信方案改进

## 当前问题

1. **直接消息通信的局限性**
   - 消息通过 AppleScript 和临时文件传递，容易丢失
   - 没有消息持久化和历史记录
   - 难以跟踪任务状态

2. **缺少结构化的任务管理**
   - 任务通过自由文本传递，格式不统一
   - 没有任务优先级和依赖关系管理
   - 团队成员难以理解任务边界

## 改进方案

### 1. 基于文件的任务队列系统

```
project_dir/
├── .ccmaster/
│   ├── tasks/
│   │   ├── pending/       # 待处理任务
│   │   ├── in_progress/   # 进行中任务
│   │   └── completed/     # 已完成任务
│   ├── messages/          # 团队成员间的消息
│   └── status/            # 各成员的状态文件
```

#### 任务文件格式 (JSON)
```json
{
  "id": "task_20250119_143022",
  "created_by": "pm_session_id",
  "assigned_to": "frontend_dev_session_id",
  "priority": "high",
  "type": "feature|bug|refactor|test",
  "title": "Implement user login component",
  "description": "Create a React component for user login with validation",
  "acceptance_criteria": [
    "Email and password fields with validation",
    "Submit button with loading state",
    "Error message display"
  ],
  "dependencies": ["task_20250119_142000"],
  "status": "pending|in_progress|blocked|completed",
  "created_at": "2025-01-19T14:30:22Z",
  "updated_at": "2025-01-19T14:30:22Z",
  "completed_at": null,
  "output": null
}
```

### 2. 改进的 MCP 工具

#### 新增工具

1. **create_task**
```python
def create_task(
    title: str,
    description: str,
    assigned_to: str,
    priority: str = "medium",
    task_type: str = "feature",
    acceptance_criteria: List[str] = None,
    dependencies: List[str] = None
) -> Dict[str, Any]:
    """创建结构化任务并分配给团队成员"""
```

2. **get_my_tasks**
```python
def get_my_tasks(
    session_id: str,
    status: str = None
) -> List[Dict[str, Any]]:
    """获取分配给特定成员的任务列表"""
```

3. **update_task_status**
```python
def update_task_status(
    task_id: str,
    status: str,
    output: str = None,
    blocker: str = None
) -> Dict[str, Any]:
    """更新任务状态"""
```

4. **watch_task_queue**
```python
def watch_task_queue(
    session_id: str,
    callback: Callable
) -> None:
    """监听新任务分配（基于文件系统事件）"""
```

### 3. 改进的团队成员 Prompt

```markdown
You are a [ROLE] in a collaborative development team.

TASK MANAGEMENT:
- Check for new tasks: /mcp__ccmaster__get_my_tasks
- Update task progress: /mcp__ccmaster__update_task_status
- Tasks have clear acceptance criteria - complete ALL criteria
- Mark task as 'completed' when ALL criteria are met
- If blocked, update status to 'blocked' with reason

WORK BOUNDARIES:
- Only work on tasks assigned to you
- Do NOT create new features without explicit tasks
- When a task is completed, wait for new assignments
- If you receive 'continue' without context, check for pending tasks

COMMUNICATION:
- For questions: /mcp__ccmaster__send_message_to_session
- For blockers: Update task status and notify relevant team member
- For completion: Update task status with output details
```

### 4. PM 的任务管理工作流

```python
# 1. 创建任务
/mcp__ccmaster__create_task 
  title="Implement user authentication"
  assigned_to="backend_dev_id"
  priority="high"
  acceptance_criteria=["JWT token generation", "Login endpoint", "Logout endpoint"]

# 2. 监控进度
/mcp__ccmaster__get_all_tasks status="in_progress"

# 3. 处理阻塞
# 如果后端被阻塞，PM可以：
- 重新分配任务
- 创建解除阻塞的新任务
- 协调团队成员解决

# 4. 验证完成
/mcp__ccmaster__get_task_output task_id="task_123"
# PM 可以运行测试验证任务是否真正完成
```

### 5. 防止无限循环的机制

1. **任务必须有明确的完成标准**
   - acceptance_criteria 是必需的
   - 团队成员必须满足所有标准才能标记完成

2. **禁用团队成员的 watch_mode**
   - 团队成员不会自动继续
   - 只有收到新任务时才工作

3. **任务状态机**
   ```
   pending → in_progress → completed
                ↓
             blocked
   ```
   - 完成的任务不能重新开始
   - 阻塞的任务需要 PM 干预

4. **空闲行为定义**
   - 团队成员空闲时只检查新任务
   - 不会主动创建新工作

### 6. 实现步骤

1. **第一阶段：修复当前问题**
   - ✅ 关闭团队成员的 watch_mode
   - ✅ 改进初始 prompt，添加任务完成指导
   - 增加 auto-continue 的智能判断

2. **第二阶段：任务队列系统**
   - 实现基于文件的任务管理
   - 添加新的 MCP 工具
   - 更新 PM 和团队成员的 prompts

3. **第三阶段：高级功能**
   - 任务依赖关系图
   - 自动任务分配建议
   - 项目进度可视化

## 优势

1. **明确的任务边界** - 每个任务都有清晰的完成标准
2. **状态可追踪** - 所有任务状态持久化在文件系统
3. **防止循环** - 任务完成后不会重复执行
4. **更好的协作** - 结构化的任务和消息系统
5. **易于调试** - 所有通信都有文件记录

## 向后兼容

- 保留现有的 send_message_to_session 用于紧急通信
- 任务系统作为主要的工作分配方式
- PM 可以选择使用旧方式或新方式