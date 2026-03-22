const { app, BrowserWindow, ipcMain, shell, dialog } = require('electron');
const path = require('path');
const log = require('electron-log');
const { BackendManager, BackendStatus } = require('./backend-manager');

// 配置日志
log.transports.file.level = 'info';
log.transports.console.level = 'debug';
log.info('Application starting...');

// 全局变量保存窗口引用
let mainWindow = null;
let backendManager = null;

// 应用配置
const config = {
  window: {
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600
  },
  backend: {
    port: 8000,
    host: '127.0.0.1',
    startupTimeout: 30000 // 30 秒
  }
};

// 开发模式检测
const isDev = process.env.NODE_ENV === 'development';

/**
 * 初始化后端管理器
 */
function initializeBackendManager() {
  log.info('Initializing backend manager...');
  
  backendManager = new BackendManager({
    pythonPath: 'python3',
    backendScript: path.join(__dirname, '../backend/main.py'),
    port: config.backend.port,
    host: config.backend.host,
    startupTimeout: config.backend.startupTimeout,
    autoRestart: true
  });
  
  // 监听状态变化
  backendManager.on('status-changed', ({ status, oldStatus }) => {
    log.info(`Backend status changed: ${oldStatus} -> ${status}`);
    
    // 通知渲染进程
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:status-changed', backendManager.getStatus());
    }
  });
  
  // 监听输出
  backendManager.on('output', (output) => {
    // 通知渲染进程
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:logs', output);
    }
  });
  
  // 监听错误
  backendManager.on('error', (error) => {
    log.error('Backend manager error:', error);
  });
  
  // 监听崩溃
  backendManager.on('crashed', ({ code, signal }) => {
    log.error(`Backend crashed (code: ${code}, signal: ${signal})`);
    
    // 显示错误通知
    if (mainWindow && !mainWindow.isDestroyed()) {
      dialog.showErrorBox(
        '后端服务崩溃',
        `后端服务意外退出（退出码：${code}）\n\n系统将尝试自动重启服务。`
      );
    }
  });
  
  // 监听致命错误
  backendManager.on('fatal-error', (error) => {
    log.error('Backend fatal error:', error);
    
    // 显示错误对话框
    if (mainWindow && !mainWindow.isDestroyed()) {
      dialog.showErrorBox(
        '后端服务启动失败',
        `后端服务无法启动：${error.message}\n\n请检查日志文件获取详细信息。\n\n日志位置：${log.transports.file.getFile().path}`
      );
    }
  });
  
  log.info('Backend manager initialized');
}

/**
 * 启动后端服务
 */
async function startBackendService() {
  if (!backendManager) {
    throw new Error('Backend manager not initialized');
  }
  
  log.info('Starting backend service...');
  
  try {
    await backendManager.start();
    log.info('Backend service started successfully');
  } catch (error) {
    log.error('Failed to start backend service:', error);
    throw error;
  }
}

/**
 * 停止后端服务
 */
async function stopBackendService() {
  if (backendManager && backendManager.isRunning()) {
    log.info('Stopping backend service...');
    await backendManager.stop();
    log.info('Backend service stopped');
  }
}

/**
 * 创建主窗口
 */
function createMainWindow() {
  log.info('Creating main window...');
  
  mainWindow = new BrowserWindow({
    width: config.window.width,
    height: config.window.height,
    minWidth: config.window.minWidth,
    minHeight: config.window.minHeight,
    title: '量数风行',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false, // 等待加载完成后再显示
    backgroundColor: '#ffffff'
  });

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    log.info('Window ready to show');
    mainWindow.show();
  });

  // 加载应用
  if (isDev) {
    // 开发模式：加载 Vite 开发服务器
    const devUrl = 'http://localhost:3002';
    log.info(`Loading development URL: ${devUrl}`);
    mainWindow.loadURL(devUrl);
    mainWindow.webContents.openDevTools();
  } else {
    // 生产模式：加载构建后的文件
    const indexPath = path.join(__dirname, '../dist-frontend/index.html');
    log.info(`Loading production file: ${indexPath}`);
    mainWindow.loadFile(indexPath);
  }

  // 处理外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // 在外部浏览器中打开链接
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  // 窗口关闭事件
  mainWindow.on('closed', () => {
    log.info('Main window closed');
    mainWindow = null;
  });

  // 渲染进程崩溃处理
  mainWindow.webContents.on('crashed', async () => {
    log.error('Renderer process crashed');
    
    const options = {
      type: 'error',
      title: '应用崩溃',
      message: '应用界面崩溃，是否重新加载？',
      buttons: ['重新加载', '退出'],
      defaultId: 0
    };
    
    const { response } = await dialog.showMessageBox(mainWindow, options);
    
    if (response === 0) {
      mainWindow.reload();
    } else {
      app.quit();
    }
  });

  return mainWindow;
}

