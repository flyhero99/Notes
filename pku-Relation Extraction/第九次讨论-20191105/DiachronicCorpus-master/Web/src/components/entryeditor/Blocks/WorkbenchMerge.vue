<template>
<div>
  <el-alert :title="'当前处于合并模式，请手动解决所有冲突后继续编辑。(还剩' + numUnresolved + '个)'" type="warning" :closable="false"></el-alert>
  <h1>{{entryeditor.word}}</h1>
  <transition-group name="list">
  <div class="block list-item" v-for="(value, key) in entryeditor.cells" :ref="'block-' + key"
       :key="value.id" :class="{'unsolved-block' : value.action !== 'match', 'active-block' : key === focusCell}"
       @click="propFocusCell=key"
       :style="{background: actionColor(value.action)}">
    <el-card class="merge-toolkit-card" v-if="value.action !== 'match'" v-show="key === focusCell" body-style="padding: 10px">
      <el-form>
        <el-form-item label="【待处理冲突】" style="margin: 0">
          <el-button type="primary" size="mini" @click="acceptChange(key)">采纳修改({{actionDescription(value.action)}})</el-button>
          <el-button type="danger" size="mini" @click="ignoreChange(key)">忽略此修改</el-button>
          <el-checkbox v-show="numSameAction !== 0" v-model="doSame" :label="'为之后的'+numSameAction+'个连续相同冲突执行相同操作。'"></el-checkbox>
        </el-form-item>
      </el-form>
    </el-card>
      <div v-if="value.action === 'match'">
        <read-only-cell-wrapper :content="value.cell" :activated="key === propFocusCell" :kernelId="entryeditor.kernel_id"></read-only-cell-wrapper>
      </div>
      <div v-else-if="value.action === 'substitute'">
        <div style="background: rgb(140, 197, 255); border-radius: 5px; margin: 5px">
          <p style="color: gray; margin: 10px">原始版本：</p>
          <read-only-cell-wrapper :content="value.cell1" :activated="key === propFocusCell" :kernelId="entryeditor.kernel_id"></read-only-cell-wrapper>
        </div>
        <div style="background: rgb(250, 236, 216); border-radius: 5px; margin: 5px">
          <p style="color: gray; margin: 10px">修改版本：</p>
          <read-only-cell-wrapper :content="value.cell2" :activated="key === propFocusCell" :kernelId="entryeditor.kernel_id"></read-only-cell-wrapper>
        </div>
      </div>
      <div v-else-if="value.action === 'delete'">
        <read-only-cell-wrapper :content="value.cell" :activated="key === propFocusCell" :kernelId="entryeditor.kernel_id"></read-only-cell-wrapper>
      </div>
      <div v-else-if="value.action === 'add'">
        <read-only-cell-wrapper :content="value.cell" :activated="key === propFocusCell" :kernelId="entryeditor.kernel_id"></read-only-cell-wrapper>
      </div>
      <!--<div v-else><vue-json-pretty :data="value"></vue-json-pretty></div>-->
      <div v-if="debug_mode">{{key}}:{{value}}</div>
  </div>
  </transition-group>

</div>
</template>

<script>
import VueJsonPretty from 'vue-json-pretty'
import ReadOnlyCellWrapper from './ReadOnlyCellWrapper'

export default {
  name: 'Workbench',
  props: ['entryeditor', 'debug_mode', 'focusCell'],
  components: {ReadOnlyCellWrapper, VueJsonPretty},
  data () {
    return {
      propFocusCell: this.focusCell,
      doSame: false
    }
  },
  methods: {
    actionColor: function (action) {
      switch (action) {
        case 'delete': return 'rgb(253, 226, 226)'
        case 'add': return 'rgb(140, 197, 255)'
        case 'substitute': return 'rgb(225, 243, 216)'
      }
    },
    actionDescription: function (action) {
      switch (action) {
        case 'delete': return '删除此单元格'
        case 'add': return '保留此单元格'
        case 'substitute': return '保留修改版本'
      }
    },
    acceptChange: function (key) {
      let len = this.doSame ? this.numSameAction + 1 : 1
      let cell = this.entryeditor.cells[key]
      switch (cell.action) {
        case 'delete':
          this.entryeditor.cells.splice(key, len)
          break
        case 'add':
          for (let i = 0; i < len; i++) {
            this.entryeditor.cells[key + i].action = 'match'
          }
          this.propFocusCell += len
          break
        case 'substitute':
          for (let i = 0; i < len; i++) {
            this.entryeditor.cells[key + i].cell = this.entryeditor.cells[key + i].cell2
            this.entryeditor.cells[key + i].action = 'match'
            delete this.entryeditor.cells[key + i].cell1
            delete this.entryeditor.cells[key + i].cell2
          }
          break
      }
    },
    ignoreChange: function (key) {
      let len = this.doSame ? this.numSameAction + 1 : 1
      let cell = this.entryeditor.cells[key]
      switch (cell.action) {
        case 'delete':
          for (let i = 0; i < len; i++) {
            this.entryeditor.cells[key + i].action = 'match'
          }
          this.propFocusCell += len
          break
        case 'add':
          this.entryeditor.cells.splice(key, len)
          break
        case 'substitute':
          for (let i = 0; i < len; i++) {
            this.entryeditor.cells[key + i].cell = this.entryeditor.cells[key + i].cell1
            this.entryeditor.cells[key + i].action = 'match'
            delete this.entryeditor.cells[key + i].cell1
            delete this.entryeditor.cells[key + i].cell2
          }
          break
      }
      cell.action = 'match'
    }
  },
  computed: {
    numUnresolved: function () {
      return this.entryeditor.cells.filter(x => x.action !== 'match').length
    },
    numSameAction: function () {
      let ret = 0
      let action = this.entryeditor.cells[this.focusCell].action
      for (let cell of this.entryeditor.cells.slice(this.focusCell + 1)) {
        if (cell.action !== action) {
          break
        }
        ret += 1
      }
      return ret
    }
  },
  watch: {
    propFocusCell: function (val) {
      this.$emit('update:focusCell', val)
    },
    numUnresolved: {
      immediate: true,
      handler: function (val) {
        if (val === 0 && this.entryeditor.status === 'MERGING') {
          this.entryeditor.status = 'NORMAL'
          this.entryeditor.cells = this.entryeditor.cells.map(x => x.cell)
        }
      }
    }
  }
}
</script>

<style scoped>
  .block {
    padding-top: 10px;
    padding-bottom: 10px;
    border: 1px solid transparent;
    border-left-width: 6px;
  }
  .unsolved-block {
    /*border-color: orangered;*/
  }
  .active-block {
    border-color: blue;
  }
  .active-edit-block {
    border-color: limegreen;
  }
  .merge-toolkit-card {
    margin: 10px;
  }
  .list-item {
    transition: all 0.5s, border 0s;
    /*display: inline-block;*/
  }
  .list-leave-active {
    position: absolute;
  }
  .list-enter, .list-leave-to
    /* .list-leave-active for below version 2.1.8 */ {
    opacity: 0;
    transform: translateX(90px);
  }
</style>
