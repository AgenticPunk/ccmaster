# PM立即进入Idle状态的Bug修复

## 问题描述
PM读取完prompt后立即停止工作，显示为idle状态，不处理项目需求。

## 根本原因

### 1. 状态初始化错误
```python
# 旧代码
self.current_status[pm_session_id] = 'idle'
self.has_seen_first_prompt[pm_session_id] = True  # 错误：PM还没处理prompt
```

PM被错误地标记为：
- 已经看到第一个prompt（实际上还没处理）
- 状态为idle（应该是processing）

### 2. monitor_status覆盖状态
```python
# 旧代码 - 总是创建idle状态文件
with open(status_file, 'w') as f:
    json.dump({'state': 'idle', 'session_id': session_id}, f)
```

即使我们设置了processing状态，monitor_status也会立即覆盖为idle。

### 3. Prompt文件格式问题
`save_initial_prompt`保存的是JSON文件，但`cat`命令会将整个JSON发送给Claude，而不是只发送prompt文本。

## 修复方案

### 1. 修正PM状态初始化
```python
# 新代码
self.current_status[pm_session_id] = 'processing'  # PM正在处理初始prompt
self.has_seen_first_prompt[pm_session_id] = False  # PM还没处理prompt
```

### 2. 修复monitor_status
```python
# 新代码 - 只在文件不存在时创建，并使用当前状态
if not status_file.exists():
    initial_state = 'idle'
    if isinstance(self.current_status, dict) and session_id in self.current_status:
        initial_state = self.current_status[session_id]
    
    with open(status_file, 'w') as f:
        json.dump({'state': initial_state, 'session_id': session_id}, f)
```

### 3. 保存纯文本prompt文件
```python
# 新代码 - 同时保存JSON和纯文本
json_file = prompts_dir / f"{session_id}_prompt.json"
self._write_json_atomic(json_file, prompt_data)

# 保存纯文本文件供cat命令使用
txt_file = prompts_dir / f"{session_id}_prompt.txt"
txt_file.write_text(prompt, encoding='utf-8')

return txt_file  # 返回txt文件路径
```

## 文件变更

1. **ccmaster/bin/ccmaster**
   - 第2823-2825行：修正PM状态初始化
   - 第1751-1759行：修复monitor_status文件创建逻辑

2. **mcp/project_communication.py**
   - 第316-320行：添加纯文本prompt文件保存

## 测试步骤

1. 启动PM模式：
   ```bash
   ccmaster pm "创建一个电商网站"
   ```

2. 检查PM状态应该是"Processing"而不是立即变为"Idle"

3. 验证prompt文件：
   ```bash
   ls .ccmaster/prompts/
   # 应该看到 .json 和 .txt 两个文件
   ```

4. 确认PM能正确处理项目需求并创建团队

## 预期行为

- PM启动后显示为"Processing"状态
- PM读取并处理项目描述
- PM使用MCP工具创建团队成员
- 只有在真正空闲时才显示"Idle"状态