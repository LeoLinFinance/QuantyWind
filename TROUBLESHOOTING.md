# 智者论坛故障排除指南

## 问题：专家和资讯不说话

### 症状
- 打开"接收资讯"和"开始讨论"开关
- 只显示系统消息："专家讨论开始..."、"提示：建议先开启..."、"专家讨论完成"
- 没有实际的资讯内容和专家分析

### 根本原因
**后端服务未启动！**

## 解决步骤

### 步骤1: 检查后端是否运行

```bash
# 方法1: 检查进程
ps aux | grep "python.*main"

# 方法2: 检查端口
lsof -i :8000

# 方法3: 测试API
curl http://localhost:8000/
```

如果没有输出或报错，说明后端未运行。

### 步骤2: 启动后端

```bash
# 进入项目目录
cd /Users/linyuxi/字节

# 启动后端
python3 backend/main.py
```

你应该看到类似的输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 步骤3: 初始化专家配置（如果还没做）

在另一个终端：
```bash
cd /Users/linyuxi/字节
python3 init_expert_configs.py
```

### 步骤4: 验证后端工作

```bash
python3 check_backend_status.py
```

应该看到：
```
✅ 后端正在运行
✅ 找到 5 个专家配置
✅ 新闻获取成功
✅ 对话历史包含 X 条消息
```

### 步骤5: 刷新前端

1. 在浏览器中刷新页面（F5或Cmd+R）
2. 打开"接收资讯"开关
3. 等待1-2秒，应该看到蓝色的新闻总结
4. 打开"开始讨论"开关
5. 等待1-3分钟，应该看到绿色的专家分析

## 常见问题

### Q1: 后端启动失败
**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
pip3 install -r requirements.txt
```

### Q2: 端口被占用
**错误**: `Address already in use`

**解决**:
```bash
# 找到占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或者修改端口
# 编辑 backend/main.py，将 port=8000 改为 port=8001
```

### Q3: 前端连接不上后端
**错误**: 浏览器控制台显示 `Failed to fetch` 或 `Network Error`

**检查**:
1. 后端是否在运行？
2. 端口是否正确？（默认8000）
3. 前端API地址是否正确？（检查 `src/pages/ExpertForumPage.tsx` 中的 `http://localhost:8000`）

### Q4: 专家分析超时
**症状**: 等待很久后显示"专家讨论完成"，但没有分析内容

**原因**: Kimi API调用时间长（20-40秒/专家）

**解决**: 
- 耐心等待（5个专家需要1.5-3分钟）
- 检查后端日志是否有错误
- 检查 `.env` 文件中的 `KIMI_API_KEY` 是否配置

### Q5: 新闻总结不显示
**症状**: 打开"接收资讯"后没有反应

**检查**:
1. 后端日志是否有错误
2. StepFun API是否配置（`.env` 中的 `STEPFUN_API_KEY`）
3. 网络连接是否正常

## 完整启动流程

### 终端1: 启动后端
```bash
cd /Users/linyuxi/字节
python3 backend/main.py
```

保持这个终端运行，不要关闭。

### 终端2: 启动前端（如果需要）
```bash
cd /Users/linyuxi/字节
npm run dev
```

### 浏览器
访问 `http://localhost:5173`（或前端显示的地址）

## 验证清单

- [ ] 后端正在运行（`ps aux | grep python.*main`）
- [ ] 端口8000可访问（`curl http://localhost:8000/`）
- [ ] 专家配置已初始化（`python3 init_expert_configs.py`）
- [ ] 前端已启动（`npm run dev`）
- [ ] 浏览器已打开智者论坛页面
- [ ] 打开"接收资讯"后1-2秒内显示新闻
- [ ] 打开"开始讨论"后1-3分钟内显示专家分析

## 调试工具

### 1. 检查后端状态
```bash
python3 check_backend_status.py
```

### 2. 诊断专家论坛
```bash
python3 diagnose_expert_forum.py
```

### 3. 测试简单专家调用
```bash
python3 test_simple_expert.py
```

### 4. 查看后端日志
后端终端会显示所有API调用和错误信息。

### 5. 查看浏览器控制台
按F12打开开发者工具，查看Console和Network标签。

## 联系支持

如果以上步骤都无法解决问题，请提供：
1. 后端日志（终端输出）
2. 浏览器控制台错误
3. `python3 check_backend_status.py` 的输出
4. 截图

## 快速修复命令

```bash
# 一键检查和修复
cd /Users/linyuxi/字节

# 1. 初始化配置
python3 init_expert_configs.py

# 2. 检查状态
python3 check_backend_status.py

# 3. 如果后端未运行，启动它
python3 backend/main.py
```
