# REQ-003: 跨平台支持需求

## 中文需求描述

### 需求概述
CCMaster当前仅支持macOS平台，限制了用户群体的扩展。需要实现对Windows和Linux平台的全面支持，确保所有主要功能在三大操作系统上都能正常运行，同时保持一致的用户体验。

### 具体需求

#### 1. Windows平台支持
**需求描述：**
- 适配Windows 10及以上版本的操作系统
- 支持Windows Terminal、PowerShell、CMD等主流终端
- 实现Windows特有的进程管理和系统调用
- 处理Windows路径格式和权限系统

**验收标准：**
- 在Windows 10/11上正常安装和运行
- 支持PowerShell Core和Windows PowerShell
- 支持Windows Terminal和传统CMD
- 正确处理Windows路径分隔符和驱动器号
- 通过Windows Defender等安全软件检测

#### 2. Linux平台支持
**需求描述：**
- 支持主流Linux发行版（Ubuntu、CentOS、Debian、Arch等）
- 适配各种终端模拟器（GNOME Terminal、KDE Konsole、Alacritty等）
- 实现Linux特有的进程管理和信号处理
- 支持不同的包管理器和安装方式

**验收标准：**
- 在Ubuntu 18.04+、CentOS 7+、Debian 10+上运行
- 支持主流桌面环境的终端
- 提供deb、rpm等格式的安装包
- 正确处理Linux文件权限和路径
- 支持SSH远程终端操作

#### 3. 平台抽象层设计
**需求描述：**
- 设计统一的平台抽象接口
- 将平台特定代码模块化，便于维护
- 确保核心逻辑在所有平台上保持一致
- 提供平台特定的优化和增强功能

**验收标准：**
- 90%以上的代码在所有平台共享
- 平台特定代码清晰分离并模块化
- 核心功能在所有平台表现一致
- 每个平台都有特定的性能优化

#### 4. 终端兼容性
**需求描述：**
- 适配不同操作系统的终端特性和限制
- 处理终端颜色、字体、编码等差异
- 支持不同的键盘输入和快捷键系统
- 实现跨平台的鼠标和触控支持

**验收标准：**
- 在20+种常用终端中正常显示
- 自动检测和适配终端能力
- 提供终端兼容性配置选项
- 优雅降级到基本功能

#### 5. 安装和分发优化
**需求描述：**
- 为每个平台提供原生的安装体验
- 支持包管理器安装（Homebrew、chocolatey、APT等）
- 提供便携版本，无需安装即可使用
- 实现自动更新机制的跨平台支持

**验收标准：**
- macOS：Homebrew、pkg安装包
- Windows：chocolatey、msi安装包、便携版
- Linux：APT、YUM、Snap、AppImage
- 所有平台支持自动更新检测

### 优先级：高
### 预计工期：10-12周
### 依赖关系：需要完成架构重构设计

---

## English Development Prompts

### Prompt 1: Windows Platform Support Implementation

```
I need to implement full Windows platform support for CCMaster, which currently only works on macOS.

Requirements:
1. Create Windows-specific terminal control:
   - Replace AppleScript-based terminal control with Windows-compatible solutions
   - Support Windows Terminal, PowerShell, and Command Prompt
   - Implement Windows API calls for terminal manipulation
   - Handle Windows-specific keyboard input and shortcuts

2. Windows process management:
   - Adapt process detection for Windows process model
   - Handle Windows service and background process detection
   - Implement Windows-specific process monitoring
   - Support Windows process security and permissions

3. Windows path and file system handling:
   - Handle Windows path separators (\\ vs /)
   - Support Windows drive letters and UNC paths
   - Manage Windows file permissions and security
   - Handle Windows-specific file locking behavior

4. Windows Terminal integration:
   - Support Windows Terminal's advanced features
   - Implement ANSI color code compatibility
   - Handle Windows Terminal tabs and panes
   - Support Windows Terminal's JSON configuration

Current macOS-specific code to replace:
- AppleScript execution in `send_prompt_to_terminal` method (lines 297-349)
- Terminal window management using osascript
- macOS-specific process detection patterns
- File path handling assuming Unix-style paths

Please implement a Windows-compatible version that maintains feature parity with the macOS version while leveraging Windows-specific capabilities where beneficial.

Libraries to consider:
- pywin32 for Windows API access
- winreg for Windows registry access
- subprocess with Windows-specific parameters
- ctypes for low-level Windows API calls
```

