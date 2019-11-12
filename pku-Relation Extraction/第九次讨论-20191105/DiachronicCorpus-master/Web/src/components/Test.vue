<template>
  <el-container>
    <el-aside width="200px">Aside</el-aside>
    <el-main>
      <div ref="d3div">
        <h3></h3>
      </div>
      <el-button @click="running = !running"><span v-if="running">暂停</span><span v-else>播放</span></el-button>
      <svg class="d3svg" :width="width" :height="height">
        <text :dx="width / 2 - word.length * 20 / 2" :dy="height / 2">{{ word }}</text>
        <transition-group tag="g" name="list">
          <g class="node" v-for="(node, index) in nodes" :key="index">
            <text :dx="node.x" :dy="node.y" :style="node.style">{{ node.text }}</text>
          </g>
        </transition-group>
      </svg>
    </el-main>
  </el-container>
</template>

<script>
import * as d3 from 'd3'

export default {
  components: {
  },
  name: 'test',
  props: [],
  data () {
    return {
      word: '测试',
      data: [
        [{token: '词语1', npmi: 0.2}, {token: '词语2', npmi: 0.6}, {token: '词语3', npmi: 0.5}]
      ],
      years: [
        1980
      ],
      links: [
        [{source: '词语1', target: '词语2', distance: 0.4},
          {source: '词语1', target: '词语3', distance: 0.1},
          {source: '词语2', target: '词语1', distance: 0.4},
          {source: '词语3', target: '词语1', distance: 0.1}]
      ],
      MAX_DATA_LEN: 30,
      width: 800,
      height: 600,
      alphaTarget: 0.3,
      fontSize: 14,
      historyPos: {},
      index: 0,
      simulation: '',
      running: true,
      job_id: 0
    }
  },
  watch: {
    running: function () {
      if (this.running) {
        this.job_id = setInterval(this.showNewWords, 4000)
      } else {
        clearInterval(this.job_id)
      }
    }
  },
  mounted () {
    window.vue = this
    this.$axios.get('static/test.json')
      .then(r => {
        this.word = '运动'
        this.data = r.data['data']['cloud_data']['data']
        this.years = r.data['data']['cloud_data']['dates']
        this.links = r.data['data']['cloud_data']['links']
        this.job_id = setInterval(this.showNewWords, 4000)
      })
    // this.showNewWords()
  },
  computed: {
    nodes: function () {
      let words = this.data[this.index]
      let links = this.links[this.index]
      let npmis = words.map(d => d.npmi)
      let rScale = d3.scaleLinear().domain([d3.min(npmis), d3.max(npmis)]).range([this.width / 2 * 0.7, 100])
      let simulation = d3.forceSimulation().alpha(this.alphaTarget)
        .force('charge', d3.forceManyBody())
        // .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(this.fontSize))
        .force('radial', d3.forceRadial(d => rScale(d.npmi), this.width / 2, this.height / 2).strength(0.2))
        .stop()
      simulation.nodes(words)
        .force('link', d3.forceLink(links).id(d => d.token).distance(d => d.distance * 5).strength(0.3))
      let coorFunc = (d, i) => this.calcCoor({x: this.width / 2, y: this.height / 2}, i * 360 / this.MAX_DATA_LEN, rScale(d.npmi))
      for (let i = 0, n = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay())); i < n; ++i) {
        simulation.tick()
      }
      // eslint-disable-next-line vue/no-side-effects-in-computed-properties
      words.map((d) => { this.historyPos[d.token] = {x: d.x, y: d.y} })
      return words.map((d, i) => {
        let coor = coorFunc(d, i)
        return {
          x: this.historyPos[d.token] ? this.historyPos[d.token].x : coor.x,
          y: this.historyPos[d.token] ? this.historyPos[d.token].y : coor.y,
          text: d.token
        }
      })
    }
  },
  methods: {
    calcCoor (o, theta, r) {
      let rad = theta * 2 * Math.PI / 360
      let x = o.x + Math.sin(rad) * r
      let y = o.y + Math.cos(rad) * r
      return {x: x, y: y}
    },
    // drawer (selector) {
    //   return {
    //     update (words, links) {
    //       texts.enter()
    //         .append('text')
    //         .text(d => d.token)
    //         .attr('font-size', fontSize)
    //         .attr('x', 0)
    //         .attr('y', d => d.y)
    //         .style('fill-opacity', 1e-6)
    //         .transition()
    //         .duration(3000)
    //         .attr('x', d => d.x - d.token.length * fontSize / 2)
    //         .style('fill-opacity', 1)
    //
    //       texts
    //         .transition()
    //         .duration(3000)
    //         .attr('x', d => d.x - d.token.length * fontSize / 2)
    //         .attr('y', d => d.y)
    //
    //       words.map((d) => { historyPos[d.token] = {x: d.x, y: d.y} })
    //
    //       texts.exit()
    //         .transition()
    //         .duration(3000)
    //         .attr('x', width)
    //         .style('fill-opacity', 1e-6)
    //         .remove()
    //         .each((d) => { delete historyPos[d.token] })
    //     }
    //   }
    // },
    showNewWords () {
    //   this.div.select('h3').text(this.years[this.index])
    //   this.svg.update(this.data[this.index], this.links[this.index])
      this.index = (this.index + 1) % this.data.length
    }
  }
}
</script>

<style scoped>
  .list-enter-active, .list-leave-active {
    transition: all 1s;
  }
  .list-enter, .list-leave-to /* .list-leave-active for <2.1.8 */ {
    opacity: 0;
    x: 0;
  }
</style>
