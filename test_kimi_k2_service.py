"""
测试更新后的Kimi Research Service (使用Kimi-k2)
"""
import sys
sys.path.append('backend')

from services.kimi_research_service import KimiResearchService

def test_kimi_service():
    """测试Kimi研究服务"""
    
    print("=" * 60)
    print("测试Kimi-k2 Research Service")
    print("=" * 60)
    
    # 初始化服务
    service = KimiResearchService()
    
    # 测试1: 宏观经济研究
    print("\n1. 测试宏观经济研究")
    print("-" * 60)
    
    try:
        result = service.research_macro_environment()
        print(f"✅ 宏观研究成功")
        print(f"   时间戳: {result['timestamp']}")
        print(f"   数据源: {result['source']}")
        print(f"   内容长度: {len(result['research_content'])} 字符")
        print(f"\n   内容预览:")
        print(f"   {result['research_content'][:300]}...")
    except Exception as e:
        print(f"❌ 宏观研究失败: {e}")
    
    # 测试2: 股票研究
    print("\n\n2. 测试股票研究 (AAPL)")
    print("-" * 60)
    
    try:
        result = service.research_stock('AAPL', 'Apple Inc.')
        print(f"✅ 股票研究成功")
        print(f"   股票: {result['symbol']}")
        print(f"   时间戳: {result['timestamp']}")
        print(f"   数据源: {result['source']}")
        print(f"   内容长度: {len(result['research_content'])} 字符")
        print(f"\n   内容预览:")
        print(f"   {result['research_content'][:300]}...")
    except Exception as e:
        print(f"❌ 股票研究失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_kimi_service()
