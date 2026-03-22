const { spawn } = require('child_process');
const axios = require('axios');
const log = require('electron-log');
const path = require('path');
const { EventEmitter } = require('events');
const { app } = require('electron');

/**
 * 获取 Python 可执行文件路径
 * 
 * 开发模式：使用系统 Python
 * 生产模式：使用打包的 Python 运行时
 */
function getPythonPath() {
  const platform = process.platform;
  const resourcesPath = process.resourcesPath;
  
  // 检查打包的 Python 是否存在
  let bundledPythonPath;
  if (platform === 'win32') {
    bundledPythonPath = path.join(resourcesPath, 'python-runtime', 'python.exe');
  } else {
    bundledPythonPath = path.join(resourcesPath, 'python-runtime', 'bin', 'python3');
  }
  
  // 如果打包的 Python 存在，使用它
  const fs = require('fs');
  if (fs.existsSync(bundledPythonPath)) {
    log.info(`Using bundled Python (production mode), platform: ${platform}`);
    log.info(`Resources path: ${resourcesPath}`);
    log.info(`Python path: ${bundledPythonPath}`);
    return bundledPythonPath;
  }
  
  // 否则使用系统 Python（开发模式）
  log.info('Using system Python (development mode)');
  return process.platform === 'win32' ? 'python' : 'python3';
}

/**
 * 获取后端脚本路径
 */
function getBackendScriptPath() {
  const resourcesPath = process.resourcesPath;
  const bundledBackendPath = path.join(resourcesPath, 'backend', 'main.py');
  
  // 检查打包的后端脚本是否存在
  const fs = require('fs');
  if (fs.existsSync(bundledBackendPath)) {
    // 生产模式：使用打包的脚本
    log.info(`Using bundled backend script: ${bundledBackendPath}`);
    return bundledBackendPath;
  }
  
  // 开发模式：使用项目目录中的脚本
  const devBackendPath = path.join(__dirname, '../backend/main.py');
  log.info(`Using development backend script: ${devBackendPath}`);
  return devBackendPath;
}

/**
 * 后端服务状态枚举
 */
const BackendStatus = {
  STOPPED: 'stopped',
  STARTING: 'starting',
  RUNNING: 'running',
  ERROR: 'error'
};

/**
 * 后端服务管理器
 * 
 * 负责启动、监控和管理 Python 后端服务
 * 
 * 功能：
 * - 启动 Python 后端服务
 * - 健康检查（轮询 /health 端点）
 * - 服务状态管理
 * - 捕获和记录后端输出
 * - 服务崩溃自动重启
 * - 优雅关闭
 */
