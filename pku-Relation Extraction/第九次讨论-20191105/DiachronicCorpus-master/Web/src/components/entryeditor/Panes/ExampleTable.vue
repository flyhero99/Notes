<template>
  <div>
    <el-row v-show="activated && editable">
      <el-col :offset="2">
        <el-form :inline="true">
          <el-form-item label="显示设置" style="margin-bottom: 0">
            <el-checkbox label="高亮关键字" v-model="styleData.highlight" size="small" border></el-checkbox>
            <el-checkbox label="显示年份" v-model="styleData.showYear" size="small" border></el-checkbox>
            <el-checkbox label="显示关键词" v-model="styleData.showWord" size="small" border></el-checkbox>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
    <el-form :inline="true" style="margin-left: 12px">
      <el-form-item v-show="styleData.showYear" label="年份" style="margin-bottom: 0">{{outputData.data.year}}</el-form-item>
      <el-form-item v-show="styleData.showWord" label="关键词" style="margin-bottom: 0">{{outputData.data.word}}</el-form-item>
    </el-form>
    <ul style="margin: 0">
      <li v-for="(value, key) in outputData.data.contents" :key="key"
          v-html="highlightKeyword(value.content)">
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ExampleTable',
  props: ['outputData', 'styleData', 'activated', 'editable'],
  methods: {
    highlightKeyword: function (content) {
      if (this.styleData.highlight) {
        return content.replace(this.outputData.data.word, '<span class="highlight">' + this.outputData.data.word + '</span>')
      }
      return content
    }
  }
}
</script>

<style scoped>
li>>>.highlight {
  color: blue;
}
</style>
