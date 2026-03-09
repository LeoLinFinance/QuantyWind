# 故障排查指南

## 🔍 问题：点击➜按钮没有反应

如果点击文章卡片右上角的➜按钮没有任何反应，请按以下步骤排查：

## 步骤1：清除浏览器缓存

浏览器可能缓存了旧版本的HTML文件。

### Chrome/Edge
1. 打开 http://localhost:8080
2. 按 `Cmd+Shift+R` (Mac) 或 `Ctrl+Shift+R` (Windows/Linux)
3. 或者按 `F12` 打开开发者工具
4. 右键点击刷新按钮，选择"清空缓存并硬性重新加载"

### Safari
1. 打开 http://localhost:8080
2. 按 `Cmd+Option+E` 清空缓存
3. 然后按 `Cmd+R` 刷新页面

### Firefox
1. 打开 http://localhost:8080
2. 按 `Cmd+Shift+R` (Mac) 或 `Ctrl+Shift+R` (Windows/Linux)

## 步骤2：检查浏览器控制台

打开浏览器开发者工具查看是否有错误：

1. 按 `F12` 或 `Cmd+Option+I` (Mac) 打开开发者工具
2. 切换到 "Console" (控制台) 标签
3. 刷新页面
4. 查看是否有红色错误信息

### 应该看到的正常日志
```
Event listeners attached to X buttons
```

### 点击按钮后应该看到
```
Button clicked!
Article ID: 123
openArticle called with id: 123
Article data received: {success: true, data: {...}}
```

## 步骤3：使用测试页面

我创建了一个简单的测试页面来验证功能：

```bash
# 打开测试页面
open http://localhost:8080/test.html
```

或在浏览器中访问：http://localhost:8080/test.html

### 测试页面功能
1. 点击测试卡片右上角的➜按钮
2. 应该看到"成功！按钮被点击了"的消息
3. 点击"测试API"按钮
4. 应该看到文章列表
5. 点击"测试打开这篇文章"按钮
6. 应该看到文章详情加载成功

如果测试页面正常工作，说明代码没问题，是主页面的缓存问题。

## 步骤4：检查服务器状态

确保后端服务正在运行：

```bash
# 检查服务器是否运行
curl http://localhost:3000/health

# 检查文章API
curl http://localhost:3000/api/articles

# 检查特定文章
curl http://localhost:3000/api/articles/8
```

### 预期输出
```json
{
  "success": true,
  "data": [...]
}
```

## 步骤5：检查HTML文件

验证HTML文件是否包含最新代码：

```bash
# 检查是否有事件绑定代码
grep -A 5 "addEventListener.*view-detail-btn" demo-web/index.html

# 检查是否有data-article-id属性
grep "data-article-id" demo-web/index.html
```

应该能看到相关代码。

## 步骤6：重启服务器

如果以上都不行，尝试重启服务器：

```bash
# 停止当前服务器 (Ctrl+C)

# 重新启动
cd backend
node production-server.js

# 在另一个终端启动web服务器
cd demo-web
python3 -m http.server 8080
```

## 步骤7：检查网络请求

在浏览器开发者工具中：

1. 切换到 "Network" (网络) 标签
2. 刷新页面
3. 查看是否成功加载 `index.html`
4. 点击按钮后，查看是否有 `/api/articles/X` 的请求

## 常见问题

### Q: 按钮显示但点击没反应
A: 这通常是浏览器缓存问题。强制刷新页面（Cmd+Shift+R）。

### Q: 控制台显示"openArticle is not defined"
A: JavaScript代码可能没有正确加载。检查HTML文件是否完整。

### Q: 控制台显示"Failed to fetch"
A: 后端服务器可能没有运行。检查 http://localhost:3000/health

### Q: 按钮根本不显示
A: CSS可能没有加载。检查页面源代码。

### Q: 点击后显示"加载文章失败"
A: API返回了错误。检查后端日志和数据库。

## 快速诊断命令

运行以下命令进行快速诊断：

```bash
# 1. 检查服务器
echo "=== 检查后端服务 ==="
curl -s http://localhost:3000/health | python3 -m json.tool

# 2. 检查文章数量
echo -e "\n=== 检查文章数量 ==="
sqlite3 backend/data/didaxueshu.db "SELECT COUNT(*) FROM articles"

# 3. 检查HTML文件
echo -e "\n=== 检查HTML代码 ==="
grep -c "addEventListener" demo-web/index.html
grep -c "data-article-id" demo-web/index.html

# 4. 检查进程
echo -e "\n=== 检查运行进程 ==="
lsof -i :3000
lsof -i :8080
```

## 如果还是不行

请提供以下信息：

1. 浏览器类型和版本
2. 浏览器控制台的完整错误信息
3. 网络标签中的请求列表
4. 运行上述诊断命令的输出

## 临时解决方案

如果急需使用，可以直接访问API：

```bash
# 获取文章列表
open http://localhost:3000/api/articles

# 查看特定文章（替换ID）
open http://localhost:3000/api/articles/8
```

或者使用curl：

```bash
# 查看文章详情
curl http://localhost:3000/api/articles/8 | python3 -m json.tool
```

## 联系支持

如果以上步骤都无法解决问题，请：

1. 截图浏览器控制台的错误信息
2. 提供诊断命令的输出
3. 说明具体的操作步骤和现象

这将帮助快速定位问题！
