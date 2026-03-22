# 需求文档：Electron 桌面应用

## 简介

将量数风行 Web 应用封装成 Electron 桌面应用，提供原生桌面体验。应用将内置 Python 后端服务，实现一键启动，支持 Windows、macOS、Linux 三个平台，并提供自动更新、系统托盘、桌面通知等原生功能。

## 术语表

- **Main_Process**: Electron 主进程，负责窗口管理、系统集成和后端服务启动
- **Renderer_Process**: Electron 渲染进程，运行 React Web 应用
- **Backend_Service**: FastAPI Python 后端服务
- **System_Tray**: 操作系统任务栏通知区域的图标
- **IPC**: 进程间通信（Inter-Process Communication）
- **Installer**: 应用安装包（.exe/.dmg/.AppImage）
- **Auto_Updater**: 自动更新模块
- **Native_Notification**: 操作系统原生通知

## 需求

### 需求 1：Electron 应用架构

**用户故事：** 作为开发者，我希望建立 Electron 应用架构，以便将现有 Web 应用封装成桌面应用。

#### 验收标准

1. THE Main_Process SHALL 创建应用主窗口并加载 React 应用
2. THE Main_Process SHALL 配置窗口属性（尺寸、最小尺寸、图标）
3. WHEN 应用启动时，THE Main_Process SHALL 初始化 IPC 通信通道
4. THE Renderer_Process SHALL 通过 preload 脚本安全访问 Node.js API
5. WHEN 用户关闭窗口时，THE Main_Process SHALL 根据配置决定退出或最小化到托盘

### 需求 2：内置 Python 后端服务

**用户故事：** 作为用户，我希望应用自动启动后端服务，以便无需手动启动前后端。

#### 验收标准

1. WHEN 应用启动时，THE Main_Process SHALL 启动 Backend_Service 子进程
2. THE Main_Process SHALL 检测后端服务端口可用性并等待服务就绪
3. WHEN Backend_Service 启动失败时，THE Main_Process SHALL 显示错误对话框并提供重试选项
4. WHEN 应用退出时，THE Main_Process SHALL 优雅关闭 Backend_Service 子进程
5. THE Main_Process SHALL 捕获后端服务日志并写入本地日志文件
6. WHEN Backend_Service 意外崩溃时，THE Main_Process SHALL 自动重启服务并通知用户

### 需求 3：跨平台打包

**用户故事：** 作为用户，我希望在不同操作系统上安装应用，以便在我的设备上使用。

#### 验收标准

1. THE 构建系统 SHALL 生成 Windows 平台的 .exe 安装包
2. THE 构建系统 SHALL 生成 macOS 平台的 .dmg 安装包
3. THE 构建系统 SHALL 生成 Linux 平台的 .AppImage 安装包
4. THE Installer SHALL 包含所有必需的依赖（Python 运行时、后端代码、前端资源）
5. WHEN 用户安装应用时，THE Installer SHALL 创建桌面快捷方式和开始菜单项
6. THE Installer SHALL 设置正确的文件关联和应用图标

### 需求 4：系统托盘集成

**用户故事：** 作为用户，我希望应用可以最小化到系统托盘，以便保持后台运行而不占用任务栏空间。

#### 验收标准

1. WHEN 应用启动时，THE Main_Process SHALL 创建 System_Tray 图标
2. WHEN 用户点击托盘图标时，THE Main_Process SHALL 显示或隐藏主窗口
3. WHEN 用户右键点击托盘图标时，THE Main_Process SHALL 显示上下文菜单（显示/隐藏、退出）
4. WHEN 用户关闭主窗口时，THE Main_Process SHALL 最小化到托盘而不退出应用
5. THE System_Tray SHALL 显示应用图标和工具提示文本

### 需求 5：桌面通知

**用户故事：** 作为用户，我希望接收桌面通知，以便及时了解价格预警和风险提醒。

#### 验收标准

1. WHEN 后端触发通知事件时，THE Main_Process SHALL 显示 Native_Notification
2. THE Native_Notification SHALL 包含标题、内容和图标
3. WHEN 用户点击通知时，THE Main_Process SHALL 显示主窗口并导航到相关页面
4. THE Main_Process SHALL 请求操作系统通知权限
5. WHEN 通知权限被拒绝时，THE Main_Process SHALL 在应用内显示提示

### 需求 6：自动更新

**用户故事：** 作为用户，我希望应用自动检查和安装更新，以便始终使用最新版本。

#### 验收标准

1. WHEN 应用启动时，THE Auto_Updater SHALL 检查可用更新
2. WHEN 发现新版本时，THE Auto_Updater SHALL 显示更新对话框
3. WHEN 用户确认更新时，THE Auto_Updater SHALL 下载并安装更新包
4. THE Auto_Updater SHALL 显示下载进度
5. WHEN 更新下载完成时，THE Auto_Updater SHALL 提示用户重启应用
6. THE Auto_Updater SHALL 支持静默更新（后台下载，下次启动时安装）

### 需求 7：窗口管理

**用户故事：** 作为用户，我希望应用记住窗口状态，以便下次启动时恢复上次的窗口位置和大小。

#### 验收标准

1. WHEN 用户调整窗口大小或位置时，THE Main_Process SHALL 保存窗口状态到本地存储
2. WHEN 应用启动时，THE Main_Process SHALL 恢复上次保存的窗口状态
3. THE Main_Process SHALL 支持全屏模式切换
4. THE Main_Process SHALL 支持最小化、最大化操作
5. WHEN 窗口状态无效时（如屏幕分辨率改变），THE Main_Process SHALL 使用默认窗口状态