/**
 * 注册 IPC 处理器
 */
function registerIPCHandlers() {
  log.info('Registering IPC handlers...');

  // 窗口操作
  ipcMain.on('window:minimize', () => {
    if (mainWindow) {
      mainWindow.minimize();
    }
  });

  ipcMain.on('window:maximize', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });

  ipcMain.on('window:close', () => {
    if (mainWindow) {
      mainWindow.close();
    }
  });

  ipcMain.on('window:fullscreen', () => {
    if (mainWindow) {
      mainWindow.setFullScreen(!mainWindow.isFullScreen());
    }
  });

  // 打开外部链接
  ipcMain.on('app:open-external', (event, url) => {
    if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
      shell.openExternal(url);
    }
  });

  // 打开日志文件夹
  ipcMain.on('app:open-log-folder', () => {
    const logPath = log.transports.file.getFile().path;
    const logDir = path.dirname(logPath);
    shell.openPath(logDir);
  });

  // 后端服务状态
  ipcMain.on('backend:status', (event) => {
    if (backendManager) {
      event.reply('backend:status-changed', backendManager.getStatus());
    } else {
      event.reply('backend:status-changed', {
        status: 'stopped',
        message: 'Backend manager not initialized'
      });
    }
  });

  ipcMain.on('backend:restart', async () => {
    if (backendManager) {
      log.info('Backend restart requested');
      try {
        await backendManager.restart();
        log.info('Backend restarted successfully');
      } catch (error) {
        log.error('Failed to restart backend:', error);
      }
    }
  });

  log.info('IPC handlers registered');
}

/**
 * 应用初始化
 */
async function initialize() {
  log.info('Initializing application...');
  log.info(`Environment: ${isDev ? 'development' : 'production'}`);
  log.info(`Electron version: ${process.versions.electron}`);
  log.info(`Node version: ${process.versions.node}`);
  log.info(`Platform: ${process.platform}`);
  log.info(`Architecture: ${process.arch}`);

  try {
    // 注册 IPC 处理器
    registerIPCHandlers();
    
    // 初始化后端管理器
    initializeBackendManager();
    
    // 并行启动窗口和后端服务
    log.info('Starting window and backend service in parallel...');
    const [window] = await Promise.all([
      Promise.resolve(createMainWindow()),
      startBackendService()
    ]);
    
    log.info('Application initialized successfully');
  } catch (error) {
    log.error('Failed to initialize application:', error);
    
    await dialog.showErrorBox(
      '初始化失败',
      `应用初始化失败：${error.message}\n\n日志文件：${log.transports.file.getFile().path}`
    );
    
    app.quit();
  }
}

/**
 * 应用就绪事件
 */
app.whenReady().then(() => {
  log.info('App ready event triggered');
  initialize();

  // macOS 特定：点击 Dock 图标时重新创建窗口
  app.on('activate', () => {
    log.info('App activate event triggered');
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    } else if (mainWindow) {
      mainWindow.show();
    }
  });
});

/**
 * 所有窗口关闭事件
 */
app.on('window-all-closed', () => {
  log.info('All windows closed');
  // macOS 上除非用户明确退出，否则保持应用运行
  if (process.platform !== 'darwin') {
    log.info('Quitting application (non-macOS)');
    app.quit();
  }
});

/**
 * 应用即将退出事件
 */
app.on('will-quit', async (event) => {
  log.info('Application will quit');
  
  // 阻止默认退出，等待后端服务停止
  if (backendManager && backendManager.isRunning()) {
    event.preventDefault();
    
    try {
      await stopBackendService();
    } catch (error) {
      log.error('Error stopping backend service:', error);
    }
    
    // 继续退出
    app.quit();
  }
});

/**
 * 应用退出前清理
 */
app.on('before-quit', () => {
  log.info('Application before quit');
});

/**
 * 全局错误处理
 */
process.on('uncaughtException', (error) => {
  log.error('Uncaught exception in main process:', error);
  log.error('Stack trace:', error.stack);
});

process.on('unhandledRejection', (reason, promise) => {
  log.error('Unhandled rejection in main process:', reason);
  log.error('Promise:', promise);
});

/**
 * 应用退出事件
 */
app.on('quit', (event, exitCode) => {
  log.info(`Application quit with exit code: ${exitCode}`);
});

log.info('Main process script loaded');
