import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import axios from 'axios'
import { useDataContext } from '../contexts/DataContext'

interface RiskModel {
  name: string
  description: string
  value: number
  accuracy: number
  validity: {
    r2: number
    mae: number
    rmse: number
  }
  parameters: Record<string, any>
  scenario: string
}

interface DatasetStats {
  total_indices: number
  total_stocks: number
  active_stocks: number
  inactive_stocks: number
  total_data_points: number
  last_full_update: string | null
}

interface PortfolioItem {
  symbol: string
  name: string
  weight: number
  selected: boolean
}

interface PortfolioRiskMetrics {
  var_95: number
  var_99: number
  cvar_95: number
  volatility: number
  sharpe_ratio: number
  sortino_ratio: number
  max_drawdown: number
  beta: number
  annual_return: number
  skewness: number
  kurtosis: number
  correlation_matrix: Record<string, Record<string, number>>
}

export default function RiskAnalysisPage() {
  // 使用全局Context保存数据，避免页面切换时重新加载
  const {
    riskData,
    setRiskData,
    riskLastUpdate,
    setRiskLastUpdate,
    setRefreshCurrentPage,
    autoRefreshEnabled,
    setAutoRefreshEnabled,
  } = useDataContext()
  
  const [riskModels, setRiskModels] = useState<RiskModel[]>(riskData || [])
  const [selectedModel, setSelectedModel] = useState<string>('VaR')
  const [loading, setLoading] = useState(false)
  const [dataLoaded, setDataLoaded] = useState(false)
  
  // 历史数据集状态
  const [datasetStats, setDatasetStats] = useState<DatasetStats | null>(null)
  const [updatingDataset, setUpdatingDataset] = useState(false)
  const [showDatasetPanel, setShowDatasetPanel] = useState(false)
  
  // 投资组合配置状态
  const [showPortfolioPanel, setShowPortfolioPanel] = useState(false)
  const [availableStocks, setAvailableStocks] = useState<PortfolioItem[]>([])
  const [portfolioRisk, setPortfolioRisk] = useState<PortfolioRiskMetrics | null>(null)
  const [calculatingRisk, setCalculatingRisk] = useState(false)
  
  // AI风险解读状态
  const [aiInterpretation, setAiInterpretation] = useState<string>('')
  const [loadingInterpretation, setLoadingInterpretation] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await axios.get('/api/risk-models')
      setRiskModels(res.data)
      setRiskData(res.data)
      setRiskLastUpdate(new Date())
      setDataLoaded(true)
    } catch (error) {
      console.error('获取风险模型数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchDatasetStats = async () => {
    try {
      const res = await axios.get('/api/historical-data/statistics')
      setDatasetStats(res.data)
    } catch (error) {
      console.error('获取数据集统计失败:', error)
    }
  }
  
  const fetchAvailableStocks = async () => {
    try {
      // 只获取当前盯盘中的活跃股票
      const res = await axios.get('/api/watchlist', { params: { use_ai: false } })
      const stocks = res.data.map((stock: any) => ({
        symbol: stock.symbol,
        name: stock.name,
        weight: 0,
        selected: false
      }))
      setAvailableStocks(stocks)
    } catch (error) {
      console.error('获取股票列表失败:', error)
    }
  }

  const updateHistoricalData = async () => {
    setUpdatingDataset(true)
    try {
      // 获取当前盯盘股票列表
      const watchlistRes = await axios.get('/api/watchlist')
      const symbols = watchlistRes.data.map((stock: any) => stock.symbol)
      
      // 更新历史数据
      const res = await axios.post('/api/historical-data/update', {
        watchlist_symbols: symbols
      })
      
      if (res.data.success) {
        alert(`数据更新完成！\n成功: ${res.data.stats.updated.length}个\n失败: ${res.data.stats.failed.length}个`)
        // 刷新统计信息
        await fetchDatasetStats()
        // 刷新风险模型
        await fetchData()
      }
    } catch (error) {
      console.error('更新历史数据失败:', error)
      alert('更新历史数据失败，请查看控制台')
    } finally {
      setUpdatingDataset(false)
    }
  }
  
  const handleStockSelect = (symbol: string) => {
    setAvailableStocks(stocks => 
      stocks.map(s => 
        s.symbol === symbol ? { ...s, selected: !s.selected } : s
      )
    )
  }
  
  const handleWeightChange = (symbol: string, weight: number) => {
    setAvailableStocks(stocks => 
      stocks.map(s => 
        s.symbol === symbol ? { ...s, weight: Math.max(0, Math.min(100, weight)) } : s
      )
    )
  }
  
  const normalizeWeights = () => {
    const selectedStocks = availableStocks.filter(s => s.selected)
    if (selectedStocks.length === 0) return
    
    const totalWeight = selectedStocks.reduce((sum, s) => sum + s.weight, 0)
    if (totalWeight === 0) {
      // 平均分配
      const avgWeight = 100 / selectedStocks.length
      setAvailableStocks(stocks => 
        stocks.map(s => 
          s.selected ? { ...s, weight: avgWeight } : s
        )
      )
    } else {
      // 归一化到100%
      setAvailableStocks(stocks => 
        stocks.map(s => 
          s.selected ? { ...s, weight: (s.weight / totalWeight) * 100 } : s
        )
      )
    }
  }
  
  const calculatePortfolioRisk = async () => {
    const selectedStocks = availableStocks.filter(s => s.selected && s.weight > 0)
    
    if (selectedStocks.length === 0) {
      alert('请至少选择一个股票并设置权重')
      return
    }
    
    const totalWeight = selectedStocks.reduce((sum, s) => sum + s.weight, 0)
    if (Math.abs(totalWeight - 100) > 0.1) {
      alert(`权重总和必须为100%，当前为${totalWeight.toFixed(1)}%`)
      return
    }
    
    setCalculatingRisk(true)
    try {
      const portfolio = selectedStocks.map(s => ({
        symbol: s.symbol,
        name: s.name,
        weight: s.weight / 100  // 转换为小数
      }))
      
      const res = await axios.post('/api/portfolio-risk', { portfolio })
      
      if (res.data.success) {
        setPortfolioRisk(res.data.risk_metrics)
        // 自动获取AI解读
        await getAiInterpretation(portfolio, res.data.risk_metrics)
      }
    } catch (error) {
      console.error('计算投资组合风险失败:', error)
      alert('计算失败，请查看控制台')
    } finally {
      setCalculatingRisk(false)
    }
  }
  
  const getAiInterpretation = async (portfolio: any[], riskMetrics: PortfolioRiskMetrics) => {
    setLoadingInterpretation(true)
    try {
      const res = await axios.post('/api/portfolio-risk/interpret', {
        portfolio,
        risk_metrics: riskMetrics
      })
      
      if (res.data.success) {
        setAiInterpretation(res.data.interpretation)
      }
    } catch (error) {
      console.error('获取AI解读失败:', error)
      setAiInterpretation('AI解读服务暂时不可用，请稍后再试。')
    } finally {
      setLoadingInterpretation(false)
    }
  }

  useEffect(() => {
    // 注册当前页面的刷新函数到Context
    setRefreshCurrentPage(() => fetchData)
    
    // 只在数据未加载时才加载（避免页面切换时重新加载）
    if (!dataLoaded && (!riskData || riskData.length === 0)) {
      fetchData()
    } else if (riskData && riskData.length > 0) {
      setRiskModels(riskData)
      setDataLoaded(true)
    }
    
    // 加载数据集统计信息和可用股票
    fetchDatasetStats()
    fetchAvailableStocks()
  }, [])

  // 自动刷新定时器（15分钟）
  useEffect(() => {
    if (!autoRefreshEnabled) return

    const interval = setInterval(() => {
      console.log('风险分析页面：自动刷新触发')
      fetchData()
    }, 15 * 60 * 1000) // 15分钟

    return () => clearInterval(interval)
  }, [autoRefreshEnabled])

  const currentModel = riskModels.find(m => m.name === selectedModel)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">风险分析看板</h2>
        <div className="flex items-center space-x-4">
          {loading && (
            <span className="text-sm text-blue-600">📊 加载数据中...</span>
          )}
          {updatingDataset && (
            <span className="text-sm text-orange-600 animate-pulse">🔄 更新历史数据中...</span>
          )}
          <button
            onClick={() => setShowDatasetPanel(!showDatasetPanel)}
            className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
          >
            📊 数据集管理
          </button>
          <button
            onClick={() => setShowPortfolioPanel(!showPortfolioPanel)}
            className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
          >
            💼 投资组合配置
          </button>
          <div className="text-sm text-gray-500">
            上次更新: {format(riskLastUpdate, 'yyyy-MM-dd HH:mm:ss')}
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
            onClick={fetchData}
            disabled={loading}
            className={`px-3 py-1 rounded ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } text-white`}
          >
            {loading ? '加载中...' : '刷新'}
          </button>
        </div>
      </div>

      {/* 数据集管理面板 */}
      {showDatasetPanel && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">历史数据集管理</h3>
          
          {datasetStats && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-sm text-gray-600">市场指数</div>
                <div className="text-2xl font-bold text-blue-600">{datasetStats.total_indices}</div>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <div className="text-sm text-gray-600">活跃股票</div>
                <div className="text-2xl font-bold text-green-600">{datasetStats.active_stocks}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">历史股票</div>
                <div className="text-2xl font-bold text-gray-600">{datasetStats.inactive_stocks}</div>
              </div>
              <div className="bg-purple-50 p-4 rounded">
                <div className="text-sm text-gray-600">总股票数</div>
                <div className="text-2xl font-bold text-purple-600">{datasetStats.total_stocks}</div>
              </div>
              <div className="bg-orange-50 p-4 rounded">
                <div className="text-sm text-gray-600">数据点总数</div>
                <div className="text-2xl font-bold text-orange-600">{datasetStats.total_data_points.toLocaleString()}</div>
              </div>
              <div className="bg-indigo-50 p-4 rounded">
                <div className="text-sm text-gray-600">最后更新</div>
                <div className="text-sm font-medium text-indigo-600">
                  {datasetStats.last_full_update 
                    ? format(new Date(datasetStats.last_full_update), 'MM-dd HH:mm')
                    : '从未更新'}
                </div>
              </div>
            </div>
          )}

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  <strong>数据集维护策略：</strong>
                </p>
                <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
                  <li>只增不删：移除的股票数据会保留，但不再更新</li>
                  <li>增量更新：只更新从上次更新到现在的交易日数据</li>
                  <li>智能同步：新增股票会自动获取近10年历史数据</li>
                </ul>
              </div>
            </div>
          </div>

          <button
            onClick={updateHistoricalData}
            disabled={updatingDataset}
            className={`w-full py-3 rounded font-medium ${
              updatingDataset
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-orange-600 hover:bg-orange-700'
            } text-white`}
          >
            {updatingDataset ? '正在更新数据集...' : '🔄 更新历史数据集'}
          </button>
          
          <p className="mt-2 text-xs text-gray-500 text-center">
            点击更新将同步所有盯盘股票和市场指数的最新数据
          </p>
        </div>
      )}

      {/* 投资组合配置面板 */}
      {showPortfolioPanel && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">投资组合风险分析</h3>
          
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-medium text-gray-700">选择股票并设置权重</h4>
              <button
                onClick={normalizeWeights}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                归一化权重
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {availableStocks.map((stock) => (
                <div key={stock.symbol} className={`border rounded p-3 ${stock.selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
                  <label className="flex items-center space-x-2 mb-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={stock.selected}
                      onChange={() => handleStockSelect(stock.symbol)}
                      className="rounded"
                    />
                    <span className="font-semibold">{stock.symbol}</span>
                  </label>
                  {stock.selected && (
                    <div className="mt-2">
                      <label className="text-xs text-gray-600">权重 (%)</label>
                      <input
                        type="number"
                        value={stock.weight}
                        onChange={(e) => handleWeightChange(stock.symbol, parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1 border rounded text-sm"
                        min="0"
                        max="100"
                        step="0.1"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm text-gray-600">
                已选择: {availableStocks.filter(s => s.selected).length} 个股票 | 
                权重总和: {availableStocks.filter(s => s.selected).reduce((sum, s) => sum + s.weight, 0).toFixed(1)}%
              </div>
              <button
                onClick={calculatePortfolioRisk}
                disabled={calculatingRisk}
                className={`px-6 py-2 rounded font-medium ${
                  calculatingRisk
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700'
                } text-white`}
              >
                {calculatingRisk ? '计算中...' : '📊 计算风险指标'}
              </button>
            </div>
          </div>
          
          {/* 风险指标结果 */}
          {portfolioRisk && (
            <div className="border-t pt-6">
              <h4 className="font-semibold text-lg mb-4">投资组合风险指标</h4>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <div className="bg-red-50 p-4 rounded">
                  <div className="text-sm text-gray-600">VaR (95%)</div>
                  <div className="text-xl font-bold text-red-600">{(portfolioRisk.var_95 * 100).toFixed(2)}%</div>
                  <div className="text-xs text-gray-500 mt-1">单日最大损失</div>
                </div>
                
                <div className="bg-red-50 p-4 rounded">
                  <div className="text-sm text-gray-600">CVaR (95%)</div>
                  <div className="text-xl font-bold text-red-600">{(portfolioRisk.cvar_95 * 100).toFixed(2)}%</div>
                  <div className="text-xs text-gray-500 mt-1">预期损失</div>
                </div>
                
                <div className="bg-orange-50 p-4 rounded">
                  <div className="text-sm text-gray-600">年化波动率</div>
                  <div className="text-xl font-bold text-orange-600">{(portfolioRisk.volatility * 100).toFixed(2)}%</div>
                  <div className="text-xs text-gray-500 mt-1">风险水平</div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded">
                  <div className="text-sm text-gray-600">年化收益率</div>
                  <div className="text-xl font-bold text-blue-600">{(portfolioRisk.annual_return * 100).toFixed(2)}%</div>
                  <div className="text-xs text-gray-500 mt-1">预期回报</div>
                </div>
                
                <div className="bg-green-50 p-4 rounded">
                  <div className="text-sm text-gray-600">夏普比率</div>
                  <div className="text-xl font-bold text-green-600">{portfolioRisk.sharpe_ratio.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">风险调整收益</div>
                </div>
                
                <div className="bg-green-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Sortino比率</div>
                  <div className="text-xl font-bold text-green-600">{portfolioRisk.sortino_ratio.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">下行风险调整</div>
                </div>
                
                <div className="bg-purple-50 p-4 rounded">
                  <div className="text-sm text-gray-600">最大回撤</div>
                  <div className="text-xl font-bold text-purple-600">{(portfolioRisk.max_drawdown * 100).toFixed(2)}%</div>
                  <div className="text-xs text-gray-500 mt-1">历史最大损失</div>
                </div>
                
                <div className="bg-indigo-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Beta系数</div>
                  <div className="text-xl font-bold text-indigo-600">{portfolioRisk.beta.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">市场敏感度</div>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded">
                  <div className="text-sm text-gray-600">偏度</div>
                  <div className="text-xl font-bold text-yellow-600">{portfolioRisk.skewness.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">收益分布偏斜</div>
                </div>
                
                <div className="bg-pink-50 p-4 rounded">
                  <div className="text-sm text-gray-600">峰度</div>
                  <div className="text-xl font-bold text-pink-600">{portfolioRisk.kurtosis.toFixed(2)}</div>
                  <div className="text-xs text-gray-500 mt-1">极端事件概率</div>
                </div>
              </div>
              
              {/* AI风险解读 */}
              <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <h5 className="font-semibold text-lg flex items-center">
                    <span className="mr-2">🤖</span>
                    AI风险解读
                  </h5>
                  {loadingInterpretation && (
                    <span className="text-sm text-blue-600 animate-pulse">生成中...</span>
                  )}
                </div>
                
                {loadingInterpretation ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600">AI正在分析您的投资组合风险...</span>
                  </div>
                ) : aiInterpretation ? (
                  <div className="prose prose-sm max-w-none">
                    <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {aiInterpretation}
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-500 text-center py-4">
                    计算风险指标后，AI将为您生成专业的风险解读
                  </div>
                )}
                
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <p className="text-xs text-gray-500 italic">
                    💡 本解读由阶跃星辰 step-1-8k 模型生成，基于历史数据分析，仅供参考，不构成投资建议。
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        {riskModels.slice(0, 4).map((model) => (
          <div key={model.name} className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">{model.name}</div>
            <div className="text-2xl font-bold mt-2">{model.value.toFixed(4)}</div>
            <div className="text-xs text-gray-400 mt-1">准确率: {(model.accuracy * 100).toFixed(1)}%</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">风险模型详情</h3>
          <div className="mb-4">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              {riskModels.map((model) => (
                <option key={model.name} value={model.name}>
                  {model.name} - {model.description}
                </option>
              ))}
            </select>
          </div>

          {currentModel && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <div className="text-sm text-gray-500">模型值</div>
                  <div className="text-xl font-bold">{currentModel.value.toFixed(4)}</div>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <div className="text-sm text-gray-500">准确率</div>
                  <div className="text-xl font-bold">{(currentModel.accuracy * 100).toFixed(2)}%</div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">有效性指标</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm text-gray-500">R²</div>
                    <div className="font-semibold">{currentModel.validity.r2.toFixed(4)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">MAE</div>
                    <div className="font-semibold">{currentModel.validity.mae.toFixed(4)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">RMSE</div>
                    <div className="font-semibold">{currentModel.validity.rmse.toFixed(4)}</div>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">模型参数</h4>
                <div className="bg-gray-50 p-3 rounded">
                  <pre className="text-sm">{JSON.stringify(currentModel.parameters, null, 2)}</pre>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">适用场景</h4>
                <p className="text-gray-700">{currentModel.scenario}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