### Prompt 2: Linux Platform Support Implementation

```
I need to implement comprehensive Linux platform support for CCMaster with compatibility across multiple distributions and desktop environments.

Requirements:
1. Linux terminal integration:
   - Support major terminal emulators (GNOME Terminal, Konsole, Alacritty, etc.)
   - Implement terminal control using D-Bus, window manager APIs, or other methods
   - Handle different shell environments (bash, zsh, fish)
   - Support both X11 and Wayland display servers

2. Linux process management:
   - Implement Linux-specific process detection and monitoring
   - Handle process signals (SIGTERM, SIGKILL, SIGUSR1, etc.)
   - Support systemd process management integration
   - Handle container environments (Docker, LXC)

3. Distribution-specific adaptations:
   - Ubuntu/Debian: APT package management integration
   - CentOS/RHEL: YUM/DNF package management
   - Arch Linux: pacman integration
   - Generic Linux: universal binary support

4. Desktop environment integration:
   - GNOME: integration with GNOME Shell and settings
   - KDE: integration with KDE Plasma and KConfig
   - XFCE, MATE: lightweight desktop support
   - Headless/server: full functionality without GUI

5. Linux-specific features:
   - SSH remote session support
   - Terminal multiplexer integration (tmux, screen)
   - Container awareness and support
   - Service/daemon mode for server environments

Current limitations to address:
- No Linux terminal control mechanism
- Process detection assumes specific patterns
- File system operations need Linux permission handling
- No package management or installation support

Please implement a robust Linux support layer that works across distributions while providing optimized experiences for popular environments.

Consider using:
- python-dbus for desktop integration
- psutil for cross-platform process management
- distro library for distribution detection
- subprocess with Linux-specific options
```

### Prompt 3: Platform Abstraction Layer Design

```
I need to create a comprehensive platform abstraction layer that allows CCMaster to run consistently across macOS, Windows, and Linux while leveraging platform-specific capabilities.

Requirements:
1. Design platform abstraction interfaces:
   - Terminal control abstraction
   - Process management abstraction  
   - File system operations abstraction
   - System integration abstraction

2. Create platform-specific implementations:
   - MacOSPlatform class with AppleScript integration
   - WindowsPlatform class with Windows API integration
   - LinuxPlatform class with D-Bus and shell integration
   - Common base class with shared functionality

3. Implement feature detection and capabilities:
   - Runtime detection of platform capabilities
   - Graceful degradation for unsupported features
   - Platform-specific optimization opportunities
   - Capability-based feature enablement

4. Configuration and settings abstraction:
   - Platform-appropriate configuration storage
   - Cross-platform configuration migration
   - Platform-specific default settings
   - Environment variable handling

5. Error handling and diagnostics:
   - Platform-specific error codes and messages
   - Diagnostic information collection per platform
   - Platform-appropriate troubleshooting guides
   - Debug information formatting

Architecture design:
```python
class PlatformInterface(ABC):
    @abstractmethod
    def send_command_to_terminal(self, window_id: str, command: str) -> bool:
        pass
    
    @abstractmethod
    def find_claude_process(self) -> Optional[int]:
        pass
    
    @abstractmethod
    def create_new_terminal_session(self, working_dir: str) -> str:
        pass

class PlatformManager:
    def __init__(self):
        self.platform = self._detect_platform()
    
    def _detect_platform(self) -> PlatformInterface:
        # Auto-detect and instantiate appropriate platform
        pass
