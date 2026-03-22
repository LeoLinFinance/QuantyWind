# 🚀 GitHub Pages 部署步骤

## ✅ 已完成的步骤

1. ✅ Git仓库已初始化
2. ✅ 所有文件已添加
3. ✅ 首次提交已完成
4. ✅ 静态数据已导出（demo-web/data.json）

---

## 📝 接下来需要你完成的步骤

### 第1步：在GitHub上创建仓库

1. 打开浏览器，访问 https://github.com/new
2. 登录你的GitHub账号（professionalleolin@gmail.com）
3. 填写仓库信息：
   - Repository name: `didaxueshu`（或你喜欢的名字）
   - Description: `滴答学术 - AI技术播客平台`
   - 选择 `Public`（公开仓库，GitHub Pages免费）
   - ⚠️ 不要勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 第2步：推送代码到GitHub

创建仓库后，GitHub会显示一个页面，复制仓库的URL（类似：`https://github.com/你的用户名/didaxueshu.git`）

然后在终端运行以下命令：

```bash
# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/你的用户名/didaxueshu.git

# 推送代码
git branch -M main
git push -u origin main
```

如果提示需要认证，可能需要：
- 使用Personal Access Token（推荐）
- 或配置SSH密钥

### 第3步：启用GitHub Pages

1. 在GitHub仓库页面，点击 `Settings`（设置）
2. 左侧菜单找到 `Pages`
3. 在 "Build and deployment" 部分：
   - Source: 选择 `Deploy from a branch`
   - Branch: 选择 `main`
   - Folder: 选择 `/demo-web`
4. 点击 `Save`（保存）

### 第4步：等待部署完成

- GitHub会自动开始部署
- 通常需要1-2分钟
- 部署完成后，页面会显示你的网站URL

### 第5步：访问你的网站

你的网站地址将是：
```
https://你的GitHub用户名.github.io/didaxueshu/index-static.html
```

---

## 🔧 如果遇到问题

### 问题1：推送时要求认证

**解决方案A：使用Personal Access Token**

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置：
   - Note: `didaxueshu-deploy`
   - Expiration: 选择有效期
   - 勾选 `repo` 权限
4. 点击 "Generate token"
5. 复制生成的token（只显示一次！）
6. 推送时，用户名输入你的GitHub用户名，密码输入这个token

**解决方案B：使用SSH**

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "professionalleolin@gmail.com"

# 添加到GitHub
# 1. 复制公钥内容
cat ~/.ssh/id_ed25519.pub

# 2. 访问 https://github.com/settings/keys
# 3. 点击 "New SSH key"
# 4. 粘贴公钥内容

# 5. 修改远程仓库URL为SSH格式
git remote set-url origin git@github.com:你的用户名/didaxueshu.git
```

### 问题2：GitHub Pages显示404

**检查清单：**
- ✅ 确认访问的是 `/index-static.html` 而不是 `/index-fixed.html`
- ✅ 确认在Settings → Pages中选择了 `/demo-web` 目录
- ✅ 等待2-3分钟让部署完成
- ✅ 清除浏览器缓存（Cmd+Shift+R）

### 问题3：文章内容显示不出来

**检查：**
- ✅ 确认 `demo-web/data.json` 文件存在
- ✅ 打开浏览器控制台（F12）查看错误信息
- ✅ 确认访问的是 `index-static.html`

---

## 📞 需要帮助？

如果遇到任何问题，请告诉我：
1. 具体的错误信息
2. 你在哪一步遇到问题
3. 浏览器控制台的错误（如果有）

---

## 🎉 部署成功后

### 分享你的网站
```
https://你的用户名.github.io/didaxueshu/index-static.html
```

### 绑定自定义域名（可选）
1. 在仓库Settings → Pages → Custom domain
2. 输入你的域名
3. 在域名服务商添加CNAME记录

### 更新内容
```bash
# 修改内容后
git add .
git commit -m "Update content"
git push
```

---

## ✨ 当前项目状态

- 📝 文章数量：49篇
- 🏷️ 分类：AI世界模型(19)、脑机接口(14)、芯片架构(9)、具身智能(7)
- 💾 数据文件：demo-web/data.json (451KB)
- 🎨 界面：渐变紫色主题，响应式设计

---

**准备好了吗？开始第1步：在GitHub上创建仓库！** 🚀
