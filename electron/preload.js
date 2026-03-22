const { contextBridge, ipcRenderer } = require('electron');

// 定义允许的 IPC 通道白名单
const validChannels = {
  send: [
    'window:minimize',
    'window:maximize',
    'window:close',
    'window:fullscreen',
    'backend:status',
    'backend:restart',
    'backend:logs',
    'notification:show',
    'update:check',
    'update:download',
    'update:install',
    'app:open-external',
    'app:open-log-folder'
  ],
  on: [
    'backend:status-changed',
    'backend:logs',
    'update:available',
    'update:progress',
    'update:downloaded',
    'update:error',
    'notification:clicked'
  ]
};

/**
 * 验证通道是否在白名单中
 */
function isValidChannel(channel, type) {
  return validChannels[type] && validChannels[type].includes(channel);
}

/**
 * 安全的 Electron API
 */
const electronAPI = {
  /**
   * 发送消息到主进程
   * @param {string} channel - IPC 通道名称
   * @param {any} data - 要发送的数据
   */
  send: (channel, data) => {
    if (isValidChannel(channel, 'send')) {
      ipcRenderer.send(channel, data);
    } else {
      console.warn(`[Preload] Attempted to send to invalid channel: ${channel}`);
    }
  },

  /**
   * 接收主进程消息
   * @param {string} channel - IPC 通道名称
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消订阅函数
   */
  on: (channel, callback) => {
    if (isValidChannel(channel, 'on')) {
      const subscription = (event, ...args) => callback(...args);
      ipcRenderer.on(channel, subscription);
      
      // 返回取消订阅函数
      return () => {
        ipcRenderer.removeListener(channel, subscription);
      };
    } else {
      console.warn(`[Preload] Attempted to listen to invalid channel: ${channel}`);
      return () => {}; // 返回空函数
    }
  },

  /**
   * 一次性接收主进程消息
   * @param {string} channel - IPC 通道名称
   * @param {Function} callback - 回调函数
   */
  once: (channel, callback) => {
    if (isValidChannel(channel, 'on')) {
      ipcRenderer.once(channel, (event, ...args) => callback(...args));
    } else {
      console.warn(`[Preload] Attempted to listen once to invalid channel: ${channel}`);
    }
  },

  /**
   * 移除监听器
   * @param {string} channel - IPC 通道名称
   * @param {Function} callback - 回调函数
   */
  removeListener: (channel, callback) => {
    if (isValidChannel(channel, 'on')) {
      ipcRenderer.removeListener(channel, callback);
    }
  },

  /**
   * 移除所有监听器
   * @param {string} channel - IPC 通道名称
   */
  removeAllListeners: (channel) => {
    if (isValidChannel(channel, 'on')) {
      ipcRenderer.removeAllListeners(channel);
    }
  },

  /**
   * 获取应用版本
   * @returns {string} 应用版本号
   */
  getAppVersion: () => {
    return process.env.npm_package_version || '1.0.0';
  },

  /**
   * 获取平台信息
   * @returns {Object} 平台信息对象
   */
  getPlatform: () => {
    return {
      platform: process.platform,
      arch: process.arch,
      isWindows: process.platform === 'win32',
      isMac: process.platform === 'darwin',
      isLinux: process.platform === 'linux'
    };
  },

  /**
   * 检查是否在 Electron 环境中
   * @returns {boolean} 是否在 Electron 中
   */
  isElectron: () => {
    return true;
  },

  /**
   * 获取 Node.js 版本
   * @returns {string} Node.js 版本
   */
  getNodeVersion: () => {
    return process.versions.node;
  },

  /**
   * 获取 Electron 版本
   * @returns {string} Electron 版本
   */
  getElectronVersion: () => {
    return process.versions.electron;
  },

  /**
   * 获取 Chrome 版本
   * @returns {string} Chrome 版本
   */
  getChromeVersion: () => {
    return process.versions.chrome;
  }
};

/**
 * 暴露安全的 API 到渲染进程
 */
try {
  contextBridge.exposeInMainWorld('electronAPI', electronAPI);
  console.log('[Preload] Electron API exposed successfully');
  console.log('[Preload] Available methods:', Object.keys(electronAPI));
  console.log('[Preload] Platform:', electronAPI.getPlatform());
} catch (error) {
  console.error('[Preload] Failed to expose Electron API:', error);
}

// 日志 preload 脚本加载
console.log('[Preload] Preload script loaded');
console.log('[Preload] Context isolation:', process.contextIsolated);
console.log('[Preload] Node integration:', process.versions.node ? 'enabled' : 'disabled');