```

Current code to refactor:
- All AppleScript code in ccmaster/bin/ccmaster
- Process detection in find_claude_pid method
- Terminal control in send_prompt_to_terminal method
- File path operations throughout the codebase

Please create a clean, extensible platform abstraction that makes it easy to add new platform support in the future.
```

### Prompt 4: Terminal Compatibility Framework

```
I need to implement a robust terminal compatibility framework that handles the diverse landscape of terminal emulators across different platforms.

Requirements:
1. Terminal capability detection:
   - Automatic detection of terminal features (color, mouse, Unicode)
   - Terminal identification and version detection
   - Feature fallback chains for unsupported capabilities
   - Performance profiling for different terminals

2. Cross-platform terminal control:
   - Unified interface for terminal manipulation
   - Platform-specific optimization paths
   - Consistent behavior across terminal types
   - Error recovery for failed terminal operations

3. Input/output standardization:
   - Cross-platform keyboard input handling
   - Mouse input abstraction where supported
   - Clipboard integration per platform
   - Text encoding and Unicode support

4. Visual compatibility:
   - Color scheme adaptation for different terminals
   - Font and character set compatibility
   - Layout adaptation for various terminal sizes
   - Accessibility features (high contrast, large text)

5. Terminal-specific optimizations:
   - iTerm2: image display, notification integration
   - Windows Terminal: modern features, theming
   - GNOME Terminal: D-Bus integration, profile support
   - VS Code Terminal: extension integration

Implementation approach:
```python
class TerminalCapabilities:
    def __init__(self):
        self.colors = self._detect_color_support()
        self.mouse = self._detect_mouse_support()
        self.unicode = self._detect_unicode_support()
        self.size = self._get_terminal_size()

class TerminalController:
    def __init__(self, capabilities: TerminalCapabilities):
        self.caps = capabilities
        self.renderer = self._create_renderer()
    
    def render_status(self, status: Status):
        # Render based on terminal capabilities
        pass
```

Current terminal handling:
- Basic ANSI color codes in Colors class
- Simple terminal size assumptions
- No terminal-specific optimizations
- Limited input handling (single character)

Please create a comprehensive terminal compatibility system that provides the best possible experience on each terminal while maintaining consistent core functionality.
```

### Prompt 5: Cross-Platform Installation and Distribution

```
I need to implement a comprehensive cross-platform installation and distribution system for CCMaster.

Requirements:
1. Platform-native package formats:
   - macOS: .pkg installer, Homebrew formula, Mac App Store (future)
   - Windows: .msi installer, Chocolatey package, Microsoft Store (future)
   - Linux: .deb, .rpm, Snap, AppImage, Flatpak

2. Package manager integration:
   - Homebrew (macOS): automatic dependency management
   - Chocolatey (Windows): Windows package management
   - APT (Debian/Ubuntu): native package management
   - YUM/DNF (RedHat/CentOS): enterprise Linux support
   - Snap/Flatpak: universal Linux packages

3. Portable and standalone versions:
   - Self-contained executables with embedded Python
   - No-install versions for restricted environments
   - USB/portable drive compatibility
   - Enterprise deployment packages

4. Auto-update system:
   - Cross-platform update detection and downloading
   - Differential updates to minimize bandwidth
   - Rollback capability for failed updates
   - Enterprise update control and approval workflows

5. Installation configuration:
   - Custom installation paths and options
   - Silent/unattended installation modes
   - Enterprise deployment scripts
   - Configuration import/export during installation

Build and distribution pipeline:
- GitHub Actions for automated building
- Multiple architecture support (x64, ARM64)
- Code signing for security (Windows Authenticode, macOS Notarization)
- Automated testing on multiple platforms

Current limitations:
- Only setup.sh script for macOS installation
- No automated building or packaging
- No update mechanism
- Manual dependency management

Please implement a professional-grade installation and distribution system that makes CCMaster easy to install and maintain across all supported platforms.

Consider using:
- PyInstaller or cx_Freeze for executable creation
- GitHub Actions for CI/CD pipeline
- Platform-specific signing tools
- Package manager APIs for automated publishing
```