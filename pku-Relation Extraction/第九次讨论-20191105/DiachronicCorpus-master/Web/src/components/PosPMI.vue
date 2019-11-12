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
        <el-radio-group id="pos" v-model="pos">
          <el-radio label="left">左邻词</el-radio><br/>
          <el-radio label="right">右邻词</el-radio>
        </el-radio-group>
        <el-button type="button" @click="onSubmit">检索</el-button>
      </div>
    </el-aside>
    <el-main>
      <div id="status" :style="status_style">status: {{status}}</div>
      <h3 align="center">按源词性查看归一化pmi</h3>
      <label>源词性：</label>
      <el-radio-group id="src_tag" v-model="src_tag" @change="refreshBarChart">
        <el-radio v-for="(value, key, index) in pmi_data['river_data']" :key="index" :label="key">{{key}}</el-radio>
      </el-radio-group>
      <div id="bar_chart">
        <chart v-for="(option, index) in bar_chart_options" :options="option" :key="index" @click="showCount($event)"
               auto-resize>
        </chart>
      </div>
    </el-main>

    <el-dialog :title="dialogTitle" :visible.sync="dialogTableVisible">
      <cooccur_count_table :params="cooccur_count_table_params">
      </cooccur_count_table>
    </el-dialog>
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
  data () {
    return {
      keyword: '',
      pos: '',
      pmi_data: {},
      src_tag: '',
      co_tag: '',
      date: '',
      dialogTitle: '',
      status: 'ready',
      status_style: {
        background: 'gray',
        color: '#fdff45'
      },
      dialogTableVisible: false,
      bar_chart_options: [],
      cooccur_count_table_params: {}
    }
  },
  name: 'PosPMI',
  methods: {
    onSubmit () {
      this.status = 'busy'
      this.status_style.color = '#ff5a49'
      this.$axios.post('/corpus/statistics/get_tag_pmi/', {
        token: this.keyword,
        pos: this.pos
      }).then(res => {
        this.status = 'success'
        this.status_style.color = '#00ff7a'
        this.pmi_data = res.data
        this.bar_chart_options = []
        this.src_tag = ''
      }).catch(err => {
        this.status = err.response.data.detail
      })
    },
    refreshBarChart () {
      this.bar_chart_options = []
      this.pmi_data['bar_data']['data'][this.src_tag].forEach((val, index) => {
        let option = {
          grid: {
            top: 20,
            bottom: 20
          },
          title: {
            text: this.pmi_data['bar_data']['tags'][index],
            top: '50%'
          },
          xAxis: {
            type: 'category',
            data: this.pmi_data['bar_data']['years']
          },
          yAxis: {
            type: 'value'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          series: [{
            name: this.pmi_data['bar_data']['tags'][index],
            data: val,
            type: 'bar',
            itemStyle: {
              normal: {
                color: new ECharts.graphic.LinearGradient(
                  0, 0, 0, 1,
                  [
                    {offset: 0, color: '#83bff6'},
                    {offset: 0.5, color: '#188df0'},
                    {offset: 1, color: '#188df0'}
                  ]
                )
              },
              emphasis: {
                color: new ECharts.graphic.LinearGradient(
                  0, 0, 0, 1,
                  [
                    {offset: 0, color: '#2378f7'},
                    {offset: 0.7, color: '#2378f7'},
                    {offset: 1, color: '#83bff6'}
                  ]
                )
              }
            }
          }]
        }
        this.bar_chart_options.push(option)
      })
    },
    showCount (event) {
      this.co_tag = event.seriesName
      this.date = event.name
      this.cooccur_count_table_params = {
        src_word: this.keyword,
        src_tag: this.src_tag,
        co_table: 'tag',
        co_tag: this.co_tag,
        date: this.date + '-01-01',
        pos_range: this.pos === 'left' ? [-1, 0] : [1, 2]
      }
      this.dialogTitle = 'co_tag=' + this.co_tag + ', date=' + this.date
      this.dialogTableVisible = true
    }
  }
}
</script>

<style scoped>
.echarts {
  height: 25%;
  width: 100%;
}
#bar_chart {
  height: 600px;
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
