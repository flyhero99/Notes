<template>
  <el-main>
    <span style="padding-left: 20px; font-style: oblique; font-size: 24px;">{{notebook.name}}</span>
    <span style="padding-left: 20px; font-size: 16px">上次保存于：{{lastSaveAt}}</span>
    <span style="padding-left: 20px; font-size: 16px; float: right">内核状态：{{kernelStatus}}</span>
    <span style="padding-left: 20px; font-size: 16px; float: right" v-if="editMode">编辑模式（快捷键已启用）</span>
    <el-menu class="menu-bar" mode="horizontal" menu-trigger="click" :unique-opened="true">
      <el-submenu index="file">
        <template slot="title">文件</template>
        <el-menu-item class="menu-bar-item" @click="createDialogVisible=true" index="file-create">新建</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="saveNotebook" index="file-save">保存</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="newNotebookName=notebook.name
        copyDialogVisible=true" index="file-save-as">另存为/复制</el-menu-item>
      </el-submenu>
      <el-submenu index="kernel">
        <template slot="title">内核</template>
        <el-menu-item class="menu-bar-item" @click="connectKernel" index="kernel-connect">连接/创建</el-menu-item>
      </el-submenu>
      <el-submenu index="cell">
        <template slot="title">单元格</template>
        <el-menu-item class="menu-bar-item" @click="executeCommand" index="cell-run">执行当前单元格</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="deleteCell" index="cell-delete">删除当前单元格</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="insertCell" index="cell-insert">在当前行后插入单元格</el-menu-item>
      </el-submenu>
      <el-submenu index="help">
        <template slot="title">帮助</template>
        <el-menu-item class="menu-bar-item" @click="helpBasicDialogVisible=true" index="help-basic">基础</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="helpCommandDialogVisible=true" index="help-command">命令</el-menu-item>
      </el-submenu>
    </el-menu>
    <el-row class="toolkit-bar">
      <el-button icon="el-icon-document" size="mini" @click="saveNotebook"></el-button>
      <el-button icon="el-icon-caret-right" size="mini" @click="executeCommand"></el-button>
      <el-select v-model="notebook.cells[focusCell].type" size="mini"
                 @focus="previousSelect=notebook.cells[focusCell].type"
                 @change="handleSelect">
        <el-option
          v-for="item in cellTypeOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-row>

    <div class="notebook" style="overflow-y: auto; position:relative; height: 75vh;" ref="notebook">
      <div class="block" v-for="(value, key) in notebook.cells" :ref="'block-' + key"
           :key="key" :class="{'active-block' : key === focusCell, 'active-edit-block' : key === focusCell && editMode}"
            @click="focusCell=key">
        <div class="code-block" v-if="value.type === 'code'">
          <el-row class="input-block">
            <el-col :span="2" align="center">
              <span style="color: blue;"> In[{{value.num}}] </span>
            </el-col>
            <el-col :span="20">
              <el-input type="textarea"
                        :ref="'input-' + key"
                        :autosize="{ minRows: 3}"
                        v-model="value.in"
                        @keydown.native="handleKeydown"
                        @focus="editMode=true"
                        @blur="editMode=false"
                        class="input-block">
              </el-input>
            </el-col>
          </el-row>
          <el-row class="output-block">
            <notebook-output-block :blockData="value" xAxisName="date" :collapse="value.collapse">
            </notebook-output-block>
          </el-row>
        </div>
        <div class="markdown-block" v-else-if="value.type.startsWith('markdown')">
          <el-row class="input-block">
            <el-col :offset="1" :span="22">
              <mavon-editor v-model="value.in"
                            :ishljs="true"
                            :subfield="false"
                            :defaultOpen="value.type === 'markdown-rendered' ? 'preview' : 'edit'"
                            :toolbarsFlag="false"
                            :boxShadow="false"
                            @dblclick.native="value.type = 'markdown'"
                            @keydown.native="handleKeydown"
                            style="min-height: 10px">

              </mavon-editor>
            </el-col>
          </el-row>
        </div>
        <editable-wiki-cell :cellData.sync="value" :kernelId="kernelId" v-else-if="value.type === 'editable-wiki'"></editable-wiki-cell>
        <div v-else>Error cell type({{value.type}})!</div>
      </div>
    </div>

    <el-dialog
      title="新建笔记本"
      :visible.sync="createDialogVisible">
      <el-form>
        <el-form-item label="笔记本名称">
          <el-input v-model="newNotebookName"></el-input>
        </el-form-item>
      </el-form>
      <el-button @click="createNotebook" type="primary">
        创建
      </el-button>
      <el-button @click="createDialogVisible=false">
        取消
      </el-button>
    </el-dialog>
    <el-dialog
      title="另存为笔记本"
      :visible.sync="copyDialogVisible">
      <el-form>
        <el-form-item label="目标笔记本名称">
          <el-input v-model="newNotebookName"></el-input>
        </el-form-item>
      </el-form>
      <el-button @click="copyNotebook" type="primary">
        另存为/复制
      </el-button>
      <el-button @click="copyDialogVisible=false">
        取消
      </el-button>
    </el-dialog>
    <el-dialog
      title="基础帮助"
      :visible.sync="helpBasicDialogVisible">
      <notebook-basic-help></notebook-basic-help>
      <el-button @click="helpBasicDialogVisible=false">
        关闭
      </el-button>
    </el-dialog>
    <el-dialog
      title="命令手册"
      :visible.sync="helpCommandDialogVisible">
      <notebook-command-help></notebook-command-help>
      <el-button @click="helpCommandDialogVisible=false">
        关闭
      </el-button>
    </el-dialog>
  </el-main>
