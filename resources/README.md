# 应用图标资源

## 📁 需要的文件

请将以下图标文件放到此目录：

- `icon.png` - 主图标（512x512 或更大，PNG 格式）
- `icon.ico` - Windows 图标
- `icon.icns` - macOS 图标

## 🎨 如何创建图标

### 方法 1：在线工具（推荐）

1. 准备一个高质量的 PNG 图标（建议 1024x1024）
2. 使用在线工具转换：
   - **PNG → ICO**: https://www.icoconverter.com/
   - **PNG → ICNS**: https://cloudconvert.com/png-to-icns

### 方法 2：使用命令行工具

```bash
# 安装 electron-icon-builder
npm install -g electron-icon-builder

# 生成所有格式（需要先有 icon.png）
electron-icon-builder --input=./icon.png --output=./resources
```

## 📝 图标规格

- **icon.png**: 512x512 或 1024x1024 像素
- **icon.ico**: 包含多个尺寸（16x16, 32x32, 48x48, 256x256）
- **icon.icns**: macOS 格式，包含多个尺寸

## 🎯 临时方案

如果暂时没有图标，可以使用占位符：
- 系统会使用 Electron 默认图标
- 后续可以随时替换

## ✅ 检查清单

- [ ] icon.png 已准备
- [ ] icon.ico 已生成（Windows）
- [ ] icon.icns 已生成（macOS）
- [ ] 图标清晰，无背景或纯色背景
- [ ] 图标在小尺寸下仍然清晰可辨