class BackendManager extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // 配置
    this.config = {
      pythonPath: config.pythonPath || getPythonPath(),
      backendScript: config.backendScript || getBackendScriptPath(),
      port: config.port || 8000,
      host: config.host || '127.0.0.1',
      startupTimeout: config.startupTimeout || 30000, // 30 秒
      healthCheckInterval: config.healthCheckInterval || 2000, // 2 秒
      maxRestartAttempts: config.maxRestartAttempts || 3,
      restartDelay: config.restartDelay || 2000, // 2 秒
      autoRestart: config.autoRestart !== false // 默认启用自动重启
    };
    
    // 状态
    this.status = BackendStatus.STOPPED;
    this.process = null;
    this.pid = null;
    this.startTime = null;
    this.restartCount = 0;
    this.healthCheckTimer = null;
    this.startupTimer = null;
    this.isShuttingDown = false;
    
    log.info('BackendManager initialized', {
      pythonPath: this.config.pythonPath,
      backendScript: this.config.backendScript,
      port: this.config.port
    });
  }
  
  /**
   * 获取健康检查 URL
   */
  getHealthCheckUrl() {
    return `http://${this.config.host}:${this.config.port}/health`;
  }
  
  /**
   * 获取后端服务 URL
   */
  getBaseUrl() {
    return `http://${this.config.host}:${this.config.port}`;
  }
  
  /**
   * 启动后端服务
   */
  async start() {
    if (this.status === BackendStatus.STARTING || this.status === BackendStatus.RUNNING) {
      log.warn('Backend service is already starting or running');
      return;
    }
    
    log.info('Starting backend service...');
    this.setStatus(BackendStatus.STARTING);
    this.isShuttingDown = false;
    
    try {
      // 启动 Python 进程
      await this.spawnProcess();
      
      // 等待服务就绪
      await this.waitForReady();
      
      // 启动健康检查
      this.startHealthCheck();
      
      this.setStatus(BackendStatus.RUNNING);
      this.startTime = new Date();
      this.restartCount = 0; // 重置重启计数
      
      log.info('Backend service started successfully', {
        pid: this.pid,
        url: this.getBaseUrl()
      });
      
    } catch (error) {
      log.error('Failed to start backend service', error);
      this.setStatus(BackendStatus.ERROR);
      this.emit('error', error);
      throw error;
    }
  }
  
  /**
   * 启动 Python 进程
   */
  spawnProcess() {
    return new Promise((resolve, reject) => {
      log.info('Spawning Python process', {
        pythonPath: this.config.pythonPath,
        script: this.config.backendScript
      });
      
      // 环境变量
      const env = {
        ...process.env,
        BACKEND_PORT: this.config.port.toString(),
        PYTHONUNBUFFERED: '1' // 禁用 Python 输出缓冲
      };
      
      // 启动进程
      this.process = spawn(this.config.pythonPath, [this.config.backendScript], {
        env,
        cwd: path.dirname(this.config.backendScript),
        stdio: ['ignore', 'pipe', 'pipe']
      });
      
      this.pid = this.process.pid;
      log.info(`Python process spawned with PID: ${this.pid}`);
      
      // 捕获 stdout
      this.process.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          log.info(`[Backend stdout] ${output}`);
          this.emit('output', output);
        }
      });
      
      // 捕获 stderr
      this.process.stderr.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          // 某些库会将正常日志输出到 stderr，所以使用 info 级别
          log.info(`[Backend stderr] ${output}`);
          this.emit('output', output);
        }
      });
      
      // 进程错误
      this.process.on('error', (error) => {
        log.error('Backend process error', error);
        this.emit('process-error', error);
        reject(error);
      });
      
      // 进程退出
      this.process.on('exit', (code, signal) => {
        log.warn(`Backend process exited`, { code, signal, pid: this.pid });
        this.handleProcessExit(code, signal);
      });
      
      // 进程启动成功
      resolve();
    });
  }
  
  /**
   * 等待服务就绪
   */
  async waitForReady() {
    log.info('Waiting for backend service to be ready...');
    
    const startTime = Date.now();
    const healthUrl = this.getHealthCheckUrl();
    
    return new Promise((resolve, reject) => {
      // 设置启动超时
      this.startupTimer = setTimeout(() => {
        const error = new Error(`Backend service startup timeout (${this.config.startupTimeout}ms)`);
        log.error(error.message);
        reject(error);
      }, this.config.startupTimeout);
      
      // 轮询健康检查
      const checkHealth = async () => {
        try {
          const response = await axios.get(healthUrl, {
            timeout: 2000,
            validateStatus: () => true // 接受所有状态码
          });
          
          if (response.status === 200) {
            clearTimeout(this.startupTimer);
            const elapsed = Date.now() - startTime;
            log.info(`Backend service is ready (took ${elapsed}ms)`);
            resolve();
          } else {
            // 继续等待
            setTimeout(checkHealth, 500);
          }
        } catch (error) {
          // 连接失败，继续等待
          setTimeout(checkHealth, 500);
        }
      };
      
      // 开始检查
      checkHealth();
    });
  }
  
  /**
   * 启动健康检查
   */
  startHealthCheck() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }
    
    log.info('Starting health check', {
      interval: this.config.healthCheckInterval,
      url: this.getHealthCheckUrl()
    });
    
    this.healthCheckTimer = setInterval(async () => {
      try {
        const response = await axios.get(this.getHealthCheckUrl(), {
          timeout: 2000,
          validateStatus: () => true
        });
        
        if (response.status !== 200) {
          log.warn('Health check failed', { status: response.status });
          this.handleHealthCheckFailure();
        }
      } catch (error) {
        log.warn('Health check error', error.message);
        this.handleHealthCheckFailure();
      }
    }, this.config.healthCheckInterval);
  }
  
  /**
   * 停止健康检查
   */
  stopHealthCheck() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
      log.info('Health check stopped');
    }
  }
  
  /**
   * 处理健康检查失败
   */
  handleHealthCheckFailure() {
    if (this.status === BackendStatus.RUNNING) {
      log.error('Backend service health check failed');
      this.setStatus(BackendStatus.ERROR);
      this.emit('health-check-failed');
      
      // 尝试重启
      if (this.config.autoRestart) {
        this.restart();
      }
    }
  }
  
  /**
   * 处理进程退出
   */
  handleProcessExit(code, signal) {
    this.stopHealthCheck();
    
    if (this.startupTimer) {
      clearTimeout(this.startupTimer);
      this.startupTimer = null;
    }
    
    this.process = null;
    this.pid = null;
    
    // 如果是正常关闭，不重启
    if (this.isShuttingDown) {
      log.info('Backend service stopped (shutdown requested)');
      this.setStatus(BackendStatus.STOPPED);
      return;
    }
    
    // 如果退出码为 0，认为是正常退出
    if (code === 0) {
      log.info('Backend service exited normally');
      this.setStatus(BackendStatus.STOPPED);
      return;
    }
    
    // 异常退出，尝试重启
    log.error(`Backend service crashed (code: ${code}, signal: ${signal})`);
    this.setStatus(BackendStatus.ERROR);
    this.emit('crashed', { code, signal });
    
    if (this.config.autoRestart && this.restartCount < this.config.maxRestartAttempts) {
      this.restartCount++;
      log.info(`Attempting to restart backend service (${this.restartCount}/${this.config.maxRestartAttempts})...`);
      
      setTimeout(() => {
        this.start().catch((error) => {
          log.error('Failed to restart backend service', error);
          this.emit('restart-failed', error);
        });
      }, this.config.restartDelay);
    } else {
      log.error('Max restart attempts reached, giving up');
      this.emit('fatal-error', new Error('Backend service failed to start after multiple attempts'));
    }
  }
  
  /**
   * 停止后端服务
   */
  async stop() {
    if (this.status === BackendStatus.STOPPED) {
      log.info('Backend service is already stopped');
      return;
    }
    
    log.info('Stopping backend service...');
    this.isShuttingDown = true;
    this.stopHealthCheck();
    
    if (this.startupTimer) {
      clearTimeout(this.startupTimer);
      this.startupTimer = null;
    }
    
    if (this.process) {
      return new Promise((resolve) => {
        const pid = this.pid;
        
        // 设置超时强制杀死进程
        const killTimer = setTimeout(() => {
          if (this.process) {
            log.warn(`Force killing backend process (PID: ${pid})`);
            this.process.kill('SIGKILL');
          }
        }, 5000); // 5 秒超时
        
        // 监听进程退出
        this.process.once('exit', () => {
          clearTimeout(killTimer);
          log.info('Backend service stopped');
          this.setStatus(BackendStatus.STOPPED);
          resolve();
        });
        
        // 发送 SIGTERM 信号
        log.info(`Sending SIGTERM to backend process (PID: ${pid})`);
        this.process.kill('SIGTERM');
      });
    } else {
      this.setStatus(BackendStatus.STOPPED);
    }
  }
  
  /**
   * 重启后端服务
   */
  async restart() {
    log.info('Restarting backend service...');
    await this.stop();
    await this.start();
  }
  
  /**
   * 设置状态
   */
  setStatus(status) {
    if (this.status !== status) {
      const oldStatus = this.status;
      this.status = status;
      log.info(`Backend status changed: ${oldStatus} -> ${status}`);
      this.emit('status-changed', { status, oldStatus });
    }
  }
  
  /**
   * 获取状态
   */
  getStatus() {
    return {
      status: this.status,
      pid: this.pid,
      port: this.config.port,
      host: this.config.host,
      baseUrl: this.getBaseUrl(),
      startTime: this.startTime,
      restartCount: this.restartCount,
      uptime: this.startTime ? Date.now() - this.startTime.getTime() : 0
    };
  }
  
  /**
   * 检查服务是否运行中
   */
  isRunning() {
    return this.status === BackendStatus.RUNNING;
  }
}

module.exports = { BackendManager, BackendStatus, getPythonPath, getBackendScriptPath };
