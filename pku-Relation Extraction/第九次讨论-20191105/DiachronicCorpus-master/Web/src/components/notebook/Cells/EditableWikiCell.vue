<template>
  <div>
    <el-row class="input-block">
      <el-col class="wiki-setting-block" :offset="1" :span="21" style="padding: 10px; border: 1px solid grey">
        <el-form>
          <el-form-item>从变量<input v-model="cellData.in.from" size="mini" style="width:40px"/>中<el-button type="text" @click="refreshData">读入</el-button></el-form-item>
          <el-form-item>向变量<input v-model="cellData.in.to" size="mini" style="width:40px"/>中<el-button type="text" @click="saveData">保存</el-button>
            <el-switch v-model="cellData.in.autoSave"
                       active-text="自动保存"
            ></el-switch>
            <el-tooltip placement="top">
              <div slot="content">这里的自动保存指将修改后的wiki内容自动上传到前面填写的变量名中。<br>不会自动保存记事本本身。</div>
              <i class="el-icon-question"></i>
            </el-tooltip>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
    <el-row v-if="cellData.out.type==='String'">
      <el-col :offset="1" :span="21" style="padding: 10px;">
        <span>{{cellData.out.detail}}</span>
      </el-col>
    </el-row>
    <el-row class="output-block" v-if="cellData.out.type==='Wiki'">
      <el-col :offset="1" :span="21" style="padding: 10px;">
        <h2 style="font-family: Kai,serif">{{cellData.out.data['word']}}：</h2>
        <div v-for="(sense, sense_key) in cellData.out.data['senses']" :key="sense_key">
          <h2>Sense {{sense['sense_id']}}</h2>
          <h3>释义：</h3>
          <el-input v-model="sense['sense']"/>
          <h3>近义词：</h3>
          <ul>
            <li v-for="(value, key) in sense['synonyms']" :key="key">
              <input v-model="value['word']"/>
              <i class="el-icon-close" style="color: grey;" @click="deleteSynonym(sense_key, key)"></i>
              <i class="el-icon-plus" style="color: grey;" @click="insertSynonym(sense_key, key)"></i>
            </li>
          </ul>
          <h3>例句：</h3>
          <div v-for="(value1, key1) in sense['examples']" :key="key1">
            <h4>{{value1['year']}}</h4>
            <ul>
              <li v-for="(value2, key2) in value1['sentences']" :key="key2">
                <el-input v-model="value1['sentences'][key2]"
                          :autosize="{ minRows: 1}">
                  <template slot="append">
                    <i class="el-icon-close" style="color: grey;" @click="deleteExample(sense_key, key1, key2)"></i>
                    <i class="el-icon-plus" style="color: grey;" @click="insertExample(sense_key, key1, key2)"></i>
                  </template>
                </el-input>
              </li>
            </ul>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'EditableWikiCell',
  props: ['cellData', 'kernelId'],
  watch: {
    outData: {
      handler: function (newVal, oldVal) {
        if (this.cellData.in.autoSave) {
          this.saveData()
        }
      },
      deep: true
    }
  },
  computed: {
    outData () {
      return this.cellData.out
    }
  },
  data () {
    return {
    }
  },
  methods: {
    refreshData: function () {
      this.$confirm('当前单元格的内容将被变量' + this.cellData.in.from + '保存的内容替换。', {'type': 'warning'}).then(res => {
        this.$utils.post('/kernel/get_wiki/', {}, {
          'kernel_id': this.kernelId,
          'name': this.cellData.in.from
        }, res => {
          this.cellData.out = res.data
        }, err => {
          this.cellData.out = err.response.data
        })
      })
    },
    saveData: function () {
      if (this.cellData.in.to === '') {
        this.$message.warning('未填写保存目标的变量名。')
        return
      }
      this.$utils.post('/kernel/save_wiki/', {}, {
        'kernel_id': this.kernelId,
        'name': this.cellData.in.to,
        'data': this.cellData.out
      }, res => {
        this.$message.success('变量' + this.cellData.in.to + '上传成功')
      })
    },
    deleteSynonym: function (senseKey, key) {
      this.cellData.out.data.senses[senseKey].synonyms.splice(key, 1)
    },
    insertSynonym: function (senseKey, key) {
      this.cellData.out.data.senses[senseKey].synonyms.splice(key + 1, 0, {
        'word': '',
        'similarity': 1.0
      })
    },
    deleteExample: function (senseKey, key1, key2) {
      this.cellData.out.data.senses[senseKey].examples[key1]['sentences'].splice(key2, 1)
    },
    insertExample: function (senseKey, key1, key2) {
      this.cellData.out.data.senses[senseKey].examples[key1]['sentences'].splice(key2 + 1, 0, '')
    }
  }
}
</script>

<style scoped>
  .highlight {
    color: red;
    padding: 0 0 0 3px;
  }
  .el-form-item {
    line-height: 0;
    margin-bottom: 0;
  }
</style>
