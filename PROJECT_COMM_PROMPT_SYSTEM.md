# 项目级初始Prompt传递系统

## 概述

PM模式和团队成员的初始prompt现在通过项目目录下的`.ccmaster/prompts/`文件夹传递，而不是临时文件。这样更可靠，也方便调试和追踪。

## 工作流程

### 1. PM启动时
```python
# PM模式启动时创建项目通信系统
self.project_comm = ProjectCommunication(working_dir)

# 保存PM的初始prompt
prompt_file_path = self.project_comm.save_initial_prompt(pm_session_id, full_prompt, "Project Manager")
```

### 2. 创建团队成员时
```python
# MCP工具create_session保存初始prompt
if initial_prompt and self.project_comm:
    prompt_file = self.project_comm.save_initial_prompt(session_id, initial_prompt, role)
    self.ccmaster.cli_log(f"Saved initial prompt for {role} to project .ccmaster/")
```

### 3. Prompt文件格式
```json
{
  "session_id": "mcp_20250119_143022_abc123",
  "role": "Frontend Developer",
  "prompt": "You are a Frontend Developer...",
  "created_at": "2025-01-19T14:30:22.123456",
  "consumed": false,
  "consumed_at": null
}
```

## 文件结构
```
project_dir/
├── .ccmaster/
│   ├── prompts/               # 初始prompts存储
│   │   ├── pm_session_id_prompt.json
│   │   ├── mcp_20250119_143022_prompt.json
│   │   └── mcp_20250119_143025_prompt.json
│   ├── tasks/                 # 任务管理
│   ├── messages/              # 团队消息
│   ├── status/                # 实时状态
│   └── events/                # 事件通知
```

## 优势

1. **持久化存储** - Prompt保存在项目目录，不会丢失
2. **可追踪** - 可以查看每个团队成员收到的初始指令
3. **防止重复消费** - 标记`consumed`防止prompt被多次使用
4. **便于调试** - 可以直接查看JSON文件了解问题
5. **支持大型prompt** - 不受临时文件10秒清理限制

## 兼容性

- 如果项目通信系统不可用，仍然使用临时文件作为后备方案
- 旧版本的CCMaster仍然可以正常工作

## 使用示例

### PM创建团队成员
```bash
/mcp__ccmaster__create_session 
  working_dir="." 
  watch_mode=false 
  role="Backend Developer" 
  initial_prompt="You are a Backend Developer specializing in Node.js..."
```

初始prompt会被保存到：
`.ccmaster/prompts/mcp_20250119_143022_abc123_prompt.json`

### 团队成员获取初始prompt
```python
# 团队成员启动时可以调用
prompt_data = project_comm.get_initial_prompt(session_id)
if prompt_data:
    initial_prompt = prompt_data['prompt']
    # 使用prompt...
```

## 注意事项

1. `.ccmaster/`目录应该添加到`.gitignore`，避免提交到版本控制
2. Prompt文件在被消费后会标记为`consumed`，但不会删除，方便审计
3. 项目通信系统在第一次使用时会自动创建必要的目录结构

这个新系统让PM模式的团队协作更加可靠和透明。