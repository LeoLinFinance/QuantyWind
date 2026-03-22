# 🚀 立即发布 - 3 步完成

## 方法 1: 使用自动化脚本（推荐）

```bash
# 运行发布脚本
./publish.sh
```

脚本会自动：
- ✅ 检查 Git 仓库状态
- ✅ 确认敏感文件已忽略
- ✅ 提交未保存的更改
- ✅ 推送到 GitHub

## 方法 2: 手动发布（3 步）

### 第 1 步：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写信息：
   - Repository name: `quantywind`
   - Description: `量数风行 - 基于 AI 的美股舆情风险分析平台`
   - 选择 **Public**
   - **不要**勾选任何初始化选项
3. 点击 "Create repository"
4. 复制显示的仓库 URL（类似：`https://github.com/你的用户名/quantywind.git`）

### 第 2 步：连接并推送

```bash
# 如果还没有初始化 Git
git init
git add .
git commit -m "Initial commit: 量数风行 - 美股舆情风险分析平台"

# 连接到 GitHub（替换为您的仓库 URL）
git remote add origin https://github.com/你的用户名/quantywind.git

# 推送代码
git push -u origin main
```

### 第 3 步：验证

1. 刷新 GitHub 仓库页面
2. 确认所有文件已上传
3. README.md 应该显示在首页

## ✅ 发布后立即做的事

### 1. 更新 README 链接（2 分钟）

编辑 `README.md`，替换以下内容：

```bash
# 查找并替换
# yourusername → 你的GitHub用户名
# your.email@example.com → 你的邮箱
```

提交更改：
```bash
git add README.md
git commit -m "docs: 更新 README 链接"
git push
```

### 2. 添加仓库标签（1 分钟）

在 GitHub 仓库页面：
1. 点击 "About" 旁边的设置图标
2. 添加 Topics：`ai`, `stock-analysis`, `investment`, `fastapi`, `react`, `typescript`, `python`
3. 保存

### 3. 创建第一个 Release（可选，3 分钟）

1. 在仓库页面点击 "Releases"
2. 点击 "Create a new release"
3. 填写：
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - 首次公开发布`
   - Description: 复制下面的内容

```markdown
## 🎉 首次公开发布

量数风行是一个开源的美股投资分析平台，集成了多个 AI 大模型。

### ✨ 主要功能
- 🤖 智者论坛：多专家 AI 对话系统
- 📊 市场洞察：实时市场数据和 AI 分析
- ⚠️ 风险分析：投资组合风险评估和解读
- 🗺️ 舆情地图：市场情绪可视化分析
- 📈 智能信号：AI 驱动的交易信号

### 🔑 使用说明
1. 克隆项目：`git clone https://github.com/你的用户名/quantywind.git`
2. 查看 [QUICKSTART.md](QUICKSTART.md) 快速开始
3. 在设置页面配置您的 AI API Key

### 📖 文档
- [完整文档](README.md)
- [快速开始](QUICKSTART.md)
- [贡献指南](CONTRIBUTING.md)

用户需要自行配置 AI 服务的 API Key，详见文档。
```

4. 点击 "Publish release"

## 🎯 推广您的项目（可选）

### 社交媒体分享模板

```
🎉 开源项目发布：量数风行 QuantyWind

一个基于 AI 的美股投资分析平台，集成了多个大模型：
✨ 多专家 AI 对话
📊 实时市场分析
⚠️ 风险评估
🗺️ 舆情可视化

技术栈：React + FastAPI + Python
开源协议：MIT

GitHub: https://github.com/你的用户名/quantywind

#开源 #AI #投资分析 #Python #React
```

### 发布到社区

- [掘金](https://juejin.cn/)
- [知乎](https://www.zhihu.com/)
- [V2EX](https://www.v2ex.com/)
- [Reddit r/opensource](https://www.reddit.com/r/opensource/)
- [Hacker News](https://news.ycombinator.com/)

## 📊 监控项目

发布后关注：
- ⭐ Stars 数量
- 👁️ Watchers
- 🔀 Forks
- 📝 Issues
- 🔧 Pull Requests

## ❓ 遇到问题？

### 推送失败？

```bash
# 如果提示需要认证，使用 Personal Access Token
# 1. 访问 https://github.com/settings/tokens
# 2. 生成新 token（勾选 repo 权限）
# 3. 推送时使用 token 作为密码
```

### .env 文件被提交了？

```bash
# 立即从历史中删除
git rm --cached .env
git commit -m "Remove .env from tracking"
git push

# 确保 .gitignore 包含 .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"
git push
```

### 需要更多帮助？

查看详细指南：
- [HOW_TO_PUBLISH.md](HOW_TO_PUBLISH.md) - 完整发布指南
- [OPENSOURCE_CHECKLIST.md](OPENSOURCE_CHECKLIST.md) - 检查清单
- [GitHub 官方文档](https://docs.github.com/)

---

## 🎊 恭喜！

您的项目已经开源发布！

接下来：
1. 定期更新代码
2. 回复 Issues
3. 审查 Pull Requests
4. 建立社区
5. 享受开源的乐趣！

**如果这个项目对您有帮助，请给我们一个 ⭐**
