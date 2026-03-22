import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { setupPWA } from './registerSW'

// 注册 Service Worker (PWA)
if ('serviceWorker' in navigator) {
  setupPWA();
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