</template>

<script>
import NotebookOutputBlock from './OutputBlock'
import EditableWikiCell from './Cells/EditableWikiCell'
import NotebookBasicHelp from './BasicHelp'
import NotebookCommandHelp from './CommandHelp'
import { mavonEditor } from 'mavon-editor'
import 'mavon-editor/dist/css/index.css'

export default {
  name: 'notebookNotebook',
  components: {NotebookOutputBlock, NotebookBasicHelp, NotebookCommandHelp, mavonEditor, EditableWikiCell},
  data () {
    return {
      notebook: {
        cells: [
          {type: ''}
        ]
      },
      createDialogVisible: false,
      copyDialogVisible: false,
      helpBasicDialogVisible: false,
      helpCommandDialogVisible: false,
      newNotebookName: '未命名',
      lastSaveAt: '未保存',
      focusCell: 0,
      kernelId: '',
      kernelStatus: '无连接',
      editMode: false,

      cellTypeOptions: [
        {
          value: 'code',
          label: '代码'
        },
        {
          value: 'markdown',
          label: 'markdown源码'
        },
        {
          value: 'markdown-rendered',
          label: '渲染的markdown'
        },
        {
          value: 'editable-wiki',
          label: '可编辑的Wiki'
        }
      ],

      previousSelect: ''
    }
  },
  methods: {
    refreshNotebook: function () {
      this.$axios.get('/entryeditor/notebook/' + this.$route.params.id + '/').then(res => {
        this.notebook = res.data
      })
      this.kernelStatus = '正在连接'
      this.$axios.get('/entryeditor/notebook/' + this.$route.params.id + '/kernel/').then(res => {
        this.kernelId = res.data['kernel_id']
        if (this.kernelId) {
          this.kernelStatus = '已连接' + this.kernelId
        } else {
          this.kernelStatus = '无连接'
        }
      }, res => {
        this.kernelStatus = '无连接'
      })
    },
    createNotebook: function () {
      this.$axios.post('/entryeditor/notebook/', {'name': this.newNotebookName}).then(res => {
        this.$message.success('笔记本创建成功')
        this.createDialogVisible = false
        this.$router.push('/notebook/' + res.data.id)
      })
    },
    saveNotebook: function () {
      if (!this.editable) {
        this.$message.warning('你无法修改属于其他人的笔记本，请另存为新的词条。')
        return
      }
      this.$axios.put('/entryeditor/notebook/' + this.notebook.id + '/', this.notebook).then(res => {
        this.$message.success('笔记本保存成功')
        this.notebook = res.data
      })
    },
    copyNotebook: function () {
      let nb = JSON.parse(JSON.stringify(this.notebook))
      nb.name = this.newNotebookName
      this.$axios.post('/entryeditor/notebook/', nb).then(res => {
        this.$message.success('笔记本复制成功')
        this.copyDialogVisible = false
        this.$router.push('/notebook/' + res.data.id)
      })
    },

    connectKernel: function () {
      this.$axios.post('/entryeditor/notebook/' + this.notebook.id + '/kernel/').then(res => {
        this.$message.success('内核连接成功')
        this.kernelId = res.data['kernel_id']
        this.kernelStatus = '已连接' + this.kernelId
      })
    },

    executeCommand: function () {
      if (this.notebook.cells[this.focusCell].type === 'code') {
        this.notebook.cells[this.focusCell].out = ''
        this.notebook.cells[this.focusCell].num = '*'
        this.$axios.post('/entryeditor/notebook/' + this.notebook.id + '/execute/',
          {'command': this.notebook.cells[this.focusCell].in}).then(res => {
          this.notebook.cells[this.focusCell].out = res.data.output
          this.notebook.cells[this.focusCell].num = res.data['executing_num']
        }).catch(err => {
          this.notebook.cells[this.focusCell].out = err.response.data.output
          this.notebook.cells[this.focusCell].active_name = 'raw'
          this.notebook.cells[this.focusCell].num = err.response.data['executing_num']
        })
      } else if (this.notebook.cells[this.focusCell].type === 'markdown') {
        this.notebook.cells[this.focusCell].type = 'markdown-rendered'
      }
    },
    deleteCell: function () {
      this.notebook.cells.splice(this.focusCell, 1)
    },
    insertCell: function () {
      this.notebook.cells.splice(this.focusCell + 1, 0, {
        'num': ' ',
        'type': 'code',
        'in': '',
        'out': '',
        'collapse': 'all',
        'active_name': 'raw'
      })
      let block = this.$refs['block-' + this.focusCell][0]
      this.$refs['notebook'].scrollTop += block.getBoundingClientRect().height
    },

    beforeunloadHandler: function (e) {
      e = e || window.event
      // 兼容IE8和Firefox 4之前的版本
      if (e) {
        e.returnValue = '离开前请确定已保存改动'
      }
      // Chrome, Safari, Firefox 4+, Opera 12+ , IE 9+
      return '离开前请确定已保存改动'
    },
    cmdOrCtrl: function (e) {
      return navigator.platform.match('Mac') ? e.metaKey : e.ctrlKey
    },
    handleKeydown: function (e) {
      if (e.altKey && e.key === 'Enter') {
        this.executeCommand()
      } else if (this.cmdOrCtrl(e) && e.key === 's') {
        this.saveNotebook()
      } else if (this.cmdOrCtrl(e) && e.shiftKey && e.key === 'Enter') {
        this.insertCell()
      } else if (this.cmdOrCtrl(e) && e.shiftKey && e.key === 'Backspace') {
        this.deleteCell()
      } else {
        return true
      }
      e.preventDefault()
      return false
    },

    handleSelect: function (val) {
      let ps = this.previousSelect
      if (this.previousSelect !== 'editable-wiki' && val !== 'editable-wiki') {
        return
      }
      this.$confirm('注意：切换可编辑Wiki类型时，该输入框原有内容将会被清空！', {'type': 'warning'}).then(_ => {
        if (val === 'editable-wiki') {
          if (typeof this.notebook.cells[this.focusCell].in === 'string') {
            this.notebook.cells[this.focusCell].in = {}
          }
        } else {
          if (typeof this.notebook.cells[this.focusCell].in === 'object') {
            this.notebook.cells[this.focusCell].in = ''
          }
        }
        this.previousSelect = val
      }).catch(_ => {
        this.notebook.cells[this.focusCell].type = ps
      })
    }
  },
  mounted () {
    this.refreshNotebook()
    window.addEventListener('beforeunload', e => this.beforeunloadHandler(e))
  },
  destroyed () {
    window.removeEventListener('beforeunload', e => this.beforeunloadHandler(e))
  },
  beforeRouteLeave (to, from, next) {
    this.$confirm('离开前请确定已保存改动', {'type': 'warning'}).then(_ => next()).catch(_ => next(false))
  },
  computed: {
    debug_mode: function () {
      return this.$route.query.debug === 'true'
    },
    editable: function () {
      return this.notebook.user.id === this.$store.state.user.id
    }
  }
}
</script>

<style scoped>
.notebook {
  background: white;
  padding-top: 30px;
}
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
</style>

<style>
.input-block .el-textarea__inner {
  font-family: monospace, 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
}
.menu-bar {
  background: lightyellow !important;
}
body > div > ul > li.el-submenu > div.el-submenu__title, .menu-bar .el-submenu__title {
  color: black !important;
  font-size: 14px !important;
  height: 22px !important;
  line-height: 18px !important;
  padding-left: 10px !important;
}
.menu-bar-item {
  color: black !important;
  height: 22px !important;
  font-size: 14px !important;
  line-height: 18px !important;
}
.menu-bar-item :hover {
  background: black;
}
.menu-bar .el-submenu__icon-arrow {
  visibility: hidden;
}
.toolkit-bar {
  padding: 2px;
  background: white;
  border-bottom: 2px solid grey;
}
.toolkit-bar .el-button{
  padding: 4px;
  margin: 2px;
  background: white;
}
.toolkit-bar .el-select{
  padding: 4px;
  background: white;
}
</style>
