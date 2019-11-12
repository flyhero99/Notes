<template>
  <div>
    <h2 style="font-family: Kai,serif">{{data['word']}}：</h2>
    <el-collapse v-model="activeSenseNames">
        <el-collapse-item v-for="(sense, key) in data['senses']" :key="key"
                          :title="'Sense'+sense['sense_id']" :name="key">
          <h3 style="margin: 1px !important;">释义：</h3>
          <span>{{sense['sense']}}</span>
          <h3 style="margin: 1px !important;">近义词：</h3>
          <span v-for="(value, key) in sense['synonyms']" :key="key">{{value['word']}}   </span>
          <h3 style="margin: 1px !important;">例句：</h3>
          <el-button type="text" @click="expandAll(key)">展开全部</el-button>
          <el-button type="text" @click="collapseAll(key)">折叠全部</el-button>
          <el-collapse v-model="activeExampleNames[key]">
            <el-collapse-item v-for="(value, key) in sense['examples']" :key="key"
                              :title="value['year'].toString()" :name="key">
              <ul style="margin: 1px !important; font-size: 14px">
                <li v-for="(value, key) in value['sentences']" :key="key">{{value}}</li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
export default {
  name: 'WikiBlock',
  props: ['data'],
  data: function () {
    return {
      activeSenseNames: [0],
      activeExampleNames: {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        8: [],
        9: []
      }
    }
  },
  methods: {
    expandAll: function (senseKey) {
      console.log(this.activeExampleNames)
      this.activeExampleNames[senseKey] = []
      for (let i = 0; i < this.data['senses'][senseKey]['examples'].length; i++) {
        this.activeExampleNames[senseKey].push(i)
      }
    },
    collapseAll: function (senseKey) {
      this.activeExampleNames[senseKey] = []
    }
  }
}
</script>

<style scoped>
  .highlight {
    color: red;
    padding: 0 0 0 3px;
  }
</style>
