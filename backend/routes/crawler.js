const express = require('express')
const router = express.Router()

// 手动触发采集
router.post('/trigger', async (req, res) => {
  try {
    // 这里可以触发一次采集任务
    res.json({ 
      success: true, 
      message: '采集任务已触发' 
    })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

module.exports = router
