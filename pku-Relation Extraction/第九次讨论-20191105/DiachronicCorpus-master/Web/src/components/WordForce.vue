<template>
    <div>
      <div ref="d3div">
        <h3></h3>
      </div>
      <el-button @click="running = !running"><span v-if="running">暂停</span><span v-else>播放</span></el-button>
      <svg class="d3svg" ref="d3svg">
        <text></text>
      </svg>
    </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  components: {
  },
  name: 'WordForce',
  props: ['word', 'data', 'years', 'links'],
  data () {
    return {
      MAX_DATA_LEN: 30,
      width: 800,
      height: 600,
      index: 0,
      svg: '',
      div: '',
      running: false,
      jobs: []
    }
  },
  watch: {
    data: function () {
      this.running = false
      this.svg = this.drawer(this.$refs.d3svg)
      this.div = d3.select(this.$refs.d3div)
      this.running = true
    },
    running: function () {
      if (this.running) {
        this.jobs.push(setInterval(this.showNewWords, 4000))
      } else {
        this.jobs.forEach(clearInterval)
        this.jobs = []
      }
    }
  },
  mounted () {
  },
  methods: {
    drawer (selector) {
      let svg = d3.select(selector).attr('width', this.width + 'px').attr('height', this.height + 'px')
      let width = this.width
      let height = this.height
      let MAX_DATA_LEN = this.MAX_DATA_LEN
      let historyPos = {}
      let alphaTarget = 0.3
      let that = this
      let fontSize = 14

      svg.select('text').text(this.word)
        .style('font-size', '20px')
        .attr('x', width / 2 - this.word.length * 20 / 2).attr('y', height / 2)
      svg.append('g')

      let calcCoor = function (o, theta, r) {
        let rad = theta * 2 * Math.PI / 360
        let x = o.x + Math.sin(rad) * r
        let y = o.y + Math.cos(rad) * r
        return {x: x, y: y}
      }

      return {
        update (words, links) {
          let npmis = words.map(d => d.npmi)
          let rScale = d3.scaleLinear().domain([d3.min(npmis), d3.max(npmis)]).range([width / 2 * 0.7, 100])
          let coorFunc = (d, i) => calcCoor({x: width / 2, y: height / 2}, i * 360 / MAX_DATA_LEN, rScale(d.npmi))

          let simulation = d3.forceSimulation().alpha(alphaTarget)
            .force('charge', d3.forceManyBody())
            // .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(fontSize))
            .force('radial', d3.forceRadial(d => rScale(d.npmi), width / 2, height / 2).strength(0.2))

          let texts = svg.select('g').selectAll('g text').data(words, d => d.token)
          let lines = svg.select('g').selectAll('g line').data(links, d => d.source + d.target)

          function dragstarted (d) {
            that.running = false
            if (!d3.event.active) simulation.alphaTarget(alphaTarget).restart()
            d.fx = d.x
            d.fy = d.y
          }

          function dragged (d) {
            d.fx = d3.event.x
            d.fy = d3.event.y
          }

          function dragended (d) {
            // that.running = true
            if (!d3.event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
            svg.append('circle')
              .attr('cx', width / 2).attr('cy', height / 2)
              .attr('r', rScale(d.npmi))
              .style('fill', 'none')
              .style('stroke', 'steelblue')
              .style('opacity', 0.5)
              .transition()
              .duration(300)
              .style('stroke', 'white')
              .style('stroke-width', '5')
              .transition()
              .duration(300)
              .style('stroke', 'steelblue')
              .style('stroke-width', '1')
              .transition()
              .duration(200)
              .style('opacity', 0)
              .remove()
          }

          words.map(function (d, i) {
            if (historyPos[d.token]) {
              d.x = historyPos[d.token].x
              d.y = historyPos[d.token].y
            } else {
              let coor = coorFunc(d, i)
              d.x = coor.x
              d.y = coor.y
            }
          })

          let textEnter = texts.enter()
            .append('text')
            .text(d => d.token)
            .attr('font-size', fontSize)
            .attr('x', d => d.x)
            .attr('y', d => d.y)
            .style('fill-opacity', 1e-6)
            .transition()
            .duration(1000)
            .style('fill-opacity', 1)

          let linesEnter = lines.enter()
            .append('line')
            .attr('stroke-width', (d) => d.distance * 5)
            .attr('stroke', '#999')
            .attr('stroke-opacity', 1e-6)
            .transition()
            .duration(1000)
            .attr('stroke-opacity', 0.6)

          texts.merge(textEnter)
            .call(d3.drag()
              .on('start', dragstarted)
              .on('drag', dragged)
              .on('end', dragended))

          simulation.nodes(words)
            .force('link', d3.forceLink(links).id(d => d.token).distance(d => d.distance * 5).strength(0.1))
            .on('tick', function ticked () {
              texts.merge(textEnter)
                .attr('x', (d) => d.x - d.token.length * fontSize / 2)
                .attr('y', (d) => d.y)
              lines.merge(linesEnter)
                .attr('x1', (d) => d.source.x)
                .attr('y1', (d) => d.source.y)
                .attr('x2', (d) => d.target.x)
                .attr('y2', (d) => d.target.y)
              words.map((d) => { historyPos[d.token] = {x: d.x, y: d.y} })
            })

          texts.exit()
            .transition()
            .duration(1000)
            .style('fill-opacity', 1e-6)
            .remove()
            .each((d) => { delete historyPos[d.token] })

          lines.exit().remove()
        }
      }
    },
    showNewWords (index = -1) {
      if (index === -1) {
        this.div.select('h3').text(this.years[this.index])
        this.svg.update(this.data[this.index], this.links[this.index])
        this.index = (this.index + 1) % this.data.length
      } else {
        this.index = index
        this.div.select('h3').text(this.years[this.index])
        this.svg.update(this.data[this.index], this.links[this.index])
      }
    }
  }
}
</script>

<style scoped>
.radius_circle circle {
  fill: none;
  stroke: red;
}
</style>
