const axios = require('axios')

async function testKimiCode() {
  const apiKey = 'sk-kimi-Ga9uU1AHbWdaz4Rg3gGolQlvVUUVso9MWEaVo9yOuSoQiHazJnVXbCTYcpgYjIgV'
  
  console.log('测试 Kimi Code API Key...\n')
  console.log('Key 前缀:', apiKey.substring(0, 20) + '...')
  console.log('Key 长度:', apiKey.length)
  
  // Kimi Code 可能使用不同的端点
  const endpoints = [
    { name: 'Moonshot 标准端点', url: 'https://api.moonshot.cn/v1/chat/completions' },
    { name: 'Kimi Code 端点', url: 'https://api.moonshot.cn/v1/code/completions' },
    { name: 'Kimi 备用端点', url: 'https://kimi.moonshot.cn/api/chat/completions' }
  ]
  
  const models = ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k', 'kimi-code']
  
  for (const endpoint of endpoints) {
    console.log(`\n📡 测试端点: ${endpoint.name}`)
    console.log(`   URL: ${endpoint.url}`)
    
    for (const model of models) {
      try {
        const response = await axios.post(
          endpoint.url,
          {
            model: model,
            messages: [
              { role: 'user', content: '你好，请用一句话介绍你自己' }
            ],
            temperature: 0.3,
            max_tokens: 100
          },
          {
            headers: {
              'Authorization': `Bearer ${apiKey}`,
              'Content-Type': 'application/json'
            },
            timeout: 30000
          }
        )
        
        console.log(`   ✅ 模型 ${model} 成功!`)
        console.log(`   回复: ${response.data.choices[0].message.content}`)
        console.log(`   使用: ${JSON.stringify(response.data.usage)}`)
        return { endpoint: endpoint.url, model }
        
      } catch (error) {
        if (error.response) {
          const status = error.response.status
          const errorType = error.response.data?.error?.type
          
          if (status === 404) {
            console.log(`   ⚠️  模型 ${model} 不存在`)
            continue
          } else if (status === 401) {
            console.log(`   ❌ 认证失败 (401)`)
            break // 如果认证失败，跳过该端点的其他模型
          } else if (status === 429) {
            console.log(`   ❌ 配额不足 (429)`)
            break
          } else {
            console.log(`   ❌ 模型 ${model} 失败: ${status} - ${errorType}`)
          }
        } else if (error.code === 'ENOTFOUND') {
          console.log(`   ❌ 端点不存在`)
          break
        } else {
          console.log(`   ❌ 网络错误: ${error.message}`)
        }
      }
    }
  }
  
  return null
}

testKimiCode().then(result => {
  console.log('\n' + '='.repeat(60))
  if (result) {
    console.log('✅ 找到可用配置!')
    console.log(`   端点: ${result.endpoint}`)
    console.log(`   模型: ${result.model}`)
  } else {
    console.log('❌ 未找到可用配置')
    console.log('💡 建议使用阶跃星辰API作为替代方案')
  }
  console.log('='.repeat(60))
})
