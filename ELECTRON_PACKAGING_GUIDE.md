# 量数风行 - 桌面应用打包指南

## 📦 目标

将量数风行打包成开箱即用的桌面应用：
- Windows: `.exe` 安装包
- macOS: `.dmg` 安装包
- Linux: `.AppImage` 安装包

用户双击安装后，点击图标即可使用，无需任何配置。

---

## 🎯 核心挑战

### 1. Python 运行时
用户电脑上可能没有 Python，需要内置 Python 运行时。

### 2. Python 依赖
需要将所有 Python 依赖（FastAPI、pandas 等）打包进去。

### 3. 环境变量
需要处理 API keys 等敏感配置。

---

## 📋 完整打包流程

### 阶段 1：准备应用图标

#### 1.1 创建应用图标

你需要准备一个高质量的图标（建议 1024x1024 PNG）：

```bash
resources/
├── icon.png      # 主图标（512x512 或更大）
├── icon.ico      # Windows 图标
└── icon.icns     # macOS 图标
```

#### 1.2 生成不同格式图标

**在线工具**：
- https://www.icoconverter.com/ （PNG → ICO）
- https://cloudconvert.com/png-to-icns （PNG → ICNS）

**或使用命令行工具**：
```bash
# 安装 electron-icon-builder
npm install -g electron-icon-builder

# 生成所有格式
electron-icon-builder --input=./icon.png --output=./resources
```

---

### 阶段 2：内置 Python 运行时（关键！）

这是最重要的步骤，有两种方案：

#### 方案 A：嵌入式 Python（推荐）✅

**优点**：
- 完全控制 Python 环境
- 用户无需安装 Python
- 依赖隔离，不会冲突

**缺点**：
- 安装包较大（~150MB）
- 需要为每个平台准备

**实现步骤**：

##### Windows

```bash
# 1. 下载嵌入式 Python
# 访问 https://www.python.org/downloads/windows/
# 下载 "Windows embeddable package (64-bit)"
# 例如：python-3.11.8-embed-amd64.zip

# 2. 解压到项目
mkdir python-runtime/windows
unzip python-3.11.8-embed-amd64.zip -d python-runtime/windows

# 3. 配置 pip
cd python-runtime/windows
# 下载 get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# 安装 pip
python.exe get-pip.py

# 4. 安装依赖
python.exe -m pip install -r ../../backend/requirements.txt

# 5. 修改 python311._pth 文件，添加：
# import site
```

##### macOS

```bash
# 1. 下载 Python
# 访问 https://www.python.org/downloads/macos/
# 下载 macOS 64-bit installer

# 2. 创建独立环境
mkdir python-runtime/macos
python3 -m venv python-runtime/macos/python-env

# 3. 激活并安装依赖
source python-runtime/macos/python-env/bin/activate
pip install -r backend/requirements.txt
deactivate
```

##### Linux

```bash
# 1. 创建虚拟环境
mkdir python-runtime/linux
python3 -m venv python-runtime/linux/python-env

# 2. 安装依赖
source python-runtime/linux/python-env/bin/activate
pip install -r backend/requirements.txt
deactivate
```

#### 方案 B：PyInstaller

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 打包后端
cd backend
pyinstaller --onefile \
  --name quantdata-backend \
  --hidden-import=uvicorn \
  --hidden-import=fastapi \
  main.py

# 3. 可执行文件在 dist/quantdata-backend
```

---

### 阶段 3：更新 Backend Manager

需要修改 `electron/backend-manager.js` 以使用打包的 Python：

```javascript
// electron/backend-manager.js

function getPythonPath() {
  const isDev = process.env.NODE_ENV === 'development';
  
  if (isDev) {
    // 开发模式：使用系统 Python
    return 'python3';
  }
  
  // 生产模式：使用打包的 Python
  const platform = process.platform;
  const resourcesPath = process.resourcesPath;
  
  if (platform === 'win32') {
    return path.join(resourcesPath, 'python-runtime', 'windows', 'python.exe');
  } else if (platform === 'darwin') {
    return path.join(resourcesPath, 'python-runtime', 'macos', 'python-env', 'bin', 'python3');
  } else {
    return path.join(resourcesPath, 'python-runtime', 'linux', 'python-env', 'bin', 'python3');
  }
}

