interface AIAnalysisModalProps {
  isOpen: boolean
  onClose: () => void
  symbol: string
  analysis: any
  loading: boolean
}

// 辅助函数：获取指标分数
function getMetricScore(metric: any): number {
  if (typeof metric === 'object' && metric !== null) {
    return metric.score || 0
  }
  return typeof metric === 'number' ? metric : 0
}

// 辅助函数：获取指标依据
function getMetricReasoning(metric: any): string {
  if (typeof metric === 'object' && metric !== null) {
    return metric.reasoning || '暂无依据'
  }
  return '暂无依据'
}

export default function AIAnalysisModal({ isOpen, onClose, symbol, analysis, loading }: AIAnalysisModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <span className="text-2xl mr-2">✨</span>
              AI智能分析 - {symbol}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 text-2xl"
            >
              ✕
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
              <span className="ml-3 text-gray-600">AI分析中...</span>
            </div>
          ) : analysis?.error ? (
            <div className="py-8">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <div className="flex items-start">
                  <span className="text-3xl mr-3">❌</span>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-red-800 mb-2">分析失败</h4>
                    <p className="text-sm text-red-700 mb-3">{analysis.message}</p>
                    {analysis.details && (
                      <div className="bg-red-100 rounded p-3 text-xs text-red-800">
                        <p className="font-semibold mb-1">详细信息：</p>
                        <p>{analysis.details}</p>
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
          ) : analysis ? (
            <div className="space-y-6">
              {/* 综合评分 */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">综合评分</p>
                    <p className="text-3xl font-bold text-purple-600">
                      {analysis.analysis?.overall_score?.toFixed(1) || 'N/A'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">当前价格</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      ${analysis.current_price?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>


              {/* 关键指标 */}
              {analysis.analysis?.key_metrics && (
                <div className="space-y-3">
                  <MetricCard
                    title="成长潜力"
                    score={getMetricScore(analysis.analysis.key_metrics.growth_potential)}
                    reasoning={getMetricReasoning(analysis.analysis.key_metrics.growth_potential)}
                    color="green"
                  />
                  <MetricCard
                    title="风险等级"
                    score={getMetricScore(analysis.analysis.key_metrics.risk_level)}
                    reasoning={getMetricReasoning(analysis.analysis.key_metrics.risk_level)}
                    color="yellow"
                  />
                  <MetricCard
                    title="估值水平"
                    score={getMetricScore(analysis.analysis.key_metrics.valuation)}
                    reasoning={getMetricReasoning(analysis.analysis.key_metrics.valuation)}
                    color="blue"
                  />
                </div>
              )}

              {/* 分析内容 */}
              <div className="space-y-4">
                <AnalysisSection
                  title="宏观环境分析"
                  content={analysis.analysis?.macro_environment}
                  icon="🌍"
                />
                <AnalysisSection
                  title="行业趋势"
                  content={analysis.analysis?.industry_trend}
                  icon="📈"
                />
                <AnalysisSection
                  title="公司基本面"
                  content={analysis.analysis?.fundamentals}
                  icon="🏢"
                />
                <AnalysisSection
                  title="技术面分析"
                  content={analysis.analysis?.technical_analysis}
                  icon="📊"
                />
              </div>

              {/* 数据来源 */}
              {analysis.data_sources && (
                <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600">
                  <p>数据来源: {analysis.data_sources.historical_days}天历史数据 | 
                    {analysis.data_sources.news_count}条新闻 | 
                    {analysis.data_sources.risk_models_used}个风险模型
                  </p>
                  <p className="mt-1">
                    {analysis.cached ? '📦 缓存数据' : '🔄 实时分析'} | 
                    更新时间: {new Date(analysis.timestamp).toLocaleString('zh-CN')}
                  </p>
                </div>
              )}

              {/* 免责声明 */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
                <p className="font-semibold">⚠️ 重要提示：</p>
                <p className="mt-1">
                  本分析由AI模型生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。
                  请根据自身风险承受能力做出投资决策。
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              暂无分析数据
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function AnalysisSection({ title, content, icon }: { title: string; content?: string; icon: string }) {
  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
        <span className="mr-2">{icon}</span>
        {title}
      </h4>
      <p className="text-sm text-gray-600 leading-relaxed">
        {content || '分析中...'}
      </p>
    </div>
  )
}

function MetricCard({ title, score, reasoning, color }: { 
  title: string
  score: number
  reasoning: string
  color: 'green' | 'yellow' | 'blue'
}) {
  const colorClasses = {
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      border: 'border-green-200'
    },
    yellow: {
      bg: 'bg-yellow-50',
      text: 'text-yellow-600',
      border: 'border-yellow-200'
    },
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-200'
    }
  }
  
  const colors = colorClasses[color]
  
  return (
    <div className={`${colors.bg} border ${colors.border} rounded-lg p-4`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-gray-700">{title}</p>
        <p className={`text-2xl font-bold ${colors.text}`}>
          {score || 'N/A'}
        </p>
      </div>
      <p className="text-xs text-gray-600 leading-relaxed">
        {reasoning}
      </p>
    </div>
  )
}
