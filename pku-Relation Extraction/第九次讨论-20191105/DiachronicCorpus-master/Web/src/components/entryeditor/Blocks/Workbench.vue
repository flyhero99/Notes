<template>
<div>
  <h1>{{entryeditor.word}}</h1>
  <h3>目录</h3>
  <el-tree :data="treeData" default-expand-all>
    <span class="custom-tree-node" slot-scope="{ node, data }">
        <span>{{ node.label }}</span>
        <span>
          <el-button type="text" size="mini" @click="scrollToCell(data.id)">跳转</el-button>
        </span>
      </span>
  </el-tree>
<!--  <ul>-->
<!--    <li v-for="value in entryeditor.cells" :key="value.id"><a :href="'#'+value.id">{{value.type}}</a> </li>-->
<!--  </ul>-->
  <el-divider></el-divider>
  <transition-group name="list">
    <div class="block list-item" v-for="(value, key) in entryeditor.cells" :ref="'block-' + value.id" :id="value.id"
         :key="value.id" :class="{'active-block' : key === focusCell, 'active-edit-block' : key === focusCell && editable}"
         @click="propFocusCell=key">
      <div v-if="value.type==='Title'">
        <title-cell :blockData="value" :activated="key === focusCell" :editable="editable"></title-cell>
      </div>
      <div v-else-if="value.type==='EditableText'">
        <el-input v-if="editable" type="textarea" :autosize="{ minRows: 1}" style="font-size: 16px" v-model="value.out"/>
        <div v-else style="font-size: 16px; margin: 10px">{{value.out}}</div>
      </div>
      <div v-else-if="value.type==='Code'">
        <code-block :blockData.sync="value" :activated="key === focusCell" :kernelId="entryeditor.kernel_id"
                    :editable="editable" :ref="value.id"></code-block>
      </div>
      <!--<div v-else><vue-json-pretty :data="value"></vue-json-pretty></div>-->
      <div v-if="debug_mode">{{key}}:{{value}}</div>
    </div>
  </transition-group>
</div>
</template>

<script>
import VueJsonPretty from 'vue-json-pretty'
import CodeBlock from './CodeBlock'
import TitleCell from '../Cells/TitleCell'

export default {
  name: 'Workbench',
  props: ['entryeditor', 'debug_mode', 'focusCell', 'editable'],
  components: {VueJsonPretty, CodeBlock, TitleCell},
  data () {
    return {
      propFocusCell: this.focusCell
    }
  },
  computed: {
    treeData: function () {
      let ret = [{id: 0, label: '目录', children: [], level: 0}]
      // let prevNode = null
      for (let c of this.entryeditor.cells) {
        if (c.type === 'Title') {
          let node = ret[ret.length - 1]
          while (node.children.length > 0 && node.children[node.children.length - 1].level < c.style.level) {
            node = node.children[node.children.length - 1]
          }
          node.children.push({id: c.id, label: c.out, children: [], level: c.style.level})
        }
      }
      return ret[0].children
    }
  },
  watch: {
    propFocusCell: function (val) {
      this.$emit('update:focusCell', val)
    }
  },
  methods: {
    executeAllCommand: function () {
      for (let cell of this.entryeditor.cells) {
        if (cell.type === 'Code') {
          this.$refs[cell.id][0].executeCommand()
        }
      }
    },
    scrollToCell: function (id) {
      this.$emit('scrollNotebook', this.$refs['block-' + id][0].offsetTop)
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
  .active-block {
    border-color: blue;
  }
  .active-edit-block {
    border-color: limegreen;
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
