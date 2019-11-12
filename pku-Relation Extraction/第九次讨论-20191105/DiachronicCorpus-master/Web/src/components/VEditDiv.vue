<template>
  <div ref="editable"
       contenteditable
       v-on="listeners"></div>
</template>
<script>
export default {
  name: 'VEditDiv',
  props: ['value'],
  computed: {
    listeners () {
      return { ...this.$listeners, input: this.onInput }
    }
  },
  mounted () {
    this.$refs.editable.innerText = this.value
  },
  methods: {
    onInput (e) {
      this.$emit('input', e.target.innerText)
    }
  }
}
</script>

<style scoped>

</style>
