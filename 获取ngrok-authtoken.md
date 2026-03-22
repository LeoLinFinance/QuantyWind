# 如何获取 ngrok authtoken 🔑

## 📍 在哪里找到 authtoken？

### 方法 1：直接访问（最快）

直接打开这个链接：
```
https://dashboard.ngrok.com/get-started/your-authtoken
```

登录后就能看到你的 authtoken！

---

## 📝 详细步骤（带截图说明）

### 第 1 步：访问 ngrok 官网

打开浏览器，访问：
```
https://ngrok.com
```

或者直接访问注册页面：
```
https://dashboard.ngrok.com/signup
```

### 第 2 步：注册账号（如果还没有）

可以选择：
- 用 Google 账号登录（最快）
- 用 GitHub 账号登录
- 用邮箱注册

**完全免费！**

### 第 3 步：登录后自动跳转

注册或登录后，会自动跳转到 Dashboard（控制面板）

### 第 4 步：找到 authtoken

有两种方法：

#### 方法 A：从侧边栏找

1. 看左侧菜单
2. 点击 "Getting Started" 或 "Your Authtoken"
3. 就能看到你的 token

#### 方法 B：直接访问

登录后直接访问：
```
https://dashboard.ngrok.com/get-started/your-authtoken
```

### 第 5 步：复制 authtoken

你会看到类似这样的内容：

```
Your Authtoken

2abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

这就是你的 authtoken！

点击旁边的 📋 复制按钮，或者手动选中复制。

---

## 🚀 配置 authtoken

### 复制 token 后，在终端运行：

```bash
ngrok config add-authtoken 你复制的token
```

例如：
```bash
ngrok config add-authtoken 2abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

### 看到这个提示就成功了：

```
Authtoken saved to configuration file: /Users/你的用户名/.ngrok2/ngrok.yml
```

---

## 💡 快速链接

### 如果你已经有账号：

1. **登录**：https://dashboard.ngrok.com/login
2. **查看 authtoken**：https://dashboard.ngrok.com/get-started/your-authtoken
3. **复制并配置**

### 如果你还没有账号：

1. **注册**：https://dashboard.ngrok.com/signup
2. 注册后自动显示 authtoken
3. **复制并配置**

---

## 🔍 找不到 authtoken？

### 方法 1：从菜单找

登录后：
1. 看左侧菜单
2. 找到 "Getting Started" 或 "Setup & Installation"
3. 点击 "Your Authtoken"

### 方法 2：从首页找

登录后：
1. 在 Dashboard 首页
2. 找到 "Connect your account" 部分
3. 会显示你的 authtoken

### 方法 3：直接访问

```
https://dashboard.ngrok.com/get-started/your-authtoken
```

---

## ⚠️ 注意事项

### authtoken 是私密的！

- ❌ 不要分享给别人
- ❌ 不要提交到 Git
- ❌ 不要公开发布

### 如果泄露了怎么办？

1. 登录 ngrok Dashboard
2. 访问：https://dashboard.ngrok.com/get-started/your-authtoken
3. 点击 "Reset" 或 "Regenerate"
4. 重新配置新的 token

---

## 🎯 完整流程示例

### 1. 注册/登录

```
访问：https://dashboard.ngrok.com/signup
用 Google 账号登录（最快）
```

### 2. 获取 token

```
自动跳转到 Dashboard
或访问：https://dashboard.ngrok.com/get-started/your-authtoken
复制显示的 token
```

### 3. 配置 token

```bash
ngrok config add-authtoken 你的token
```

### 4. 验证配置

```bash
ngrok config check
```

如果显示配置文件路径，就成功了！

### 5. 开始使用

```bash
npm run dev
ngrok http 3000
```

---

## 📱 移动端查看

如果你在手机上：

1. 访问：https://dashboard.ngrok.com
2. 登录账号
3. 点击菜单 ☰
4. 选择 "Your Authtoken"
5. 复制 token
6. 发送到电脑上配置

---

## 🔧 配置文件位置

authtoken 配置后保存在：

**Mac/Linux:**
```
~/.ngrok2/ngrok.yml
```

**Windows:**
```
C:\Users\你的用户名\.ngrok2\ngrok.yml
```

你可以直接查看这个文件：
```bash
cat ~/.ngrok2/ngrok.yml
```

会显示：
```yaml
authtoken: 你的token
version: "2"
```

---

## 🎁 一键打开 authtoken 页面

我可以创建一个脚本帮你直接打开：

```bash
#!/bin/bash
open https://dashboard.ngrok.com/get-started/your-authtoken
```

---

## 📚 相关链接

- **注册页面**：https://dashboard.ngrok.com/signup
- **登录页面**：https://dashboard.ngrok.com/login
- **Authtoken 页面**：https://dashboard.ngrok.com/get-started/your-authtoken
- **文档**：https://ngrok.com/docs

---

## 🚀 下一步

获取并配置 authtoken 后：

1. ✅ 运行 `npm run dev` 启动应用
2. ✅ 运行 `ngrok http 3000` 启动隧道
3. ✅ 复制显示的网址分享给别人

或者使用我创建的一键脚本：
```bash
./远程访问-ngrok.sh
```

---

**总结：访问 https://dashboard.ngrok.com/get-started/your-authtoken 就能看到你的 authtoken！** 🎉
