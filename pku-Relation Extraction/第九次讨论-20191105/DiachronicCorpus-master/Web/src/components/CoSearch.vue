<template>
  <el-container>
    <el-aside width="200px">
      <div id="search_panel">
        <label>共现检索：</label>
        <el-input
          placeholder="请输入中心词"
          v-model="keyword"
          id="keyword">
        </el-input>
        <el-radio-group id="table" v-model="co_table">
          <el-radio label="word">词语</el-radio><br/>
          <el-radio label="tag">词性</el-radio>
        </el-radio-group>
        <el-input
          placeholder="请输入共现词"
          v-model="co_word"
          id="coword">
        </el-input>
        <el-slider v-model="pos_range" :step="1" show-stops range :min="-5" :max="5">
        </el-slider>
        <label>共现位置：{{pos_range}}</label>
        <el-button type="button" @click="onSubmit">检索</el-button>
      </div>
    </el-aside>
    <el-main>
      <div id="status" :style="status_style">status: {{status}}</div>
      <h3 align="center">频率统计</h3>
      <cooccur_count_table :params="cooccur_count_table_params" :keyword="keyword">
      </cooccur_count_table>
    </el-main>
  </el-container>
</template>

<script>
import ECharts from 'vue-echarts/components/ECharts'
import CooccurCountTable from './CooccurCountTable'

export default {
  components: {
    chart: ECharts,
    cooccur_count_table: CooccurCountTable
  },
  name: 'co-search',
  data () {
    return {
      keyword: '',
      co_word: '',
      co_table: 'word',
      status: 'ready',
      status_style: {
        background: 'gray',
        color: '#fdff45'
      },
      cooccur_count_table_params: {},
      pos_range: [0, 1]
    }
  },
  methods: {
    onSubmit () {
      this.cooccur_count_table_params = {
        src_word: this.keyword,
        src_tag: '*',
        co_table: this.co_table,
        co_tag: this.co_word,
        date: '*',
        pos_range: [this.pos_range[0], this.pos_range[1] + 1]
      }
    }
  }
}
</script>

<style scoped>
  .echarts {
    height: 100%;
    width: 100%;
  }
  #bar_chart {
    height: 300px;
    width: 800px;
  }
  #search_panel {
    margin: 20px;
    align-content: center;
    line-height: 40px;
  }
</style>
