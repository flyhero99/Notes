<template>
  <div>
    <el-table :data="countTableData" v-loading="loading">
      <el-table-column property="co_word" label="共现词" width="150">
      </el-table-column>
      <el-table-column property="cnt" label="词频" width="200">
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button
            size="mini"
            @click="showDetail(scope.$index, scope.row)">查看具体例子</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog
      :title="innerTitle"
      :visible.sync="innerVisible"
      append-to-body>
      <cooccur_table :params="cooccur_table_params">
      </cooccur_table>
    </el-dialog>
  </div>
</template>

<script>
import CooccurTable from './CooccurTable'

export default {
  components: {
    cooccur_table: CooccurTable
  },
  name: 'cooccur-count-table',
  props: ['params'],
  data () {
    return {
      countTableData: [],
      cooccur_table_params: {},
      loading: false,
      innerTitle: '',
      innerVisible: false
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
      this.$axios.post('/corpus/statistics/get_cooccur_count/', params
      ).then(res => {
        this.loading = false
        this.countTableData = res.data
      }).catch(err => {
        console.error(err)
        this.status = err
      })
    },
    showDetail (index, row) {
      this.cooccur_table_params = {'table1': 'word',
        'table2': 'word',
        'token1': this.params['src_word'],
        'token2': row.co_word,
        'date': this.params['date'],
        'pos_range': this.params['pos_range']}
      this.innerTitle = 'co_word=' + row.co_word + ', date=' + this.params['date']
      this.innerVisible = true
    }
  }
}
</script>

<style scoped>

</style>
