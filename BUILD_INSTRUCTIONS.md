# 量数风行 - 完整打包指南

## 🎯 目标

生成开箱即用的安装包：
- **Windows**: `量数风行-1.0.0-Setup.exe`
- **macOS**: `量数风行-1.0.0.dmg`

---

## 📋 前置要求

### 所有平台
- Node.js 18+
- npm 或 yarn
- Git

### Windows 打包
- Windows 10/11
- Python 3.11+ (用于准备运行时)

### macOS 打包
- macOS 10.15+
- Xcode Command Line Tools
- Python 3.11+

---

## 🚀 完整打包流程

### 步骤 1：准备应用图标

#### 1.1 创建图标文件

你需要准备一个高质量的 PNG 图标（建议 1024x1024）。

#### 1.2 生成不同格式

**方法 A：在线工具（推荐）**

1. 访问 https://www.icoconverter.com/
2. 上传你的 PNG 图标
3. 下载生成的 `.ico` 文件（Windows）

4. 访问 https://cloudconvert.com/png-to-icns
5. 上传你的 PNG 图标
6. 下载生成的 `.icns` 文件（macOS）

**方法 B：命令行工具**

```bash
# 安装工具
npm install -g electron-icon-builder

# 生成所有格式
electron-icon-builder --input=./your-icon.png --output=./resources
```

#### 1.3 放置图标文件

将生成的图标文件放到 `resources/` 目录：

```
resources/
├── icon.png      # 主图标
├── icon.ico      # Windows 图标
└── icon.icns     # macOS 图标
```

---

### 步骤 2：准备 Python 运行时

这是最关键的步骤！

#### Windows 平台

```bash
# 1. 运行准备脚本
scripts\prepare-python-runtime.bat

# 2. 按照脚本提示操作：

# 2.1 下载嵌入式 Python
# 访问: https://www.python.org/downloads/windows/
# 下载: python-3.11.8-embed-amd64.zip

# 2.2 解压到 python-runtime/win/

# 2.3 下载 get-pip.py
cd python-runtime/win
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# 2.4 安装 pip
python.exe get-pip.py

# 2.5 修改 python311._pth
# 打开文件，取消注释 "import site" 这一行

# 2.6 安装依赖
python.exe -m pip install -r ..\..\backend\requirements.txt

# 2.7 验证
python.exe -m pip list
```

#### macOS/Linux 平台

```bash
# 运行准备脚本（自动完成所有步骤）
./scripts/prepare-python-runtime.sh
```

脚本会自动：
1. 创建 Python 虚拟环境
2. 安装所有依赖
3. 验证安装

---

### 步骤 3：构建前端

```bash
# 安装依赖（如果还没安装）
npm install

# 构建前端
npm run build
```

这会将 React 应用构建到 `dist-frontend/` 目录。

---

### 步骤 4：打包应用

#### Windows 打包

```bash
# 在 Windows 上运行
npm run electron:build:win
```

生成文件：
- `dist/量数风行-1.0.0-Setup.exe` - 安装包（~150MB）
- `dist/win-unpacked/` - 未打包版本（用于测试）

#### macOS 打包

```bash
# 在 macOS 上运行
npm run electron:build:mac
```

生成文件：
- `dist/量数风行-1.0.0.dmg` - 安装包（~150MB）
- `dist/mac/量数风行.app` - 应用包

---

## 🧪 测试打包应用

### Windows

```bash
# 方法 1：安装测试
.\dist\量数风行-1.0.0-Setup.exe

# 方法 2：直接运行未打包版本
.\dist\win-unpacked\量数风行.exe
```

### macOS

```bash
# 方法 1：挂载 DMG
open dist/量数风行-1.0.0.dmg

# 方法 2：直接运行
open dist/mac/量数风行.app
```

---

## 📦 打包产物说明

### Windows

```
dist/
├── 量数风行-1.0.0-Setup.exe          # 安装包（~150MB）
│   ├── 包含 Electron 应用
│   ├── 包含 Python 运行时
│   ├── 包含后端代码和依赖
│   └── 包含前端资源
│
└── win-unpacked/                      # 未打包版本
    ├── 量数风行.exe                   # 可执行文件
    ├── resources/                     # 资源目录
    │   ├── app.asar                  # 应用代码
    │   ├── python-runtime/           # Python 运行时
    │   └── backend/                  # 后端代码
    └── ...
```

### macOS

```
dist/
├── 量数风行-1.0.0.dmg                 # 安装包（~150MB）
│   └── 包含 量数风行.app
│
└── mac/
    └── 量数风行.app/                  # 应用包
        └── Contents/
            ├── MacOS/
            │   └── 量数风行           # 可执行文件
            └── Resources/
                ├── app.asar          # 应用代码
                ├── python-runtime/   # Python 运行时
                └── backend/          # 后端代码
```

---

## 🔍 故障排除

### 问题 1：Python 找不到模块

**症状**：打包后启动失败，日志显示 "ModuleNotFoundError"

**解决方案**：

Windows:
```bash
# 检查 python311._pth 文件
# 确保包含以下内容：
python311.zip
.
Lib\site-packages
import site
```

