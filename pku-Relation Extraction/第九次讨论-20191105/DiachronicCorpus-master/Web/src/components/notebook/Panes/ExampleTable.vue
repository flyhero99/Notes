<template>
  <el-table :data="data">
    <el-table-column property="sentence_id" label="id" width="150">
    </el-table-column>
    <el-table-column property="left" label="内容" :formatter="instanceFormatter" align="right">
    </el-table-column>
    <el-table-column property="right" label="" align="left">
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  name: 'ExampleTable',
  props: ['data'],
  data () {
    return {
    }
  },
  methods: {
    instanceFormatter (row, column, cellValue, index) {
      let content = cellValue
      return this.$createElement('div', [
        content.substring(0, row.so),
        this.$createElement('span', {'class': 'highlight'}, content.substring(row.so, row.eo)),
        content.substring(row.eo)
      ])
    }
  }
}
</script>

<style scoped>
  .highlight {
    color: red;
    padding: 0 0 0 3px;
  }
</style>
