# PWA 安装说明

## 快速开始

### 1. 安装依赖

```bash
npm install -D vite-plugin-pwa workbox-window
```

### 2. 准备应用图标

**临时方案**（快速测试）：
你可以先使用任何 PNG 图片作为临时图标，重命名为以下文件名并放到 `public/` 目录：

```
public/
  ├── icon-72.png
  ├── icon-96.png
  ├── icon-128.png
  ├── icon-144.png
  ├── icon-152.png
  ├── icon-192.png   ⭐ 必需
  ├── icon-384.png
  └── icon-512.png   ⭐ 必需
```

**正式方案**（推荐）：

1. 准备一个 512x512 的应用图标（PNG 格式）
2. 使用在线工具生成所有尺寸：
   - 访问：https://realfavicongenerator.net/
   - 或：https://www.pwabuilder.com/imageGenerator
3. 下载生成的图标包
4. 解压到 `public/` 目录

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 4. 测试 PWA 功能

#### Chrome/Edge 桌面端

1. 打开 http://localhost:3000
2. 按 F12 打开开发者工具
3. 切换到 "Application" 标签
4. 检查：
   - **Manifest**：应该显示应用信息
   - **Service Workers**：应该显示 "activated and running"
   - **Cache Storage**：应该有缓存条目

5. 测试安装：
   - 地址栏右侧会出现 ⊕ 安装图标
   - 点击安装
   - 应用会添加到桌面/开始菜单
   - 从桌面启动，以独立窗口运行

#### 测试离线功能

1. 在开发者工具的 "Network" 标签
2. 勾选 "Offline" 复选框
3. 刷新页面
4. 应该仍然可以看到缓存的内容

### 5. 添加安装提示到应用

在你的主布局组件中添加：

```typescript
import { InstallPWA } from './components/InstallPWA';

function App() {
  return (
    <div>
      {/* 你的应用内容 */}
      
      {/* PWA 安装提示 */}
      <InstallPWA />
    </div>
  );
}
```

### 6. 构建生产版本

```bash
# 构建
npm run build

# 预览
npm run preview
```

## 用户安装指南

### Windows/Mac/Linux (Chrome/Edge)

1. 访问网站
2. 点击地址栏右侧的 ⊕ 图标
3. 点击"安装"
4. 应用会添加到桌面
5. 双击桌面图标启动

### iOS (Safari)

1. 访问网站
2. 点击底部的"分享"按钮 📤
3. 向下滚动，选择"添加到主屏幕"
4. 点击"添加"
5. 应用图标会出现在主屏幕
6. 点击图标启动

### Android (Chrome)

1. 访问网站
2. 浏览器会自动弹出"安装应用"横幅
3. 点击"安装"
4. 应用会添加到主屏幕和应用抽屉
5. 像原生应用一样启动

## PWA 功能特性

### ✅ 已实现

- **离线访问**：缓存静态资源，离线也能使用
- **自动更新**：检测到新版本自动提示更新
- **桌面图标**：可以安装到桌面/主屏幕
- **独立窗口**：以独立窗口运行，类似原生应用
- **快速加载**：利用缓存，加载速度更快
- **响应式**：适配桌面和移动设备

### 🔄 可选功能

- **推送通知**：可以发送通知给用户
- **后台同步**：离线时的操作可以在联网后同步
- **分享功能**：可以分享内容到其他应用

## 调试技巧

### Chrome DevTools

**Application 标签**：
- Manifest：查看应用清单配置
- Service Workers：查看 SW 状态和日志
- Cache Storage：查看缓存的文件
- Clear storage：清除所有数据重新测试

**Lighthouse**：
- 点击 "Lighthouse" 标签
- 勾选 "Progressive Web App"
- 点击 "Generate report"
- 查看 PWA 评分和改进建议

### 常见问题

**Q: 看不到安装提示？**
A: 
- 检查是否已经安装过
- 确保使用 HTTPS 或 localhost
- 检查 manifest.json 是否正确
- 清除浏览器缓存重试

**Q: Service Worker 不工作？**
A:
- 检查控制台是否有错误
- 在 Application > Service Workers 中点击 "Update"
- 勾选 "Update on reload"

**Q: 图标不显示？**
A:
- 检查图标文件是否存在
- 确保图标尺寸正确
- 清除缓存重新加载

**Q: 离线不工作？**
A:
- 确保 Service Worker 已激活
- 检查缓存策略配置
- 查看 Cache Storage 中是否有缓存

## 性能优化

当前配置已包含：

1. **预缓存**：构建时缓存所有静态资源
2. **运行时缓存**：
   - API 请求：NetworkFirst（优先网络，失败用缓存）
   - 图片：CacheFirst（优先缓存，节省流量）
3. **缓存限制**：
   - API 缓存：100 条，1 小时
   - 图片缓存：60 张，30 天
4. **自动清理**：超过限制自动删除旧缓存

## 部署注意事项

### HTTPS 要求

PWA 必须通过 HTTPS 提供（localhost 除外）。部署时确保：

1. 配置 SSL 证书
2. 强制 HTTPS 重定向
3. 更新 manifest.json 中的 start_url

### 域名配置

在 `public/manifest.json` 中更新：

```json
{
  "start_url": "https://yourdomain.com/",
  "scope": "https://yourdomain.com/"
}
```

### 缓存策略

根据实际情况调整 `vite.config.ts` 中的缓存配置：

```typescript
runtimeCaching: [
  {
    urlPattern: /^https:\/\/yourdomain\.com\/api\//,
    handler: 'NetworkFirst',
    options: {
      cacheName: 'api-cache',
      expiration: {
        maxEntries: 100,
        maxAgeSeconds: 60 * 60 // 根据需要调整
      }
    }
  }
]
```

## 下一步

1. **安装依赖**：`npm install -D vite-plugin-pwa workbox-window`
2. **准备图标**：创建或使用临时图标
3. **测试功能**：启动开发服务器测试
4. **添加提示**：在 App.tsx 中添加 `<InstallPWA />`
5. **构建部署**：构建生产版本并部署

## 与 Electron 对比

| 特性 | PWA (当前) | Electron (备选) |
|------|-----------|----------------|
| 开发时间 | ✅ 已完成 | 需要 1-2 周 |
| 安装大小 | ✅ 几 MB | ⚠️ 几十 MB |
| 更新方式 | ✅ 自动 | 需要下载 |
| 跨平台 | ✅ 全平台 | ✅ 全平台 |
| 离线功能 | ✅ 支持 | ✅ 支持 |
| 系统集成 | ⚠️ 有限 | ✅ 完整 |
| 分发方式 | ✅ 网址 | 需要安装包 |
| 开发成本 | ✅ 零成本 | 需要额外开发 |

PWA 是快速验证的最佳选择！如果后续需要更深度的系统集成（如文件系统访问、系统托盘等），再考虑 Electron。

## 总结

PWA 配置已完成！现在只需要：

```bash
# 1. 安装依赖
npm install -D vite-plugin-pwa workbox-window

# 2. 准备图标（或使用临时图标）
# 将图标文件放到 public/ 目录

# 3. 启动测试
npm run dev

# 4. 在浏览器中测试安装
# 地址栏会出现安装图标
```

用户访问网站后就可以"安装"到桌面，像原生应用一样使用！🎉
