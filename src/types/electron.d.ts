/**
 * Electron API 类型定义
 * 
 * 这个文件定义了通过 preload 脚本暴露给渲染进程的 Electron API
 */

interface PlatformInfo {
  platform: string;
  arch: string;
  isWindows: boolean;
  isMac: boolean;
  isLinux: boolean;
}

interface ElectronAPI {
  /**
   * 发送消息到主进程
   */
  send: (channel: string, data?: any) => void;

  /**
   * 接收主进程消息
   * @returns 取消订阅函数
   */
  on: (channel: string, callback: (...args: any[]) => void) => () => void;

  /**
   * 一次性接收主进程消息
   */
  once: (channel: string, callback: (...args: any[]) => void) => void;

  /**
   * 移除监听器
   */
  removeListener: (channel: string, callback: Function) => void;

  /**
   * 移除所有监听器
   */
  removeAllListeners: (channel: string) => void;

  /**
   * 获取应用版本
   */
  getAppVersion: () => string;

  /**
   * 获取平台信息
   */
  getPlatform: () => PlatformInfo;

  /**
   * 检查是否在 Electron 环境中
   */
  isElectron: () => boolean;

  /**
   * 获取 Node.js 版本
   */
  getNodeVersion: () => string;

  /**
   * 获取 Electron 版本
   */
  getElectronVersion: () => string;

  /**
   * 获取 Chrome 版本
   */
  getChromeVersion: () => string;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
