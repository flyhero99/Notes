<template>
  <el-col :span="8" :offset="8">
    <h1>登录</h1>
    <el-form>
      <el-form-item label="用户名">
        <el-input type="text" name="user" v-model="loginForm.user">
        </el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input type="password" name="password" v-model="loginForm.password">
        </el-input>
      </el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form>
  </el-col>
</template>

<script>
export default {
  name: 'login',
  data () {
    return {
      loginForm: {// 表单中的参数
        user: '',
        password: ''
      }
    }
  },
  methods: {
    resetForm: function () {
      this.loginForm.user = ''
      this.loginForm.password = ''
    },
    submitForm: function () {
      let user = this.loginForm.user
      let password = this.loginForm.password
      this.$axios.post('/common/session/', {
        username: user,
        password: password
      }).then(res => {
        this.$message.info('登录成功，欢迎' + res.data.user.username)
        this.$store.commit('update_user', res.data.user)
        this.$router.push('/')
      })
    }
  },
  computed: {
  }
}
</script>

<style scoped>

</style>
