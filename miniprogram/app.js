App({
  globalData: {
    apiBase: 'https://your-api-domain.com/api',
    userInfo: null
  },

  onLaunch() {
    console.log('滴答学术启动')
    this.checkUpdate()
  },

  checkUpdate() {
    const updateManager = wx.getUpdateManager()
    updateManager.onUpdateReady(() => {
      wx.showModal({
        title: '更新提示',
        content: '新版本已准备好，是否重启应用？',
        success: (res) => {
          if (res.confirm) {
            updateManager.applyUpdate()
          }
        }
      })
    })
  }
})
