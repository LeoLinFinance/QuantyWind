#!/usr/bin/env python3
"""
数据库初始化脚本

此脚本用于初始化安全远程访问部署系统的数据库。
它会创建数据库（如果不存在）并应用所有迁移。

使用方法：
    python scripts/init_database.py
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from dotenv import load_dotenv
import subprocess

# 加载环境变量
load_dotenv()

def parse_database_url(url: str) -> dict:
    """
    解析数据库 URL
    
    Args:
        url: 数据库连接 URL
        
    Returns:
        dict: 包含数据库连接信息的字典
    """
    # 格式：postgresql://username:password@host:port/database
    parts = url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    return {
        'username': user_pass[0],
        'password': user_pass[1] if len(user_pass) > 1 else '',
        'host': host_port[0],
        'port': host_port[1] if len(host_port) > 1 else '5432',
        'database': host_port_db[1] if len(host_port_db) > 1 else 'quantflow'
    }

def create_database_if_not_exists():
    """
    创建数据库（如果不存在）
    """
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://quantflow_user:password@localhost:5432/quantflow"
    )
    
    db_info = parse_database_url(database_url)
    database_name = db_info['database']
    
    # 连接到 postgres 数据库（默认数据库）
    admin_url = f"postgresql://{db_info['username']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/postgres"
    
    try:
        print(f"正在检查数据库 '{database_name}' 是否存在...")
        engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
            )
            exists = result.fetchone() is not None
            
            if not exists:
                print(f"数据库 '{database_name}' 不存在，正在创建...")
                conn.execute(text(f'CREATE DATABASE "{database_name}"'))
                print(f"✓ 数据库 '{database_name}' 创建成功")
            else:
                print(f"✓ 数据库 '{database_name}' 已存在")
        
        engine.dispose()
        return True
        
    except OperationalError as e:
        print(f"✗ 数据库连接失败: {e}")
        print("\n请确保：")
        print("1. PostgreSQL 服务正在运行")
        print("2. 数据库凭证正确（检查 .env 文件）")
        print("3. 用户有创建数据库的权限")
        return False
    except Exception as e:
        print(f"✗ 创建数据库时出错: {e}")
        return False

def run_migrations():
    """
    运行 Alembic 迁移
    """
    try:
        print("\n正在应用数据库迁移...")
        
        # 检查当前迁移状态
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print(f"当前迁移状态: {result.stdout.strip()}")
        
        # 应用迁移
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✓ 迁移应用成功")
            print(result.stdout)
            return True
        else:
            print("✗ 迁移应用失败")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("✗ 未找到 alembic 命令")
        print("请先安装 alembic: pip install alembic")
        return False
    except Exception as e:
        print(f"✗ 运行迁移时出错: {e}")
        return False

def verify_tables():
    """
    验证表是否创建成功
    """
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://quantflow_user:password@localhost:5432/quantflow"
    )
    
    try:
        print("\n正在验证表结构...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            expected_tables = ['users', 'sessions', 'audit_logs', 'licenses', 'alembic_version']
            
            print(f"找到 {len(tables)} 个表:")
            for table in tables:
                status = "✓" if table in expected_tables else "?"
                print(f"  {status} {table}")
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                print(f"\n⚠ 缺少表: {', '.join(missing_tables)}")
                return False
            
            print("\n✓ 所有必需的表都已创建")
            return True
            
        engine.dispose()
        
    except Exception as e:
        print(f"✗ 验证表时出错: {e}")
        return False

def main():
    """
    主函数
    """
    print("=" * 60)
    print("安全远程访问部署系统 - 数据库初始化")
    print("=" * 60)
    
    # 步骤 1: 创建数据库
    if not create_database_if_not_exists():
        print("\n✗ 数据库初始化失败")
        sys.exit(1)
    
    # 步骤 2: 运行迁移
    if not run_migrations():
        print("\n✗ 数据库初始化失败")
        sys.exit(1)
    
    # 步骤 3: 验证表
    if not verify_tables():
        print("\n⚠ 数据库初始化完成，但表验证失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ 数据库初始化成功！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 运行应用: python backend/main.py")
    print("2. 或使用 Docker: docker-compose up")
    print("\n查看迁移状态: alembic current")
    print("查看迁移历史: alembic history")

if __name__ == "__main__":
    main()
