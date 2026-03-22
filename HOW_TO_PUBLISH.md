# 如何发布到 GitHub - 完整指南

本指南将一步步教您如何将量数风行项目发布到 GitHub。

## 📋 发布前准备

### 1. 检查当前状态

```bash
# 查看当前 Git 状态
git status

# 查看是否有未提交的更改
git diff
```

### 2. 确认敏感信息已清理

```bash
# 检查 .env 文件是否被忽略
git check-ignore .env

# 应该输出: .env
# 如果没有输出，说明 .env 可能会被提交，需要检查 .gitignore
```

### 3. 测试功能（可选但推荐）

```bash
# 启动后端
cd backend
python main.py

# 在另一个终端启动前端
npm run dev

# 访问 http://localhost:3000 测试功能
```

## 🚀 发布步骤

### 步骤 1: 初始化 Git 仓库（如果还没有）

```bash
# 检查是否已经是 Git 仓库
git status

# 如果提示 "not a git repository"，则初始化
git init

# 添加所有文件
git add .

# 创建第一次提交
git commit -m "Initial commit: 量数风行 - 美股舆情风险分析平台"
```

### 步骤 2: 创建 GitHub 仓库

1. **访问 GitHub**
   - 打开 https://github.com
   - 登录您的账号

2. **创建新仓库**
   - 点击右上角的 "+" 按钮
   - 选择 "New repository"

3. **填写仓库信息**
   - Repository name: `quantywind` （或您喜欢的名字）
   - Description: `量数风行 - 基于 AI 的美股舆情风险分析平台`
   - 选择 Public（公开）
   - **不要**勾选 "Initialize this repository with a README"
   - **不要**添加 .gitignore 或 license（我们已经有了）
   - 点击 "Create repository"

4. **记录仓库 URL**
   - 创建后会显示类似：`https://github.com/你的用户名/quantywind.git`

### 步骤 3: 连接本地仓库到 GitHub

```bash
# 添加远程仓库（替换为您的仓库 URL）
git remote add origin https://github.com/你的用户名/quantywind.git

# 验证远程仓库
git remote -v

# 应该看到：
# origin  https://github.com/你的用户名/quantywind.git (fetch)
# origin  https://github.com/你的用户名/quantywind.git (push)
```

### 步骤 4: 推送代码到 GitHub

```bash
# 推送到 main 分支
git push -u origin main

# 如果您的默认分支是 master，使用：
# git push -u origin master

# 如果遇到认证问题，可能需要：
# 1. 使用 Personal Access Token (推荐)
# 2. 或配置 SSH key
```

### 步骤 5: 验证发布

1. 刷新 GitHub 仓库页面
2. 应该能看到所有文件
3. README.md 会自动显示在首页

### 步骤 6: 创建第一个 Release（可选）

1. 在 GitHub 仓库页面，点击 "Releases"
2. 点击 "Create a new release"
3. 填写信息：
   - Tag version: `v1.0.0`
   - Release title: `v1.0.0 - 首次公开发布`
   - Description: 
     ```
     ## 🎉 首次公开发布
     
     量数风行是一个开源的美股投资分析平台，集成了多个 AI 大模型。
     
     ### ✨ 主要功能
     - 智者论坛：多专家 AI 对话
     - 市场洞察：实时市场数据和分析
     - 风险分析：投资组合风险评估
     - 舆情地图：市场情绪可视化
     
     ### 🔑 使用说明
     请查看 README.md 获取详细的安装和使用指南。
     
     用户需要自行配置 AI 服务的 API Key。
     ```
4. 点击 "Publish release"

## 🔐 GitHub 认证设置

### 方法 1: Personal Access Token (推荐)

1. **创建 Token**
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - Note: `QuantyWind Development`
   - Expiration: 选择有效期
   - 勾选权限：
     - `repo` (完整的仓库访问权限)
   - 点击 "Generate token"
   - **复制并保存 token**（只显示一次！）

2. **使用 Token**
   ```bash
   # 推送时会要求输入用户名和密码
   # Username: 你的GitHub用户名
   # Password: 粘贴刚才复制的 token（不是你的 GitHub 密码）
   
   # 或者直接在 URL 中使用（不推荐，会暴露 token）
   git remote set-url origin https://你的token@github.com/你的用户名/quantywind.git
   ```

