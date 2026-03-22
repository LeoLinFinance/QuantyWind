# Alpha Vantage API 集成指南

## 为什么选择Alpha Vantage

经过测试，Yahoo Finance已经完全封锁了免费API访问。Alpha Vantage是目前最好的免费替代方案：

✅ **官方支持** - 稳定可靠的API服务
✅ **免费版本** - 无需信用卡，邮箱注册即可
✅ **数据完整** - 20年+历史数据
✅ **数据准确** - 专业的金融数据提供商

## 免费版限制

- **请求频率**: 5次/分钟
- **每日请求**: 500次/天
- **数据延迟**: 实时数据

**对我们的影响**:
- 首次更新12个标的需要约3分钟（12 × 12秒间隔）
- 每天可以更新约40次（500次 ÷ 12个标的）
- 完全够用！

## 注册步骤

### 1. 访问注册页面

打开浏览器访问：
```
https://www.alphavantage.co/support/#api-key
```

### 2. 填写注册信息

- **Email**: 你的邮箱地址
- **Organization**: 可以填 "Personal" 或 "Individual"
- **Purpose**: 选择 "Personal/Educational"

### 3. 获取API Key

提交后会立即显示你的API key，类似：
```
ABCD1234EFGH5678
```

**重要**: 保存好这个key，后面需要用到！

### 4. 验证邮箱（可选）

检查邮箱，可能会收到确认邮件。

## 配置步骤

### 1. 打开.env文件

```bash
nano .env
```

或使用任何文本编辑器打开项目根目录下的 `.env` 文件。

### 2. 添加API Key

在文件中添加或修改以下行：

```env
ALPHA_VANTAGE_API_KEY=你的API_KEY
```

例如：
```env
ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678
```

### 3. 保存文件

保存并关闭编辑器。

### 4. 重启后端服务

```bash
cd backend
python3 main.py
```

## 测试API Key

### 方法1: 使用测试脚本

```bash
python3 test_alpha_vantage.py
```

### 方法2: 手动测试

```bash
python3 -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

if not api_key:
    print('❌ 未找到API key')
else:
    print(f'✅ API key已设置: {api_key[:4]}...{api_key[-4:]}')
    
    # 测试API
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'AAPL',
        'apikey': api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'Time Series (Daily)' in data:
        print('✅ API测试成功！')
        dates = list(data['Time Series (Daily)'].keys())
        print(f'获取到 {len(dates)} 天的数据')
        print(f'最新日期: {dates[0]}')
    elif 'Error Message' in data:
        print(f'❌ API错误: {data[\"Error Message\"]}')
    elif 'Note' in data:
        print(f'⚠️ API限流: {data[\"Note\"]}')
    else:
        print(f'❌ 未知错误: {data}')
"
```

## 使用历史数据更新功能

### 1. 打开浏览器

访问: http://localhost:5173

### 2. 进入风险分析看板

点击导航栏的"风险分析看板"

### 3. 打开数据集管理

点击"📊 数据集管理"按钮

### 4. 更新历史数据

点击"🔄 更新历史数据集"按钮

### 5. 观察更新过程

**后端控制台会显示**:

```
============================================================
开始更新历史数据
盯盘股票: ['AAPL', 'MSFT', 'TSLA', ...]
============================================================

📊 更新市场指数...

处理指数: ^IXIC
📥 更新 ^IXIC 从 2016-03-10 到 2026-03-10
📥 正在从Alpha Vantage获取 ^IXIC 的历史数据...
✅ ^IXIC 成功获取 2500 条数据
⏳ 等待12秒（API限流保护）...
✅ ^IXIC 更新了 2500 条数据

处理指数: ^GSPC
📥 更新 ^GSPC 从 2016-03-10 到 2026-03-10
📥 正在从Alpha Vantage获取 ^GSPC 的历史数据...
✅ ^GSPC 成功获取 2500 条数据
⏳ 等待12秒（API限流保护）...
✅ ^GSPC 更新了 2500 条数据

... (继续处理其他标的)

============================================================
更新完成!
成功: 12 个
失败: 0 个
============================================================
```

