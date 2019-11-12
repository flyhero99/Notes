<template>
  <el-main>
    <h1>EntryEditor</h1>
    <el-button @click="createDialogVisible=true" size="small">新建</el-button>
    <el-table
      :data="entryeditors"
      v-loading="loading"
      element-loading-text="如果长时间处于加载状态有可能是后端服务器失去了连接"
      @cell-mouse-enter="(row, column, cell, event) => this.focusedItem=row.id"
    >
      <el-table-column
        label="笔记本名称"
        prop="name">
        <template slot-scope="scope">
          <el-link :underline="false" @click="$router.push(scope.row.id.toString())">
            {{ scope.row.name }}
          </el-link>
          <el-button class="text-button" type="text" icon="el-icon-edit-outline" @click="onClickRenameButton(scope.row)"
                v-if="scope.row.user.id === $store.state.user.id"
                v-show="scope.row.id === focusedItem"></el-button>
          <el-button class="text-button" type="text" icon="el-icon-delete" @click="deleteEntryEditor(scope.row)"
                     v-if="scope.row.user.id === $store.state.user.id"
                     v-show="scope.row.id === focusedItem"></el-button>
        </template>
      </el-table-column>
      <el-table-column
        label="他人可见"
        prop="is_public"
      >
        <template slot-scope="scope">
          <el-switch
            v-model="scope.row.is_public"
            active-color="#13ce66"
            inactive-color="#ff4949"
            :disabled="scope.row.user.id !== $store.state.user.id"
            @change="changePublic(scope.row.id, scope.row.is_public)"
          >
          </el-switch>
        </template>
      </el-table-column>
      <el-table-column
        label="创建者"
        prop="user.username">
      </el-table-column>
      <el-table-column
        label="创建于"
        prop="created_at">
      </el-table-column>
      <el-table-column
        label="修改于"
        prop="updated_at">
      </el-table-column>
    </el-table>
    <el-dialog
      title="新建笔记本"
      :visible.sync="createDialogVisible">
      <el-form>
        <el-form-item label="笔记本名称">
          <el-input v-model="newEntryEditorName"></el-input>
        </el-form-item>
      </el-form>
      <el-button @click="createEntryEditor" type="primary">
        创建
      </el-button>
      <el-button @click="createDialogVisible=false">
        取消
      </el-button>
    </el-dialog>
    <el-dialog
      title="重命名笔记本"
      :visible.sync="renameDialogVisible">
      <el-form>
        <el-form-item label="重命名为">
          <el-input v-model="newEntryEditorName"></el-input>
        </el-form-item>
      </el-form>
      <el-button @click="renameEntryEditor" type="primary">
        重命名
      </el-button>
      <el-button @click="renameDialogVisible=false">
        取消
      </el-button>
    </el-dialog>
  </el-main>
</template>

<script>
export default {
  name: 'EntryEditorIndex',
  data () {
    return {
      entryeditors: [],
      createDialogVisible: false,
      copyDialogVisible: false,
      renameDialogVisible: false,
      newEntryEditorName: '未命名',
      selectedRow: {},
      focusedItem: -1,
      loading: true
    }
  },
  methods: {
    refreshTable: function () {
      this.loading = true
      this.$axios.get('/entryeditor/entryeditor/').then(res => {
        this.entryeditors = res.data
      }).finally(_ => { this.loading = false })
    },
    createEntryEditor: function () {
      this.$axios.post('/entryeditor/entryeditor/', {'name': this.newEntryEditorName}).then(res => {
        this.$message.success('笔记本创建成功')
        this.createDialogVisible = false
        this.refreshTable()
      })
    },
    deleteEntryEditor: function (row) {
      this.$confirm('确认删除？', {type: 'warning'}).then(_ => {
        this.$axios.delete('/entryeditor/entryeditor/' + row.id + '/').then(res => {
          this.$message.success('笔记本删除成功')
          this.refreshTable()
        })
      })
    },
    onClickRenameButton: function (row) {
      this.selectedRow = row
      this.newEntryEditorName = row.name
      this.renameDialogVisible = true
    },
    renameEntryEditor: function () {
      this.$axios.patch('/entryeditor/entryeditor/' + this.selectedRow.id + '/', {'name': this.newEntryEditorName}).then(res => {
        this.$message.success('笔记本重命名成功')
        this.renameDialogVisible = false
        this.refreshTable()
      })
    },
    changePublic: function (id, status) {
      this.$axios.patch('/entryeditor/entryeditor/' + id + '/', {'is_public': status}).then(res => {
      })
    }
  },
  mounted () {
    this.refreshTable()
  }
}
</script>

<style scoped>
  .menu-bar {
    border: 3px;
    background-color: lightgrey;
  }
  .text-button {
    padding: 0;
    margin: 0;
  }
</style>
