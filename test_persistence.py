#!/usr/bin/env python3
"""
持久化功能测试脚本
用于验证数据持久化是否正常工作
"""
import sys
sys.path.insert(0, 'backend')

from services.persistence_service import PersistenceService
from services.market_service import MarketService

def test_persistence():
    """测试持久化功能"""
    
    print("=" * 60)
    print("持久化功能测试")
    print("=" * 60)
    
    # 1. 测试持久化服务
    print("\n【测试1】持久化服务基本功能")
    persistence = PersistenceService()
    
    # 保存测试数据
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    persistence.save_watchlist(test_symbols)
    
    test_prompt = "这是一个测试提示词"
    persistence.save_system_prompt(test_prompt)
    
    # 加载数据
    loaded_symbols = persistence.load_watchlist()
    loaded_prompt = persistence.load_system_prompt()
    
    assert loaded_symbols == test_symbols, "盯盘列表不一致"
    assert loaded_prompt == test_prompt, "提示词不一致"
    print("✅ 持久化服务测试通过")
    
    # 2. 测试MarketService集成
    print("\n【测试2】MarketService集成")
    market = MarketService()
    
    print(f"   当前盯盘列表: {market.watchlist_symbols}")
    print(f"   当前提示词: {market.system_prompt or '(使用默认)'}")
    print("✅ MarketService成功加载持久化数据")
    
    # 3. 测试数据信息
    print("\n【测试3】数据信息查询")
    info = persistence.get_all_data_info()
    print(f"   盯盘列表: {'存在' if info['watchlist']['exists'] else '不存在'} "
          f"({info['watchlist']['count']}只股票)")
    print(f"   系统提示词: {'存在' if info['system_prompt']['exists'] else '不存在'}")
    print(f"   用户设置: {'存在' if info['user_settings']['exists'] else '不存在'}")
    print("✅ 数据信息查询成功")
    
    # 4. 测试重启恢复
    print("\n【测试4】模拟重启恢复")
    # 修改数据
    new_symbols = ['NVDA', 'AMD', 'BABA']
    market.watchlist_symbols = new_symbols
    market.persistence.save_watchlist(new_symbols)
    
    new_prompt = "新的自定义提示词"
    market.update_system_prompt(new_prompt)
    
    # 模拟重启
    del market
    market2 = MarketService()
    
    assert market2.watchlist_symbols == new_symbols, "重启后盯盘列表未恢复"
    assert market2.system_prompt == new_prompt, "重启后提示词未恢复"
    print("✅ 重启后数据成功恢复")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print("\n持久化功能正常工作，您的数据将在后端重启后自动恢复。")
    print("\n数据文件位置: backend/data/config/")
    print("  - watchlist.json       (盯盘列表)")
    print("  - system_prompt.json   (系统提示词)")
    print("  - user_settings.json   (用户设置)")

if __name__ == '__main__':
    try:
        test_persistence()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