**预计耗时**: 约3分钟（12个标的 × 12秒间隔 + 处理时间）

### 6. 查看结果

前端应该显示：
```
数据更新完成！
成功: 12个
失败: 0个
```

数据集统计应该显示：
- 市场指数: 3
- 活跃股票: 9
- 总数据点数: 30000+

## API限流处理

### 自动保护机制

代码已经实现了自动限流保护：

1. **请求间隔**: 每次请求后自动等待12秒
2. **限流检测**: 如果收到限流响应，会提示用户
3. **错误处理**: 优雅处理各种API错误

### 如果遇到限流

**错误信息**:
```
⚠️ AAPL API限流: Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute...
```

**解决方案**:
1. 等待1分钟后重试
2. 或者升级到付费版（30次/分钟）

### 每日请求限制

**免费版**: 500次/天

**我们的使用**:
- 首次更新: 12次（3个指数 + 9个股票）
- 日常增量更新: 12次
- 每天可以更新约40次

**建议**:
- 不要频繁点击更新按钮
- 每天更新1-2次即可
- 使用增量更新节省请求次数

## 数据质量

### Alpha Vantage vs Yahoo Finance

| 特性 | Alpha Vantage | Yahoo Finance |
|------|---------------|---------------|
| 可用性 | ✅ 可用 | ❌ 封锁 |
| 数据准确性 | ✅ 高 | ✅ 高 |
| 历史数据 | ✅ 20年+ | ✅ 20年+ |
| 免费版限制 | 5次/分钟 | 完全封锁 |
| 稳定性 | ✅ 稳定 | ❌ 不稳定 |

### 数据字段

Alpha Vantage提供完整的OHLCV数据：
- Open（开盘价）
- High（最高价）
- Low（最低价）
- Close（收盘价）
- Volume（成交量）

## 常见问题

### Q1: API key在哪里找？

A: 注册后立即显示，也会发送到你的邮箱。如果丢失，可以重新注册一个新邮箱。

### Q2: 免费版够用吗？

A: 对于我们的使用场景完全够用。每天更新1-2次，远低于500次限制。

### Q3: 可以获取实时数据吗？

A: 免费版提供的是实时数据（无延迟），但有请求频率限制。

### Q4: 支持哪些股票市场？

A: 支持美股、港股、A股等全球主要市场。

### Q5: 如果需要更高频率怎么办？

A: 可以升级到付费版：
- Premium: $49.99/月，30次/分钟
- Enterprise: 定制方案

### Q6: 数据会自动更新吗？

A: 不会，需要手动点击"更新历史数据集"按钮。这样可以控制API使用量。

### Q7: 可以同时更新多个标的吗？

A: 代码会串行更新（一个接一个），自动处理API限流。

### Q8: 更新失败怎么办？

A: 查看后端控制台的错误信息：
- 如果是限流，等待1分钟后重试
- 如果是API key错误，检查.env配置
- 如果是网络错误，检查网络连接

## 升级到付费版（可选）

如果需要更高的请求频率，可以升级：

### Premium计划 ($49.99/月)
- 30次/分钟
- 无每日限制
- 优先支持

### 升级步骤
1. 访问：https://www.alphavantage.co/premium/
2. 选择计划并付款
3. 获取新的API key
4. 更新.env文件中的API key

## 备用方案

如果Alpha Vantage也无法满足需求，还有以下选项：

1. **Polygon.io** - 免费版5次/分钟
2. **IEX Cloud** - 免费版50,000次/月
3. **Quandl** - 部分数据免费
4. **本地CSV文件** - 手动下载数据

## 总结

Alpha Vantage是目前最好的免费历史数据解决方案：

✅ 稳定可靠
✅ 数据准确
✅ 免费版够用
✅ 易于集成

现在请：
1. 注册Alpha Vantage账号
2. 获取API key
3. 配置到.env文件
4. 重启后端服务
5. 测试历史数据更新

---

**文档创建时间**: 2026年3月10日
**API提供商**: Alpha Vantage
**免费版限制**: 5次/分钟，500次/天
**状态**: ✅ 可用
