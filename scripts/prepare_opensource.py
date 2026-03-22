#!/usr/bin/env python3
"""
准备开源发布脚本
清理所有硬编码的 API Key 和敏感信息
"""
import os
import re
from pathlib import Path

# 需要清理的文件模式
FILES_TO_CLEAN = [
    "backend/services/*.py",
    "backend/routers/*.py",
    "backend/models/*.py",
]

# API Key 模式
API_KEY_PATTERNS = [
    (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = os.getenv("STEPFUN_API_KEY", "")'),
    (r'STEPFUN_API_KEY\s*=\s*["\'][^"\']+["\']', 'STEPFUN_API_KEY = os.getenv("STEPFUN_API_KEY", "")'),
    (r'KIMI_API_KEY\s*=\s*["\'][^"\']+["\']', 'KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")'),
    (r'sk-[a-zA-Z0-9]{20,}', 'YOUR_API_KEY_HERE'),
    (r'[0-9a-zA-Z]{40,}', 'YOUR_API_KEY_HERE'),  # 长字符串可能是 API Key
]


def clean_file(file_path: Path):
    """清理单个文件中的 API Key"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用所有清理模式
        for pattern, replacement in API_KEY_PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已清理: {file_path}")
            return True
        else:
            print(f"⏭️  无需清理: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 清理失败 {file_path}: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("准备开源发布 - 清理敏感信息")
    print("=" * 60)
    
    cleaned_count = 0
    total_count = 0
    
    # 遍历所有需要清理的文件
    for pattern in FILES_TO_CLEAN:
        for file_path in Path(".").glob(pattern):
            total_count += 1
            if clean_file(file_path):
                cleaned_count += 1
    
    print("=" * 60)
    print(f"清理完成: {cleaned_count}/{total_count} 个文件被修改")
    print("=" * 60)
    
    # 检查 .env 文件
    if Path(".env").exists():
        print("\n⚠️  警告: .env 文件仍然存在")
        print("   请确保不要将 .env 文件提交到版本控制")
        print("   .gitignore 已配置忽略 .env 文件")
    
    print("\n✅ 开源准备完成！")
    print("\n下一步:")
    print("1. 检查所有修改的文件")
    print("2. 确认没有遗漏的敏感信息")
    print("3. 运行测试确保功能正常")
    print("4. 提交到 Git 仓库")
    print("5. 推送到 GitHub")


if __name__ == "__main__":
    main()
