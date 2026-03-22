# 美股市场舆情与风险分析平台

一个实时监控美股市场舆情、分析风险并提供可视化洞察的综合平台。

## 核心功能

### 1. 市场洞察盯盘页
- 盘前至盘后每15分钟更新市场洞察
- 实时追踪纳斯达克、标普500、罗素2000指数
- 个股盯盘（支持自定义添加）
- AI生成的舆情影响分析

### 2. 风险分析看板页
- 20+种专业风险模型（VaR、ES、GARCH、EWMA等）
- 每小时更新风险指标
- 模型准确率和有效性指标（R²、MAE、RMSE）
- 可视化风险数据展示

### 3. 市场风险舆情地图页
- 全球风险舆情地图标注
- AI自动识别舆情地区和风险等级
- 不确定地区舆情单独展示
- 每小时更新舆情数据

## 技术栈

### 前端
- React 18 + TypeScript
- Tailwind CSS（样式）
- React Router（路由）
- Recharts（图表）
- React Simple Maps（地图）
- Axios（HTTP请求）

### 后端
- Python FastAPI
- Pandas + NumPy（数据处理）
- APScheduler（定时任务）
- Scipy + Scikit-learn（风险模型）

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- npm 或 yarn

### 安装步骤

1. 克隆项目并安装前端依赖：
```bash
npm install
```

2. 安装后端依赖：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入API密钥
```

4. 启动后端服务：
```bash
cd backend
python main.py
```

5. 启动前端开发服务器（新终端）：
```bash
npm run dev
```

6. 访问应用：
打开浏览器访问 http://localhost:3000

## API密钥获取

### 免费API资源
- **NewsAPI**: https://newsapi.org/ （舆情数据）
- **IEX Cloud**: https://iexcloud.io/ （美股数据，免费版）
- **Polygon.io**: https://polygon.io/ （市场数据，免费版）
- **OpenAI**: https://platform.openai.com/ （AI分析，有免费额度）

## 项目结构

```
.
├── src/                    # 前端源码
│   ├── components/         # React组件
│   ├── pages/             # 页面组件
│   │   ├── MarketInsightPage.tsx
│   │   ├── RiskAnalysisPage.tsx
│   │   └── SentimentMapPage.tsx
│   ├── App.tsx
│   └── main.tsx
├── backend/               # 后端源码
│   ├── routers/          # API路由
│   ├── services/         # 业务逻辑
│   │   ├── market_service.py
│   │   ├── risk_service.py
│   │   ├── sentiment_service.py
│   │   └── scheduler.py
│   └── main.py
├── package.json
├── requirements.txt
└── README_PROJECT.md
```

## 数据更新频率

- 市场洞察：每15分钟（交易时段）/ 每2小时（非交易时段）
- 风险分析：每1小时
- 舆情地图：每1小时

## 风险模型列表

平台集成20+种专业风险模型：

1. VaR（风险价值）
2. ES（预期损失）
3. GARCH波动率模型
4. EWMA波动率模型
5. Amihud流动性比率
6. Pearson相关系数
7. RSI超买超卖
8. MACD背离
9. 舆情情绪回归
10. EVT极值理论
11. PE分位数
12. PB分位数
13. Beta系数
14. Sharpe比率
15. 最大回撤
16. Sortino比率
17. 波动率偏度
18. 波动率峰度
19. 换手率风险
20. 舆情传播速度

每个模型包含：
- 模型值
- 准确率（基于历史回测）
- 有效性指标（R²、MAE、RMSE）
- 参数配置
- 适用场景说明

## 合规声明

本平台提供的所有分析和数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。请在做出投资决策前咨询专业的财务顾问。

数据来源：NewsAPI、IEX Cloud、Polygon.io等免费API服务。

## 后续开发计划

- [ ] 接入真实API数据源
- [ ] 集成OpenAI/Claude进行AI分析
- [ ] 用户注册和个性化设置
- [ ] 邮件预警功能
- [ ] 风险模型对比功能
- [ ] 数据导出功能
- [ ] 移动端适配
- [ ] 历史数据回测

## 许可证

MIT License
