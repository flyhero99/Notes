<template>
  <div>
    <el-table :data="similarTableData" v-loading="loading">
      <el-table-column property="id" label="id" width="150">
      </el-table-column>
      <el-table-column property="content" label="内容">
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
export default {
  components: {
    instance_detail: () => import('./InstanceDetail')
  },
  name: 'similar-table',
  props: ['params'],
  data () {
    return {
      instance_detail_params: {},
      similarTableData: [],
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
      this.$axios.get('/corpus/sentence/' + params['id'] + '/neighbors/').then(res => {
        this.loading = false
        this.similarTableData = res.data
      }).catch(err => {
        console.error(err)
        this.status = err
      })
    },
    showDetail (index, row) {
      this.instance_detail_params = {'id': row.id}
      this.dialogVisible = true
    }
  }
}
</script>

<style scoped>
  .highlight {
    color: chartreuse;
    padding: 0 3px;
  }
</style>
