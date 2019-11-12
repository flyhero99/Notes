<template>
  <div>
    <el-form :inline="true" v-show="activated && editable">
      <el-form-item label="标题级别">
        <el-input-number v-model="blockData.style['level']"
                         size="mini" controls-position="right"
                         :min="1" :max="5" @change="onChangeLevel"></el-input-number>
      </el-form-item>
      <el-form-item label="字号"><el-input v-model="blockData.style['font-size']" size="small"></el-input></el-form-item>
      <el-form-item label="字体风格">
        <el-select v-model="blockData.style['font-style']" size="small">
          <el-option label="正常" value="normal"></el-option>
          <el-option label="斜体" value="italic"></el-option>
          <el-option label="倾斜" value="oblique"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="字体粗细">
        <el-select v-model="blockData.style['font-weight']" size="small">
          <el-option label="正常" value="normal"></el-option>
          <el-option label="粗体" value="bold"></el-option>
          <el-option label="更粗" value="bolder"></el-option>
          <el-option label="更细" value="lighter"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <v-edit-div v-if="editable" class='title' :style="blockData.style" v-model="blockData.out"></v-edit-div>
    <div v-else class='title' :style="blockData.style">{{blockData.out}}</div>
  </div>
</template>

<script>
import VEditDiv from '../../VEditDiv'

export default {
  name: 'TitleCell',
  props: ['blockData', 'activated', 'editable'],
  components: {VEditDiv},
  methods: {
    onChangeLevel: function (level) {
      const DEFAULT_FONT_SIZE = [null, '24px', '20px', '18px', '16px', '16px']
      const DEFAULT_FONT_STYLE = [null, 'normal', 'italic', 'italic', 'italic', 'italic']
      const DEFAULT_FONT_WEIGHT = [null, 'normal', 'normal', 'normal', 'bold', 'bold']
      this.blockData.style['font-size'] = DEFAULT_FONT_SIZE[level]
      this.blockData.style['font-style'] = DEFAULT_FONT_STYLE[level]
      this.blockData.style['font-weight'] = DEFAULT_FONT_WEIGHT[level]
    }
  }
}
</script>

<style scoped>
  .title {
    margin-top: 0;
    margin-bottom: 0;
    display: block;
    font-size: 1.5em;
    -webkit-margin-start: 0px;
    -webkit-margin-end: 0px;
  }
  .el-form-item {
    margin-bottom: 3px;
  }
</style>
