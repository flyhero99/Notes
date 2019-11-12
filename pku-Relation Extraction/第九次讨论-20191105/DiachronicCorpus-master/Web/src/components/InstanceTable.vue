<template>
  <div>
    <el-pagination
      :page-size.sync="page_size"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @current-change="handleCurrentChange"
      @size-change="handleSizeChange">
    </el-pagination>
    <el-table :data="instanceTableData" v-loading="loading">
      <el-table-column property="sentence_id" label="id" width="100">
      </el-table-column>
      <el-table-column property="left" label="内容" width="450" :formatter="instanceFormatter" align="right">
      </el-table-column>
      <el-table-column property="right" label="" width="450" align="left">
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template slot-scope="scope">
          <el-button
            size="mini"
            @click="showDetail(scope.$index, scope.row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog
      title="句子详情"
      :visible.sync="dialogVisible">
      <instance_detail :params="instance_detail_params">
      </instance_detail>
    </el-dialog>
  </div>
</template>

<script>
import InstanceDetail from './InstanceDetail'

export default {
  components: {
    instance_detail: InstanceDetail
  },
  name: 'instance-table',
  props: ['params', 'total'],
  data () {
    return {
      instance_detail_params: {},
      instanceTableData: [],
      loading: false,
      dialogVisible: false,
      page_size: 10,
      page_num: 1
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
      params['page_num'] = this.page_num - 1
      params['page_size'] = this.page_size
      console.log(this.page_size)
      this.loading = true
      this.$axios.post('/corpus/statistics/get_instance/', params
      ).then(res => {
        this.loading = false
        this.instanceTableData = res.data
      }).catch(err => {
        console.error(err)
        this.status = err
      })
    },
    instanceFormatter (row, column, cellValue, index) {
      let content = cellValue
      return this.$createElement('div', [
        content.substring(0, row.so),
        this.$createElement('span', {'class': 'highlight'}, content.substring(row.so, row.eo)),
        content.substring(row.eo)
      ])
    },
    showDetail (index, row) {
      this.instance_detail_params = {'id': row.sentence_id}
      this.dialogVisible = true
    },
    handleCurrentChange (val) {
      this.page_num = val
      this.refreshTable(this.params)
    },
    handleSizeChange (val) {
      this.page_size = val
      this.refreshTable(this.params)
    }
  }
}
</script>

<style scoped>
  .highlight {
    color: chartreuse;
    padding: 0 0 0 3px;
  }
</style>
