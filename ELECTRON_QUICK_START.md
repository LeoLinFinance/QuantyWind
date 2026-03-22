# Electron 桌面应用快速启动指南

## 📦 已完成的配置

✅ 安装了 Electron 相关依赖
✅ 创建了项目结构（electron/ 目录）
✅ 配置了 electron-builder 打包工具
✅ 创建了主进程入口（main.js）
✅ 创建了 Preload 脚本（preload.js）
✅ 配置了 TypeScript 类型定义
✅ 更新了 package.json 脚本
✅ 配置了 Vite 构建输出

## 🚀 开发模式

### 方式一：一键启动（推荐）✨

现在只需一个命令即可启动应用，后端服务会自动启动！

```bash
npm run electron:dev
```

这会自动：
1. 启动 Vite 开发服务器（前端）
2. 等待服务器就绪
3. 启动 Electron 应用
4. **自动启动 Python 后端服务** ✨
5. 自动打开开发者工具

### 方式二：手动启动（用于调试）

如果需要单独调试后端，可以手动启动：

**终端 1 - 启动后端**：
```bash
cd backend
python3 main.py
```

**终端 2 - 启动 Electron**：
```bash
npm run electron:dev
```

**终端 3（可选）- 单独启动前端**：
```bash
npm run dev
```

## 🔨 构建打包

### 1. 准备应用图标

将以下图标文件放到 `resources/` 目录：
- `icon.png` - 通用图标（512x512 或更大）
- `icon.ico` - Windows 图标
- `icon.icns` - macOS 图标

可以使用在线工具转换：
- https://www.icoconverter.com/
- https://cloudconvert.com/

### 2. 构建前端

```bash
npm run build
```

这会将前端构建到 `dist-frontend/` 目录。

### 3. 打包应用

```bash
# 打包当前平台
npm run electron:build

# 打包 Windows
npm run electron:build:win

# 打包 macOS
npm run electron:build:mac

# 打包 Linux
npm run electron:build:linux
```

打包产物在 `dist/` 目录。

## 📁 项目结构

```
.
├── electron/                 # Electron 相关代码
│   ├── main.js              # 主进程入口 ✅
│   ├── preload.js           # Preload 脚本 ✅
│   ├── backend-manager.js   # 后端服务管理器（待实现）
│   ├── window-manager.js    # 窗口管理器（待实现）
│   ├── tray-manager.js      # 系统托盘（待实现）
│   ├── menu.js              # 应用菜单（待实现）
│   ├── updater.js           # 自动更新（待实现）
│   └── logger.js            # 日志模块（待实现）
├── resources/               # 应用资源
│   └── icon-placeholder.txt # 图标占位符
├── src/                     # React 前端（现有）
│   └── types/
│       └── electron.d.ts    # Electron API 类型定义 ✅
├── backend/                 # Python 后端（现有）
├── dist-frontend/           # 前端构建输出
├── dist/                    # Electron 打包输出
├── package.json             # 项目配置 ✅
├── electron-builder.yml     # 打包配置 ✅
└── vite.config.ts           # Vite 配置 ✅
```

## 🔧 在前端使用 Electron API

```typescript
// 检查是否在 Electron 环境中
if (window.electronAPI?.isElectron()) {
  console.log('Running in Electron');
  
  // 获取应用版本
  const version = window.electronAPI.getAppVersion();
  
  // 获取平台信息
  const platform = window.electronAPI.getPlatform();
  
  // 发送消息到主进程
  window.electronAPI.send('window:minimize');
  
  // 监听主进程消息
  const unsubscribe = window.electronAPI.on('backend:status-changed', (status) => {
    console.log('Backend status:', status);
  });
  
  // 取消监听
  unsubscribe();
}
```

## 📝 下一步任务

根据 `.kiro/specs/electron-desktop-app/tasks.md`：

- [x] 任务 1：设置 Electron 项目结构和基础配置 ✅
- [ ] 任务 2：实现主进程入口和窗口创建
  - [ ] 2.1 创建 electron/main.js 主进程入口 ✅（基础版本）
  - [ ] 2.3 创建 electron/preload.js 脚本 ✅
- [ ] 任务 3：实现后端服务管理器
- [ ] 任务 4：实现窗口管理器
- [ ] 任务 5：实现系统托盘管理器
- [ ] ...

## 🐛 故障排除

### 问题：Electron 窗口空白

**解决方案**：
1. 检查前端开发服务器是否运行（http://localhost:3002）
2. 检查控制台是否有错误
3. 打开开发者工具查看详细错误

### 问题：后端 API 无法访问

**解决方案**：
1. 确保后端服务已启动（http://localhost:8000）
2. 检查后端日志
3. 测试健康检查端点：`curl http://localhost:8000/health`

### 问题：打包失败

**解决方案**：
1. 确保已运行 `npm run build` 构建前端
2. 检查 `dist-frontend/` 目录是否存在
3. 检查 `electron-builder.yml` 配置
4. 查看详细错误日志

## 📚 参考资源

- [Electron 官方文档](https://www.electronjs.org/docs)
- [electron-builder 文档](https://www.electron.build/)
- [Electron 安全最佳实践](https://www.electronjs.org/docs/tutorial/security)

## ✨ 当前状态

**任务 1 已完成**！基础项目结构已搭建完成，可以开始开发模式测试。

下一步建议：
1. 测试开发模式：`npm run electron:dev`
2. 继续实现任务 2：完善主进程功能
3. 实现任务 3：后端服务自动启动
