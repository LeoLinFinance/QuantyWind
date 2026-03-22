import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { DataProvider } from './contexts/DataContext'
import Layout from './components/Layout'
import MarketInsightPage from './pages/MarketInsightPage'
import RiskAnalysisPage from './pages/RiskAnalysisPage'
import SentimentMapPage from './pages/SentimentMapPage'
import ExpertForumPage from './pages/ExpertForumPage'
import SettingsPage from './pages/SettingsPage'
import { InstallPWA } from './components/InstallPWA'

function App() {
  return (
    <DataProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/expert-forum" replace />} />
            <Route path="expert-forum" element={<ExpertForumPage />} />
            <Route path="market-insight" element={<MarketInsightPage />} />
            <Route path="risk-analysis" element={<RiskAnalysisPage />} />
            <Route path="sentiment-map" element={<SentimentMapPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <InstallPWA />
    </DataProvider>
  )
}

export default App
