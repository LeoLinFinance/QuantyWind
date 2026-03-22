"""
诊断专家模型超时问题
"""
import asyncio
import time
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试配置
STEPFUN_BASE_URL = "https://api.stepfun.com/v1"
STEPFUN_MODEL = "step-1-32k"
TEST_API_KEY = "71l4il2y6OSbR76taoahpsCSfWepmQZpEUsLG2GYqpFOVK8LEV0PyynJ2MUp29q23"

def test_without_timeout():
    """测试不设置超时的情况"""
    print("\n" + "="*60)
    print("测试1: 不设置HTTP超时（默认行为）")
    print("="*60)
    
    try:
        start_time = time.time()
        
        client = OpenAI(
            api_key=TEST_API_KEY,
            base_url=STEPFUN_BASE_URL
        )
        
        print("发送请求...")
        response = client.chat.completions.create(
            model=STEPFUN_MODEL,
            messages=[
                {"role": "system", "content": "你是一位专业的投资分析师"},
                {"role": "user", "content": "请简单介绍一下苹果公司"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        elapsed = time.time() - start_time
        print(f"✅ 请求成功，耗时: {elapsed:.2f}秒")
        print(f"响应长度: {len(response.choices[0].message.content)} 字符")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 请求失败，耗时: {elapsed:.2f}秒")
        print(f"错误: {type(e).__name__}: {e}")

def test_with_timeout():
    """测试设置HTTP超时的情况"""
    print("\n" + "="*60)
    print("测试2: 设置HTTP超时（60秒）")
    print("="*60)
    
    try:
        start_time = time.time()
        
        client = OpenAI(
            api_key=TEST_API_KEY,
            base_url=STEPFUN_BASE_URL,
            timeout=60.0  # 设置60秒HTTP超时
        )
        
        print("发送请求...")
        response = client.chat.completions.create(
            model=STEPFUN_MODEL,
            messages=[
                {"role": "system", "content": "你是一位专业的投资分析师"},
                {"role": "user", "content": "请简单介绍一下苹果公司"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        elapsed = time.time() - start_time
        print(f"✅ 请求成功，耗时: {elapsed:.2f}秒")
        print(f"响应长度: {len(response.choices[0].message.content)} 字符")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 请求失败，耗时: {elapsed:.2f}秒")
        print(f"错误: {type(e).__name__}: {e}")

def test_with_asyncio_timeout():
    """测试asyncio超时控制"""
    print("\n" + "="*60)
    print("测试3: 使用asyncio超时控制（45秒）")
    print("="*60)
    
    async def make_request():
        from concurrent.futures import ThreadPoolExecutor
        
        def sync_call():
            client = OpenAI(
                api_key=TEST_API_KEY,
                base_url=STEPFUN_BASE_URL,
                timeout=60.0
            )
            
            response = client.chat.completions.create(
                model=STEPFUN_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的投资分析师"},
                    {"role": "user", "content": "请简单介绍一下苹果公司"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        try:
            start_time = time.time()
            print("发送请求（45秒超时）...")
            
            with ThreadPoolExecutor() as executor:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, sync_call),
                    timeout=45.0
                )
            
            elapsed = time.time() - start_time
            print(f"✅ 请求成功，耗时: {elapsed:.2f}秒")
            print(f"响应长度: {len(result)} 字符")
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"❌ asyncio超时，耗时: {elapsed:.2f}秒")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ 请求失败，耗时: {elapsed:.2f}秒")
            print(f"错误: {type(e).__name__}: {e}")
    
    asyncio.run(make_request())

def test_complex_query():
    """测试复杂查询（模拟实际场景）"""
    print("\n" + "="*60)
    print("测试4: 复杂查询（模拟实际专家分析）")
    print("="*60)
    
    # 构建类似实际场景的复杂查询
    complex_query = """【对话历史】
用户: 请分析一下当前市场情况

【当前持仓详情】
AAPL - Apple Inc.
  持仓: 100股
  成本价: $150.00
  当前价: $175.50 (+17.00%)
  市值: $17,550.00
  盈亏: +$2,550.00 (+17.00%)

TSLA - Tesla Inc.
  持仓: 50股
  成本价: $200.00
  当前价: $245.30 (+22.65%)
  市值: $12,265.00
  盈亏: +$2,265.00 (+22.65%)

【投资组合总览】
  总市值: $29,815.00
  总成本: $25,000.00
  总盈亏: +$4,815.00 (+19.26%)
  现金余额: $10,000.00

请根据以上对话历史、最新资讯和持仓情况，提供你的专业分析和建议。"""
    
    try:
        start_time = time.time()
        
        client = OpenAI(
            api_key=TEST_API_KEY,
            base_url=STEPFUN_BASE_URL,
            timeout=60.0
        )
        
        print("发送复杂查询...")
        response = client.chat.completions.create(
            model=STEPFUN_MODEL,
            messages=[
                {"role": "system", "content": "你是一位资深选股分析师，专注于投前分析。根据产业链状况、行业政策与前景、股票标的的近期表现以及财报等，综合推荐5-10只美股和港股。请提供具体的股票代码、推荐理由和风险提示。"},
                {"role": "user", "content": complex_query}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        elapsed = time.time() - start_time
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 'N/A'
        
        print(f"✅ 请求成功，耗时: {elapsed:.2f}秒")
        print(f"响应长度: {len(content)} 字符")
        print(f"Token使用: {tokens}")
        print(f"\n响应预览:\n{content[:200]}...")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 请求失败，耗时: {elapsed:.2f}秒")
        print(f"错误: {type(e).__name__}: {e}")

def main():
    print("\n" + "="*60)
    print("专家模型超时问题诊断")
    print("="*60)
    
    print("\n可能的超时原因:")
    print("1. OpenAI客户端没有设置HTTP超时")
    print("2. 网络延迟或API服务器响应慢")
    print("3. 查询过于复杂，模型生成时间长")
    print("4. API限流或并发限制")
    print("5. max_tokens设置过大")
    
    # 运行测试
    test_without_timeout()
    test_with_timeout()
    test_with_asyncio_timeout()
    test_complex_query()
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)
    
    print("\n建议的修复方案:")
    print("1. 为OpenAI客户端设置合理的HTTP超时（如60秒）")
    print("2. 增加asyncio超时时间到60秒")
    print("3. 优化查询内容，减少不必要的上下文")
    print("4. 考虑降低max_tokens（如从2000降到1500）")
    print("5. 添加重试机制")

if __name__ == "__main__":
    main()
