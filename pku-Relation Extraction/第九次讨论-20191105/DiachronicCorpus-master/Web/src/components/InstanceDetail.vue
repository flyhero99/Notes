<template>
<div>
  <el-form class="instance-detail" label-position="left" :v-loading="loading">
    <el-form-item label="句子id">
      <span>{{ instanceDetailData.id }}</span>
    </el-form-item>
    <el-form-item label="content">
      <span>{{ instanceDetailData.content }}</span>
    </el-form-item>
    <el-form-item label="词性标注">
      <span>{{ instanceDetailData.part_of_speech }}</span>
    </el-form-item>
    <el-form-item label="近义句">
      <el-button
        size="mini"
        @click="showSimilar(instanceDetailData.id)">近义句</el-button>
    </el-form-item>
  </el-form>
  <el-dialog
    title="近义句"
    :visible.sync="dialogVisible"
    append-to-body>
    <similar_table :params="similar_table_params">
    </similar_table>
  </el-dialog>
</div>
</template>

<script>
import SimilarTable from './SimilarTable'

export default {
  components: {
    similar_table: SimilarTable
  },
  name: 'instance-detail',
  props: ['params'],
  data () {
    return {
      instanceDetailData: [],
      loading: false,
      dialogVisible: false,
      similar_table_params: {}
    }
  },
  watch: {
    params: {
      immediate: true,
      handler (newVal, oldVal) {
        if (Object.keys(newVal).length === 0) { return }
        this.refreshDetail(newVal)
      }
    }
  },
  methods: {
    refreshDetail (params) {
      this.loading = true
      this.$axios.get('/corpus/sentence/' + params['id'] + '/').then(res => {
        this.loading = false
        this.instanceDetailData = res.data
      }).catch(err => {
        console.error(err)
        this.status = err
      })
    },
    showSimilar (id) {
      this.similar_table_params = {'id': id}
      this.dialogVisible = true
    }
  }
}
</script>

<style scoped>
  .instance-detail {
  }
  .instance-detail label {
    width: 90px;
    color: #99a9bf;
  }
  .instance-detail .el-form-item {
    margin-right: 0;
    margin-bottom: 0;
  }
</style>
