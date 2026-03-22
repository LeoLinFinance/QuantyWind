# PWA 测试快速指令

## 🚀 启动测试（3 步）

### 1. 启动开发服务器
```bash
npm run dev
```

### 2. 打开浏览器
访问：http://localhost:3000

### 3. 打开开发者工具
按 F12，切换到 "Application" 标签

---

## ✅ 检查清单

### Manifest（清单）
- [ ] 名称显示正确
- [ ] 8 个图标都存在
- [ ] 主题色是蓝色

### Service Worker
- [ ] 状态是 "activated and running"
- [ ] 可以看到 sw.js 或 dev-sw.js

### Cache Storage
- [ ] 有缓存条目

### 安装功能
- [ ] 地址栏有 ⊕ 安装图标
- [ ] 或右下角有安装提示
- [ ] 可以成功安装

### 离线功能
- [ ] Network 标签勾选 Offline
- [ ] 刷新后仍可访问

---

## 🎯 快速命令

```bash
# 检查 PWA 设置
./test-pwa-setup.sh

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

---

## 📱 安装测试

### 桌面（Chrome/Edge）
1. 点击地址栏 ⊕ 图标
2. 点击"安装"
3. 从桌面启动

### 手机（Chrome）
1. 等待安装横幅
2. 点击"安装"
3. 从主屏幕启动

---

## 🐛 遇到问题？

### 看不到安装提示
```bash
# 清除缓存，重新加载
# 或在 Application > Service Workers 点击 Unregister
```

### Service Worker 不工作
```bash
# 勾选 "Update on reload"
# 刷新页面
```

### 图标不显示
```bash
# 检查文件
ls public/icon-*.svg

# 应该看到 8 个文件
```

---

## 📚 详细文档

- `PWA_READY.md` - 完整说明
- `PWA_QUICK_START.md` - 快速指南
- `INSTALL_PWA_INSTRUCTIONS.md` - 安装说明

---

**现在就运行 `npm run dev` 开始测试！** 🎉
