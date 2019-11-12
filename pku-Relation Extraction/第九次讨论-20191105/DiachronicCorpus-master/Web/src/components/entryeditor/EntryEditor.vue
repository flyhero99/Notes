<template>
  <el-main>
    <span style="padding-left: 20px; font-style: oblique; font-size: 24px;">{{entryeditor.name}}</span>
    <span style="padding-left: 20px; font-size: 16px">上次保存于：{{entryeditor.updated_at}}</span>
    <span style="padding-left: 20px; font-size: 16px">自动保存：
      <el-switch
        v-model="ifAutoSave"
        active-color="#13ce66"
        inactive-color="#ff4949">
      </el-switch></span>
    <span style="padding-left: 20px; font-size: 16px">{{saveStatus}}</span>
    <span style="padding-left: 20px; font-size: 16px; float: right">内核状态：{{entryeditor.kernel_id}}</span>
    <el-menu class="menu-bar" mode="horizontal" menu-trigger="click" :unique-opened="true">
      <el-submenu index="file">
        <template slot="title">文件</template>
        <el-menu-item class="menu-bar-item" @click="createDialogVisible=true" index="file-create">新建</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="saveEntryEditor" index="file-save">保存词条</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="newEntryEditorName=entryeditor.name
        copyDialogVisible=true" index="file-save-as">另存为/复制</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="createCheckpoint" index="file-checkpoint">创建记录点</el-menu-item>
        <el-submenu index="file-revert">
          <template slot="title">回滚记录点</template>
          <el-menu-item v-for="(value, key, index) in checkpoints" :key="index" class="menu-bar-item"
                        @click="revertCheckpoint(value)" :index="'file-revert-'+key">{{value.created_at}}</el-menu-item>
        </el-submenu>
        <el-menu-item class="menu-bar-item" @click="mergeDialogVisible=true" index="file-merge"
                      :disabled="entryeditor.status !== 'NORMAL'">比较/合并</el-menu-item>
      </el-submenu>
      <!--<el-submenu index="kernel">-->
        <!--<template slot="title">内核</template>-->
        <!--<el-menu-item class="menu-bar-item" @click="connectKernel" index="kernel-connect">连接/创建</el-menu-item>-->
      <!--</el-submenu>-->
      <el-tooltip :disabled="entryeditor.status !== 'MERGING'" content="合并模式下无法修改单元格" placement="top">
        <el-submenu index="cell" :disabled="entryeditor.status !== 'NORMAL'">
          <template slot="title">单元格</template>
          <el-menu-item class="menu-bar-item" @click="executeAllCommand" index="cell-run">执行全部单元格</el-menu-item>
          <el-menu-item class="menu-bar-item" @click="deleteCell" index="cell-delete">删除当前单元格</el-menu-item>
          <el-menu-item class="menu-bar-item" @click="moveUpCell" index="cell-move-up">与上方单元格交换</el-menu-item>
          <el-menu-item class="menu-bar-item" @click="moveDownCell" index="cell-move-down">与下方单元格交换</el-menu-item>
          <el-submenu index="cell-insert">
            <template slot="title">在当前行后插入单元格</template>
            <el-menu-item v-for="(value, key, index) in allCellType" :key="index" class="menu-bar-item"
                          @click="insertCell(key)" :index="'cell-insert-'+key">{{value}}</el-menu-item>
          </el-submenu>
        </el-submenu>
      </el-tooltip>
      <el-submenu index="help" disabled>
        <template slot="title">帮助</template>
        <el-menu-item class="menu-bar-item" @click="helpBasicDialogVisible=true" index="help-basic">基础</el-menu-item>
        <el-menu-item class="menu-bar-item" @click="helpCommandDialogVisible=true" index="help-command">命令</el-menu-item>
      </el-submenu>
      <button v-if="debug_mode" @click="$router.push({path: $route.params.path})">退出调试</button>
      <button v-else @click="$router.push({path: $route.params.path, query: {debug: 'true'}})">调试模式</button>
      <span v-if="entryeditor.status === 'NORMAL'">单元格类型：{{getCellType(focusCell)}}</span>
      <span v-else-if="entryeditor.status === 'MERGING'">合并模式</span>
      <span v-if="!editable">|只读模式</span>
    </el-menu>
    <el-row class="toolkit-bar">
      <div class="button-group">
        <el-button icon="el-icon-document" size="mini" title='新建词条' @click="createDialogVisible=true"></el-button>
        <el-button icon="el-icon-document-checked" size="mini" title='保存词条' @click="saveEntryEditor"></el-button>
        <el-button icon="el-icon-document-copy" size="mini" title='另存为词条' @click="newEntryEditorName=entryeditor.name
          copyDialogVisible=true"></el-button>
      </div>
      <div class="button-group">
        <el-button icon="el-icon-top" size="mini" title='与上方单元格交换' @click="moveUpCell"></el-button>
        <el-button icon="el-icon-bottom" size="mini" title='与下方单元格交换' @click="moveDownCell"></el-button>
      </div>
      <div class="button-group">
        <el-button size="mini" title='创建标题单元格' @click="insertCell('Title')">T</el-button>
        <el-button size="mini" title='创建文字单元格' @click="insertCell('EditableText')">E</el-button>
        <el-button size="mini" title='创建代码单元格' @click="insertCell('Code')">C</el-button>
      </div>
    </el-row>

    <div class="notebook" style="overflow-y: auto; position:relative; height: 75vh;" ref="notebook">
      <h3 v-if="entryeditor.status === 'UNINITIALIZED'">未初始化</h3>
      <workbench v-else-if="entryeditor.status === 'NORMAL'" :entryeditor.sync="entryeditor" :debug_mode="debug_mode"
                 :focusCell.sync="focusCell" :editable="editable" ref="workbench" @scrollNotebook="scrollNotebook"></workbench>
      <workbench-merge v-else-if="entryeditor.status === 'MERGING'" :entryeditor.sync="entryeditor" :debug_mode="debug_mode"
                       :focusCell.sync="focusCell" ></workbench-merge>
    </div>

    <el-dialog title="初始化编辑器" :visible.sync="initDialogVisible"
               :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
      <el-form>
        <el-form-item label="词条词语">
          <el-input v-model="initWord" placeholder="词条词语"></el-input>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="useEmptyEE">
            使用空白布局
            <el-tooltip placement="top">
              <div slot="content">默认会为编辑器添加一些基本框架，比如读音、释义、例句等条目。勾选此项以获得完全空白的布局。</div>
              <i class="el-icon-question"></i>
            </el-tooltip>
          </el-checkbox>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="initEntryEditor(initWord)">初始化</el-button>
      </span>
    </el-dialog>
    <el-dialog title="新建词条编辑器" :visible.sync="createDialogVisible">
      <el-form>
        <el-form-item label="词条编辑器名称">
          <el-input v-model="newEntryEditorName"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="createEntryEditor" type="primary">
          创建
        </el-button>
        <el-button @click="createDialogVisible=false">
          取消
        </el-button>
      </span>
    </el-dialog>
    <el-dialog title="另存为词条编辑器" :visible.sync="copyDialogVisible">
      <el-form>
        <el-form-item label="目标词条编辑器名称">
          <el-input v-model="newEntryEditorName"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="copyEntryEditor" type="primary">
          另存为/复制
        </el-button>
        <el-button @click="copyDialogVisible=false">
          取消
        </el-button>
      </span>
    </el-dialog>
    <el-dialog title="比较/合并" :visible.sync="mergeDialogVisible">
      <el-form>
        <el-form-item label="祖先版本">
          <el-table
          :data="parentEntryEditors"
          :show-header="false"
          size="mini"
          style="line-height: 10px"
          max-height="250"
          @row-click="mergeEntryEditor($event.parent_ee)">
            <el-table-column
              label="笔记本名称"
              prop="parent_ee.name">
            </el-table-column>
            <el-table-column
              label="创建者"
              prop="parent_ee.user.username">
            </el-table-column>
            <el-table-column
              label="创建于"
              prop="parent_ee.created_at"
              sortable
              width="150px">
            </el-table-column>
            <el-table-column
              label="修改于"
              prop="parent_ee.updated_at"
              sortable
              width="150px">
            </el-table-column>
          </el-table>
        </el-form-item>
        <el-form-item label="子孙版本">
          <el-table
            :data="childEntryEditors"
            :show-header="false"
            size="mini"
            style="line-height: 10px"
            max-height="250"
            @row-click="mergeEntryEditor($event.child_ee)">
            <el-table-column
              label="笔记本名称"
              prop="child_ee.name">
            </el-table-column>
            <el-table-column
              label="创建者"
              prop="child_ee.user.username">
            </el-table-column>
            <el-table-column
              label="创建于"
              prop="child_ee.created_at"
              sortable
              width="150px">
            </el-table-column>
            <el-table-column
              label="修改于"
              prop="child_ee.updated_at"
              sortable
              width="150px">
            </el-table-column>
          </el-table>
        </el-form-item>
        <el-form-item label="输入词语、标题或id搜索">
          <el-input
            v-model="searchPattern"
            size="mini"
            placeholder="输入词语、标题或id搜索"/>
          <el-table
            :data="searchedEntryEditors"
            :show-header="false"
            size="mini"
            style="line-height: 10px"
            max-height="250"
            @row-click="mergeEntryEditor($event)">
            <el-table-column
              label="笔记本名称"
              prop="name">
            </el-table-column>
            <el-table-column
              label="创建者"
              prop="user.username">
            </el-table-column>
            <el-table-column
              label="创建于"
              prop="created_at"
              sortable
              width="150px">
            </el-table-column>
            <el-table-column
              label="修改于"
              prop="updated_at"
              sortable
              width="150px">
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="mergeDialogVisible=false">
          取消
        </el-button>
      </span>
    </el-dialog>
    <el-dialog title="基础帮助" :visible.sync="helpBasicDialogVisible">
      <!--<notebook-basic-help></notebook-basic-help>-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="helpBasicDialogVisible=false">
          关闭
        </el-button>
      </span>
    </el-dialog>
    <el-dialog title="命令手册" :visible.sync="helpCommandDialogVisible">
      <!--<notebook-command-help></notebook-command-help>-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="helpCommandDialogVisible=false">
          关闭
        </el-button>
      </span>
    </el-dialog>
  </el-main>
