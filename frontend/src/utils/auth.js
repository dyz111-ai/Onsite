// 获取当前登录用户
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

// 获取 token
export const getToken = () => {
  return localStorage.getItem('token')
}

// 检查是否已登录
export const isAuthenticated = () => {
  return !!getToken()
}

// 退出登录
export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  window.location.href = '/login'
}
