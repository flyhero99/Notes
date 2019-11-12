<template>
  <div>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>交互方式</span>
      </div>
      <p>在Input中输入指令，执行后可以在Output中看到多种格式的输出，通过标签页切换输出格式。</p>
      <p>可以通过 单元格-执行当前单元格 执行命令，也可以在编辑模式下通过快捷键 alt+enter 执行命令。</p>
      <p>初次打开一个新建的笔记本时，请先通过 内核-连接/新建 连接内核。</p>
      <p>被选中的单元格会以蓝色边框显示。</p>
      <p>具体支持的指令请参考 帮助-命令 选单。</p>
    </el-card>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>编辑模式</span>
      </div>
      <p>点击Input中的输入框即进入编辑模式，此时可以使用一系列预定义的快捷键。点击其他地方退出编辑模式。</p>
      <p>工作区的右上角将指示此时是否处于编辑模式，以及内核信息。</p>
    </el-card>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>快捷键</span>
      </div>
      <el-form>
        <el-form-item label="执行当前单元格"><span>alt+enter</span></el-form-item>
        <el-form-item label="保存笔记本"><span>ctrl/cmd+s</span></el-form-item>
        <el-form-item label="创建cell"><span>ctrl/cmd+shift+enter</span></el-form-item>
        <el-form-item label="删除cell"><span>ctrl/cmd+shift+backspace</span></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'NotebookBasicHelp'
}
</script>

<style scoped>
.box-card {
  margin-bottom: 10px;
}
.el-form-item {
  margin-bottom: 5px;
}
</style>
