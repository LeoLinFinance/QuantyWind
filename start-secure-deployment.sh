#!/bin/bash
# 安全部署快速启动脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "量数风行 - 安全部署启动脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未安装 Docker"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：未安装 Docker Compose"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"
echo ""

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "⚠️  警告：未找到 .env 文件"
    echo "正在从 .env.example 创建 .env 文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "⚠️  重要：请编辑 .env 文件并配置以下内容："
    echo "   1. 数据库密码 (POSTGRES_PASSWORD)"
    echo "   2. Redis 密码 (REDIS_PASSWORD)"
    echo "   3. 应用密钥 (SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY)"
    echo "   4. API 密钥 (STEPFUN_API_KEY, KIMI_API_KEY, etc.)"
    echo ""
    echo "💡 提示：运行 'python3 generate-secrets.py' 生成安全密钥"
    echo ""
    read -p "是否现在生成密钥？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 generate-secrets.py
        echo ""
        echo "请将上述密钥复制到 .env 文件中"
        echo ""
    fi
    read -p "配置完成后按 Enter 继续..."
fi

echo "✅ 找到 .env 文件"
echo ""

# 检查 SSL 证书是否存在
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "⚠️  警告：未找到 SSL 证书"
    echo "正在生成自签名证书（仅用于开发环境）..."
    cd nginx
    chmod +x generate-ssl-cert.sh
    ./generate-ssl-cert.sh
    cd ..
    echo "✅ SSL 证书已生成"
    echo ""
    echo "⚠️  注意：这是自签名证书，浏览器会显示安全警告"
    echo "   生产环境请使用 Let's Encrypt 或购买的证书"
    echo ""
else
    echo "✅ 找到 SSL 证书"
    echo ""
fi

# 询问是否构建镜像
echo "准备启动服务..."
read -p "是否需要重新构建 Docker 镜像？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在构建 Docker 镜像..."
    docker-compose build
    echo "✅ 镜像构建完成"
    echo ""
fi

# 启动服务
echo "正在启动服务..."
docker-compose up -d

echo ""
echo "=========================================="
echo "✅ 服务启动成功！"
echo "=========================================="
echo ""
echo "服务状态："
docker-compose ps
echo ""
echo "访问地址："
echo "  - 前端应用: https://localhost/"
echo "  - 健康检查: https://localhost/health"
echo "  - API 文档: https://localhost/api/docs (仅开发环境)"
echo ""
echo "常用命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose stop"
echo "  - 重启服务: docker-compose restart"
echo "  - 查看状态: docker-compose ps"
echo ""
echo "⚠️  首次启动可能需要几分钟初始化数据库"
echo "   请运行 'docker-compose logs -f app' 查看启动日志"
echo ""
echo "📚 详细文档："
echo "  - 部署指南: DOCKER_DEPLOYMENT.md"
echo "  - 安全清单: SECURITY_CHECKLIST.md"
echo "  - 快速开始: SECURE_DEPLOYMENT_README.md"
echo ""
