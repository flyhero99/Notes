<template>
  <el-menu default-active="1" class="el-menu-demo" mode="horizontal" :router="true"
           background-color="#545c64"
           text-color="#fff"
           active-text-color="#ffd04b">
    <el-menu-item index="/">首页</el-menu-item>
    <el-submenu index="/searching">
      <template slot="title">检索</template>
      <el-menu-item index="/search">单检索</el-menu-item>
      <el-menu-item index="/cosearch">共现检索</el-menu-item>
      <el-menu-item index="/pmi">PMI变迁</el-menu-item>
      <el-menu-item index="/pos_pmi">PosPMI变迁</el-menu-item>
      <el-menu-item index="/phrase_pmi">PMI变迁（短语）</el-menu-item>
    </el-submenu>
    <el-menu-item index="/notebook/">笔记本</el-menu-item>
    <el-menu-item index="/entryeditor/">词条在线编辑</el-menu-item>
    <el-menu-item index="/about">关于</el-menu-item>
    <el-menu-item index="/" @click="logout" class="right logout" v-if="$store.state.user.is_active">
      登出({{$store.state.user.username}})
    </el-menu-item>
    <el-menu-item index="/login" class="right" v-else>登录</el-menu-item>
  </el-menu>
</template>

<script>
export default {
  name: 'dcHeader',
  methods: {
    refreshHeader () {
      this.$axios.get('/common/session/').then(res => {
        this.$store.commit('update_user', res.data.user)
      })
    },
    logout () {
      this.$axios.delete('/common/session/0/').then(res => {
        this.$message.info('已登出，请刷新页面')
        this.$store.commit('update_user', {})
        this.$router.push('/')
      })
    }
  },
  created () {
    this.refreshHeader()
  }
}
</script>

<style scoped>
  .right {
    float: right;
    font-size: 16px;
  }
</style>
