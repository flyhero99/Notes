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
      <h3 align="center">按源词性查看npmi</h3>
      <label>源词性：</label>
      <el-radio-group id="src_tag" v-model="src_tag" @change="refreshRiverChart">
        <el-radio v-for="(value, key, index) in pmi_data['river_data']" :key="index" :label="key">{{key}}</el-radio>
      </el-radio-group>
      <div id="river_chart">
        <chart :options="river_chart_option" auto-resize>
        </chart>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import ECharts from 'vue-echarts/components/ECharts'

export default {
  components: {
    chart: ECharts
  },
  data () {
    return {
      keyword: '',
      pos: '',
      pmi_data: {},
      src_tag: '',
      status: 'ready',
      status_style: {
        background: 'gray',
        color: '#fdff45'
      },
      river_chart_option: {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'line',
            lineStyle: {
              color: 'rgba(0,0,0,0.2)',
              width: 1,
              type: 'solid'
            }
          }
        },
        legend: {
          data: []
        },
        singleAxis: {
          top: 50,
          bottom: 50,
          axisTick: {},
          axisLabel: {},
          type: 'time',
          axisPointer: {
            animation: true,
            label: {
              show: true
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed',
              opacity: 0.2
            }
          }
        },

        series: [
          {
            type: 'themeRiver',
            label: {
              fontSize: 10,
              padding: [0, 0, 0, -10]
            },
            itemStyle: {
              emphasis: {
                shadowBlur: 20,
                shadowColor: 'rgba(0, 0, 0, 0.8)'
              }
            },
            data: []
          }
        ]
      }
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
        this.river_chart_option.legend.data = []
        this.river_chart_option.series[0].data = []
        this.src_tag = ''
      }).catch(err => {
        this.status = err
      })
    },
    refreshRiverChart () {
      this.river_chart_option.legend.data = this.pmi_data['river_data'][this.src_tag]['co_tags']
      this.river_chart_option.series[0].data = this.pmi_data['river_data'][this.src_tag]['data']
    }
  },
  mounted: function () {

  }
}
</script>

<style scoped>
.echarts {
  height: 100%;
  width: 100%;
}
#river_chart {
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
