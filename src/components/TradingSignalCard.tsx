interface TradingSignalCardProps {
  signal: any
  loading: boolean
}

export default function TradingSignalCard({ signal, loading }: TradingSignalCardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">生成交易信号中...</span>
        </div>
      </div>
    )
  }

  if (!signal) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-center text-gray-500">暂无交易信号</p>
      </div>
    )
  }

  if (signal.error) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start">
              <span className="text-3xl mr-3">❌</span>
              <div className="flex-1">
                <h4 className="text-lg font-semibold text-red-800 mb-2">信号生成失败</h4>
                <p className="text-sm text-red-700 mb-3">{signal.message}</p>
                {signal.details && (
                  <div className="bg-red-100 rounded p-3 text-xs text-red-800">
                    <p className="font-semibold mb-1">详细信息：</p>
                    <p>{signal.details}</p>
                  </div>
                )}
                <div className="mt-4 space-y-2 text-sm text-red-700">
                  <p className="font-semibold">可能的解决方案：</p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>确认后端服务已启动（端口8000）</li>
                    <li>检查.env文件中的API密钥配置（STEPFUN_API_KEY或KIMI_API_KEY）</li>
                    <li>查看浏览器控制台和后端日志获取详细错误信息</li>
                    <li>确认该股票代码有足够的历史数据</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case 'strong_buy':
        return 'bg-green-600 text-white'
      case 'buy':
        return 'bg-green-500 text-white'
      case 'hold':
        return 'bg-gray-500 text-white'
      case 'sell':
        return 'bg-red-500 text-white'
      case 'strong_sell':
        return 'bg-red-600 text-white'
      default:
        return 'bg-gray-500 text-white'
    }
  }

  const getSignalText = (signalType: string) => {
    switch (signalType) {
      case 'strong_buy':
        return '强烈买入'
      case 'buy':
        return '买入'
      case 'hold':
        return '持有'
      case 'sell':
        return '卖出'
      case 'strong_sell':
        return '强烈卖出'
      default:
        return '持有'
    }
  }

  const getSignalIcon = (signalType: string) => {
    if (signalType.includes('buy')) {
      return '↑'
    } else if (signalType.includes('sell')) {
      return '↓'
    } else {
      return '—'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* 信号头部 */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{signal.symbol}</h3>
            <p className="text-sm text-gray-500">当前价格: ${signal.current_price?.toFixed(2)}</p>
          </div>
          <div className={`px-4 py-2 rounded-lg ${getSignalColor(signal.signal)} flex items-center space-x-2`}>
            <span className="text-xl">{getSignalIcon(signal.signal)}</span>
            <span className="font-semibold">{getSignalText(signal.signal)}</span>
          </div>
        </div>
        <div className="mt-3">
          <div className="flex items-center">
            <span className="text-sm text-gray-600 mr-2">置信度:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${signal.confidence}%` }}
              ></div>
            </div>
            <span className="ml-2 text-sm font-semibold text-blue-600">{signal.confidence}%</span>
          </div>
        </div>
      </div>


      {/* 价格水平 */}
      <div className="p-6 bg-gray-50">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">关键价格水平</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500">目标价</p>
            <p className="text-lg font-semibold text-green-600">${signal.target_price?.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500">止损价</p>
            <p className="text-lg font-semibold text-red-600">${signal.stop_loss?.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500">阻力位</p>
            <p className="text-lg font-semibold text-gray-700">${signal.resistance_level?.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500">支撑位</p>
            <p className="text-lg font-semibold text-gray-700">${signal.support_level?.toFixed(2)}</p>
          </div>
        </div>
      </div>

      {/* 信号依据 */}
      <div className="p-6">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">信号依据</h4>
        <div className="space-y-3">
          <div className="border-l-4 border-blue-500 pl-3">
            <p className="text-xs font-semibold text-gray-600">技术面</p>
            <p className="text-sm text-gray-700 mt-1">{signal.reasoning?.technical || '分析中...'}</p>
          </div>
          <div className="border-l-4 border-purple-500 pl-3">
            <p className="text-xs font-semibold text-gray-600">舆情面</p>
            <p className="text-sm text-gray-700 mt-1">{signal.reasoning?.sentiment || '分析中...'}</p>
          </div>
          <div className="border-l-4 border-green-500 pl-3">
            <p className="text-xs font-semibold text-gray-600">基本面</p>
            <p className="text-sm text-gray-700 mt-1">{signal.reasoning?.fundamentals || '分析中...'}</p>
          </div>
        </div>
      </div>

      {/* 时间戳 */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        {signal.cached ? '📦 缓存数据' : '🔄 实时分析'} | 
        更新时间: {new Date(signal.timestamp).toLocaleString('zh-CN')}
      </div>

      {/* 免责声明 */}
      <div className="px-6 py-3 bg-yellow-50 border-t border-yellow-200 text-xs text-yellow-800">
        ⚠️ 本信号由AI生成，仅供参考，不构成投资建议。请自行判断并承担投资风险。
      </div>
    </div>
  )
}
