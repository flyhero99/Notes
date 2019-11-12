<template>
  <el-container>
    <el-aside width="200px">
      <div id="search_panel">
        <label>中心短语（用空格划分词语）：</label>
        <el-input
          placeholder="请输入中心短语"
          v-model="keyword"
          id="keyword">
        </el-input>
        <el-button type="button" @click="onSubmit">检索</el-button>
      </div>
    </el-aside>
    <el-main>
      <div id="status" :style="status_style">status: {{status}}</div>
      <h3 align="center">按年份查看npmi</h3>
      <el-slider v-model="slider.value" :step="1" show-stops :disabled="slider.disabled"
                 :min="slider.min" :max="slider.max" @change="refreshBarChart" show-input>
      </el-slider>
      <div id="bar_chart">
        <chart :options="bar_chart_option" auto-resize @click="showDetail($event)">
        </chart>
      </div>
      <h3 align="center">top 30 npmi词语随年份变化</h3>
      <chart id="scatter_chart" :options="scatter_chart_option" auto-resize @click="showDetail($event)">
      </chart>

      <el-dialog
        :title="dialogTitle"
        :visible.sync="dialogVisible">
        <cooccur_table :params="cooccur_table_params">
        </cooccur_table>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script>
import ECharts from 'vue-echarts/components/ECharts'
import CooccurTable from './CooccurTable'

export default {
  components: {
    chart: ECharts,
    cooccur_table: CooccurTable
  },
  data () {
    return {
      keyword: '',
      pmi_data: null,
      status: 'ready',
      status_style: {
        background: 'gray',
        color: '#fdff45'
      },
      slider: {
        value: 0,
        disabled: true,
        min: 1900,
        max: 1900
      },
      bar_chart_option: {
        title: {
          text: ''
        },
        legend: {
          data: ['nPMI']
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
          name: 'nPMI',
          type: 'bar',
          data: []
        }]
      },
      scatter_chart_option: {
        title: {
          text: 'top K npmi'
        },
        legend: {
          data: ['top K npmi'],
          left: 'right'
        },
        tooltip: {
          position: 'top'
        },
        grid: {
          left: 2,
          bottom: 10,
          right: 10,
          containLabel: true
        },
        xAxis: [{
          type: 'category',
          data: [],
          splitLine: {
            show: true,
            lineStyle: {
              color: '#999',
              type: 'dashed'
            }
          },
          axisLine: {
            show: false
          }
        }, {
          type: 'category',
          data: [],
          position: 'top',
          axisLine: {
            show: false
          }
        }],
        yAxis: {
          type: 'category',
          data: [],
          boundaryGap: false,
          splitLine: {
            show: true,
            lineStyle: {
              color: '#999',
              type: 'dashed'
            }
          },
          axisLine: {
            show: false
          },
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        series: [{
          name: 'nPMI',
          type: 'scatter',
          symbol: 'roundRect',
          symbolSize: function (val) {
            return [80, Math.max(0, val[2] - 0.4) * 60]
          },
          data: [],
          animationDelay: function (idx) {
            return idx * 2
          }
        }]
      },

      cooccur_table_params: {},
      dialogTitle: '',
      dialogVisible: false
    }
  },
  name: 'PhrasePMI',
  methods: {
    onSubmit () {
      this.status = 'busy'
      this.status_style.color = '#ff5a49'
      this.$axios.post('/corpus/statistics/get_phrase_pmi/', {
        tokens: this.keyword.split(' ')
      }).then(res => {
        this.status = 'success'
        this.status_style.color = '#00ff7a'
        this.pmi_data = res.data
        let years = Object.keys(this.pmi_data['bar']).map(x => { return parseInt(x) })
        this.slider.min = Math.min.apply(null, years)
        this.slider.max = Math.max.apply(null, years)
        this.slider.disabled = false
        this.slider.value = this.slider.min
        this.refreshBarChart()
        this.refreshScatterChart()
      }).catch(err => {
        this.status = err
      })
    },
    refreshBarChart () {
      this.bar_chart_option.title.text = this.slider.value.toString()
      this.bar_chart_option.xAxis.data = this.pmi_data['bar'][this.slider.value.toString()]['token']
      this.bar_chart_option.series[0].data = this.pmi_data['bar'][this.slider.value.toString()]['npmi']
    },
    refreshScatterChart () {
      this.scatter_chart_option.xAxis[0].data = this.pmi_data['scatter']['dates']
      this.scatter_chart_option.xAxis[1].data = this.pmi_data['scatter']['dates']
      this.scatter_chart_option.yAxis.data = this.pmi_data['scatter']['tokens']
      this.scatter_chart_option.series[0].data = this.pmi_data['scatter']['data']
    },
    showDetail (event) {
      let coWord = ''
      let date = ''
      if (event.seriesType === 'scatter') {
        date = this.pmi_data['scatter']['dates'][event.value[0]] + '-01-01'
        coWord = this.pmi_data['scatter']['tokens'][event.value[1]]
      } else {
        date = this.slider.value + '-01-01'
        coWord = event.name
      }
      this.cooccur_table_params = {'table1': 'word',
        'table2': 'word',
        'token1': this.keyword,
        'token2': coWord,
        'date': date,
        'pos_range': [-5, 5]}
      this.dialogTitle = 'co_word=' + coWord + ', date=' + date
      this.dialogVisible = true
    }
  },
  mounted: function () {
    this.scatter_chart_option.tooltip.formatter = params => {
      return this.pmi_data['scatter']['tokens'][parseInt(params.value[1])] + '，' +
        this.pmi_data['scatter']['dates'][parseInt(params.value[0])] + '，' +
        params.value[2]
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
#scatter_chart {
  height: 1400px;
  width: 800px;
}
#search_panel {
  margin: 20px;
  align-content: center;
  line-height: 40px;
}
.el-slider {
  width: 300px;
  margin: auto;
}
</style>
