#!/usr/bin/env python3
"""
同步历史数据
从风险分析页面使用的数据源同步到AI分析服务
"""
import sys
sys.path.insert(0, 'backend')

from services.historical_data_service import HistoricalDataService
import json

def sync_data():
    """同步历史数据"""
    print("="*60)
    print("历史数据同步")
    print("="*60)
    
    # 初始化历史数据服务
    service = HistoricalDataService()
    
    # 重新加载数据
    service.reload_data()
    
    # 显示当前数据状态
    print("\n📊 当前数据状态:")
    print("-"*60)
    
    # 指数数据
    print(f"\n指数数据:")
    for symbol, info in service.data['indices'].items():
        data_count = len(info.get('data', []))
        last_update = info.get('last_update', 'N/A')
        print(f"  {symbol:8s} - {info['name']:20s} - {data_count:4d} 条数据 - 更新: {last_update[:10] if last_update != 'N/A' else 'N/A'}")
    
    # 股票数据
    print(f"\n股票数据:")
    for symbol, info in service.data['stocks'].items():
        data_count = len(info.get('data', []))
        last_update = info.get('last_update', 'N/A')
        is_active = info.get('is_active', False)
        status = "✅" if is_active else "⚠️"
        print(f"  {status} {symbol:8s} - {info['name']:35s} - {data_count:4d} 条数据 - 更新: {last_update[:10] if last_update != 'N/A' else 'N/A'}")
    
    # 元数据
    print(f"\n元数据:")
    metadata = service.data.get('metadata', {})
    print(f"  数据源: {metadata.get('data_source', 'N/A')}")
    print(f"  最后更新: {metadata.get('last_update', 'N/A')[:19] if metadata.get('last_update') else 'N/A'}")
    
    # 统计
    total_stocks = len(service.data['stocks'])
    total_indices = len(service.data['indices'])
    active_stocks = sum(1 for info in service.data['stocks'].values() if info.get('is_active', False))
    
    print(f"\n📈 数据统计:")
    print(f"  股票总数: {total_stocks}")
    print(f"  活跃股票: {active_stocks}")
    print(f"  指数总数: {total_indices}")
    
    # 数据质量检查
    print(f"\n🔍 数据质量检查:")
    print("-"*60)
    
    issues = []
    
    # 检查空数据
    for symbol, info in service.data['stocks'].items():
        data_count = len(info.get('data', []))
        if data_count == 0:
            issues.append(f"❌ {symbol}: 无数据")
        elif data_count < 20:
            issues.append(f"⚠️  {symbol}: 数据不足 ({data_count} 条，建议至少20条)")
    
    if issues:
        print("发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ 所有数据质量检查通过")
    
    # 建议
    print(f"\n💡 建议:")
    print("-"*60)
    
    if total_stocks == 0:
        print("  1. 运行 python3 init_mock_data.py 初始化模拟数据")
        print("  2. 或配置真实数据源API密钥")
    elif any(len(info.get('data', [])) < 20 for info in service.data['stocks'].values()):
        print("  1. 部分股票数据不足，建议更新数据")
        print("  2. 运行数据更新API: POST /api/historical-data/update")
    else:
        print("  ✅ 数据充足，可以正常使用AI分析功能")
    
    print("\n" + "="*60)
    print("同步完成")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        sync_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
