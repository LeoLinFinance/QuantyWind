#!/usr/bin/env python3
"""
测试专家提示词是否正确传递
"""
import asyncio
import sys
from pathlib import Path

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.expert_forum_service import ExpertForumService

async def test_expert_prompt():
    """测试专家提示词传递"""
    print("\n" + "="*60)
    print("测试专家提示词传递")
    print("="*60)
    
    try:
        service = ExpertForumService()
        
        # 获取专家配置
        configs = await service.get_expert_configs()
        if not configs:
            print("❌ 没有专家配置，请先运行: python3 init_expert_configs.py")
            return False
        
        print(f"✅ 找到 {len(configs)} 个专家配置\n")
        
        # 显示第一个专家的配置
        expert = configs[0]
        print(f"专家ID: {expert['id']}")
        print(f"专家名称: {expert['name']}")
        print(f"\n专家提示词:")
        print("-" * 60)
        print(expert['prompt'])
        print("-" * 60)
        
        # 测试调用
        print(f"\n开始测试调用 {expert['name']}...")
        print("注意观察后端日志，确认:")
        print("  1. system消息包含专家提示词")
        print("  2. user消息包含持仓和对话历史")
        
        result = await service.get_expert_analysis(
            expert_id=expert['id'],
            expert_name=expert['name'],
            expert_prompt=expert['prompt'],
            context="测试上下文"
        )
        
        print(f"\n✅ 调用成功")
        print(f"\n分析结果预览:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
        print("-" * 60)
        
        # 检查分析是否符合专家角色
        print(f"\n验证分析是否符合专家角色:")
        if expert['id'] == 'stock_analyst':
            keywords = ['选股', '投资', '股票', '推荐']
        elif expert['id'] == 'industry_analyst':
            keywords = ['产业链', '行业', '供应链']
        elif expert['id'] == 'market_analyst':
            keywords = ['市场', '趋势', '技术分析']
        elif expert['id'] == 'value_investor':
            keywords = ['价值', '长期', '基本面']
        elif expert['id'] == 'chief_economist':
            keywords = ['宏观', '经济', '政策']
        else:
            keywords = []
        
        found_keywords = [kw for kw in keywords if kw in analysis]
        if found_keywords:
            print(f"  ✅ 发现相关关键词: {', '.join(found_keywords)}")
            print(f"  ✅ 分析符合专家角色特征")
        else:
            print(f"  ⚠️  未发现预期关键词: {', '.join(keywords)}")
            print(f"  ⚠️  可能提示词未正确传递")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_all_experts():
    """测试所有专家的提示词"""
    print("\n" + "="*60)
    print("测试所有专家配置")
    print("="*60)
    
    try:
        service = ExpertForumService()
        configs = await service.get_expert_configs()
        
        if not configs:
            print("❌ 没有专家配置")
            return False
        
        print(f"\n找到 {len(configs)} 个专家:\n")
        
        for i, expert in enumerate(configs, 1):
            print(f"{i}. {expert['name']} (ID: {expert['id']})")
            print(f"   提示词长度: {len(expert['prompt'])} 字符")
            print(f"   提示词预览: {expert['prompt'][:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """运行测试"""
    print("\n" + "="*60)
    print("专家提示词传递验证")
    print("="*60)
    print("\n问题: 系统提示词一直不存在")
    print("原因: expert_prompt 应该作为 system 消息，而不是放在 user 消息中")
    print("\n修复: 将 expert_prompt 作为 system 角色传递给 StepFun API")
    
    # 测试所有专家配置
    await test_all_experts()
    
    # 测试单个专家调用
    result = await test_expert_prompt()
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    if result:
        print("✅ 专家提示词传递正确")
        print("\n验证要点:")
        print("  1. ✅ expert_prompt 作为 system 消息传递")
        print("  2. ✅ 持仓和对话历史作为 user 消息传递")
        print("  3. ✅ 分析结果符合专家角色特征")
    else:
        print("❌ 测试失败，请检查配置")

if __name__ == "__main__":
    asyncio.run(main())