### 需求 8：快捷键支持

**用户故事：** 作为用户，我希望使用快捷键操作应用，以便提高使用效率。

#### 验收标准

1. THE Main_Process SHALL 注册全局快捷键（显示/隐藏窗口）
2. THE Main_Process SHALL 注册应用内快捷键（刷新、开发者工具、全屏）
3. WHEN 用户按下快捷键时，THE Main_Process SHALL 执行对应操作
4. THE Main_Process SHALL 在菜单中显示快捷键提示
5. WHEN 快捷键冲突时，THE Main_Process SHALL 使用备用快捷键

### 需求 9：本地数据存储

**用户故事：** 作为用户，我希望应用缓存数据到本地，以便离线访问和提高加载速度。

#### 验收标准

1. THE Main_Process SHALL 提供本地数据存储路径（用户数据目录）
2. THE Backend_Service SHALL 使用本地 SQLite 数据库存储持久化数据
3. THE Renderer_Process SHALL 使用 localStorage 和 IndexedDB 缓存前端数据
4. WHEN 网络不可用时，THE 应用 SHALL 从本地缓存加载数据
5. THE 应用 SHALL 定期清理过期缓存数据

### 需求 10：应用菜单

**用户故事：** 作为用户，我希望通过应用菜单访问常用功能，以便快速操作。

#### 验收标准

1. THE Main_Process SHALL 创建原生应用菜单（文件、编辑、视图、窗口、帮助）
2. THE 应用菜单 SHALL 包含常用操作（刷新、设置、关于、退出）
3. WHEN 用户点击菜单项时，THE Main_Process SHALL 执行对应操作或发送 IPC 消息
4. THE 应用菜单 SHALL 根据平台自动适配（macOS 应用菜单在顶部）
5. THE 应用菜单 SHALL 支持多语言（中文/英文）

### 需求 11：开发者工具

**用户故事：** 作为开发者，我希望在开发模式下访问调试工具，以便排查问题。

#### 验收标准

1. WHEN 应用以开发模式启动时，THE Main_Process SHALL 自动打开开发者工具
2. THE Main_Process SHALL 提供快捷键打开/关闭开发者工具
3. THE Main_Process SHALL 在开发模式下启用热重载
4. THE Main_Process SHALL 在开发模式下显示详细日志
5. WHEN 应用以生产模式启动时，THE Main_Process SHALL 禁用开发者工具访问

### 需求 12：错误处理和日志

**用户故事：** 作为开发者，我希望应用记录错误和日志，以便排查问题和改进应用。

#### 验收标准

1. THE Main_Process SHALL 捕获未处理的异常并记录到日志文件
2. THE Main_Process SHALL 捕获渲染进程崩溃并尝试重启
3. THE 应用 SHALL 将日志文件存储在用户数据目录
4. THE 日志系统 SHALL 记录不同级别的日志（info、warn、error）
5. THE 日志系统 SHALL 自动轮转日志文件（按大小或日期）
6. WHEN 发生严重错误时，THE Main_Process SHALL 显示错误对话框并提供日志路径

### 需求 13：性能优化

**用户故事：** 作为用户，我希望应用启动快速且运行流畅，以便获得良好的使用体验。

#### 验收标准

1. THE Main_Process SHALL 在 3 秒内显示主窗口
2. THE Backend_Service SHALL 在 5 秒内完成启动
3. THE 应用 SHALL 使用代码分割和懒加载优化前端资源
4. THE 应用 SHALL 限制内存使用（主进程 < 200MB，渲染进程 < 500MB）
5. THE 应用 SHALL 使用 V8 快照加速启动

### 需求 14：安全性

**用户故事：** 作为用户，我希望应用保护我的数据安全，以便放心使用。

#### 验收标准

1. THE Main_Process SHALL 启用上下文隔离（contextIsolation）
2. THE Main_Process SHALL 禁用 Node.js 集成在渲染进程中
3. THE Main_Process SHALL 使用 preload 脚本暴露安全的 API
4. THE 应用 SHALL 验证所有 IPC 消息来源
5. THE Backend_Service SHALL 仅监听本地回环地址（127.0.0.1）
6. THE 应用 SHALL 加密存储敏感数据（API 密钥、用户凭证）

### 需求 15：功能完整性

**用户故事：** 作为用户，我希望桌面应用保留所有 Web 应用功能，以便无缝迁移。

#### 验收标准

1. THE 桌面应用 SHALL 支持市场洞察功能（股票数据、AI 分析）
2. THE 桌面应用 SHALL 支持风险分析功能（投资组合风险评估）
3. THE 桌面应用 SHALL 支持舆情地图功能（新闻情感分析）
4. THE 桌面应用 SHALL 支持智者论坛功能（AI 专家对话）
5. THE 桌面应用 SHALL 保持与 Web 应用相同的 UI/UX
6. THE 桌面应用 SHALL 支持所有现有 API 端点

## 非功能性需求

### 性能
- 应用启动时间 < 8 秒（冷启动）
- 窗口响应时间 < 100ms
- 内存占用 < 700MB（总计）

### 兼容性
- Windows 10/11 (x64)
- macOS 10.15+ (x64/arm64)
- Linux (Ubuntu 20.04+, x64)

### 可维护性
- 代码复用现有 React 前端
- 模块化架构便于更新
- 完整的错误日志和监控

### 可用性
- 一键安装，无需配置
- 自动更新，无需手动下载
- 友好的错误提示和帮助文档
