# CCMaster - Claude Code 会话管理器

一个能够启动 Claude Code 会话并实时监控其活动状态的命令行工具。

## 功能特性

- **自动启动终端**：在新的终端窗口中打开 Claude Code
- **实时状态监控**：显示彩色状态指示器：
  - 🟡 **Processing**（黄色）- 正在处理您的提示词
  - 🟢 **Working**（绿色）- Claude 正在使用工具
  - 🔴 **Idle**（红色）- Claude 已完成所有任务
- **工具活动跟踪**：显示 Claude 使用的每个工具及其开始/完成标记
- **会话管理**：使用唯一 ID 跟踪所有 Claude 会话
- **简洁输出**：每次交互只显示一条空闲消息，展示必要信息
- **持久化日志**：记录所有活动以供后续查看

## 安装

1. 克隆或下载此仓库
2. 运行安装脚本：
   ```bash
   ./setup.sh
   ```
3. 如果无法写入 `/usr/local/bin`，请将 ccmaster bin 目录添加到 PATH：
   ```bash
   export PATH="/path/to/ccmaster/ccmaster/bin:$PATH"
   ```

## 使用方法

### 启动新会话（默认命令）
```bash
# 在当前目录启动
ccmaster

# 在指定目录启动
ccmaster start -d /path/to/project
```

运行 ccmaster 时，它会：
1. 打开一个新的终端窗口运行 Claude
2. 显示实时状态更新
3. 持续监控直到 Claude 会话结束

示例输出：
```
🚀 Starting Claude session in /Users/liuyuantao
📍 Session ID: 20250718_021539

[02:15:43] ● Processing
[02:15:44] → Using Read
[02:15:45] ✓ Completed Read
[02:15:46] → Using Edit
[02:15:47] ✓ Completed Edit
[02:15:48] ● Idle
```

按 `Ctrl+C` 停止监控（Claude 继续运行）。

### 列出所有会话
```bash
ccmaster list
```

显示所有会话及其状态、PID 和工作目录。

### 查看会话日志
```bash
ccmaster logs SESSION_ID
```

显示特定会话的完整活动日志。

## 工作原理

1. **钩子集成**：CCMaster 配置 Claude 的钩子来跟踪：
   - `PreToolUse`：检测 Claude 开始使用工具的时机
   - `UserPromptSubmit`：检测您提交提示词的时机

2. **状态跟踪**：每个会话在 `~/.ccmaster/status/` 中都有自己的状态文件

3. **智能空闲检测**：通过以下方式确保每次交互只显示一条空闲消息：
   - 跟踪对话周期
   - 在无活动 2 秒后自动检测空闲状态
   - 防止重复的空闲通知

4. **会话隔离**：每个会话独立运行，拥有自己的：
   - 状态文件
   - 日志文件
   - 进程监控

## 配置

配置存储在 `~/.ccmaster/config.json`：
```json
{
  "claude_code_command": "claude",
  "default_working_dir": "/Users/username",
  "monitor_interval": 0.5
}
```

## 文件结构

```
~/.ccmaster/
├── config.json          # 全局配置
├── sessions.json        # 会话注册表
├── status/             # 会话状态文件
│   └── SESSION_ID.json
└── logs/               # 会话日志
    └── SESSION_ID.log
```

## 故障排除

- **命令未找到**：确保 ccmaster 在您的 PATH 中
- **无状态更新**：检查 Claude 的设置是否允许钩子
- **多个空闲消息**：更新到最新版本

## 系统要求

- macOS（使用 AppleScript 控制终端）
- Python 3.6+
- 已安装 Claude Code CLI 并可通过 `claude` 命令访问