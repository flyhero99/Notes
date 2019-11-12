// import axios from 'axios'
// import config from './config'
import {Message} from 'element-ui'

export default {
  getNowFormatDate: function () {
    let date = new Date()
    let seperator1 = '-'
    let seperator2 = ':'
    let month = date.getMonth() + 1
    let strDate = date.getDate()
    let hours = date.getHours()
    let minutes = date.getHours()
    let seconds = date.getSeconds()
    if (month >= 1 && month <= 9) {
      month = '0' + month
    }
    if (strDate >= 0 && strDate <= 9) {
      strDate = '0' + strDate
    }
    if (hours >= 0 && hours <= 9) {
      hours = '0' + hours
    }
    if (minutes >= 0 && minutes <= 9) {
      minutes = '0' + minutes
    }
    if (seconds >= 0 && seconds <= 9) {
      seconds = '0' + seconds
    }
    return date.getFullYear() + seperator1 + month + seperator1 + strDate +
      ' ' + hours + seperator2 + minutes + seperator2 + seconds
  },
  errorHandler: function (err) {
    if (err.response) {
      // 请求已经发出，但是服务器响应返回的状态吗不在2xx的范围内
      if (err.response.data.hasOwnProperty('detail')) {
        Message.error(err.response.data['detail'])
      } else if (err.response.status === 500) {
        Message.error('Whoops, 服务器好像出了点问题。')
      } else {
        Message.error(err.message)
      }
    } else {
      // 一些错误是在设置请求的时候触发
      console.log('Error', err.message)
    }
  },
  isEmptyObject: function (obj) {
    for (let n in obj) {
      return false
    }
    return true
  }
}
