/**
 * Service Worker 注册和更新管理
 */

import { registerSW } from 'virtual:pwa-register';

// 注册 Service Worker 并处理更新
export function setupPWA() {
  const updateSW = registerSW({
    onNeedRefresh() {
      // 当有新版本可用时
      if (confirm('发现新版本！点击确定更新应用。')) {
        updateSW(true);
      }
    },
    onOfflineReady() {
      // 当应用可以离线使用时
      console.log('应用已准备好离线使用');
      
      // 可以显示一个提示
      showNotification('应用已准备好离线使用', 'success');
    },
    onRegistered(registration) {
      // Service Worker 注册成功
      console.log('Service Worker 已注册');
      
      // 每小时检查一次更新
      if (registration) {
        setInterval(() => {
          registration.update();
        }, 60 * 60 * 1000);
      }
    },
    onRegisterError(error) {
      console.error('Service Worker 注册失败:', error);
    }
  });

  return updateSW;
}

// 显示通知的辅助函数
function showNotification(message: string, type: 'success' | 'info' | 'warning' | 'error') {
  // 这里可以集成你的通知组件
  // 暂时使用简单的 console.log
  console.log(`[${type.toUpperCase()}] ${message}`);
  
  // 如果浏览器支持通知 API
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('量数风行', {
      body: message,
      icon: '/icon-192.png',
      badge: '/icon-72.png'
    });
  }
}

// 请求通知权限
export async function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }
  return Notification.permission === 'granted';
}

// 检查是否在 PWA 模式下运行
export function isPWA(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
         (window.navigator as any).standalone === true ||
         document.referrer.includes('android-app://');
}

// 检查是否支持 PWA
export function supportsPWA(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window;
}
