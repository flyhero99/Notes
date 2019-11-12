// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import router from './router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'
import App from './App'
import Vuex from 'vuex'
import 'echarts'
import Config from './config'
import utils from './utils'
import AsyncComputed from 'vue-async-computed'

Vue.config.productionTip = false
Vue.use(ElementUI)
Vue.use(Vuex)
Vue.use(AsyncComputed)
axios.defaults.withCredentials = true
let instance = axios.create({
  baseURL: Config.baseUrl,
  withCredentials: true
})
if (Config.isDevelopmentEnv) {
  instance.defaults.auth = {
    username: 'wuxian',
    password: '123456'
  }
}
instance.interceptors.response.use(function (response) {
  return response
}, function (error) {
  utils.errorHandler(error)
  return Promise.reject(error)
})
Vue.prototype.$axios = instance
Vue.prototype.$global = Config
Vue.prototype.$utils = utils

const store = new Vuex.Store({
  state: {
    user: {}
  },
  mutations: {
    update_user (state, user) {
      state.user = user
    }
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  render: h => h(App),
  router,
  store,
  components: { App },
  template: '<App/>'
})
