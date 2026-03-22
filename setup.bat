@echo off
REM 量数风行 - Windows 快速设置脚本

echo ==================================
echo 量数风行 QuantyWind - 快速设置
echo ==================================
echo.

REM 检查 Python
echo 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.9+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python 版本: %PYTHON_VERSION%

REM 检查 Node.js
echo 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Node.js，请先安装 Node.js 16+
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js 版本: %NODE_VERSION%

REM 创建 .env 文件
echo.
echo 配置环境变量...
if not exist .env (
    copy .env.example .env
    echo ✅ 已创建 .env 文件
    echo 💡 提示: 您可以稍后在应用设置页面配置 API Key
) else (
    echo ⏭️  .env 文件已存在，跳过
)

REM 安装后端依赖
echo.
echo 安装后端依赖...
cd backend
if not exist venv (
    python -m venv venv
    echo ✅ 已创建虚拟环境
)

call venv\Scripts\activate.bat
pip install -r requirements.txt
echo ✅ 后端依赖安装完成

REM 初始化数据库
echo.
echo 初始化数据库...
if not exist alembic\versions mkdir alembic\versions
alembic upgrade head
echo ✅ 数据库初始化完成

cd ..

REM 安装前端依赖
echo.
echo 安装前端依赖...
call npm install
echo ✅ 前端依赖安装完成

REM 完成
echo.
echo ==================================
echo ✅ 设置完成！
echo ==================================
echo.
echo 下一步：
echo.
echo 1. 启动后端服务（命令提示符 1）：
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 2. 启动前端服务（命令提示符 2）：
echo    npm run dev
echo.
echo 3. 访问应用：
echo    http://localhost:3000
echo.
echo 4. 配置 API Key：
echo    访问 http://localhost:3000/settings
echo    添加您的 AI 服务 API Key
echo.
echo 📖 更多信息请查看 README.md 和 QUICKSTART.md
echo.
pause
