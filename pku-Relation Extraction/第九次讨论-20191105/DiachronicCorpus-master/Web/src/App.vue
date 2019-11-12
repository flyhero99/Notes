<template>
  <el-container>
    <el-header>
      <dc-header></dc-header>
    </el-header>
    <router-view :key="$route.fullPath"></router-view>
    <el-footer>
      <dc-footer></dc-footer>
    </el-footer>
  </el-container>
</template>

<script>
import dcHeader from '@/components/Header.vue'
import dcFooter from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {dcHeader, dcFooter},
  mounted () {
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.el-footer {
  background-color: #B3C0D1;
  color: #333;
  text-align: center;
  line-height: 4px;
}

.el-aside {
  background-color: #D3DCE6;
  color: #333;
}

.el-header {
  padding: 0;
}

.el-main {
  background-color: #E9EEF3;
  color: #333;
}

body{
  margin:0;
  padding:0;
}
</style>
