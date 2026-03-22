# 开源发布检查清单

在将项目推送到 GitHub 之前，请确保完成以下检查：

## ✅ 代码清理

- [x] 移除所有硬编码的 API Keys
- [x] 更新 .env.example 文件，移除敏感信息
- [x] 确认 .gitignore 正确配置
- [x] 检查所有服务文件使用环境变量

## ✅ 文档完善

- [x] 创建 README.md
- [x] 创建 LICENSE 文件
- [x] 创建 CONTRIBUTING.md
- [x] 添加 API Key 获取指南

## ✅ 功能实现

- [x] 用户可配置 API Key 的数据库模型
- [x] API Key 管理的后端接口
- [x] 设置页面的前端界面
- [x] 所有 AI 服务支持用户自定义 Key

## ✅ 安全检查

- [ ] 运行 `git log` 确认历史提交中没有敏感信息
- [ ] 检查 .env 文件未被提交
- [ ] 确认所有 API Key 都已加密存储
- [ ] 测试没有 API Key 时的降级处理

## ✅ 测试验证

- [ ] 后端服务正常启动
- [ ] 前端应用正常运行
- [ ] 设置页面可以添加/删除 API Key
- [ ] AI 功能使用用户配置的 Key
- [ ] 数据库迁移脚本正常运行

## 📝 发布步骤

### 1. 最终检查

```bash
# 检查是否有未提交的敏感文件
git status

# 查看将要提交的内容
git diff

# 确认 .env 文件被忽略
git check-ignore .env
```

### 2. 清理历史（如果需要）

如果之前的提交中包含敏感信息，需要清理历史：

```bash
# 使用 BFG Repo-Cleaner 或 git filter-branch
# 警告：这会重写历史，需要强制推送

# 示例：移除所有 .env 文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### 3. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库（不要初始化 README）
3. 记录仓库 URL

### 4. 推送代码

```bash
# 添加远程仓库
git remote add origin https://github.com/yourusername/quantywind.git

# 推送代码
git push -u origin main
```

### 5. 配置 GitHub 仓库

1. 添加项目描述和标签
2. 设置 GitHub Pages（如果需要）
3. 配置 Issues 模板
4. 添加 GitHub Actions（CI/CD）

### 6. 发布第一个版本

```bash
# 创建标签
git tag -a v1.0.0 -m "First public release"

# 推送标签
git push origin v1.0.0
```

### 7. 在 GitHub 上创建 Release

1. 访问仓库的 Releases 页面
2. 点击 "Create a new release"
3. 选择 v1.0.0 标签
4. 填写发布说明
5. 发布

## 🎉 发布后

- [ ] 在社交媒体分享项目
- [ ] 提交到开源项目目录（如 awesome-lists）
- [ ] 监控 Issues 和 Pull Requests
- [ ] 定期更新文档和依赖

## ⚠️ 注意事项

1. **永远不要提交敏感信息**
   - API Keys
   - 密码
   - 私钥
   - 个人信息

2. **保持文档更新**
   - README 应该始终反映最新功能
   - API 文档要与代码同步

3. **及时响应社区**
   - 回复 Issues
   - 审查 Pull Requests
   - 感谢贡献者

4. **遵循语义化版本**
   - MAJOR.MINOR.PATCH
   - 主版本号：不兼容的 API 修改
   - 次版本号：向下兼容的功能性新增
   - 修订号：向下兼容的问题修正

## 📞 需要帮助？

如果在开源发布过程中遇到问题：

1. 查看 GitHub 官方文档
2. 搜索相关问题
3. 在项目 Issues 中提问
4. 联系维护者

---

祝开源之旅顺利！🚀