</template>

<script>
import Workbench from './Blocks/Workbench'
import WorkbenchMerge from './Blocks/WorkbenchMerge'
import uuid4 from 'uuid/v4'

export default {
  name: 'EntryEditor',
  components: {Workbench, WorkbenchMerge},
  data () {
    return {
      entryeditor: {
        'name': '',
        'word': '',
        'kernel_id': '',
        'status': '',
        'cells': [
          {
            'in': '',
            'out': '',
            'style': '',
            'type': ''
          }
        ],
        'user': {
          'id': '',
          'username': ''
        }
      },
      entryeditorSaved: {},
      initWord: '',
      useEmptyEE: false,
      newEntryEditorName: '',
      focusCell: 0,
      initDialogVisible: false,
      createDialogVisible: false,
      copyDialogVisible: false,
      mergeDialogVisible: false,
      helpBasicDialogVisible: false,
      helpCommandDialogVisible: false,

      timer: null,
      saveMethod: '',
      checkpoints: [],
      searchPattern: '',
      ifAutoSave: (this.$route.query.autosave || 'true') === 'true',

      allCellType: {
        'Title': '标题',
        'EditableText': '可编辑文本',
        'Code': '代码块'
      }
    }
  },
  watch: {
    entryeditor: {
      deep: true,
      immediate: true,
      handler: function (val) {
        for (let cell of val.cells) {
          if (!cell.id) {
            cell.id = uuid4()
          }
        }
      }
    }
  },
  methods: {
    refreshEntryEditor: function () {
      this.$axios.get('/entryeditor/entryeditor/' + this.$route.params.id + '/').then(res => {
        this.entryeditor = res.data
        this.entryeditorSaved = JSON.parse(JSON.stringify(this.entryeditor))
        if (this.entryeditor.status === 'UNINITIALIZED') {
          this.initDialogVisible = true
        }
      })
    },
    refreshCheckpoints: function () {
      this.$axios.get('/entryeditor/entryeditor_checkpoint/', {params: {entryeditor: this.$route.params.id}}).then(res => {
        this.checkpoints = res.data
      })
    },
    createEntryEditor: function () {
      this.$axios.post('/entryeditor/entryeditor/', {'name': this.newEntryEditorName}).then(res => {
        this.$message.success('笔记本创建成功')
        this.createDialogVisible = false
        this.$router.push('/entryeditor/' + res.data.id)
      })
    },
    createCheckpoint: function () {
      if (!this.editable) {
        this.$message.warning('你无法修改属于其他人的词条，请另存为新的词条。')
        return
      }
      this.saveEntryEditor()
      this.$axios.post('/entryeditor/entryeditor_checkpoint/', {
        'name_bak': this.entryeditor.name,
        'word_bak': this.entryeditor.word,
        'cells_bak': this.entryeditor.cells,
        'status_bak': this.entryeditor.status,
        'entryeditor': this.entryeditor.id}).then(res => {
        this.refreshCheckpoints()
        this.$message.success('记录点创建成功')
        this.saveMethod = '已手动保存'
      })
    },
    revertCheckpoint: function (checkpoint) {
      this.$axios.get('/entryeditor/entryeditor_checkpoint/' + checkpoint.id + '/').then(res => {
        this.entryeditor.word = res.data.word_bak
        this.entryeditor.name = res.data.name_bak
        this.entryeditor.status = res.data.status_bak
        this.entryeditor.cells = JSON.parse(JSON.stringify(res.data.cells_bak))
        this.$message.success('记录点回滚成功')
        this.autoSave()
      })
    },
    saveEntryEditor: function () {
      if (!this.editable) {
        this.$message.warning('你无法修改属于其他人的词条，请另存为新的词条。')
        return
      }
      this.$axios.put('/entryeditor/entryeditor/' + this.entryeditor.id + '/', this.entryeditor).then(res => {
        this.$notify.success('笔记本保存成功')
        this.entryeditor = res.data
        this.entryeditorSaved = JSON.parse(JSON.stringify(this.entryeditor))
      })
    },
    copyEntryEditor: function () {
      let ee = JSON.parse(JSON.stringify(this.entryeditor))
      ee.name = this.newEntryEditorName
      this.$axios.post('/entryeditor/entryeditor/', ee).then(res => {
        this.$message.success('笔记本复制成功')
        this.copyDialogVisible = false
        this.$axios.post('/entryeditor/entryeditor_fork/', {
          parent: this.entryeditor.id,
          child: res.data.id
        })
        this.$router.push('/entryeditor/' + res.data.id)
      })
    },
    initEntryEditor: function (word) {
      if (word === '') {
        this.$message.error('请输入一个词语')
        return
      }
      const loading = this.$loading({
        lock: true,
        text: '初始化中',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      this.$axios.post('/entryeditor/entryeditor/' + this.entryeditor.id + '/init/', {'word': this.initWord, 'empty': this.useEmptyEE}).then(res => {
        this.$message.success('笔记本初始化成功')
        this.initDialogVisible = false
        this.entryeditor = res.data
      }).finally(() => loading.close())
    },
    mergeEntryEditor: function (row) {
      this.$confirm('确认合并词条编辑器"' + row.name + '"？', {type: 'primary'}).then(_ => {
        const loading = this.$loading({
          lock: true,
          text: '合并中',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        this.autoSave()
        this.$axios.get('/entryeditor/entryeditor/' + this.entryeditor.id + '/diff/' + row.id + '/').then(res => {
          this.entryeditor.status = 'MERGING'
          this.entryeditor.cells = res.data
          this.mergeDialogVisible = false
        }).finally(() => loading.close())
      }).catch(_ => {})
    },

    deleteCell: function () {
      this.entryeditor.cells.splice(this.focusCell, 1)
    },
    insertCell: function (cellType) {
      this.entryeditor.cells.splice(this.focusCell + 1, 0, {
        'in': '',
        'out': '[新单元格]',
        'style': {},
        'type': cellType
      })
      // let block = this.$refs['block-' + this.focusCell][0]
      // this.$refs['notebook'].scrollTop += block.getBoundingClientRect().height
    },
    swapArray: function (arr, index1, index2) {
      arr[index1] = arr.splice(index2, 1, arr[index1])[0]
      return arr
    },
    moveUpCell: function () {
      if (this.focusCell === 0) {
        return
      }
      this.swapArray(this.entryeditor.cells, this.focusCell, this.focusCell - 1)
      this.focusCell -= 1
    },
    moveDownCell: function () {
      if (this.focusCell === this.entryeditor.cells.length - 1) {
        return
      }
      this.swapArray(this.entryeditor.cells, this.focusCell, this.focusCell + 1)
      this.focusCell += 1
    },
    executeAllCommand: function () {
      this.$refs.workbench.executeAllCommand()
    },
    autoSave: function () {
      if (this.ifAutoSave && this.editable && this.isDirty) {
        this.saveEntryEditor()
      }
    },
    beforeunloadHandler: function (e) {
      clearInterval(this.timer)
      this.autoSave()
    },

    getCellType: function (key) {
      if (this.entryeditor.cells[key]) {
        return this.allCellType[this.entryeditor.cells[key].type]
      }
    },
    scrollNotebook: function (top) {
      this.$refs['notebook'].scrollTop = top
    }
  },
  created () {
    window.addEventListener('beforeunload', e => this.beforeunloadHandler(e))
  },
  mounted () {
    this.refreshEntryEditor()
    this.refreshCheckpoints()
    this.timer = setInterval(() => {
      if (this.ifAutoSave && this.editable && this.isDirty) {
        this.saveEntryEditor()
        this.saveMethod = '已自动保存'
      }
    }, 2 * 60 * 1000)
  },
  destroyed () {
    this.beforeunloadHandler()
  },
  computed: {
    debug_mode: function () {
      return this.$route.query.debug === 'true'
    },
    editable: function () {
      return this.entryeditor.user.id === this.$store.state.user.id
    },
    isDirty: function () {
      return JSON.stringify(this.entryeditorSaved) !== JSON.stringify(this.entryeditor)
    },
    saveStatus: function () {
      if (this.isDirty) {
        return '有未保存的改动'
      }
      return this.saveMethod
    }
  },
  asyncComputed: {
    parentEntryEditors: async function () {
      return this.$axios.get('/entryeditor/entryeditor_fork/', {
        params: {
          child: this.entryeditor.id
        }
      }).then(res => res.data)
    },
    childEntryEditors: async function () {
      return this.$axios.get('/entryeditor/entryeditor_fork/', {
        params: {
          parent: this.entryeditor.id
        }
      }).then(res => res.data)
    },
    searchedEntryEditors: async function () {
      if (this.searchPattern === '') {
        return []
      }
      return this.$axios.get('/entryeditor/entryeditor/', {
        params: {
          search: this.searchPattern
        }
      }).then(res => res.data)
    }
  }
}
</script>

<style scoped>
  .notebook {
    background: white;
    padding-top: 30px;
    padding-left: 15px;
    padding-right: 15px;
  }
  .button-group {
    padding: 0 4px 0 4px;
    border-right: #99a9bf 2px solid;
    width: auto;
    float: left
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
