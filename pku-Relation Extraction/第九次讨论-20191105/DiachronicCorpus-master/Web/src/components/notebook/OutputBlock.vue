<template>
  <div>
    <el-col :span="2" align="center">
      <span style="color: red;"> Out[{{blockData.num}}] </span>
      <el-select v-model="blockData.collapse" size="mini" style="width: 75px">
        <el-option v-for="item in collapseOptions"
                   :key="item.value"
                   :value="item.value"
                   :label="item.label">
        </el-option>
      </el-select>
    </el-col>
    <el-col :span="20">
      <el-tabs type="border-card" v-model="blockData.active_name">
        <el-tab-pane label="raw输出" name="raw" :class="paneClass">
          <span style="display:block; min-height: 100px;">{{blockData.out}}</span>
        </el-tab-pane>
        <el-tab-pane label="格式化json" name="prettify-json" :class="paneClass">
          <vue-json-pretty :data="blockData.out"></vue-json-pretty>
        </el-tab-pane>
        <el-tab-pane label="表格" name="table" v-if="isAvaliable(blockData.out.type, 'table')" :class="paneClass">
          <el-table :data="blockData.out.data">
            <el-table-column
              v-for="(value, key) in columns"
              :prop="value"
              :label="value"
              :key="key"
              ></el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="图表" name="chart" v-if="isAvaliable(blockData.out.type, 'chart')" :class="paneClass">
          <e-charts :options="options" auto-resize>
          </e-charts>
        </el-tab-pane>
        <el-tab-pane label="例句表格" name="example-table" v-if="isAvaliable(blockData.out.type, 'example-table')"
                     :class="paneClass">
          <example-table :data="blockData.out.data">
          </example-table>
        </el-tab-pane>
        <el-tab-pane label="Wiki" name="wiki" v-if="isAvaliable(blockData.out.type, 'wiki')" :class="paneClass">
          <wiki-block :data="blockData.out.data">
          </wiki-block>
        </el-tab-pane>
      </el-tabs>
    </el-col>
  </div>
</template>

<script>
import ECharts from 'vue-echarts/components/ECharts'
import ExampleTable from './Panes/ExampleTable'
import WikiBlock from './Panes/WikiBlock'
import VueJsonPretty from 'vue-json-pretty'

export default {
  name: 'NotebookOutputBlock',
  components: {ECharts, ExampleTable, WikiBlock, VueJsonPretty},
  props: ['blockData', 'xAxisName', 'collapse'],
  watch: {
    blockData: {
      handler: function (newVal, oldVal) {
        if (!this.availableTab[newVal.out.type].includes(newVal.active_name)) {
          newVal.active_name = 'raw'
        }
      },
      deep: true
    }
  },
  data () {
    return {
      availableTab: {
        'ListWithChart': ['raw', 'table', 'chart'],
        'List': ['raw', 'table'],
        'Boolean': ['raw'],
        'String': ['raw'],
        'ExampleList': ['raw', 'example-table'],
        'Wiki': ['raw', 'wiki']
      },
      collapseOptions: [
        {value: 'close', label: '隐藏'},
        {value: 'collapse', label: '折叠'},
        {value: 'all', label: '展开'}
      ]
    }
  },
  computed: {
    columns () {
      if (!Array.isArray(this.blockData.out.data) || this.$utils.isEmptyObject(this.blockData.out.data)) {
        return []
      }
      return Object.keys(this.blockData.out.data[0])
    },
    options () {
      let opt = {
        title: {
          text: ''
        },
        legend: {
          data: this.columns.filter(x => x !== this.xAxisName)
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        xAxis: {
          data: this.blockData.out.data.map(x => x[this.xAxisName]),
          axisLabel: {
            interval: 0,
            rotate: -60
          }
        },
        yAxis: {},
        series: []
      }
      for (let key of this.columns) {
        if (key === this.xAxisName) {
          continue
        }
        opt.series.push({
          name: key,
          type: 'bar',
          data: this.blockData.out.data.map(x => x[key])
        })
      }
      return opt
    },
    paneClass () {
      return {
        'closed-pane': this.collapse === 'close',
        'collapsed-pane': this.collapse === 'collapse',
        'opened-pane': this.collapse === 'all'
      }
    }
  },
  methods: {
    isAvaliable: function (type, tab) {
      if (!(type in this.availableTab)) {
        return false
      }
      return this.availableTab[type].includes(tab)
    }
  }
}
</script>

<style scoped>
.closed-pane {
  overflow-y: auto;
  max-height: 0;
}
.collapsed-pane {
  overflow-y: auto;
  max-height: 300px;
}
.opened-pane {
  overflow-y: auto;
  max-height: none;
}
</style>
