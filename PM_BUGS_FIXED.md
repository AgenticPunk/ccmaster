# PM模式Bug修复总结

## 1. 任务状态文件夹问题 ✅

### 问题
- 使用多个文件夹（pending/, in_progress/, blocked/, completed/, cancelled/）来区分任务状态
- 文件需要在不同文件夹间移动，增加复杂性和出错风险

### 修复
- 改为单一 `tasks/` 目录
- 任务状态作为JSON文件中的一个字段
- 更新任务状态时直接修改JSON文件，无需移动文件

### 代码改动
```python
# project_communication.py
# 旧代码：创建多个状态子目录
self.tasks_dir / 'pending',
self.tasks_dir / 'in_progress',
# ...

# 新代码：单一目录
self.tasks_dir,  # Single tasks directory

# 更新任务时不再移动文件
self._write_json_atomic(task_file, task_data)  # 直接更新同一文件
```

## 2. 团队创建卡住问题 ✅

### 问题
- MCP工具在初始化时立即创建ProjectCommunication实例
- 此时ccmaster可能还未完全初始化，导致卡住

### 修复
- 改为延迟初始化（lazy initialization）
- 只在第一次需要使用时才初始化ProjectCommunication

### 代码改动
```python
# tools.py
def __init__(self, ccmaster_instance):
    # 旧代码：立即初始化
    # self.project_comm = ProjectCommunication(working_dir)
    
    # 新代码：延迟初始化
    self.project_comm = None
    self._project_comm_initialized = False

def _ensure_project_comm(self):
    """第一次使用时才初始化"""
    if not self._project_comm_initialized:
        self._project_comm_initialized = True
        try:
            self.project_comm = ProjectCommunication(os.getcwd())
```

## 3. PM模式仍使用临时文件 ✅

### 问题
- PM启动时创建临时文件存储prompt
- 与新的项目通信系统不一致

### 修复
- 优先使用项目通信系统保存prompt到 `.ccmaster/prompts/`
- 只在项目通信不可用时才使用临时文件作为后备

### 代码改动
```python
# ccmaster/bin/ccmaster
# 保存PM prompt
if self.project_comm:
    prompt_file_path = self.project_comm.save_initial_prompt(pm_session_id, full_prompt, "Project Manager")
    prompt_file_to_use = str(prompt_file_path)
else:
    # 只作为后备方案
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    prompt_file_to_use = temp_file.name

# AppleScript中使用
do script "cat '{prompt_file_to_use}'" in newTab
```

## 改进后的架构

### 项目通信目录结构
```
project_dir/
├── .ccmaster/
│   ├── tasks/          # 所有任务文件（状态在JSON中）
│   ├── messages/       # 团队消息
│   ├── status/         # 实时状态
│   ├── events/         # 事件通知
│   └── prompts/        # 初始prompts（持久化存储）
```

### 任务文件示例
```json
{
  "id": "task_20250119_143022_abc123",
  "title": "实现登录组件",
  "status": "in_progress",  // 状态直接存储在JSON中
  "assigned_to": "frontend_dev_id",
  "created_at": "2025-01-19T14:30:22Z",
  // ... 其他字段
}
```

## 优势

1. **简化的任务管理** - 单一目录，状态在JSON中，无需文件移动
2. **稳定的初始化** - 延迟加载避免启动时卡住
3. **统一的通信机制** - PM和团队成员都使用项目级通信系统
4. **更好的可追踪性** - 所有prompt和任务都持久化在项目目录

## 测试建议

1. 测试PM模式启动：`ccmaster pm "创建一个电商网站"`
2. 验证 `.ccmaster/` 目录正确创建
3. 检查任务创建和状态更新是否正常
4. 确认团队成员创建不再卡住