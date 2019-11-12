<template>
  <div>
    <h3>npmi环绕式布局</h3>
    <div class="help">
      <p>画布中央是中心词。</p>
      <p>周围的词语距离中心词越近，说明pmi值越高。</p>
      <p>因为词语的顺序是根据pmi排序的，所以在第一年中，周边的词应该是成螺旋线向外扩散的。</p>
      <p>但是在后续的年份中，为了保证同一个词所在的角度不变，螺旋线中间会出现间断点。</p>
    </div>
    <div ref="d3div">
      <h3></h3>
    </div>
    <svg class="d3svg" ref="d3svg"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3'
import * as d3ease from 'd3-ease'

export default {
  components: {
  },
  name: 'WordCircle',
  props: ['word', 'data', 'years'],
  data () {
    return {
      MAX_DATA_LEN: 30,
      width: 800,
      height: 600,
      index: 0,
      svg: '',
      div: '',
      running: false
    }
  },
  watch: {
    data: function () {
      this.svg = this.drawer(this.$refs.d3svg)
      this.div = d3.select(this.$refs.d3div)
      if (!this.running) {
        this.running = true
        this.showNewWords()
      }
    }
  },
  mounted () {
  },
  methods: {
    drawer (selector) {
      let svg = d3.select(selector).attr('width', this.width + 'px').attr('height', this.height + 'px')
      svg.selectAll('*').remove()
      let width = this.width
      let height = this.height
      let MAX_DATA_LEN = this.MAX_DATA_LEN
      let token2slot = {}
      let slot2token = {}

      svg.append('text').text(this.word)
        .style('font-size', '20px')
        .attr('x', this.width / 2).attr('y', this.height / 2)
      svg = svg.append('g')

      let calcCoor = function (o, theta, r) {
        let rad = theta * 2 * Math.PI / 360
        let x = o.x + Math.sin(rad) * r
        let y = o.y + Math.cos(rad) * r
        return {x: x, y: y}
      }

      let assignSlot = function (token) {
        if (token2slot[token]) { return token2slot[token] } else {
          for (let i = 0; i < MAX_DATA_LEN; i++) {
            if (!slot2token[i]) {
              slot2token[i] = token
              token2slot[token] = i
              return i
            }
          }
        }
      }

      return {
        update (words) {
          let tokens = new Set(words.map(d => d.token))
          let npmis = words.map(d => d.npmi)
          for (let token in token2slot) {
            if (!tokens.has(token)) {
              slot2token[token2slot[token]] = null
              token2slot[token] = null
            }
          }

          let rScale = d3.scaleLinear().domain([d3.min(npmis), d3.max(npmis)]).range([width / 2 * 0.7, 100])

          let texts = svg.selectAll('g text').data(words, d => d.token)
          let coorFunc = (d, i) => calcCoor({x: width / 2, y: height / 2}, assignSlot(d.token) * 360 / MAX_DATA_LEN, rScale(d.npmi))

          texts.enter()
            .append('text').text(d => d.token)
            .attr('x', (d, i) => coorFunc(d, i).x)
            .attr('y', (d, i) => coorFunc(d, i).y)
            .style('fill-opacity', 1e-6)
            .attr('font-size', d => 20)
            .transition()
            .duration(2000)
            .style('fill-opacity', 1)

          texts
            .transition()
            .duration(4000)
            .ease(d3ease.easeLinear)
            .attr('font-size', d => 20)
            .attr('x', (d, i) => coorFunc(d, i).x)
            .attr('y', (d, i) => coorFunc(d, i).y)

          texts.exit()
            .transition()
            .duration(2000)
            .style('fill-opacity', 1e-6)
            .remove()
        }
      }
    },
    showNewWords () {
      this.index = (this.index + 1) % this.data.length
      this.div.select('h3').text(this.years[this.index])
      this.svg.update(this.data[this.index])
      if (this.running) { setTimeout(() => { this.showNewWords() }, 4000) }
    }
  }
}
</script>

<style scoped>

</style>
