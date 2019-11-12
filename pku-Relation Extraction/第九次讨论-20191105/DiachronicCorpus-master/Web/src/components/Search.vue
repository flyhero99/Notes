<template>
  <el-container>
    <el-aside width="200px">
      <div id="search_panel">
        <label>中心词：</label>
        <el-input
          placeholder="请输入中心词"
          v-model="keyword"
          id="keyword">
        </el-input>
        <el-button type="button" @click="onSubmit">检索</el-button>
      </div>
    </el-aside>
    <el-main>
      <div id="status" :style="status_style">status: {{status}}</div>
      <h3 align="center">词频随年份变化</h3>
      <div id="bar_chart">
        <chart :options="bar_chart_option" auto-resize @click="showDetail($event)">
        </chart>
      </div>
      <h3 align="center">{{table_title}}</h3>
      <instance_table :params="instance_table_params" :total="total">
      </instance_table>
    </el-main>
  </el-container>
</template>

<script>
import ECharts from 'vue-echarts/components/ECharts'
import InstanceTable from './InstanceTable'

export default {
  components: {
    chart: ECharts,
    instance_table: InstanceTable
  },
  name: 'search',
  data () {
    return {
      keyword: '',
      pmi_data: null,
      status: 'ready',
      status_style: {
        background: 'gray',
        color: '#fdff45'
      },
      bar_chart_option: {
        title: {
          text: ''
        },
        legend: {
          data: ['count']
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        xAxis: {
          data: [],
          axisLabel: {
            interval: 0,
            rotate: -60
          }
        },
        yAxis: {},
        series: [{
          name: 'count',
          type: 'bar',
          data: []
        }]
      },
      instance_table_params: {},
      table_title: 'date=',
      total: 0
    }
  },
  methods: {
    onSubmit () {
      this.status = 'busy'
      this.status_style.color = '#ff5a49'
      this.$axios.post('/corpus/statistics/get_count/', {
        token: this.keyword
      }).then(res => {
        this.status = 'success'
        this.status_style.color = '#00ff7a'
        this.data = res.data
        this.refreshBarChart()
      }).catch(err => {
        this.status = err.response.data.detail
      })
    },
    refreshBarChart () {
      this.bar_chart_option.xAxis.data = this.data['date']
      this.bar_chart_option.series[0].data = this.data['cnt']
    },
    showDetail (event) {
      this.instance_table_params = {
        'token': this.keyword,
        'date': event.name + '-01-01'
      }
      this.total = event.value
      this.table_title = 'date=' + event.name
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
