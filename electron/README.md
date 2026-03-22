# Electron 桌面应用

## 目录结构

```
electron/
├── main.js              # 主进程入口
├── preload.js           # Preload 脚本（安全桥接）
├── backend-manager.js   # 后端服务管理器（待实现）
├── window-manager.js    # 窗口管理器（待实现）
├── tray-manager.js      # 系统托盘管理器（待实现）
├── menu.js              # 应用菜单（待实现）
├── updater.js           # 自动更新模块（待实现）
└── logger.js            # 日志模块（待实现）
```

## 开发模式

```bash
# 启动开发模式（前端 + Electron）
npm run electron:dev
```

这会：
1. 启动 Vite 开发服务器（http://localhost:3002）
2. 等待服务器就绪
3. 启动 Electron 应用并加载开发服务器

## 构建打包

```bash
# 构建所有平台
npm run electron:build

# 仅构建 Windows
npm run electron:build:win

# 仅构建 macOS
npm run electron:build:mac

# 仅构建 Linux
npm run electron:build:linux
```

## 安全配置

- **contextIsolation**: 启用上下文隔离
- **nodeIntegration**: 禁用 Node.js 集成
- **sandbox**: 启用沙箱模式
- **preload**: 使用 preload 脚本安全暴露 API

## IPC 通信

### 渲染进程 -> 主进程

```typescript
// 发送消息
window.electronAPI?.send('window:minimize');

// 发送带数据的消息
window.electronAPI?.send('notification:show', {
  title: '标题',
  body: '内容'
});
```

### 主进程 -> 渲染进程

```typescript
// 监听消息
const unsubscribe = window.electronAPI?.on('backend:status-changed', (status) => {
  console.log('Backend status:', status);
});

// 取消监听
unsubscribe?.();
```

## 日志

日志文件位置：
- **macOS**: `~/Library/Logs/量数风行/main.log`
- **Windows**: `%USERPROFILE%\AppData\Roaming\量数风行\logs\main.log`
- **Linux**: `~/.config/量数风行/logs/main.log`

## 下一步

1. 实现后端服务管理器（backend-manager.js）
2. 实现窗口状态持久化（window-manager.js）
3. 实现系统托盘（tray-manager.js）
4. 实现应用菜单（menu.js）
5. 实现自动更新（updater.js）
