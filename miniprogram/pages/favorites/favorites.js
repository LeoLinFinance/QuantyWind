const app = getApp()

Page({
  data: {
    favorites: [],
    loading: false
  },

  onShow() {
    this.loadFavorites()
  },

  loadFavorites() {
    const favoriteIds = wx.getStorageSync('favorites') || []
    
    if (favoriteIds.length === 0) {
      this.setData({ favorites: [] })
      return
    }

    this.setData({ loading: true })

    // 批量获取收藏的文章
    const requests = favoriteIds.map(id => 
      new Promise((resolve) => {
        wx.request({
          url: `${app.globalData.apiBase}/articles/${id}`,
          success: (res) => {
            if (res.data.success) {
              resolve(res.data.data)
            } else {
              resolve(null)
            }
          },
          fail: () => resolve(null)
        })
      })
    )

    Promise.all(requests).then(articles => {
      this.setData({
        favorites: articles.filter(a => a !== null),
        loading: false
      })
    })
  },

  goToDetail(e) {
    const articleId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${articleId}`
    })
  },

  removeFavorite(e) {
    const articleId = e.currentTarget.dataset.id
    
    wx.showModal({
      title: '提示',
      content: '确定取消收藏？',
      success: (res) => {
        if (res.confirm) {
          let favorites = wx.getStorageSync('favorites') || []
          favorites = favorites.filter(id => id !== articleId)
          wx.setStorageSync('favorites', favorites)
          this.loadFavorites()
          wx.showToast({ title: '已取消收藏', icon: 'success' })
        }
      }
    })
  }
})
