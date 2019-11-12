<template>
  <div>
    <el-row class="input-block" v-show="activated && editable">
      <el-col :span="2" style="display: flex;justify-content:center;align-items:Center;">
        <span style="color: blue;"> 命令: </span>
      </el-col>
      <el-col :span="20">
        <el-autocomplete popper-class="my-autocomplete" v-model="blockData.in" size="large"
                         class="input-block" :fetch-suggestions="querySearch" @select="handleSelect">
          <el-button slot="append" icon="el-icon-caret-right" @click="executeCommand"></el-button>
          <template slot-scope="{ item }">
            <div class="pattern">{{ item.pattern }}</div>
            <span class="help">{{ item.help }}</span>
          </template>
        </el-autocomplete>
      </el-col>
    </el-row>
    <el-row class="output-block">
      <div v-if="this.loading">
        <el-alert type="info" title="" :closable="false">计算中...</el-alert>
      </div>
      <div v-else-if="blockData.out===''">
        <el-alert type="info" title="" :closable="false">无输出</el-alert>
      </div>
      <list-with-chart  v-else-if="blockData.out.type==='ListWithChart'"
                        :outputData.sync="blockData.out" :styleData.sync="blockData.style" :activated="activated" :editable="editable"></list-with-chart>
      <el-alert v-else-if="blockData.out.type==='Error'"
                :title='blockData.out.detail' type="warning" :closable="false"></el-alert>
      <div v-else-if="blockData.out.type==='ExampleTable'">
        <example-table :outputData.sync="blockData.out" :styleData.sync="blockData.style" :activated="activated" :editable="editable"></example-table>
      </div>
      <div v-else-if="blockData.out.type==='String'">
        <el-col :span="20">
<!--          <el-alert type="info" title="" :closable="false">{{blockData.out.data}}</el-alert>-->
          <el-input v-if="editable" type="textarea" :autosize="{ minRows: 1}" style="font-size: 16px" v-model="blockData.out.data"/>
          <div v-else style="font-size: 16px; margin: 10px">{{value.out}}</div>
        </el-col>
      </div>
      <el-alert v-else title="暂未支持的输出格式，打开调试模式以得到原始输出。" type="warning" :closable="false"></el-alert>
    </el-row>
  </div>
</template>

<script>
import ListWithChart from '../Panes/ListWithChart'
import ExampleTable from '../Panes/ExampleTable'

export default {
  name: 'CodeBlock',
  components: {ExampleTable, ListWithChart},
  props: ['blockData', 'activated', 'kernelId', 'editable'],
  data () {
    return {
      loading: false,
      commands: [
        {'pattern': 'freq(pattern=)', 'help': '查询词频率'},
        {'pattern': 'sense_freq(word=, sense_id=)', 'help': '查询词义频率'},
        {'pattern': 'sense_examples(word=, sense_id=, year=, offset=, num=)', 'help': '查询词义例句'},
        {'pattern': 'synonyms(word=)', 'help': '查询同义词'},
        {'pattern': 'multi_synonyms(word=)', 'help': '查询多词义同义词'}
      ]
    }
  },
  methods: {
    executeCommand: function () {
      if (this.blockData.type === 'Code') {
        this.loading = true
        this.blockData.out = ''
        this.$axios.post('/entryeditor/entryeditor/' + this.$route.params.id + '/execute/',
          {'command': this.blockData.in}).then(res => {
          this.loading = false
          this.blockData.out = res.data.output
        }, err => {
          this.loading = false
          this.blockData.out = err.response.data.output
          this.blockData.out.type = 'Error'
        })
      }
    },
    querySearch: function (queryString, cb) {
      let commands = this.commands
      let results = queryString ? commands.filter(this.createFilter(queryString)) : commands
      // 调用 callback 返回建议列表的数据
      cb(results)
    },
    createFilter: function (queryString) {
      return (command) => {
        return (command.pattern.toLowerCase().indexOf(queryString.toLowerCase()) === 0)
      }
    },
    handleSelect: function (item) {
      this.blockData.in = item.pattern
    }
  },
  watch: {
    blockData: {
      deep: true,
      immediate: true,
      handler: function (val) {
        if (val['out'] === '[新单元格]') {
          val['out'] = {
            data: '[新单元格]',
            type: 'String'
          }
        }
        if (val['out']['type'] === 'List') {
          val['out']['type'] = 'String'
          val['out']['data'] = val['out']['data'].map(x => x.word).join('，')
        }
        if (val['out']['type'] === 'ListWithList') {
          val['out']['type'] = 'String'
          val['out']['data'] = val['out']['data'].map(x => x.map(xx => xx.word).join('，')).join('\n')
        }
        if (val['out']['type'] === 'ListWithChart') {
          if (val['style'] === '' || val['style'] === {} || val['style']['x'] === undefined) {
            val['style'] = {
              x: 100,
              y: 0,
              w: 400,
              h: 300
            }
          }
        }
        if (val['out']['type'] === 'ExampleTable') {
          if (val['style'] === '' || val['style'] === {} || val['style']['highlight'] === undefined) {
            val['style'] = {
              highlight: true,
              showYear: true,
              showWord: false
            }
          }
        }
      }
    }
  }
}
</script>

<style>
.input-block {
  width: 100%;
}

.my-autocomplete li {
  line-height: normal;
  padding: 7px;
}

.my-autocomplete li .pattern {
  text-overflow: ellipsis;
  overflow: hidden;
}
.my-autocomplete li .help {
  font-size: 12px;
  color: #b4b4b4;
}

.my-autocomplete li .highlighted .addr {
    color: #ddd;
}
</style>
