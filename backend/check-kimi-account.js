const axios = require('axios')

async function checkKimiAccount() {
  const apiKey = 'sk-lFxuEqj2Ke57WONHYzewESJhEKAAiU11ftadXRiRRN5i35lk'
  
  console.log('检查 Kimi 账户状态...\n')
  
  // 1. 测试简单请求
  console.log('1️⃣ 测试基础连接...')
  try {
    const response = await axios.post(
      'https://api.moonshot.cn/v1/chat/completions',
      {
        model: 'moonshot-v1-8k',
        messages: [
          { role: 'user', content: '你好' }
        ],
        max_tokens: 10
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    console.log('✅ 连接成功!')
    console.log('回复:', response.data.choices[0].message.content)
    console.log('使用tokens:', response.data.usage)
    return true
    
  } catch (error) {
    if (error.response) {
      console.error('❌ 请求失败')
      console.error('状态码:', error.response.status)
      console.error('错误详情:', JSON.stringify(error.response.data, null, 2))
      
      if (error.response.status === 429) {
        console.log('\n💡 错误原因: 账户余额不足或配额用尽')
        console.log('💡 建议: 请前往 https://platform.moonshot.cn 充值或检查配额')
      } else if (error.response.status === 401) {
        console.log('\n💡 错误原因: API Key 无效或已过期')
      }
    } else {
      console.error('❌ 网络错误:', error.message)
    }
    return false
  }
}

checkKimiAccount()
