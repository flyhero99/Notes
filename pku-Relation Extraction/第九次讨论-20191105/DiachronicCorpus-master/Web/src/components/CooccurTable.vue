<template>
  <div>
    <el-table :data="instanceTableData" v-loading="loading">
      <el-table-column property="sentence_id" label="id" width="150">
      </el-table-column>
      <el-table-column property="content" label="内容" :formatter="instanceFormatter">
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button
            size="mini"
            @click="showDetail(scope.$index, scope.row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog
      title="句子详情"
      :visible.sync="dialogVisible"
      append-to-body>
      <instance_detail :params="instance_detail_params">
      </instance_detail>
    </el-dialog>
  </div>
</template>

<script>
import InstanceDetail from './InstanceDetail'

export default {
  name: 'cooccur-table',
  components: {
    instance_detail: InstanceDetail
  },
  props: ['params'],
  data () {
    return {
      instanceTableData: [],
      instance_detail_params: {},
      loading: false,
      dialogVisible: false
    }
  },
  watch: {
    params: {
      immediate: true,
      handler (newVal, oldVal) {
        if (Object.keys(newVal).length === 0) { return }
        this.refreshTable(newVal)
      }
    }
  },
  methods: {
    refreshTable (params) {
      this.loading = true
      this.$axios.post('/corpus/statistics/get_cooccur/', {
        table1: params['table1'],
        table2: params['table2'],
        token1: params['token1'],
        token2: params['token2'],
        date: params['date'],
        pos_range: params['pos_range']
      }).then(res => {
        this.loading = false
        this.instanceTableData = res.data
      }).catch(err => {
        console.error(err)
        this.status = err
      })
    },
    instanceFormatter (row, column, cellValue, index) {
      let content = cellValue
      let so1 = Math.min(row.so1, row.so2)
      let so2 = Math.max(row.so1, row.so2)
      let eo1 = Math.min(row.eo1, row.eo2)
      let eo2 = Math.max(row.eo1, row.eo2)
      return this.$createElement('div', [
        content.substring(0, so1),
        this.$createElement('span', {'class': 'highlight'}, content.substring(so1, eo1)),
        content.substring(eo1, so2),
        this.$createElement('span', {'class': 'highlight'}, content.substring(so2, eo2)),
        content.substring(eo2)
      ])
    },
    showDetail (index, row) {
      this.instance_detail_params = {'id': row.sentence_id}
      this.dialogVisible = true
    }
  }
}
</script>

<style scoped>
  .highlight {
    color: #0000ff;
    padding: 0 3px;
  }
</style>