// 在 BackendManager 构造函数中使用
this.config = {
  pythonPath: config.pythonPath || getPythonPath(),
  // ...
};
```

---

### 阶段 4：更新 electron-builder 配置

```yaml
# electron-builder.yml
appId: com.quantdata.fengxing
productName: 量数风行
copyright: Copyright © 2024

directories:
  output: dist
  buildResources: resources

files:
  - electron/**/*
  - dist-frontend/**/*
  - backend/**/*
  - resources/**/*
  - package.json
  - "!backend/**/__pycache__"
  - "!backend/**/*.pyc"
  - "!backend/**/.pytest_cache"

# 包含 Python 运行时
extraResources:
  - from: python-runtime/${os}
    to: python-runtime
    filter:
      - "**/*"
  - from: backend
    to: backend
    filter:
      - "**/*"
      - "!**/__pycache__"
      - "!**/*.pyc"

win:
  target:
    - nsis
  icon: resources/icon.ico
  artifactName: ${productName}-${version}-Setup.${ext}

mac:
  target:
    - dmg
  icon: resources/icon.icns
  category: public.app-category.finance
  hardenedRuntime: true
  gatekeeperAssess: false

linux:
  target:
    - AppImage
  icon: resources/icon.png
  category: Finance
  artifactName: ${productName}-${version}.${ext}

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: ${productName}
  installerIcon: resources/icon.ico
  uninstallerIcon: resources/icon.ico
  installerHeaderIcon: resources/icon.ico

dmg:
  title: ${productName} ${version}
  icon: resources/icon.icns
  background: resources/dmg-background.png
  contents:
    - x: 410
      y: 150
      type: link
      path: /Applications
    - x: 130
      y: 150
      type: file
```

---

### 阶段 5：处理环境变量和配置

#### 5.1 创建配置管理器

```javascript
// electron/config-manager.js
const Store = require('electron-store');
const path = require('path');

class ConfigManager {
  constructor() {
    this.store = new Store({
      name: 'config',
      defaults: {
        apiKeys: {
          alphaVantage: '',
          twelveData: '',
          stepfun: '',
          kimi: ''
        },
        backend: {
          port: 8000,
          host: '127.0.0.1'
        }
      }
    });
  }
  
  // 获取配置
  get(key) {
    return this.store.get(key);
  }
  
  // 设置配置
  set(key, value) {
    this.store.set(key, value);
  }
  
  // 获取所有 API keys
  getApiKeys() {
    return this.store.get('apiKeys');
  }
  
  // 设置 API key
  setApiKey(service, key) {
    this.store.set(`apiKeys.${service}`, key);
  }
}

