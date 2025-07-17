# CCMaster - Claude Code 会话管理器

CCMaster 是一个为 Claude Code 设计的智能会话管理工具。它能自动启动新的终端窗口，实时监控 Claude 的工作状态，并在监视模式下提供自动续写功能，让长对话更加流畅高效。

## ✨ 核心功能

- 🚀 **一键启动**：自动打开终端并启动 Claude Code 会话
- 📊 **实时状态监控**：显示 Claude 的工作状态（空闲/处理中/工作中）
- 🔧 **工具活动跟踪**：显示 Claude 当前正在使用的工具
- 👁️ **监视模式**：当 Claude 空闲时自动发送 "continue" 命令
- 🎯 **会话级钩子**：每个会话都有独立的钩子配置，更好的控制
- 📝 **会话历史**：查看任何会话的所有提示词和详细日志
- 🎨 **美观的输出**：彩色编码的状态指示器，便于阅读
- ⌨️ **交互式控制**：在任何会话中按 [w] 键切换监视模式
- 🔢 **轮次限制**：使用 --maxturn 设置最大自动续写次数

## 🛠 安装

### 系统要求

- macOS（使用 AppleScript 进行终端自动化）
- Python 3.6+
- 已安装并配置好 Claude Code CLI

### 快速安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/ccmaster.git
cd ccmaster

# 运行安装脚本
./setup.sh

# 或者使用 sudo（如果需要）
sudo ./setup.sh
```

## 📖 使用方法

### 基本命令

```bash
# 在当前目录启动新的 Claude 会话
ccmaster

# 在指定目录启动新会话
ccmaster start -d /path/to/project

# 在当前目录以监视模式启动（自动续写）
ccmaster watch

# 在指定目录以监视模式启动
ccmaster watch -d /path/to/project

# 以监视模式启动，最多自动续写 100 次
ccmaster watch --maxturn 100

# 列出所有会话
ccmaster list

# 查看会话日志
ccmaster logs 20240124_143022

# 查看会话的用户提示词
ccmaster prompts 20240124_143022
```

### 交互式控制

在会话期间，您可以使用键盘快捷键：
- **[w]** - 开启/关闭监视模式
  - 当达到最大轮次时，按 [w] 会重置计数器并立即续写

### 监视模式功能

监视模式会在 Claude 完成响应后变为空闲时自动发送 "continue" 命令：

```bash
# 基础监视模式 - 无限制自动续写
ccmaster watch

# 限制监视模式 - 50 轮后停止
ccmaster watch --maxturn 50
```

当达到轮次限制时：
- 监视模式自动关闭
- 按 [w] 重置计数器并恢复自动续写
- 如果 Claude 处于空闲状态，会立即发送 continue 命令

### 输出示例

```
🚀 正在 /Users/yourname/project 启动 Claude 会话
📍 会话 ID: 20240124_143022
👁️  监视模式：开启 - 空闲后将自动续写（最多 10 轮）

[14:30:22] ● 处理中
[14:30:23] ▶ 用户："创建一个 Python 网络服务器"
[14:30:24] ● 工作中
[14:30:24] → 使用 Write
[14:30:25] → 使用 Edit
[14:30:28] ● 空闲
[14:30:29] ▶ 自动续写 (1/10)
[14:30:30] ● 处理中
...
[14:35:45] 🛑 已达到最大自动续写轮次 (10) - 监视模式已禁用
[14:35:45] 💡 按 [w] 重新启用并继续
```

## 🏗 架构设计

CCMaster 使用基于钩子的架构来监控 Claude Code：

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CCMaster  │────▶│ Claude Code  │────▶│    钩子     │
│    监控器   │     │     会话     │     │ (会话级别)  │
└─────────────┘     └──────────────┘     └─────────────┘
       ▲                                          │
       │                                          │
       └──────────────────────────────────────────┘
                      状态更新
```

### 核心组件

1. **会话管理器** (`ccmaster/bin/ccmaster`)
   - 主要协调器，采用简化可靠的设计
   - 通过 AppleScript 简单启动终端
   - 使用基础进程检测的健壮监控
   - 智能的自动续写和多级回退方法

2. **钩子系统** (`ccmaster/hooks/`)
   - `pre_tool_use.py` - 跟踪工具使用情况
   - `user_prompt_submit.py` - 捕获用户提示词
   - `stop_hook.py` - 检测 Claude 何时完成响应
   - 每个会话都有独立的钩子配置

3. **监控系统**
   - 简单的进程检测（无复杂的 PID 跟踪）
   - 容错的会话监控（5 次失败后才声明结束）
   - 实时状态文件位于 `~/.ccmaster/status/`
   - 会话日志位于 `~/.ccmaster/logs/`
   - 用户提示词保存在单独的日志文件中

4. **自动续写系统**
   - 直接检测运行 Claude 的终端标签页
   - 多级回退（查找 Claude 标签页 → 最前面的终端）
   - 清晰的成功/失败反馈
   - 不依赖窗口焦点或精确时机

## 🔧 配置

配置文件位置：`~/.ccmaster/config.json`

```json
{
  "claude_code_command": "claude",
  "monitor_interval": 0.5
}
```

注意：CCMaster 默认始终使用当前工作目录来启动会话。

## 📁 文件结构

```
~/.ccmaster/
├── config.json          # 全局配置
├── sessions.json        # 会话元数据
├── status/              # 实时状态文件
│   └── SESSION_ID.json
└── logs/                # 会话日志
    ├── SESSION_ID.log
    └── SESSION_ID_prompts.log
```

## 🐛 故障排除

### 会话立即结束
现在通过简化的方法更加可靠：
- CCMaster 等待 3 秒钟让 Claude 启动
- 需要连续 5 次失败（10 秒）才会声明会话结束
- 使用简单的进程检测而非复杂的 PID 跟踪

### 自动续写不工作
- 确保您处于监视模式（绿色的"监视模式：开启"消息）
- 检查 Claude 是否已完成响应（显示"空闲"状态）
- CCMaster 会在自动续写失败时显示清晰的错误消息
- 如果主要方法失败，会尝试发送到最前面的终端

### 无法切换监视模式
- 确保 ccmaster 窗口具有焦点
- [w] 键只在 ccmaster 监控窗口中有效
- 监视模式切换独立于终端焦点工作

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。