3. **保存凭据（可选）**
   ```bash
   # macOS
   git config --global credential.helper osxkeychain
   
   # Windows
   git config --global credential.helper winstor
   
   # Linux
   git config --global credential.helper store
   ```

### 方法 2: SSH Key

1. **生成 SSH Key**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # 按 Enter 使用默认位置
   # 可以设置密码或直接 Enter 跳过
   ```

2. **添加到 GitHub**
   ```bash
   # 复制公钥
   cat ~/.ssh/id_ed25519.pub
   
   # 或在 macOS 上
   pbcopy < ~/.ssh/id_ed25519.pub
   ```
   
   - 访问 https://github.com/settings/keys
   - 点击 "New SSH key"
   - Title: `My Computer`
   - Key: 粘贴公钥
   - 点击 "Add SSH key"

3. **使用 SSH URL**
   ```bash
   # 更改远程仓库 URL 为 SSH
   git remote set-url origin git@github.com:你的用户名/quantywind.git
   
   # 推送
   git push -u origin main
   ```

## 📝 更新 README 中的链接

发布后，需要更新 README.md 中的占位符链接：

```bash
# 编辑 README.md
# 将所有 "yourusername" 替换为您的 GitHub 用户名
# 将所有 "your.email@example.com" 替换为您的邮箱

# 提交更改
git add README.md
git commit -m "docs: 更新 README 中的链接"
git push
```

## 🎨 美化 GitHub 仓库

### 1. 添加 Topics（标签）

在仓库页面：
- 点击设置图标（齿轮）旁边的 "Add topics"
- 添加相关标签：
  - `ai`
  - `stock-analysis`
  - `investment`
  - `fastapi`
  - `react`
  - `typescript`
  - `python`
  - `trading`

### 2. 设置 About（关于）

- Description: `量数风行 - 基于 AI 的美股舆情风险分析平台`
- Website: 如果有部署的网站
- Topics: 已在上面添加

### 3. 添加 Social Preview（社交预览图）

- 在仓库 Settings → Options → Social preview
- 上传一张 1280x640 的预览图

## 📢 推广您的项目

### 1. 社交媒体

分享到：
- Twitter/X
- LinkedIn
- 微信公众号
- 知乎
- 掘金

### 2. 开源社区

提交到：
- [Awesome Lists](https://github.com/topics/awesome)
- [Product Hunt](https://www.producthunt.com/)
- [Hacker News](https://news.ycombinator.com/)
- [Reddit](https://www.reddit.com/r/opensource/)

### 3. 技术博客

撰写文章：
- 项目介绍
- 技术架构
- 开发心得
- 使用教程

## 🔄 后续维护

### 日常更新

```bash
# 修改代码后
git add .
git commit -m "feat: 添加新功能"
git push

# 或使用更规范的提交信息
git commit -m "feat: 添加用户偏好设置功能"
git commit -m "fix: 修复 API 调用超时问题"
git commit -m "docs: 更新安装文档"
```

### 版本发布

```bash
# 创建新版本标签
git tag -a v1.1.0 -m "Version 1.1.0 - 添加新功能"
git push origin v1.1.0

# 然后在 GitHub 上创建对应的 Release
```

### 处理 Issues 和 PR

- 及时回复 Issues
- 审查 Pull Requests
- 感谢贡献者
- 维护友好的社区氛围

## ⚠️ 常见问题

### Q: 推送时提示 "Permission denied"

A: 检查认证设置，确保使用了正确的 Token 或 SSH Key

### Q: 推送时提示 "rejected"

A: 可能是远程仓库有更新，先拉取：
```bash
git pull origin main --rebase
git push
```

### Q: 不小心提交了敏感信息怎么办？

A: 立即从历史中删除：
```bash
# 使用 BFG Repo-Cleaner
brew install bfg  # macOS
# 或从 https://rtyley.github.io/bfg-repo-cleaner/ 下载

# 删除敏感文件
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送（警告：会重写历史）
git push --force
```

### Q: 如何让项目更受欢迎？

A: 
1. 写好 README 和文档
2. 及时回复 Issues
3. 保持代码质量
4. 定期更新
5. 积极推广
6. 建立社区

## 📞 需要帮助？

如果在发布过程中遇到问题：

1. 查看 [GitHub 官方文档](https://docs.github.com/)
2. 搜索相关问题
3. 在项目 Issues 中提问

---

祝您发布顺利！🎉

如果这个指南对您有帮助，请给项目一个 ⭐
