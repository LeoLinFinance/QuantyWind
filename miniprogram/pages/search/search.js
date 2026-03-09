const app = getApp()

Page({
  data: {
    keyword: '',
    results: [],
    searching: false,
    searched: false
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    const { keyword } = this.data
    if (!keyword.trim()) {
      wx.showToast({ title: '请输入关键词', icon: 'none' })
      return
    }

    this.setData({ searching: true })

    wx.request({
      url: `${app.globalData.apiBase}/articles/search`,
      data: { keyword },
      success: (res) => {
        if (res.data.success) {
          this.setData({
            results: res.data.data,
            searched: true
          })
        }
      },
      fail: () => {
        wx.showToast({ title: '搜索失败', icon: 'none' })
      },
      complete: () => {
        this.setData({ searching: false })
      }
    })
  },

  goToDetail(e) {
    const articleId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${articleId}`
    })
  }
})
