import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import axios from 'axios'
import VolumeSparkline from '../components/VolumeSparkline'
import { useDataContext } from '../contexts/DataContext'
import AIAnalysisModal from '../components/AIAnalysisModal'
import TradingSignalCard from '../components/TradingSignalCard'

// @ts-ignore - 保留接口定义供未来使用
interface MarketInsight {
  timestamp: string
  sentiment: string
  analysis: string
  indices: {
    nasdaq: number
    sp500: number
    russell: number
    nasdaq_change: number
    sp500_change: number
    russell_change: number
  }
}

interface Stock {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  volumeHistory: number[]
  sentiment: string
}

export default function MarketInsightPage() {
  // 使用全局Context保存数据，避免页面切换时重新加载
  const {
    marketInsight,
    setMarketInsight,
    watchlist,
    setWatchlist,
    marketLastUpdate,
    setMarketLastUpdate,
    setRefreshCurrentPage,
    autoRefreshEnabled,
    setAutoRefreshEnabled,
  } = useDataContext()
  
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false) // AI分析加载状态
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [showPromptEditor, setShowPromptEditor] = useState(false)
  const [systemPrompt, setSystemPrompt] = useState('')
  const [useAI, setUseAI] = useState(true)
  const [dataLoaded, setDataLoaded] = useState(false) // 标记数据是否已加载
  
  // AI分析模态框状态
  const [showAIAnalysis, setShowAIAnalysis] = useState(false)
  const [selectedStock, setSelectedStock] = useState<string>('')
  const [aiAnalysisData, setAiAnalysisData] = useState<any>(null)
  const [aiAnalysisLoading, setAiAnalysisLoading] = useState(false)
  
  // 交易信号状态
  const [showTradingSignal, setShowTradingSignal] = useState(false)
  const [tradingSignalData, setTradingSignalData] = useState<any>(null)
  const [tradingSignalLoading, setTradingSignalLoading] = useState(false)

  // 分步加载：先加载基础数据（价格、涨跌幅、成交量）
  const fetchBasicData = async (forceRefresh: boolean = false) => {
    setLoading(true)
    try {
      const [insightRes, stocksRes] = await Promise.all([
        axios.get('/api/market-insight', { params: { force_refresh: forceRefresh } }),
        axios.get('/api/watchlist', { params: { use_ai: false, force_refresh: forceRefresh } })
      ])
      setMarketInsight(insightRes.data)
      setWatchlist(stocksRes.data)
      setMarketLastUpdate(new Date())
      setDataLoaded(true)
    } catch (error) {
      console.error('获取基础数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 加载AI分析（可选，较慢）
  const fetchAIAnalysis = async (forceRefresh: boolean = false) => {
    if (!useAI) return
    
    setAiLoading(true)
    try {
      const stocksRes = await axios.get('/api/watchlist', { 
        params: { use_ai: true, force_refresh: forceRefresh } 
      })
      setWatchlist(stocksRes.data)
    } catch (error) {
      console.error('获取AI分析失败:', error)
    } finally {
      setAiLoading(false)
    }
  }

  // 完整刷新（用于手动刷新按钮）
  const fetchData = async (forceRefresh: boolean = false) => {
    await fetchBasicData(forceRefresh)
    if (useAI) {
      await fetchAIAnalysis(forceRefresh)
    }
  }

  const fetchSystemPrompt = async () => {
    try {
      const res = await axios.get('/api/system-prompt')
      setSystemPrompt(res.data.prompt)
    } catch (error) {
      console.error('获取系统提示词失败:', error)
    }
  }

  useEffect(() => {
    // 注册当前页面的刷新函数到Context
    setRefreshCurrentPage(() => () => fetchData(true)) // 手动刷新时强制更新
    
    // 只在数据未加载时才加载（避免页面切换时重新加载）
    if (!dataLoaded) {
      // 首次加载：先加载基础数据，再加载AI分析（使用缓存）
      fetchBasicData(false).then(() => {
        if (useAI) {
          fetchAIAnalysis(false)
        }
      })
    }
    fetchSystemPrompt()
  }, [])

  // 自动刷新定时器（15分钟）
  useEffect(() => {
    if (!autoRefreshEnabled) return

    const interval = setInterval(() => {
      console.log('市场洞察页面：自动刷新触发（使用缓存）')
      fetchData(false) // 自动刷新时使用缓存
    }, 15 * 60 * 1000) // 15分钟

    return () => clearInterval(interval)
  }, [autoRefreshEnabled])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    try {
      const res = await axios.get('/api/search-stock', {
        params: { query: searchQuery }
      })
      setSearchResults(res.data)
    } catch (error) {
      console.error('搜索失败:', error)
    }
  }

  const handleAddStock = async (symbol: string) => {
    try {
      const res = await axios.post(`/api/watchlist/${symbol}`)
      if (res.data.success) {
        // 只获取新添加股票的数据，不影响其他股票的舆情
        const newStockRes = await axios.get<Stock>(`/api/stock/${symbol}`)
        // 添加到现有列表，保留其他股票的舆情信息
        setWatchlist(prev => [...prev, newStockRes.data])
        setSearchQuery('')
        setSearchResults([])
        console.log(`✅ 已添加 ${symbol}，其他股票舆情信息已保留`)
      } else {
        alert(res.data.message)
      }
    } catch (error) {
      console.error('添加股票失败:', error)
    }
  }

  const handleRemoveStock = async (symbol: string) => {
    if (!confirm(`确定要移除 ${symbol} 吗？`)) return
    try {
      const res = await axios.delete(`/api/watchlist/${symbol}`)
      if (res.data.success) {
        // 直接从前端状态中移除，不重新获取列表，保留其他股票的舆情信息
        setWatchlist(prev => prev.filter(stock => stock.symbol !== symbol))
        console.log(`✅ 已移除 ${symbol}，其他股票舆情信息已保留`)
      }
    } catch (error) {
      console.error('移除股票失败:', error)
    }
  }

  const handleSavePrompt = async () => {
    try {
      await axios.post('/api/system-prompt', { prompt: systemPrompt })
      setShowPromptEditor(false)
      fetchData(true) // 保存提示词后强制刷新
    } catch (error) {
      console.error('保存提示词失败:', error)
    }
  }
  
  // AI分析处理函数
  const handleAIAnalysis = async (symbol: string) => {
    setSelectedStock(symbol)
    setShowAIAnalysis(true)
    setAiAnalysisLoading(true)
    setAiAnalysisData(null)
    
    try {
      console.log(`🤖 开始AI分析: ${symbol}`)
      const res = await axios.get(`/api/ai-signals/analyze/${symbol}`)
      console.log('✅ AI分析成功:', res.data)
      setAiAnalysisData(res.data)
    } catch (error: any) {
      console.error('❌ AI分析失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '未知错误'
      setAiAnalysisData({
        error: true,
        message: `AI分析失败: ${errorMsg}`,
        details: error.response?.status === 500 ? '服务器内部错误，请检查后端日志' :
                 error.response?.status === 400 ? '数据不足或参数错误' :
                 error.code === 'ERR_NETWORK' ? '无法连接到后端服务，请确认后端是否启动' :
                 '请稍后重试'
      })
    } finally {
      setAiAnalysisLoading(false)
    }
  }
  
  // 交易信号处理函数
  const handleTradingSignal = async (symbol: string) => {
    setSelectedStock(symbol)
    setShowTradingSignal(true)
    setTradingSignalLoading(true)
    setTradingSignalData(null)
    
    try {
      console.log(`📊 开始生成交易信号: ${symbol}`)
      const res = await axios.get(`/api/ai-signals/trading-signal/${symbol}`)
      console.log('✅ 交易信号生成成功:', res.data)
      setTradingSignalData(res.data)
    } catch (error: any) {
      console.error('❌ 交易信号生成失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '未知错误'
      setTradingSignalData({
        error: true,
        message: `交易信号生成失败: ${errorMsg}`,
        details: error.response?.status === 500 ? '服务器内部错误，请检查后端日志' :
                 error.response?.status === 400 ? '数据不足或参数错误' :
                 error.code === 'ERR_NETWORK' ? '无法连接到后端服务，请确认后端是否启动' :
                 '请稍后重试'
      })
    } finally {
      setTradingSignalLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">市场洞察盯盘</h2>
        <div className="flex items-center space-x-4">
          {aiLoading && (
            <span className="text-sm text-blue-600 animate-pulse">🤖 AI分析中...</span>
          )}
          {loading && (
            <span className="text-sm text-blue-600">📊 加载数据中...</span>
          )}
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={useAI}
              onChange={(e) => setUseAI(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">启用AI舆情分析</span>
          </label>
          <button
            onClick={() => setShowPromptEditor(!showPromptEditor)}
            className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
          >
            编辑提示词
          </button>
          <div className="text-sm text-gray-500">
            上次更新: {format(marketLastUpdate, 'yyyy-MM-dd HH:mm:ss')}
          </div>
          {/* iOS风格自动刷新开关 */}
          <label className="flex items-center space-x-2 cursor-pointer">
            <span className="text-sm text-gray-600">自动刷新</span>
            <div
              onClick={() => autoRefreshEnabled ? setAutoRefreshEnabled(false) : setAutoRefreshEnabled(true)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoRefreshEnabled ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoRefreshEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </div>
          </label>
          <button
            onClick={() => fetchData(true)} // 手动刷新时强制更新
            disabled={loading || aiLoading}
            className={`px-3 py-1 rounded ${
              loading || aiLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } text-white`}
          >
            {loading || aiLoading ? '加载中...' : '🔄 刷新'}
          </button>
          {useAI && (
            <button
              onClick={() => fetchAIAnalysis(true)} // 手动更新舆情时强制刷新
              disabled={aiLoading}
              className={`px-3 py-1 rounded ${
                aiLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-purple-600 hover:bg-purple-700'
              } text-white text-sm`}
              title="手动触发AI舆情分析"
            >
              {aiLoading ? 'AI分析中...' : '🤖 更新舆情'}
            </button>
          )}
        </div>
      </div>

      {showPromptEditor && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">编辑AI系统提示词</h3>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="w-full h-40 px-3 py-2 border border-gray-300 rounded-md"
            placeholder="输入自定义的系统提示词..."
          />
          <div className="mt-4 flex space-x-2">
            <button
              onClick={handleSavePrompt}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              保存
            </button>
            <button
              onClick={() => setShowPromptEditor(false)}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              取消
            </button>
          </div>
        </div>
      )}

      {marketInsight && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">市场整体洞察</h3>
          <div className="mb-4">
            <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
              marketInsight.sentiment === '乐观' ? 'bg-green-100 text-green-800' :
              marketInsight.sentiment === '谨慎' ? 'bg-yellow-100 text-yellow-800' :
              marketInsight.sentiment === '中性' ? 'bg-blue-100 text-blue-800' :
              'bg-red-100 text-red-800'
            }`}>
              {marketInsight.sentiment}
            </span>
          </div>
          <p className="text-gray-700 mb-4">{marketInsight.analysis}</p>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-500">纳斯达克</div>
              <div className="text-xl font-bold">{marketInsight.indices.nasdaq.toFixed(2)}</div>
              <div className={`text-sm ${marketInsight.indices.nasdaq_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {marketInsight.indices.nasdaq_change >= 0 ? '+' : ''}{marketInsight.indices.nasdaq_change.toFixed(2)}%
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-500">标普500</div>
              <div className="text-xl font-bold">{marketInsight.indices.sp500.toFixed(2)}</div>
              <div className={`text-sm ${marketInsight.indices.sp500_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {marketInsight.indices.sp500_change >= 0 ? '+' : ''}{marketInsight.indices.sp500_change.toFixed(2)}%
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-500">罗素2000</div>
              <div className="text-xl font-bold">{marketInsight.indices.russell.toFixed(2)}</div>
              <div className={`text-sm ${marketInsight.indices.russell_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {marketInsight.indices.russell_change >= 0 ? '+' : ''}{marketInsight.indices.russell_change.toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">个股盯盘</h3>
          <div className="flex space-x-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="搜索股票代码（如AAPL）"
              className="px-3 py-2 border border-gray-300 rounded-md"
            />
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              搜索
            </button>
          </div>
        </div>

        {searchResults.length > 0 && (
          <div className="mb-4 p-4 bg-blue-50 rounded">
            <h4 className="font-medium mb-2">搜索结果：</h4>
            {searchResults.map((result) => (
              <div key={result.symbol} className="flex justify-between items-center py-2">
                <div>
                  <span className="font-semibold">{result.symbol}</span>
                  <span className="ml-2 text-gray-600">{result.name}</span>
                  <span className="ml-2 text-xs text-gray-500">{result.exchange}</span>
                </div>
                <button
                  onClick={() => handleAddStock(result.symbol)}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                >
                  添加
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">价格</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">涨跌幅</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">成交量</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">成交量周趋势</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">舆情提示</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {watchlist.map((stock) => (
                <tr key={stock.symbol}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{stock.symbol}</div>
                    <div className="text-sm text-gray-500">{stock.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">${stock.price.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={stock.change >= 0 ? 'text-green-600' : 'text-red-600'}>
                      <div className="font-medium">
                        {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                      </div>
                      <div className="text-xs">
                        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">{stock.volume.toLocaleString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <VolumeSparkline data={stock.volumeHistory || []} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs">
                    {aiLoading ? (
                      <span className="text-blue-600 animate-pulse">AI分析中...</span>
                    ) : (
                      stock.sentiment || (useAI ? '等待分析' : '-')
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleAIAnalysis(stock.symbol)}
                        className="text-purple-600 hover:text-purple-800 text-sm font-medium"
                        title="AI智能分析"
                      >
                        🤖 分析
                      </button>
                      <button
                        onClick={() => handleTradingSignal(stock.symbol)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        title="交易信号"
                      >
                        📊 信号
                      </button>
                      <button
                        onClick={() => handleRemoveStock(stock.symbol)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        移除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* AI分析模态框 */}
      <AIAnalysisModal
        isOpen={showAIAnalysis}
        onClose={() => setShowAIAnalysis(false)}
        symbol={selectedStock}
        analysis={aiAnalysisData}
        loading={aiAnalysisLoading}
      />
      
      {/* 交易信号模态框 */}
      {showTradingSignal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white">
              <h3 className="text-lg font-semibold">交易信号 - {selectedStock}</h3>
              <button
                onClick={() => setShowTradingSignal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="p-4">
              <TradingSignalCard signal={tradingSignalData} loading={tradingSignalLoading} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
