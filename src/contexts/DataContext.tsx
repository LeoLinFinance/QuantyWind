import { createContext, useContext, useState, ReactNode, Dispatch, SetStateAction, useEffect } from 'react'

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

interface DataContextType {
  // 市场洞察数据
  marketInsight: MarketInsight | null
  setMarketInsight: Dispatch<SetStateAction<MarketInsight | null>>
  watchlist: Stock[]
  setWatchlist: Dispatch<SetStateAction<Stock[]>>
  marketLastUpdate: Date
  setMarketLastUpdate: Dispatch<SetStateAction<Date>>
  
  // 风险分析数据
  riskData: any
  setRiskData: (data: any) => void
  riskLastUpdate: Date
  setRiskLastUpdate: (date: Date) => void
  
  // 舆情地图数据
  sentimentData: any
  setSentimentData: (data: any) => void
  sentimentLastUpdate: Date
  setSentimentLastUpdate: (date: Date) => void
  
  // 自动刷新功能
  autoRefreshEnabled: boolean
  setAutoRefreshEnabled: (enabled: boolean) => void
  refreshCurrentPage: () => void
  setRefreshCurrentPage: (fn: () => void) => void
}

const DataContext = createContext<DataContextType | undefined>(undefined)

// 辅助函数：从sessionStorage加载数据
function loadFromStorage<T>(key: string, defaultValue: T): T {
  try {
    const cached = sessionStorage.getItem(key)
    if (cached) {
      return JSON.parse(cached)
    }
  } catch (error) {
    console.error(`加载${key}缓存失败:`, error)
  }
  return defaultValue
}

// 辅助函数：保存数据到sessionStorage
function saveToStorage(key: string, value: any): void {
  try {
    if (value !== null && value !== undefined) {
      sessionStorage.setItem(key, JSON.stringify(value))
    }
  } catch (error) {
    console.error(`保存${key}到缓存失败:`, error)
  }
}

export function DataProvider({ children }: { children: ReactNode }) {
  // 市场洞察状态 - 从缓存初始化
  const [marketInsight, setMarketInsight] = useState<MarketInsight | null>(
    () => loadFromStorage('marketInsight', null)
  )
  const [watchlist, setWatchlist] = useState<Stock[]>(
    () => loadFromStorage('watchlist', [])
  )
  const [marketLastUpdate, setMarketLastUpdate] = useState<Date>(new Date())
  
  // 风险分析状态 - 从缓存初始化
  const [riskData, setRiskData] = useState<any>(
    () => loadFromStorage('riskData', null)
  )
  const [riskLastUpdate, setRiskLastUpdate] = useState<Date>(new Date())
  
  // 舆情地图状态 - 从缓存初始化
  const [sentimentData, setSentimentData] = useState<any>(
    () => loadFromStorage('sentimentData', null)
  )
  const [sentimentLastUpdate, setSentimentLastUpdate] = useState<Date>(new Date())
  
  // 自动刷新功能
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState<boolean>(false)
  const [refreshCurrentPage, setRefreshCurrentPage] = useState<() => void>(() => () => {})

  // 保存市场洞察数据到缓存
  useEffect(() => {
    saveToStorage('marketInsight', marketInsight)
  }, [marketInsight])

  useEffect(() => {
    saveToStorage('watchlist', watchlist)
  }, [watchlist])

  // 保存风险分析数据到缓存
  useEffect(() => {
    saveToStorage('riskData', riskData)
  }, [riskData])

  // 保存舆情地图数据到缓存
  useEffect(() => {
    saveToStorage('sentimentData', sentimentData)
  }, [sentimentData])

  return (
    <DataContext.Provider
      value={{
        marketInsight,
        setMarketInsight,
        watchlist,
        setWatchlist,
        marketLastUpdate,
        setMarketLastUpdate,
        riskData,
        setRiskData,
        riskLastUpdate,
        setRiskLastUpdate,
        sentimentData,
        setSentimentData,
        sentimentLastUpdate,
        setSentimentLastUpdate,
        autoRefreshEnabled,
        setAutoRefreshEnabled,
        refreshCurrentPage,
        setRefreshCurrentPage,
      }}
    >
      {children}
    </DataContext.Provider>
  )
}

export function useDataContext() {
  const context = useContext(DataContext)
  if (context === undefined) {
    throw new Error('useDataContext must be used within a DataProvider')
  }
  return context
}
