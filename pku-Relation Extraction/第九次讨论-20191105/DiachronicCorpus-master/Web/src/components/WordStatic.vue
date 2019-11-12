<template>
  <div>
    <div>
      <h3>
        {{ years ? years[index] : '' }}
      </h3>
    </div>
    <!--<el-button @click="running = !running"><span v-if="running">暂停</span><span v-else>播放</span></el-button>-->
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
  name: 'WordStatic',
  props: ['word', 'data', 'years', 'links', 'index', 'width', 'height', 'highlight'],
  data () {
    return {
      MAX_DATA_LEN: 30,
      svg: '',
      running: false,
      jobs: []
    }
  },
  watch: {
    data: function () {
      this.svg = this.drawer(this.$refs.d3svg)
      this.showNewWords(this.index)
    },
    index: function () {
      this.showNewWords(this.index)
    },
    running: function () {
      if (this.running) {
        this.jobs.push(setInterval(this.showNewWords, 4000))
      } else {
        this.jobs.forEach(clearInterval)
        this.jobs = []
      }
    },
    highlight: function (val, oldVal) {
      if (val !== '') {
        d3.select('#' + val).style('fill', 'red')
      }
      if (oldVal !== '') {
        d3.select('#' + oldVal).style('fill', null)
      }
    }
  },
  methods: {
    drawer (selector) {
      let svg = d3.select(selector).attr('width', this.width + 'px').attr('height', this.height + 'px')
      let width = this.width
      let height = this.height
      let MAX_DATA_LEN = this.MAX_DATA_LEN
      let historyPos = {}
      let alphaTarget = 0.3
      let fontSize = 14

      svg.select('text').text(this.word)
        .style('font-size', '20px')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
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
          let rScale = d3.scaleLinear().domain([d3.min(npmis), d3.max(npmis)]).range([width / 2 * 0.65, 30])
          let coorFunc = (d, i) => calcCoor({x: width / 2, y: height / 2}, i * 360 / MAX_DATA_LEN, rScale(d.npmi))

          let simulation = d3.forceSimulation().alpha(alphaTarget)
            .force('charge', d3.forceManyBody())
            // .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(fontSize))
            .force('radial', d3.forceRadial(d => rScale(d.npmi), width / 2, height / 2).strength(0.2))
            .stop()

          let texts = svg.select('g').selectAll('g text').data(words, d => d.token)
          let lines = svg.select('g').selectAll('g line').data(links, d => d.source + d.target)

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

          simulation.nodes(words)
            .force('link', d3.forceLink(links).id(d => d.token).distance(d => d.distance * 5).strength(0.3))

          for (let i = 0, n = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay())); i < n; ++i) {
            simulation.tick()
          }

          let linesEnter = lines.enter()
            .append('line')
            .attr('stroke-width', (d) => d.distance * 5)
            .attr('stroke', '#999')
            .attr('stroke-opacity', 1e-6)
            .attr('x1', (d) => d.source.x)
            .attr('y1', (d) => d.source.y)
            .attr('x2', (d) => d.target.x)
            .attr('y2', (d) => d.target.y)
            .transition()
            .duration(3000)
            .attr('stroke-opacity', 1e-6)
            .transition()
            .duration(1000)
            .attr('stroke-opacity', 0.6)

          lines
            .transition()
            .duration(3000)
            .attr('x1', (d) => d.source.x)
            .attr('y1', (d) => d.source.y)
            .attr('x2', (d) => d.target.x)
            .attr('y2', (d) => d.target.y)

          lines.merge(linesEnter).on('mouseover', (d, i) => {
            // console.log(this)
            // svg.append('text')
            //   .attr('id', 't' + d.source.token + '-' + d.target.token + '-' + i)
            //   .attr('x', 100)
            //   .attr('y', 100)
            //   .text(d.distance)
          })
          //
          lines.merge(linesEnter).on('mouseout', (d, i) => {
            // d3.select('#t' + d.source.token + '-' + d.target.token + '-' + i).remove()
          })

          let textsEnter = texts.enter()
            .append('text')
            .text(d => d.token)
            .attr('font-size', fontSize)
            .attr('text-anchor', 'middle')
            .attr('x', 0)
            .attr('y', d => d.y)
            .attr('id', d => d.token)
            .style('fill-opacity', 1e-6)
            .transition()
            .duration(3000)
            .attr('x', d => d.x)
            .style('fill-opacity', 1)

          texts
            .style('fill-opacity', 1)
            .transition()
            .duration(3000)
            .attr('x', d => d.x)
            .attr('y', d => d.y)

          texts.merge(textsEnter).on('mouseover', (d, i) => {
            d3.select('#' + d.token).style('fill', 'white')
            let tooltip = d3.select('#t' + d.token)
            if (tooltip.empty()) {
              tooltip = svg.append('text')
                .attr('id', 't' + d.token)
                .attr('x', d.x)
                .attr('y', d.y - fontSize)
                .attr('font-size', fontSize)
                .attr('text-anchor', 'middle')
                .style('fill', 'white')
                .text('nPMI: ' + d.npmi)
            }
            let bbox = tooltip.node().getBBox()
            if (d3.select('#r' + d.token).empty()) {
              svg.insert('rect', 'text')
                .attr('id', 'r' + d.token)
                .attr('x', d.x - bbox.width / 2 - 5)
                .attr('y', d.y - bbox.height - fontSize)
                .attr('rx', 10)
                .attr('ry', 10)
                .attr('width', bbox.width + 5 * 2)
                .attr('height', bbox.height + fontSize + 5 * 2)
                .attr('fill', 'black')
                .attr('fill-opacity', 0.4)
                // .on('mouseout', () => {
                //   d3.select('#' + d.token).style('fill', null)
                //   d3.select('#t' + d.token).remove()
                //   d3.select('#r' + d.token).remove()
                // })
            }
          })

          texts.merge(textsEnter).on('mouseout', (d, i) => {
            d3.select('#' + d.token).style('fill', null)
            d3.select('#t' + d.token).remove()
            d3.select('#r' + d.token).remove()
          })

          words.map((d) => {
            historyPos[d.token] = {x: d.x, y: d.y}
          })

          texts.exit()
            .transition()
            .duration(3000)
            .attr('x', width)
            .style('fill-opacity', 1e-6)
            .remove()
            .each((d) => {
              delete historyPos[d.token]
            })

          lines.exit().remove()
        }
      }
    },
    showNewWords (index = -1) {
      if (index === -1) {
        this.svg.update(this.data[this.index], this.links[this.index])
        this.index = (this.index + 1) % this.data.length
      } else {
        this.index = index
        this.svg.update(this.data[this.index], this.links[this.index])
      }
    }
  },
  mounted () {
    window.static = this
    window.d3 = d3
  }
}
</script>

<style scoped>
  .radius_circle circle {
    fill: none;
    stroke: red;
  }
  .line :hover {
    stroke-opacity: 1;
  }
</style>
