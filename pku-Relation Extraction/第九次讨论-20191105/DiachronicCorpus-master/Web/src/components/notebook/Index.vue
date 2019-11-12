<template>
  <el-main>
    <h1>Notebook</h1>
    <el-button @click="createDialogVisible=true" size="small">新建</el-button>
    <el-table
      :data="notebooks">
      <el-table-column
        label="running"
        prop="running">
        <template slot-scope="scope">
          <i class="el-icon-success" v-if="scope.row.running" style="color: green;">运行中</i>
          <i class="el-icon-error" v-else style="color: grey;">未运行</i>
        </template>
      </el-table-column>
      <el-table-column
        label="笔记本名称"
        prop="name">
      </el-table-column>
      <el-table-column
        label="创建于"
        prop="created_at">
      </el-table-column>
      <el-table-column
        label="修改于"
        prop="updated_at">
      </el-table-column>
      <el-table-column label="操作" width="300">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="primary"
            @click="$router.push(scope.row.id.toString())">打开</el-button>
          <el-button
            size="mini"
            @click="onClickRenameButton(scope.row)">重命名</el-button>
          <el-button
            size="mini"
            type="danger"
            @click="deleteNotebook(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
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
      title="重命名笔记本"
      :visible.sync="renameDialogVisible">
      <el-form>
        <el-form-item label="目标笔记本名称">
          <el-input v-model="newNotebookName"></el-input>
        </el-form-item>
      </el-form>
      <el-button @click="renameNotebook" type="primary">
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
  name: 'notebookIndex',
  data () {
    return {
      notebooks: [],
      createDialogVisible: false,
      copyDialogVisible: false,
      renameDialogVisible: false,
      newNotebookName: '未命名',
      selectedRow: ''
    }
  },
  methods: {
    refreshTable: function () {
      this.$axios.get('/entryeditor/notebook/').then(res => {
        this.notebooks = res.data
      })
    },
    createNotebook: function () {
      this.$axios.post('/entryeditor/notebook/', {'name': this.newNotebookName}).then(res => {
        this.$message.success('笔记本创建成功')
        this.createDialogVisible = false
        this.refreshTable()
      })
    },
    deleteNotebook: function (row) {
      this.$confirm('确认删除？', {type: 'warning'}).then(_ => {
        this.$axios.delete('/entryeditor/notebook/' + row.id + '/').then(res => {
          this.$message.success('笔记本删除成功')
          this.refreshTable()
        })
      })
    },
    onClickRenameButton: function (row) {
      this.selectedRow = row
      this.newNotebookName = row.name
      this.renameDialogVisible = true
    },
    renameNotebook: function () {
      this.$axios.patch('/entryeditor/notebook/' + this.selectedRow.id + '/', {'name': this.newNotebookName}).then(res => {
        this.$message.success('笔记本重命名成功')
        this.renameDialogVisible = false
        this.refreshTable()
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
</style>
