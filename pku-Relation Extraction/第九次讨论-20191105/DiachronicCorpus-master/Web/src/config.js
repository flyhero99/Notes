let baseUrl = ''
let isDevelopmentEnv = process.env.NODE_ENV === 'development'
if (isDevelopmentEnv) {
  baseUrl = 'http://162.105.86.36:6566'
} else {
  baseUrl = 'http://162.105.86.36:6567'
}

export default {
  name: 'Config',
  baseUrl,
  isDevelopmentEnv
}
