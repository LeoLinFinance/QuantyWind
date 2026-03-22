# 数据持久化 - 快速开始

## 🚀 立即使用

数据持久化功能已经自动启用，无需任何配置！

### 自动保存的数据

1. **盯盘股票列表** - 添加或删除股票时自动保存
2. **AI系统提示词** - 修改提示词时自动保存
3. **用户设置** - 修改设置时自动保存

### 验证功能

运行测试脚本验证持久化功能：

```bash
python3 test_persistence.py
```

预期输出：
```
✅ 持久化服务测试通过
✅ MarketService成功加载持久化数据
✅ 数据信息查询成功
✅ 重启后数据成功恢复
🎉 所有测试通过！
```

## 📋 使用场景

### 场景1：添加股票到盯盘

1. 在前端添加股票（如TSLA）
2. 后端自动保存到 `data/config/watchlist.json`
3. 重启后端
4. ✅ TSLA仍在盯盘列表中

### 场景2：自定义AI提示词

1. 在前端修改系统提示词
2. 后端自动保存到 `data/config/system_prompt.json`
3. 重启后端
4. ✅ 自定义提示词仍然生效

### 场景3：开发调试

1. 配置好盯盘列表和提示词
2. 修改代码并重启后端
3. ✅ 无需重新配置，直接继续开发

## 🔍 查看数据

### 方法1：查看JSON文件

```bash
# 查看盯盘列表
cat backend/data/config/watchlist.json

# 查看系统提示词
cat backend/data/config/system_prompt.json
```

### 方法2：使用API

```bash
# 获取所有数据信息
curl http://localhost:8000/api/persistence/info

# 获取盯盘列表
curl http://localhost:8000/api/persistence/watchlist

# 获取系统提示词
curl http://localhost:8000/api/persistence/system-prompt
```

## 🛠️ 管理数据

### 备份数据

```bash
# 备份配置目录
cp -r backend/data/config backend/data/config.backup
```

### 恢复数据

```bash
# 恢复配置
cp -r backend/data/config.backup/* backend/data/config/
```

### 清除数据

```bash
# 方法1：使用API
curl -X DELETE http://localhost:8000/api/persistence/clear-all

# 方法2：直接删除文件
rm backend/data/config/*.json
```

## ❓ 常见问题

### Q: 数据保存在哪里？
A: `backend/data/config/` 目录下的JSON文件

### Q: 会自动保存吗？
A: 是的，添加/删除/修改时自动保存

### Q: 重启后会丢失吗？
A: 不会，数据会自动恢复

### Q: 可以手动编辑JSON文件吗？
A: 可以，但建议重启后端使更改生效

### Q: 如何迁移到新环境？
A: 复制 `backend/data/config/` 目录即可

## 📚 更多信息

- 详细说明：`DATA_PERSISTENCE_GUIDE.md`
- 实现总结：`PERSISTENCE_IMPLEMENTATION_SUMMARY.md`
- 测试脚本：`test_persistence.py`

---

**提示**：数据持久化功能已经在后台默默工作，您只需正常使用即可！
