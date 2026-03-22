# 智者论坛 - 快速启动指南

## 一键启动

### 1. 安装依赖（首次运行）

```bash
# 前端依赖（可选，如果不想安装@headlessui/react，已有备用实现）
# npm install @headlessui/react

# 后端依赖已在requirements.txt中
```

### 2. 启动服务

在项目根目录打开两个终端：

**终端1 - 启动后端**
```bash
cd backend
python main.py
```

**终端2 - 启动前端**
```bash
npm run dev
```

### 3. 访问智者论坛

打开浏览器访问：http://localhost:5173/expert-forum

## 功能演示

### 场景1：获取市场资讯

1. 点击"接收资讯"开关（打开）
2. 等待几秒，KimiClaw会返回最新的市场资讯
3. 资讯会显示在对话区域
4. 之后每小时自动更新一次

### 场景2：专家讨论

1. 确保已有一些上下文信息（可以先开启资讯接收）
2. 点击"开始讨论"开关（打开）
3. 5位专家会依次发言：
   - 选股分析师（如果今天还没调用过）
   - 产业链分析师
   - 市场分析师
   - 长期价值投资分析师
   - 首席经济学家
4. 每位专家的分析会依次显示在对话区域

### 场景3：配置专家提示词

1. 点击"配置专家"按钮
2. 在弹出的模态框中选择要编辑的专家
3. 点击"编辑"按钮
4. 修改提示词内容
5. 点击"保存"保存配置
6. 配置会自动保存到`data/expert_configs.json`

## 测试数据准备

### 添加测试持仓

运行以下Python脚本添加测试持仓：

```python
import sys
sys.path.append('backend')

from services.portfolio_service import PortfolioService

portfolio_service = PortfolioService()

# 添加测试持仓
portfolio_service.add_holding('AAPL', 100, 150.0)  # 苹果
portfolio_service.add_holding('TSLA', 50, 200.0)   # 特斯拉
portfolio_service.add_holding('NVDA', 30, 400.0)   # 英伟达
portfolio_service.add_holding('MSFT', 80, 300.0)   # 微软
portfolio_service.add_holding('GOOGL', 40, 120.0)  # 谷歌

print("✅ 测试持仓已添加")
```

或者直接运行测试脚本：

```bash
python test_expert_forum.py
```

## 常见问题

### Q1: 页面显示空白
**A**: 检查浏览器控制台是否有错误，确认后端服务是否正常运行

### Q2: 专家分析很慢
**A**: 这是正常的，因为每个专家都需要调用Kimi API进行在线研究，每次大约需要10-30秒

### Q3: 提示"请等待X分钟后再次调用"
**A**: 这是频率限制保护，每10分钟只能调用一次专家讨论

### Q4: 选股分析师没有发言
**A**: 选股分析师每天只调用一次，如果今天已经调用过，会自动跳过

### Q5: 配置保存后刷新页面丢失
**A**: 配置应该会自动保存到文件，检查`data/expert_configs.json`是否存在且有写入权限

## 目录结构

```
.
├── src/
│   └── pages/
│       └── ExpertForumPage.tsx          # 智者论坛页面
├── backend/
│   ├── routers/
│   │   └── expert_forum.py              # API路由
│   └── services/
│       ├── expert_forum_service.py      # 核心服务
│       ├── portfolio_service.py         # 投资组合服务
│       └── kimi_research_service.py     # Kimi API服务
├── data/
│   ├── expert_configs.json              # 专家配置（自动生成）
│   └── portfolio.json                   # 投资组合（自动生成）
├── EXPERT_FORUM_SETUP.md                # 详细设置说明
├── KIMICLAW_INTEGRATION.md              # KimiClaw集成说明
└── test_expert_forum.py                 # 测试脚本
```

## API端点

所有API端点都在 `http://localhost:8000/api/expert-forum/` 下：

- `POST /news` - 获取新闻资讯
- `POST /news/stop` - 停止新闻推送
- `POST /expert-analysis` - 获取专家分析
- `GET /configs` - 获取专家配置
- `POST /configs` - 保存专家配置

## 下一步

1. 根据实际需求调整专家提示词
2. 添加更多测试持仓
3. 如果有独立的KimiClaw服务，参考`KIMICLAW_INTEGRATION.md`进行集成
4. 根据使用情况优化API调用频率

## 技术支持

如有问题，请检查：
1. 后端日志输出
2. 浏览器控制台错误
3. 网络请求状态（F12 -> Network）
4. 数据文件权限
