import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import axios from 'axios'
import { ComposableMap, Geographies, Geography, Marker } from 'react-simple-maps'
import { useDataContext } from '../contexts/DataContext'

interface SentimentEvent {
  id: string
  country?: string
  countryCode?: string
  summary: string
  riskDetails?: string
  affectedIndustries?: string[]
  timestamp: string
  riskLevel: 'high' | 'medium' | 'low'
  relatedStocks: string[]
  coordinates?: [number, number]
  source?: string
  url?: string
}

interface IndustryInsight {
  title: string
  content: string
  related_stocks: string[]
  sentiment: 'positive' | 'neutral' | 'negative'
}

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

export default function SentimentMapPage() {
  // 使用全局Context保存数据，避免页面切换时重新加载
  const {
    sentimentData,
    setSentimentData,
    sentimentLastUpdate,
    setSentimentLastUpdate,
    setRefreshCurrentPage,
    autoRefreshEnabled,
    setAutoRefreshEnabled,
  } = useDataContext()
  
  const [events, setEvents] = useState<SentimentEvent[]>(sentimentData?.events || [])
  const [industryInsights, setIndustryInsights] = useState<IndustryInsight[]>(sentimentData?.insights || [])
  const [riskFilter, setRiskFilter] = useState<string>('all')
  const [loading, setLoading] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<SentimentEvent | null>(null)
  const [showPromptEditor, setShowPromptEditor] = useState(false)
  const [customPrompt, setCustomPrompt] = useState('')
  const [defaultPrompt, setDefaultPrompt] = useState('')
  const [dataLoaded, setDataLoaded] = useState(false) // 标记数据是否已加载

  const fetchData = async () => {
    setLoading(true)
    try {
      // 获取舆情地图数据
      const params = customPrompt ? { custom_prompt: customPrompt } : {}
      const res = await axios.get('/api/sentiment-map', { params })
      setEvents(res.data.located)
      
      // 获取产业链洞察
      const watchlistRes = await axios.get('/api/watchlist')
      const symbols = watchlistRes.data.map((stock: any) => stock.symbol)
      let insights: IndustryInsight[] = []
      if (symbols.length > 0) {
        const insightsRes = await axios.post('/api/industry-insights', symbols)
        insights = insightsRes.data
        setIndustryInsights(insights)
      }
      
      // 保存到Context
      setSentimentData({
        events: res.data.located,
        insights: insights
      })
      setSentimentLastUpdate(new Date())
      setDataLoaded(true)
    } catch (error) {
      console.error('获取舆情地图数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchDefaultPrompt = async () => {
    try {
      const res = await axios.get('/api/sentiment-map/default-prompt')
      setDefaultPrompt(res.data.prompt)
    } catch (error) {
      console.error('获取默认提示词失败:', error)
    }
  }

  useEffect(() => {
    // 注册当前页面的刷新函数到Context
    setRefreshCurrentPage(() => fetchData)
    
    // 只在数据未加载时才加载（避免页面切换时重新加载）
    fetchDefaultPrompt()
    
    if (!dataLoaded && (!sentimentData || !sentimentData.events || sentimentData.events.length === 0)) {
      fetchData()
    } else if (sentimentData && sentimentData.events && sentimentData.events.length > 0) {
      setEvents(sentimentData.events)
      setIndustryInsights(sentimentData.insights || [])
      setDataLoaded(true)
    }
  }, [])

  // 自动刷新定时器（15分钟）
  useEffect(() => {
    if (!autoRefreshEnabled) return

    const interval = setInterval(() => {
      console.log('舆情地图页面：自动刷新触发')
      fetchData()
    }, 15 * 60 * 1000) // 15分钟

    return () => clearInterval(interval)
  }, [autoRefreshEnabled])

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return '#ef4444'
      case 'medium': return '#f59e0b'
      case 'low': return '#3b82f6'
      default: return '#6b7280'
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-50'
      case 'negative': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const filteredEvents = riskFilter === 'all' 
    ? events 
    : events.filter(e => e.riskLevel === riskFilter)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">市场风险舆情地图</h2>
        <div className="flex items-center space-x-4">
          {loading && (
            <span className="text-sm text-blue-600">正在分析最新舆情...</span>
          )}
          <div className="text-sm text-gray-500">
            上次更新: {format(sentimentLastUpdate, 'yyyy-MM-dd HH:mm:ss')}
          </div>
          <button
            onClick={() => setShowPromptEditor(!showPromptEditor)}
            className="px-3 py-1 rounded bg-purple-600 hover:bg-purple-700 text-white"
          >
            编辑提示词
          </button>
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
            {loading ? '分析中...' : '刷新'}
          </button>
        </div>
      </div>

      {/* System Prompt 编辑器 */}
      {showPromptEditor && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">自定义分析提示词</h3>
          <textarea
            value={customPrompt || defaultPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            className="w-full h-64 p-3 border rounded font-mono text-sm"
            placeholder="输入自定义提示词..."
          />
          <div className="mt-4 flex space-x-3">
            <button
              onClick={() => {
                fetchData()
                setShowPromptEditor(false)
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              应用并刷新
            </button>
            <button
              onClick={() => {
                setCustomPrompt('')
                fetchData()
              }}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              恢复默认
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

      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex space-x-4 mb-4">
          <button
            onClick={() => setRiskFilter('all')}
            className={`px-4 py-2 rounded ${riskFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            全部
          </button>
          <button
            onClick={() => setRiskFilter('high')}
            className={`px-4 py-2 rounded ${riskFilter === 'high' ? 'bg-red-600 text-white' : 'bg-gray-200'}`}
          >
            高风险
          </button>
          <button
            onClick={() => setRiskFilter('medium')}
            className={`px-4 py-2 rounded ${riskFilter === 'medium' ? 'bg-yellow-600 text-white' : 'bg-gray-200'}`}
          >
            中风险
          </button>
          <button
            onClick={() => setRiskFilter('low')}
            className={`px-4 py-2 rounded ${riskFilter === 'low' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            低风险
          </button>
        </div>

        <ComposableMap>
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill="#E5E7EB"
                  stroke="#9CA3AF"
                />
              ))
            }
          </Geographies>
          {filteredEvents.map((event) => 
            event.coordinates && (
              <Marker 
                key={event.id} 
                coordinates={event.coordinates}
                onClick={() => setSelectedEvent(event)}
              >
                <circle r={8} fill={getRiskColor(event.riskLevel)} opacity={0.8} style={{ cursor: 'pointer' }} />
              </Marker>
            )
          )}
        </ComposableMap>
      </div>

      {/* 事件详情弹窗 */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setSelectedEvent(null)}>
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-gray-900">风险事件详情</h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <span className={`px-3 py-1 text-sm rounded ${
                  selectedEvent.riskLevel === 'high' ? 'bg-red-100 text-red-800' :
                  selectedEvent.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {selectedEvent.riskLevel === 'high' ? '高风险' : 
                   selectedEvent.riskLevel === 'medium' ? '中风险' : '低风险'}
                </span>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">事件摘要</h4>
                <p className="text-gray-900">{selectedEvent.summary}</p>
              </div>
              
              {selectedEvent.riskDetails && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">风险详情</h4>
                  <p className="text-gray-600">{selectedEvent.riskDetails}</p>
                </div>
              )}
              
              {selectedEvent.affectedIndustries && selectedEvent.affectedIndustries.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">受影响产业</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedEvent.affectedIndustries.map((industry, idx) => (
                      <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-800 rounded text-sm">
                        {industry}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">国家/地区</h4>
                  <p className="text-gray-600">{selectedEvent.country || '未确定'}</p>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">时间</h4>
                  <p className="text-gray-600">{format(new Date(selectedEvent.timestamp), 'yyyy-MM-dd HH:mm')}</p>
                </div>
              </div>
              
              {selectedEvent.relatedStocks.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">相关股票</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedEvent.relatedStocks.map((stock, idx) => (
                      <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm font-mono">
                        {stock}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedEvent.url && (
                <div>
                  <a 
                    href={selectedEvent.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    查看新闻来源 →
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 产业链洞察 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">产业链洞察</h3>
        {loading ? (
          <div className="text-center text-gray-500 py-8">正在分析产业链动态...</div>
        ) : industryInsights.length === 0 ? (
          <div className="text-center text-gray-500 py-8">暂无产业链洞察数据</div>
        ) : (
          <div className="space-y-4">
            {industryInsights.map((insight, idx) => (
              <div key={idx} className={`border-l-4 ${
                insight.sentiment === 'positive' ? 'border-green-500' :
                insight.sentiment === 'negative' ? 'border-red-500' :
                'border-gray-400'
              } pl-4 py-3 hover:bg-gray-50 transition-colors`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="text-gray-900 font-semibold mb-2">{insight.title}</h4>
                    <p className="text-gray-700 leading-relaxed mb-3">{insight.content}</p>
                    {insight.related_stocks.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        <span className="text-sm text-gray-500">相关股票:</span>
                        {insight.related_stocks.map((stock, i) => (
                          <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-mono">
                            {stock}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className={`ml-4 px-3 py-1 text-xs rounded whitespace-nowrap ${getSentimentColor(insight.sentiment)}`}>
                    {insight.sentiment === 'positive' ? '积极' : 
                     insight.sentiment === 'negative' ? '消极' : '中性'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