macOS/Linux:
```bash
# 重新创建虚拟环境
rm -rf python-runtime/darwin  # 或 linux
./scripts/prepare-python-runtime.sh
```

### 问题 2：打包后后端启动失败

**症状**：应用启动但后端无响应

**解决方案**：

1. 检查日志文件：
   - Windows: `%USERPROFILE%\AppData\Roaming\量数风行\logs\main.log`
   - macOS: `~/Library/Logs/量数风行/main.log`

2. 验证 Python 路径：
   ```javascript
   // 在 electron/backend-manager.js 中添加日志
   log.info('Python path:', this.config.pythonPath);
   log.info('Backend script:', this.config.backendScript);
   ```

3. 手动测试 Python：
   ```bash
   # Windows
   .\dist\win-unpacked\resources\python-runtime\python.exe --version
   
   # macOS
   ./dist/mac/量数风行.app/Contents/Resources/python-runtime/bin/python3 --version
   ```

### 问题 3：安装包太大

**症状**：安装包超过 200MB

**解决方案**：

1. 清理 Python 运行时：
   ```bash
   # 删除不必要的文件
   cd python-runtime/win  # 或 darwin/linux
   rm -rf test/
   rm -rf __pycache__/
   find . -name "*.pyc" -delete
   find . -name "*.pyo" -delete
   ```

2. 优化 electron-builder 配置：
   ```yaml
   # electron-builder.yml
   files:
     - "!**/node_modules/*/{test,__tests__,tests}"
     - "!**/*.{md,txt}"
   ```

### 问题 4：macOS 无法打开（安全限制）

**症状**：macOS 提示 "无法打开，因为它来自身份不明的开发者"

**解决方案**：

用户端：
```bash
# 右键点击应用 → 打开
# 或使用命令行
xattr -cr /Applications/量数风行.app
```

开发者端（需要 Apple Developer 账号）：
```bash
# 申请证书并签名
# 在 electron-builder.yml 中配置：
mac:
  identity: "Developer ID Application: Your Name (TEAM_ID)"
```

### 问题 5：前端资源加载失败

**症状**：应用启动后显示空白页面

**解决方案**：

1. 确保前端已构建：
   ```bash
   npm run build
   ls dist-frontend/  # 应该看到 index.html 等文件
   ```

2. 检查 main.js 中的路径：
   ```javascript
   // 生产模式应该加载：
   mainWindow.loadFile(path.join(__dirname, '../dist-frontend/index.html'));
   ```

---

## 📝 完整打包检查清单

### 准备阶段
- [ ] 应用图标已准备（icon.png, icon.ico, icon.icns）
- [ ] Python 运行时已准备（python-runtime/win 或 darwin）
- [ ] 所有依赖已安装（npm install）
- [ ] 后端依赖已安装到 Python 运行时

### 构建阶段
- [ ] 前端已构建（npm run build）
- [ ] dist-frontend/ 目录存在且包含文件
- [ ] 开发模式测试通过（npm run electron:dev）

### 打包阶段
- [ ] electron-builder.yml 配置正确
- [ ] 打包命令执行成功
- [ ] dist/ 目录包含安装包

### 测试阶段
- [ ] 安装包可以正常安装
- [ ] 应用可以启动
- [ ] 前端界面正常显示
- [ ] 后端服务自动启动
- [ ] 所有功能正常工作

---

## 🎯 快速开始（TL;DR）

### Windows

```bash
# 1. 准备 Python 运行时
scripts\prepare-python-runtime.bat
# 按照提示完成 Python 设置

# 2. 构建前端
npm run build

# 3. 打包
npm run electron:build:win

# 4. 测试
.\dist\量数风行-1.0.0-Setup.exe
```

### macOS

```bash
# 1. 准备 Python 运行时
./scripts/prepare-python-runtime.sh

# 2. 构建前端
npm run build

# 3. 打包
npm run electron:build:mac

# 4. 测试
open dist/量数风行-1.0.0.dmg
```

---

## 📚 相关文档

- `ELECTRON_PACKAGING_GUIDE.md` - 详细打包指南
- `ELECTRON_QUICK_START.md` - 快速启动指南
- `ELECTRON_PROGRESS.md` - 开发进度
- `electron/README.md` - Electron 目录说明

---

## 💡 提示

1. **首次打包建议**：先在当前平台测试，确保能正常打包
2. **调试技巧**：使用 `dist/win-unpacked` 或 `dist/mac` 中的未打包版本调试
3. **Python 版本**：建议使用 Python 3.11，与开发环境保持一致
4. **图标准备**：可以先使用占位符，后续再替换
5. **增量开发**：先确保基础功能能打包运行，再逐步添加功能

---

## 🎉 成功标志

当你看到以下文件时，说明打包成功：

- ✅ `dist/量数风行-1.0.0-Setup.exe` (Windows)
- ✅ `dist/量数风行-1.0.0.dmg` (macOS)

用户下载后：
1. 双击安装
2. 点击图标启动
3. 自动启动前后端
4. 开始使用！

**恭喜！你已经成功将量数风行打包成开箱即用的桌面应用！** 🎊
