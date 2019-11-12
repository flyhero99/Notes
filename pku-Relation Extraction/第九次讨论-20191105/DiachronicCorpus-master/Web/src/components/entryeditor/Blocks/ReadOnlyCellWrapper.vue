<template>
  <div>
    <div v-if="content.type==='Title'">
      <title-cell :blockData="content" :activated="activated" :editable="false"></title-cell>
    </div>
    <div v-else-if="content.type==='EditableText'">
      <div style="font-size: 16px; margin: 10px">{{content.out}}</div>
    </div>
    <div v-else-if="content.type==='Code'">
      <code-block :blockData.sync="content" :activated="activated" :kernelId="kernelId" :editable="false"></code-block>
    </div>
  </div>
</template>

<script>
import CodeBlock from './CodeBlock'
import TitleCell from '../Cells/TitleCell'

export default {
  name: 'ReadOnlyCellWrapper',
  props: ['content', 'activated', 'kernelId'],
  components: {CodeBlock, TitleCell}
}
</script>

<style scoped>

</style>
