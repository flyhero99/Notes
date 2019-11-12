<template>
  <div>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>基础语法</span>
      </div>
      <p>赋值语句：[variable_name]=[expression]，其中[expression]可以是一个变量名，也可以是下列函数列表中的函数。</p>
      <p>回显语句：[expression]，其中[expression]的定义同上，这个语句将直接显示表达式内容，并将其赋值给变量ans。</p>
      <p>函数调用：function(param1=value)，其中必须显式写明参数名，不可以使用位置参数。例如，freq(pattern=使用)是一个合法的函数，但freq(使用)是不合法的。</p>
      <p>特别的，字符串可以以双引号或不包裹引号来表示。</p>
      <p>实际上，整个语言的运行机制都是以函数为单位的，因此赋值语句实际上是一个名为assign的函数，回显语句是一个名为get的函数。</p>
    </el-card>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>函数列表</span>
      </div>
      <el-form>
        <el-form-item label="show()"><span>显示工作区所有的变量名。输出支持的显示格式：raw、表格。</span></el-form-item>
        <el-form-item label="freq(pattern)"><span>获取pattern的频率，默认以年为单位分割。输出支持的显示格式：raw、表格、图表。</span></el-form-item>
        <el-form-item label="compare(name1, name2, by)"><span>比较两个结果集，name1和name2是两个变量名，by是对齐的列名，一般是date。输出将会根据两个结果集相同的字段名进行合并。输出支持的显示格式：raw、表格、图表。</span></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'NotebookCommandHelp'
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
