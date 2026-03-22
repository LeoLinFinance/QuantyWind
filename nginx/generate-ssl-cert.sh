#!/bin/bash
# SSL 证书生成脚本（用于开发环境）
# 生产环境请使用 Let's Encrypt 或购买的证书

echo "生成自签名 SSL 证书（仅用于开发环境）..."

# 创建 SSL 目录
mkdir -p ssl

# 生成私钥和证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=QuantFlow/OU=Development/CN=localhost"

echo "SSL 证书生成完成！"
echo "证书位置: nginx/ssl/cert.pem"
echo "私钥位置: nginx/ssl/key.pem"
echo ""
echo "注意：这是自签名证书，仅用于开发环境。"
echo "生产环境请使用 Let's Encrypt 或购买的证书。"
