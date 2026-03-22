"""
测试新闻总结服务
"""
import sys
sys.path.append('backend')

from services.news_summary_service import NewsSummaryService
import asyncio

async def test_news_summary():
    """测试新闻总结服务"""
    
    print("=" * 60)
    print("测试新闻总结服务")
    print("=" * 60)
    
    # 初始化服务
    service = NewsSummaryService()
    
    # 测试新闻总结
    print("\n1. 测试新闻总结功能")
    print("-" * 60)
    
    try:
        result = service.summarize_news()
        
        print(f"✅ 新闻总结成功")
        print(f"   新闻数量: {result['news_count']}")
        print(f"   持仓股票: {', '.join(result['portfolio_symbols'])}")
        print(f"   时间戳: {result['timestamp']}")
        print(f"   数据源: {result['source']}")
        print(f"\n   总结内容:")
        print(f"   {result['summary'][:500]}...")
        
    except Exception as e:
        print(f"❌ 新闻总结失败: {e}")
    
    # 测试自定义提示词
    print("\n\n2. 测试自定义提示词")
    print("-" * 60)
    
    custom_prompt = """你是一位保守型投资顾问。请根据新闻资讯，重点关注：
1. 市场风险和不确定性
2. 防御性投资机会
3. 需要规避的高风险领域
请提供稳健的投资建议。"""
    
    try:
        result = service.summarize_news(custom_prompt=custom_prompt)
        
        print(f"✅ 自定义提示词总结成功")
        print(f"   总结内容:")
        print(f"   {result['summary'][:500]}...")
        
    except Exception as e:
        print(f"❌ 自定义提示词总结失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_news_summary())
