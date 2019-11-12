<template>
  <el-container>
    <el-main>
      <div id="status" :style="status_style">status: {{status}}</div>
      <el-row id="search_panel">
        <el-col :span="6">
          <el-form label-width="80px">
            <el-form-item label="中心词：">
              <el-input placeholder="请输入中心词" v-model="keyword" id="keyword" style="width: 150px">
              </el-input>
              <el-button type="button" @click="onSubmit">检索</el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12">
          <el-slider v-model="slider.value" :step="1" show-stops :disabled="slider.disabled"
                     :min="slider.min" :max="slider.max" @change="refreshBarChart" show-input>
          </el-slider>
        </el-col>
      </el-row>
      <el-col :span="12">
        <h3 align="center">按年份查看npmi</h3>
        <div id="bar_chart">
          <chart :options="bar_chart_option" auto-resize @click="showDetail($event)"
                 @mouseover="highlight = $event.name" @mouseout="highlight = ''">
          </chart>
        </div>
      </el-col>
      <el-col :span="12">
        <el-tabs v-model="activeName">
          <el-tab-pane label="详细数据" name="statics">
            <h3 align="center">top 30 npmi词语随年份变化</h3>
            <chart id="scatter_chart" :options="scatter_chart_option" auto-resize @click="showDetail($event)">
            </chart>
          </el-tab-pane>
          <el-tab-pane label="词云" name="wordCloud">
            <word_cloud :cloud_data="word_cloud_data" :index="slider.value-slider.min">
            </word_cloud>
          </el-tab-pane>
<!--          <el-tab-pane label="环绕式" name="wordCircle">-->
<!--            <word_circle :word="keyword" :data="word_cloud_data.data" :years="word_cloud_data.dates">-->
<!--            </word_circle>-->
<!--          </el-tab-pane>-->
<!--          <el-tab-pane label="力学布局" name="wordForce">-->
<!--          <word_force :word="keyword" :data="word_cloud_data.data" :years="word_cloud_data.dates"-->
<!--                       :links="word_cloud_data.links">-->
<!--          </word_force>-->
<!--          </el-tab-pane>-->
          <el-tab-pane label="静态力布局" name="wordStatic">
            <word_static :word="keyword" :data="word_cloud_data.data" :years="word_cloud_data.dates"
                        :links="word_cloud_data.links" :index="slider.value-slider.min" :highlight.sync="highlight"
                         :width="500" :height="500">
            </word_static>
          </el-tab-pane>
        </el-tabs>
      </el-col>

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
import WordCloud from './WordCloud'
import WordCircle from './WordCircle'
import WordForce from './WordForce'
import WordStatic from './WordStatic'

export default {
  components: {
    chart: ECharts,
    cooccur_table: CooccurTable,
    word_cloud: WordCloud,
    word_circle: WordCircle,
    word_force: WordForce,
    word_static: WordStatic
  },
  data () {
    return {
      keyword: '',
      highlight: '',
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
      dialogVisible: false,

      activeName: 'wordStatic',
      word_cloud_data: {
        data: [[]],
        dates: []
      }
    }
  },
  name: 'PMI',
  methods: {
    onSubmit () {
      this.status = 'busy'
      this.status_style.color = '#ff5a49'
      this.$axios.post('/corpus/statistics/get_pmi/', {
        token: this.keyword
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
        this.word_cloud_data = res.data['cloud_data']
      }).catch(err => {
        this.status = err.response.data.detail
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
  width: 100%;
}
#scatter_chart {
  height: 1400px;
  width: 100%;
}
#search_panel {
  padding: 20px 0;
  align-content: center;
  line-height: 40px;
  background: aliceblue;
}
.el-slider {
  width: 300px;
  margin: auto;
}
  .el-form-item {
    margin-bottom: 0;
  }
</style>