module.exports = { ConfigManager };
```

#### 5.2 首次启动配置向导

创建一个设置页面，让用户输入 API keys：

```javascript
// electron/setup-window.js
function createSetupWindow() {
  const setupWindow = new BrowserWindow({
    width: 600,
    height: 400,
    title: '量数风行 - 初始设置',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  setupWindow.loadFile('setup.html');
  return setupWindow;
}
```

---

### 阶段 6：构建和打包

#### 6.1 添加构建脚本

在 `package.json` 中添加：

```json
{
  "scripts": {
    "build:frontend": "vite build",
    "build:all": "npm run build:frontend && npm run electron:build",
    "electron:build": "electron-builder",
    "electron:build:win": "electron-builder --win",
    "electron:build:mac": "electron-builder --mac",
    "electron:build:linux": "electron-builder --linux",
    "electron:build:all": "electron-builder -mwl"
  }
}
```

#### 6.2 执行构建

```bash
# 1. 构建前端
npm run build:frontend

# 2. 打包应用（当前平台）
npm run electron:build

# 或者打包所有平台（需要在对应平台上执行）
npm run electron:build:all
```

---

## 📦 打包产物

构建完成后，在 `dist/` 目录会生成：

### Windows
```
dist/
├── 量数风行-1.0.0-Setup.exe          # 安装包（~150MB）
└── win-unpacked/                      # 未打包版本（测试用）
```

### macOS
```
dist/
├── 量数风行-1.0.0.dmg                 # 安装包（~150MB）
└── mac/量数风行.app                   # 应用包
```

### Linux
```
dist/
├── 量数风行-1.0.0.AppImage            # 安装包（~150MB）
└── linux-unpacked/                    # 未打包版本
```

---

## 🧪 测试打包应用

### Windows
```bash
# 安装
.\dist\量数风行-1.0.0-Setup.exe

# 或直接运行未打包版本
.\dist\win-unpacked\量数风行.exe
```

### macOS
```bash
# 挂载 DMG
open dist/量数风行-1.0.0.dmg

# 或直接运行
open dist/mac/量数风行.app
```

### Linux
```bash
# 添加执行权限
chmod +x dist/量数风行-1.0.0.AppImage

# 运行
./dist/量数风行-1.0.0.AppImage
```

---

## 🔍 常见问题

### 1. 打包后 Python 找不到模块

**原因**：Python 路径配置错误

**解决**：
- 检查 `python311._pth`（Windows）
- 确保 `site-packages` 在路径中

### 2. 打包后后端启动失败

**原因**：依赖缺失或路径错误

**解决**：
- 检查所有依赖是否安装
- 使用 `console.log` 调试路径
- 查看日志文件

### 3. 安装包太大

**原因**：包含了不必要的文件

**解决**：
- 在 `electron-builder.yml` 中配置 `files` 过滤
- 排除测试文件、文档等

### 4. macOS 无法打开（安全限制）

**原因**：应用未签名

**解决**：
- 用户：右键 → 打开
- 开发者：申请 Apple Developer 证书签名

---

## 🚀 发布流程

### 1. 版本管理

```bash
# 更新版本号
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0
```

### 2. 创建 GitHub Release

```bash
# 1. 提交代码
git add .
git commit -m "Release v1.0.0"
git tag v1.0.0
git push origin main --tags

# 2. 在 GitHub 创建 Release
# 上传打包产物到 Release
```

### 3. 自动更新配置

在 `electron-builder.yml` 中配置：

```yaml
publish:
  provider: github
  owner: your-username
  repo: quantdata-fengxing
```

---

## 📝 下一步任务清单

要完成打包，你需要：

- [ ] **任务 15.1**：准备应用图标
- [ ] **任务 15.2**：准备 Python 运行时
  - [ ] Windows 嵌入式 Python
  - [ ] macOS Python 虚拟环境
  - [ ] Linux Python 虚拟环境
- [ ] **任务 15.3**：更新 backend-manager.js
- [ ] **任务 15.4**：完善 electron-builder.yml
- [ ] **任务 15.5**：创建配置管理器
- [ ] **任务 15.6**：创建首次启动向导
- [ ] **任务 15.7**：测试打包应用
- [ ] **任务 15.8**：在所有平台测试

---

## 💡 建议

1. **先在当前平台测试**：不要一开始就打包所有平台
2. **使用未打包版本调试**：`dist/win-unpacked` 等目录
3. **逐步添加功能**：先确保基础功能能打包运行
4. **保留开发模式**：方便调试

---

## 🎯 最终目标

用户体验：
1. 下载安装包（~150MB）
2. 双击安装
3. 首次启动：输入 API keys（可选）
4. 点击图标启动应用
5. 自动启动前后端服务
6. 开始使用！

---

**准备好开始打包了吗？** 🚀

我建议先从任务 15.2 开始，准备 Python 运行时。这是最关键的一步！
