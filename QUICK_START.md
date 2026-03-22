# 量数风行 QuantyWind - 快速启动指南

## 项目简介
个人美股舆情风险专家 - 实时市场洞察、风险分析、舆情地图

## 功能概览

### 1. 市场洞察盯盘页 📊
- 实时美股指数（纳斯达克、S&P500、罗素2000）
- 个股盯盘（默认10只热门股票）
- AI舆情分析（基于实时新闻）
- 成交量周趋势可视化
- 每15分钟自动更新

### 2. 风险分析看板页 📈
- 20+专业风险模型（VaR、ES等）
- 实时风险指标计算
- 历史数据回测
- 模型准确率展示
- 每1小时自动更新

### 3. 市场风险舆情地图页 🌍
- AI智能风险分类（高/中/低）
- 世界地图可视化
- 实时新闻分析
- 地理位置自动识别
- 每1小时自动更新

## 环境要求

- Node.js 16+
- Python 3.8+
- npm 或 yarn

## 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入API密钥：
```
# 阶跃星辰 API Key
STEPFUN_API_KEY=1yJ2pD9HyHqZ6I4FxytOJZZWvv9dJjqyy5l9OUuOL6qB9XOgMjaAI3XXe8cDS4fKW

# Kimi API Key (备用)
KIMI_API_KEY=sk-kimi-FJDncfhpX6spNzcJDfrAde70wqotpAuKxhvUfZHmHP8fbyOYdGCa0WYAhP8FT7Hv
```

### 3. 安装前端依赖
```bash
npm install
```

### 4. 安装后端依赖
```bash
pip3 install -r requirements.txt
```

## 启动应用

### 方式一：分别启动（推荐开发环境）

**终端1 - 启动后端**
```bash
cd backend
python3 main.py
```
后端将运行在: http://localhost:8000

**终端2 - 启动前端**
```bash
npm run dev
```
前端将运行在: http://localhost:5173

### 方式二：使用脚本启动

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

## 访问应用

打开浏览器访问: http://localhost:5173

## 测试功能

### 测试舆情地图AI分析
```bash
python3 test_sentiment_map.py
```

### 测试市场数据获取
```bash
cd backend
python3 -c "from services.market_service import MarketService; ms = MarketService(); print(ms.get_market_overview())"
```

## 功能使用指南

### 市场洞察盯盘页
1. 查看实时指数和个股价格
2. 点击"搜索股票"添加自定义盯盘股
3. 点击"启用AI分析"获取舆情洞察
4. 点击"编辑提示词"自定义AI分析角度
5. 点击删除按钮移除不需要的股票

### 风险分析看板页
1. 查看各类风险模型指标
2. 切换不同风险模型查看详情
3. 查看模型准确率和有效性
4. 筛选个股/指数查看对应风险

### 市场风险舆情地图页
1. 查看世界地图上的风险事件标记
2. 使用风险等级筛选（全部/高/中/低）
3. 点击地图标记查看事件详情
4. 查看不确定地区事件列表
5. 点击"查看详情"链接阅读完整新闻

## 数据更新频率

- **市场洞察**: 每15分钟（盘前至盘后）
- **风险分析**: 每1小时
- **舆情地图**: 每1小时

## API端点

### 市场数据
- `GET /api/market-overview` - 市场概览
- `GET /api/watchlist` - 盯盘股票列表
- `POST /api/watchlist` - 添加盯盘股票
- `DELETE /api/watchlist/{symbol}` - 删除盯盘股票
- `GET /api/search/{symbol}` - 搜索股票

### 风险分析
- `GET /api/risk-analysis` - 风险分析数据

### 舆情地图
- `GET /api/sentiment-map` - 舆情地图数据

## 故障排除

### 问题1: 后端启动失败
**解决方案**: 检查Python版本和依赖安装
```bash
python3 --version  # 应该 >= 3.8
pip3 install -r requirements.txt
```

### 问题2: 前端启动失败
**解决方案**: 清除缓存并重新安装
```bash
rm -rf node_modules package-lock.json
npm install
```

### 问题3: API调用失败
**解决方案**: 检查.env文件中的API密钥是否正确配置

### 问题4: 数据不更新
**解决方案**: 手动点击刷新按钮，或检查网络连接

## 技术栈

### 前端
- React 18
- TypeScript
- Vite
- TailwindCSS
- Recharts (图表)
- react-simple-maps (地图)

### 后端
- FastAPI
- Python 3.8+
- feedparser (RSS解析)
- requests (HTTP请求)

### AI模型
- 阶跃星辰 (StepFun)
- Kimi (备用)

## 项目结构

```
.
├── backend/
│   ├── main.py                 # 后端入口
│   ├── routers/                # API路由
│   │   ├── market.py
│   │   ├── risk.py
│   │   └── sentiment.py
│   └── services/               # 业务逻辑
│       ├── market_service.py
│       ├── risk_service.py
│       ├── sentiment_service.py
│       ├── news_service.py
│       ├── ai_service.py
│       └── yahoo_finance_api.py
├── src/
│   ├── App.tsx                 # 前端入口
│   ├── components/             # 组件
│   │   ├── Layout.tsx
│   │   └── VolumeSparkline.tsx
│   └── pages/                  # 页面
│       ├── MarketInsightPage.tsx
│       ├── RiskAnalysisPage.tsx
│       └── SentimentMapPage.tsx
├── .env                        # 环境变量
├── requirements.txt            # Python依赖
├── package.json                # Node依赖
└── README.md                   # 项目说明
```

## 性能优化

1. **缓存机制**: 所有数据服务都实现了缓存
2. **按需加载**: 页面切换不重新加载数据
3. **批量处理**: AI分析采用批量处理
4. **异步请求**: 所有API调用都是异步的

## 安全说明

1. **API密钥**: 请妥善保管.env文件，不要提交到版本控制
2. **数据来源**: 所有数据来自公开免费API
3. **风险声明**: 本系统仅供分析参考，不构成投资建议

## 联系支持

如有问题，请查看以下文档：
- `ARCHITECTURE.md` - 系统架构说明
- `DEVELOPMENT_GUIDE.md` - 开发指南
- `SENTIMENT_MAP_COMPLETE.md` - 舆情地图功能说明
- `NEWS_INTEGRATION_COMPLETE.md` - 新闻集成说明

## 更新日志

### 2026-03-10
- ✅ 完成市场风险舆情地图AI分析功能
- ✅ 优化风险等级分类算法
- ✅ 改进地理位置识别准确率
- ✅ 修复TypeScript类型错误
- ✅ 添加功能测试脚本

### 之前版本
- ✅ 实时新闻集成
- ✅ AI舆情分析
- ✅ 成交量趋势可视化
- ✅ 股票搜索和盯盘管理
- ✅ 页面导航性能优化

---

**量数风行 QuantyWind** - 让数据洞察风险，让风险可视可控
