<template>
  <div>
    <el-row v-show="activated && editable">
      <el-col :offset="2" >
        <el-form :inline="true">
          <el-form-item label="x"><el-input-number v-model="styleData.x" :min="0" controls-position="right" size="small"></el-input-number></el-form-item>
          <el-form-item label="y"><el-input-number v-model="styleData.y" :min="0" :max="maxY" controls-position="right" size="small"></el-input-number></el-form-item>
          <el-form-item label="w"><el-input-number v-model="styleData.w" :min="0" controls-position="right" size="small"></el-input-number></el-form-item>
          <el-form-item label="h"><el-input-number v-model="styleData.h" :min="0" controls-position="right" size="small"></el-input-number></el-form-item>
        </el-form>
        <el-form :inline="true">
          <el-form-item label="图表类型">
            <el-select v-model="styleData.type" >
              <el-option
                v-for="item in seriesTypes"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="颜色"><el-color-picker v-model="styleData.color" :predefine="predefineColors"></el-color-picker></el-form-item>
        </el-form>
      </el-col>
    </el-row>
    <div style="border: 0 solid red;" :style="{height: (styleData.y+styleData.h)+'px'}">
      <vue-draggable-resizable :parent="true" :resizable="editable" :draggable="editable" style="border: 0 solid green; position: relative"
                               :x="styleData.x" :y="styleData.y" :w="styleData.w" :h="styleData.h" @resizing="onResize"
                               @dragging="onDrag">
        <e-charts :options="options" auto-resize :style="{top: styleData.y+'px', width: styleData.w+'px', height: styleData.h+'px'}">
        </e-charts>
      </vue-draggable-resizable>
    </div>
  </div>
</template>

<script>
import ECharts from 'vue-echarts/components/ECharts'
import VueDraggableResizable from 'vue-draggable-resizable'

export default {
  name: 'ListWithChart',
  components: {ECharts, VueDraggableResizable},
  props: ['outputData', 'styleData', 'activated', 'editable'],
  data () {
    return {
      maxY: 50,
      xAxisName: 'date',
      predefineColors: [
        '#c05050',
        '#2ec7c9',
        '#b6a2de',
        '#5ab1ef',
        '#ffb980',
        '#d87a80',
        '#8d98b3',
        '#e5cf0d',
        '#97b552',
        '#95706d',
        '#dc69aa',
        '#07a2a4',
        '#9a7fd1',
        '#588dd5',
        '#f5994e',
        '#59678c',
        '#c9ab00',
        '#7eb00a',
        '#6f5553',
        '#c14089'],
      seriesTypes: [{
        value: 'bar',
        label: '柱状图'
      }, {
        value: 'scatter',
        label: '散点图'
      }, {
        value: 'line',
        label: '折线图'
      }]
    }
  },
  methods: {
    onDrag: function (left, top) {
      this.styleData.x = left
      this.styleData.y = top
    },
    onResize: function (left, top, width, height) {
      this.styleData.x = left
      this.styleData.y = top
      this.styleData.w = width
      this.styleData.h = height
    }
  },
  computed: {
    columns () {
      if (!Array.isArray(this.outputData.data) || this.$utils.isEmptyObject(this.outputData.data)) {
        return []
      }
      return Object.keys(this.outputData.data[0])
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
          data: this.outputData.data.map(x => x[this.xAxisName]),
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
          type: this.styleData.type || this.seriesTypes[0]['value'],
          itemStyle: {
            color: this.styleData.color || this.predefineColors[0]
          },
          data: this.outputData.data.map(x => x[key])
        })
      }
      return opt
    }
  },
  created () {
    window.styleData = this.styleData
  }
}
</script>

<style scoped>
</style>
