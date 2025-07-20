# 团队通信系统修复总结

## 问题描述
- PM的prompt传递已经修复，但团队成员（非PM的ClaudeCode实例）仍在使用临时文件
- 所有的消息传递都应该通过项目级的`.ccmaster/`目录进行

## 修复内容

### 1. 修改 `send_continue_to_claude` 函数

**旧代码**：
```python
# 总是使用临时文件
temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
temp_file.write(message)
temp_file.close()
```

**新代码**：
```python
# 优先使用项目通信系统
if self.project_comm:
    try:
        message_file_path = self.project_comm.save_initial_prompt(
            f"{session_id}_msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            message,
            "Message"
        )
        message_file_to_use = str(message_file_path)
        use_project_comm = True
    except Exception as e:
        self.logger.warning(f"Failed to save message to project comm: {e}")

# 只在项目通信不可用时才使用临时文件
if not message_file_to_use:
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(message)
    temp_file.close()
    message_file_to_use = temp_file.name
```

### 2. 确保所有会话模式都初始化项目通信

在以下函数中添加了项目通信初始化：
- `start_session_and_monitor` - 单会话模式
- `start_multi_session_and_monitor` - 多会话模式
- `start_pm_mode` - PM模式（已有）

```python
# 初始化项目通信系统
if HAS_PROJECT_COMM and not self.project_comm:
    try:
        self.project_comm = ProjectCommunication(working_dir)
        self.cli_log("Initialized project communication in .ccmaster/", log_type='info', color=Colors.GREEN)
    except Exception as e:
        self.cli_log(f"Could not initialize project communication: {e}", log_type='warning')
```

### 3. 文件清理逻辑更新

- 项目通信系统的文件是持久化的，不会被清理
- 只有临时文件才会在10秒后被清理

```python
# 只在使用临时文件时才清理
if not use_project_comm and message_file_to_use:
    def cleanup_temp():
        time.sleep(10)
        try:
            os.unlink(message_file_to_use)
        except:
            pass
    threading.Thread(target=cleanup_temp, daemon=True).start()
```

## 通信文件结构

现在所有的团队通信都通过项目目录下的`.ccmaster/`进行：

```
project_dir/
├── .ccmaster/
│   ├── prompts/               # 初始prompts和消息
│   │   ├── pm_session_prompt.txt           # PM的初始prompt
│   │   ├── pm_session_prompt.json          # PM的元数据
│   │   ├── mcp_xxx_prompt.txt              # 团队成员的初始prompt
│   │   ├── mcp_xxx_prompt.json             # 团队成员的元数据
│   │   ├── session_msg_20250119_xxx.txt    # 发送给团队成员的消息
│   │   └── session_msg_20250119_xxx.json   # 消息元数据
│   ├── tasks/                 # 任务管理
│   ├── messages/              # 团队消息（未来可用于更复杂的消息系统）
│   ├── status/                # 实时状态
│   └── events/                # 事件通知
```

## 优势

1. **统一的通信机制** - PM和团队成员都使用相同的项目级通信系统
2. **持久化存储** - 所有通信记录都保存在项目目录，便于调试和审计
3. **避免临时文件问题** - 不再依赖可能被过早清理的临时文件
4. **更好的可追踪性** - 可以查看所有发送给团队成员的消息历史

## 测试步骤

1. 启动PM模式或普通会话：
   ```bash
   ccmaster pm "创建一个电商网站"
   # 或
   ccmaster watch
   ```

2. 检查`.ccmaster/`目录是否创建：
   ```bash
   ls -la .ccmaster/
   ```

3. 当PM发送消息给团队成员时，检查prompts目录：
   ```bash
   ls -la .ccmaster/prompts/
   # 应该看到 session_msg_*.txt 文件
   ```

4. 验证消息内容：
   ```bash
   cat .ccmaster/prompts/session_msg_*.txt
   ```

## 向后兼容

- 如果项目通信系统初始化失败，仍会回退到临时文件
- 错误会记录在日志中，但不会中断正常操作
- 临时文件仍会在10秒后被清理

现在整个团队的通信都通过`.ccmaster/`目录进行，实现了真正的项目级协作。