<template>
  <div>
    <h3>npmi词云</h3>
    <div class="help">
      <p>文字的大小表示npmi的绝对大小，颜色深度表示当年与前一年npmi的差异。</p>
      <p>也就是说，文字颜色越深，越是表示这个词在这一年突然出现的搭配。</p>
    </div>
    <h3>{{ date }}</h3>
    <svg class="word-cloud" ref="wordCloud"></svg>
<!--    <el-button @click="handler()"><span v-if="running">暂停</span><span v-else>播放</span></el-button>-->
  </div>
</template>

<script>
import * as d3 from 'd3'
import * as d3cloud from 'd3-cloud'
export default {
  name: 'word-cloud',
  props: ['cloud_data', 'index'],
  data () {
    return {
      running: false
    }
  },
  watch: {
    index: function () {
      this.word_cloud.update(this.cloud_data['data'][this.index])
    }
  },
  methods: {
    wordCloud (selector) {
      // let fill = d3.scale.category20();
      let fill = d3.scaleLinear()
        .domain([0, 1, 2, 3, 4, 5, 6, 10, 15, 20, 100])
        .range(['#ddd', '#ccc', '#bbb', '#aaa', '#999', '#888', '#777', '#666', '#555', '#444', '#333', '#222'])

      // Construct the word cloud's SVG element
      let svg = d3.select(selector)
        .attr('width', 500)
        .attr('height', 500)
        .append('g')
        .attr('transform', 'translate(250,250)')

      // Draw the word cloud
      function draw (words) {
        let cloud = svg.selectAll('g text')
          .data(words, function (d) { return d.token })

        // Entering words
        cloud.enter()
          .append('text')
          .style('font-family', 'Impact')
          // .style('fill', function (d, i) { return fill(d.diff * 100) })
          .attr('text-anchor', 'middle')
          .attr('font-size', 1)
          .text(function (d) { return d.token })
          .transition()
          .duration(2000)
          .attr('transform', function (d) {
            return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')'
          })
          .style('font-size', function (d) { return d.size + 'px' })

        // Entering and existing words
        cloud
          .transition()
          .duration(2000)
          .style('font-size', function (d) { return d.size + 'px' })
          .attr('transform', function (d) {
            return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')'
          })
          .style('fill-opacity', 1)
          .style('fill', function (d, i) { return fill(d.diff * 100) })

        // Exiting words
        cloud.exit()
          .transition()
          .duration(1000)
          .style('fill-opacity', 1e-6)
          .attr('font-size', 1)
          .remove()
      }

      // Use the module pattern to encapsulate the visualisation code. We'll
      // expose only the parts that need to be public.
      return {

        // Recompute the word cloud for a new set of words. This method will
        // asycnhronously call draw when the layout has been computed.
        // The outside world will need to call this function, so make it part
        // of the wordCloud return value.
        update: function (words) {
          d3cloud().size([500, 500])
            .words(words)
            .padding(5)
            // .rotate(function () { return ~~(Math.random() * 2) * 90 })
            .rotate(function () { return 0 })
            .font('Impact')
            .fontSize(function (d) { return (d.npmi - 0.4) * 200 })
            .on('end', draw)
            .start()
        }
      }
    }
  },
  computed: {
    date: function () {
      return this.cloud_data['dates'][this.index]
    }
  },
  mounted () {
    this.word_cloud = this.wordCloud(this.$refs.wordCloud)
  }
}
</script>

<style scoped>

</style>
