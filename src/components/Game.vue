<script setup>
import Board from './Board.vue'
import Goal from './Goal.vue'
import Permute from '../Permute.js'
import SimpleGraph from '../SimpleGraph.js'
</script>

<script>
export default {
  data() {
    return {
      beads: 0,
      won: false,
      history: [],
      tail: null,
      showTail: false,
      showCross: false,
      focusIsClick: false,
      clickingButton: false,
      spinButtonClicked: false,
      smallSpinButtonClicked: false,
      showOldArrow: false,
      backwardsInLoop: false,
      continuingLoop: false,

      /*
      animation legend:
      0 = static
      1 = animate
      2 = animate alternate
      */
      animations: new Uint8Array(0),
      oldBeads: [],

      // trophy state
      trophyAlternate: false,
      oldHole: 0,
      reversed: false,
      trophyPushed: false,
      trophyWasPushed: false,
      justWon: false,
      hasWon: false,
      trophyEnterPaused: false,
      trophyExitPaused: false,
    }
  },
  props: {
    graphId: String,
    state: { beads: Number, history: Array },
    initialTail: Number,
    autofocus: Boolean,
    curvedPaths: Boolean,
    canAnimate: Boolean,
  },
  emits: ['update:won', 'update:state', 'update:tail'],
  computed: {
    graph() {
      return SimpleGraph.fromString(this.graphId)
    },
    size() {
      return SimpleGraph.bytesToNodeCount(this.graph)
    },
    edges() {
      let edges = []
      let [firstA, firstB] = []
      if (this.backwardsInLoop) {
        if (this.oldHole == this.history[1]) {
          firstA = this.history[1]
          firstB = this.history[2]
        } else {
          firstA = this.history[this.history.length - 2]
          firstB = this.history[this.history.length - 3]
        }
        if (firstB < firstA) {
          [firstB, firstA] = [firstA, firstB]
        }
        
        edges.push([firstA, firstB])
      }

      let [secondA, secondB] = this.history
      if (this.history.length >= 2) {
        if (secondB < secondA) {
          [secondB, secondA] = [secondA, secondB]
        }

        edges.push([secondA, secondB])
      }

      if (this.continuingLoop) {
        firstA = this.history[this.history.length - 1]
        firstB = this.history[this.history.length - 2]
        if (firstB < firstA) {
          [firstB, firstA] = [firstA, firstB]
        }
        
        edges.push([firstA, firstB])
      }

      for (let a = 0; a < this.size; a++) {
        for (let b = a + 1; b < this.size; b++) {
          if (
            SimpleGraph.hasEdge(this.graph, a, b) &&
              (a != firstA || b != firstB) &&
              (a != secondA || b != secondB)
          ) {
            edges.push([a, b])
          }
        }
      }

      return edges
    },
    idColors() {
      return [
        [],
        [],
        [4],
        [1, 4],
        [0, 1, 4],
        [0, 1, 3, 4],
        [0, 1, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
      ][this.size]
    },
    colorHex() {
      return [
        "#cacaca",
        "#b51d14",
        "#ddb310",
        "#00b25d",
        "#00beff",
        "#3e59f0", // 4053d3 -> color-mix(in lch, #4d64ff, #0750f4) = #3e59f0
        "#fb49b0",
      ]
    },
    colorIds() {
      let colorIds = new Int8Array(6).fill(-1)
      for (let [id, color] of this.idColors.entries()) {
        colorIds[color] = id
      }

      return colorIds
    },
    hole() {
      return this.history[this.history.length - 1]
    },
    loopEnd() {
      return this.extra.length - 1
    },
    loopStart() {
      let sentinel = this.extra[this.loopEnd]
      for (let i = this.loopEnd - 2; i > 0; i--) {
        if (this.extra[i] == sentinel) {
          return i
        }
      }

      return 0
    },
    activeEnd() {
      return this.history.length - 1
    },
    activeStart() {
      return this.history.length >= 2 &&
        this.hole == this.history[0] && this.tail == this.history[1] && this.showTail ?
        0 : this.loopStart
    },
    deadEnd() {
      let edges = 0
      for (let i = 0; i < this.size; i++) {
        edges += SimpleGraph.hasEdge(this.graph, this.hole, i)
        if (edges > 1) {
          return false
        }
      }

      return true
    },
    reversing() {
      return this.history.length >= 2 &&
        this.tail == this.history[this.history.length - 2]
    },
    nodeXs() {
      let xs = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        xs[i] = 100 * Math.sin(2 * Math.PI * i / this.size)
      }

      return xs
    },
    nodeYs() {
      let ys = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        ys[i] = -100 * Math.cos(2 * Math.PI * i / this.size)
      }

      return ys
    },
    goalAngles() {
      return [
        [],
        [90],
        [80, 100],
        [80, 15, -15],
        [80, 170, 100, 190],
        [80, 15, 105, 255, -15],
        [80, 15, 165, 105, 195, -15],
        [80, 40, 170, 105, 255, 195, -40],
      ]
    },
    goalXs() {
      let xs = new Float64Array(this.size)
      let angles = this.goalAngles[this.size]
      for (let i = 0; i < this.size; i++) {
        xs[i] = this.nodeXs[i] + 30 * Math.sin(angles[i] * Math.PI / 180)
      }

      return xs
    },
    goalYs() {
      let ys = new Float64Array(this.size)
      let angles = this.goalAngles[this.size]
      for (let i = 0; i < this.size; i++) {
        ys[i] = this.nodeYs[i] - 30 * Math.cos(angles[i] * Math.PI / 180)
      }

      return ys
    },
    edgePaths() {
      let controlLength = 30
      let edgePaths = {}
      for (let a = 0; a < this.size; a++) {
        edgePaths[[a, a].toString()] = `M ${this.nodeXs[a]} ${this.nodeYs[a]}`
      }

      for (let [baseA, baseB] of this.edges) {
        for (let [a, b] of [[baseA, baseB], [baseB, baseA]]) {
          let name = [a, b].toString()
          let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
          let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
          edgePaths[name] =
              `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2}`
        }
      }

      if (!this.curvedPaths) {
        if (this.showTail && this.tail == this.extra[this.loopStart]) {
          let id = Permute.getValue(this.beads, this.tail) - 1
          let a = this.oldBeads[id]
          if (a != this.hole) {
            let b = this.tail
            let name = [a, b].toString()
            let c = this.hole
            let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
            let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
            let dx3 = this.nodeXs[c] - x2, dy3 = this.nodeYs[c] - y2
            let scale = 0.1 / Math.sqrt(dx3 * dx3 + dy3 * dy3)
            dx3 *= scale
            dy3 *= scale
            edgePaths[name] = 
                `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2} l ${dx3} ${dy3}`
          }
        }

        return edgePaths
      }

      let endTangent = [0, 0]
      if (this.extra[this.loopStart] == this.extra[this.loopEnd]) {
        let a = this.extra[this.loopEnd - 1], b = this.extra[this.loopEnd]
        endTangent = this.getTangent(this.extra[this.loopStart + 1], b, a)
      }

      let lastTangent = [-endTangent[0], -endTangent[1]]
      for (let i = this.loopStart + 1; i <= this.loopEnd; i++) {
        let a = this.extra[i - 1], b = this.extra[i]
        let tangent = endTangent
        if (i < this.loopEnd) {
          tangent = this.getTangent(this.extra[i + 1], b, a)
        }

        let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
        let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
        let [dx1, dy1] = lastTangent, [dx2, dy2] = tangent
        let x0 = x1 + dx1 * controlLength, y0 = y1 + dy1 * controlLength
        let x3 = x2 + dx2 * controlLength, y3 = y2 + dy2 * controlLength
        edgePaths[[a, b].toString()] =
          `M ${x1} ${y1} C ${x0} ${y0}, ${x3} ${y3}, ${x2} ${y2}`
        edgePaths[[b, a].toString()] =
          `M ${x2} ${y2} C ${x3} ${y3}, ${x0} ${y0}, ${x1} ${y1}`
        lastTangent = [-tangent[0], -tangent[1]]
      }

      return edgePaths
    },
    edgeClasses() {
      let edgeClasses = {}
      for (let [a, b] of this.edges) {
        edgeClasses[[a, b].toString()] = {edge: true}
        edgeClasses[[b, a].toString()] = {edge: true}
      }

      for (let i = this.activeStart; i < this.activeEnd; i++) {
        let a = this.history[i], b = this.history[i + 1]
        edgeClasses[[a, b].toString()]['active'] = true
        edgeClasses[[b, a].toString()]['active'] = true
      }

      if (this.showTail) {
        edgeClasses[[this.hole, this.tail].toString()]['arrow'] = true
        edgeClasses[[this.tail, this.hole].toString()]['arrow'] = true
      }

      return edgeClasses
    },
    headRadius() {
      return 12
    },
    headHeight() {
      return this.headRadius * Math.sqrt(1.5)
    },
    headPath() {
      let r = this.headRadius, hr = 0.5 * this.headHeight
      return `M ${hr} ${-r} L ${-hr} ${0} L ${hr} ${r}`
    },
    headShadowWidth() {
      return 12
    },
    edgeStrokeWidth() {
      return 4
    },
    edgeConeRadius() {
      // there is a notch in the back of the arrow head shadow to prevent it
      // from covering the arrow edge. the notch is exactly as wide as the
      // arrow edge where it intersects the arrow, but it gets wider further
      // away from the intersection in case the arrow edge is slightly curved.
      // this value controls the width of the widest part of the notch. it
      // should be larger than 0.5 * edgeStrokeWidth
      return 4
    },
    headShadowPath() {
      let r = this.headRadius, hr = 0.5 * this.headHeight
      let sr = 0.5 * this.headShadowWidth
      let cos = this.headHeight
      let sin = this.headRadius
      let cot = cos / sin
      let scale = sr / Math.sqrt(cos * cos + sin * sin)
      cos *= scale
      sin *= scale
      let er = 0.5 * this.edgeStrokeWidth
      let fr = er // fr is head stroke radius, which happens to be the same as edge stroke radius
      let v = sr / sin // distance from center of arrow head to the concave corner, if the stroke had unit radius
      let cr = this.edgeConeRadius
      return `M ${hr + sin} ${-r + cos} A ${sr} ${sr} 0 0 0 ${hr - sin} ${-r - cos} L ${-hr - sin} ${-cos} A ${sr} ${sr} 0 0 0 ${-hr - sin} ${cos} L ${hr - sin} ${r + cos} A ${sr} ${sr} 0 0 0 ${hr + sin} ${r - cos} L ${-hr + sr * v + cr * cot} ${cr} L ${-hr + fr * v + er * cot} ${er} L ${-hr} ${0} L ${-hr + fr * v + er * cot} ${-er} L ${-hr + sr * v + cr * cot} ${-cr} Z`
    },
    terminatorRadius() {
      return this.curvedPaths ? 28 : 36
    },
    crossRadius() {
      return 18
    },
    crossPath() {
      let d = this.crossRadius * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    arrowPath() {
      return this.edgePaths[[this.hole, this.tail].toString()]
    },
    oldArrowPath() {
      return this.edgePaths[[this.oldHole, this.hole].toString()]
    },
    beadRadius() {
      return 10
    },
    beadHeight() {
      return this.beadRadius * Math.sqrt(3)
    },
    beadClasses() {
      let result = []
      for (let id = 0; id < this.size - 1; id++) {
        let node = Permute.findValue(this.beads, id + 1)
        let historyIndex = this.extra.indexOf(node, this.activeStart)
        result.push(
          {
            bead: true,
            tail: node == this.tail && this.showTail &&
              (node != this.extra[this.loopStart] || this.oldBeads[id] == this.hole),
            onPath: historyIndex >= 0 && historyIndex <= this.activeEnd,
            animate: this.animations[id],
            alternate: this.animations[id] == 2,
            reverse: historyIndex > 0 && this.oldBeads[id] == this.extra[historyIndex - 1],
          }
        )
      }

      return result
    },
    beadOffsetPaths() {
      let result = []
      for (let id = 0; id < this.size - 1; id++) {
        let node = Permute.findValue(this.beads, id + 1)
        let edge =
          node == this.tail && this.showTail &&
            node != this.extra[this.loopStart] ?
          [this.hole, this.tail] :
          [this.oldBeads[id], node]
        let path = this.edgePaths[edge.toString()]
        result.push(`path('${path}')`)
      }

      return result
    },
    trophyExitStart() {
      if (this.reversed) {
        return this.oldHole
      } else if (this.history.length >= 2) {
        return this.history[this.history.length - 2]
      }

      return this.hole
    },
    trophyExitEnd() {
      if (
        this.history.length >= 3 && this.reversed &&
        this.oldHole == this.history[1]
      ) {
        return this.history[2]
      } else if (this.reversed) {
        return this.getIngress(this.oldHole, this.hole)
      } else if (this.history.length >= 3) {
        return this.history[this.history.length - 3]
      } else if (this.history.length >= 2) {
        let center = this.history[this.history.length - 2]
        return this.getIngress(center, this.hole)
      }

      return this.hole
    },
    trophyPushedStart() {
      return this.hole
    },
    trophyPushedEnd() {
      if (this.history.length >= 2) {
        if (this.hole == this.history[0]) {
          if (this.reversing) {
            return this.history[1]
          }

          return this.history[this.history.length - 2]
        } else if (this.reversing) {
          return this.getIngress(this.hole, this.history[this.history.length - 2])
        }

        return this.history[this.history.length - 2]
      }

      return this.getIngress(this.hole, this.tail)
    },
    trophyEnterStart() {
        if (this.reversed) {
        if (this.history.length >= 2) {
          return this.history[this.history.length - 2]
        } else {
          return this.getIngress(this.hole, this.oldHole)
        }
      } else if (this.history.length >= 2) {
        if (this.history[0] == this.hole) {
          return this.history[1]
        }

        let egress = this.history[this.history.length - 2]
        return this.getIngress(this.hole, egress)
      }

      return this.hole
    },
    trophyEnterEnd() {
      return this.hole
    },
    trophyExitPath() {
      let edge = [this.trophyExitStart, this.trophyExitEnd]
      let path = this.edgePaths[edge.toString()]
      return `path('${path}')`
    },
    trophyEnterPath() {
      let edge = this.trophyPushed ?
        [this.trophyPushedStart, this.trophyPushedEnd] :
        [this.trophyEnterStart, this.trophyEnterEnd]
      let path = this.edgePaths[edge.toString()]
      return `path('${path}')`
    },
    trophyExitClasses() {
      return {
        trophy: true,
        reverse: this.reversed,
        wasPushed: this.trophyWasPushed,
        unpaused: !this.trophyExitPaused,
      }
    },
    trophyEnterClasses() {
      return {
        trophy: true,
        enter: true,
        reverse: this.trophyPushed ? this.reversing : this.reversed,
        pushed: this.showTail,
        wasPushed: this.trophyPushed,
        unpaused: !this.trophyEnterPaused,
      }
    },
    normalBeadScale() {
      return 1
    },
    activeBeadScale() {
      return 5/3
    },
    clickRadius() {
      return 42
    },
    spinButtonY() {
      return -15
    },
    smallClickRadius() {
      return 20
    },
    smallSpinButtonY() {
      return this.clickRadius - this.smallClickRadius - this.spinButtonY
    },
    spinPath() {
      return this.getSpinPath(10, 11)
    },
    smallSpinPath() {
      return this.getSpinPath(7, 9)
    },
    extra() {
      // extrapolate history to the future if there's no choice of moves
      if (this.history.length <= 1) {
        return this.showTail ? [this.hole, this.tail] : this.history
      }

      let loop = [...this.history]
      loop.pop()
      let seen = new Set(loop)
      let prev = loop[loop.length - 1]
      let node = this.hole
      while (node >= 0) {
        loop.push(node)
        if (seen.has(node)) {
          break
        }

        let next = this.getForcedTail(prev, node)
        prev = node
        node = next
      }

      if (
        loop.length == this.history.length &&
        !this.reversing &&
        this.showTail
      ) {
        loop.push(this.tail)
      }

      return loop
    },
    canSpin() {
      return this.history.length >= 2 && ( // must be 2 and not 3
        this.hole == this.history[0] || (
          this.extra[this.loopStart] == this.extra[this.loopEnd] && (
            this.extra.length > this.history.length + 1 ||
            this.getForcedTail(
              this.history[this.history.length - 2],
              this.hole,
            ) >= 0
          )
        )
      )
    },
    clockwise() {
      let minA = Infinity, minB = Infinity
      let clockwise = false
      for (let i = this.loopStart; i < this.loopEnd; i++) {
        let node1 = this.extra[i], node2 = this.extra[i + 1]
        let y1 = this.getHeightRank(node1)
        let y2 = this.getHeightRank(node2)
        let minY = Math.min(y1, y2)
        let maxY = Math.max(y1, y2)
        if (minY < minA || (minY == minA && maxY < minB)) {
          minA = minY
          minB = maxY
          let x1 = this.getXRank(node1)
          let x2 = this.getXRank(node2)
          if (y1 < y2) {
            let node0 = this.extra[
              i <= this.loopStart ? this.loopEnd - 1 : i - 1
            ]
            let y0 = this.getHeightRank(node0)
            if (y0 == y2) {
              let x0 = this.getXRank(node0)
              clockwise = x0 < x2
            } else {
              clockwise = x1 < x2
            }
          } else {
            let node3 = this.extra[
              i >= this.loopEnd - 1 ? this.loopStart + 1 : i + 2
            ]
            let y3 = this.getHeightRank(node3)
            if (y3 == y1) {
              let x3 = this.getXRank(node3)
              clockwise = x1 < x3
            } else {
              clockwise = x1 < x2
            }
          }
        }
      }

      return clockwise
    },
  },
  methods: {
    getTangent(i, j, k) {
      let x1 = this.nodeXs[i], y1 = this.nodeYs[i]
      let x2 = this.nodeXs[j], y2 = this.nodeYs[j]
      let x3 = this.nodeXs[k], y3 = this.nodeYs[k]

      let dx1 = x2 - x1, dy1 = y2 - y1
      let len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1)

      let dx2 = x3 - x2, dy2 = y3 - y2
      let len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2)

      let dx3 = dx1 * len2 + dx2 * len1
      let dy3 = dy1 * len2 + dy2 * len1
      let len3 = Math.sqrt(dx3 * dx3 + dy3 * dy3)

      let factor = len3 > 0 ? 1 / len3 : 0
      return [dx3 * factor, dy3 * factor]
    },
    getSpinPath(r, w) {
      let tailAngle = 160, headAngle = -30, sweep = 0, largeArc = 1
      let s = -1 + 2 * sweep
      let x1 = r * Math.sin(tailAngle * Math.PI / 180)
      let y1 = -r * Math.cos(tailAngle * Math.PI / 180)
      let u = Math.sin(headAngle * Math.PI / 180)
      let v = -Math.cos(headAngle * Math.PI / 180)
      let x2 = r * u, y2 = r * v
      let h = w * Math.sqrt(0.375)
      let neck = 4.5
      let nx = s * -neck * v, ny = s * neck * u
      let dx1 = s * (0.5 * w * u + h * v), dy1 = s * (0.5 * w * v - h * u)
      let dx2 = s * (-.5 * w * u + h * v), dy2 = s * (-.5 * w * v - h * u)
      return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} ${sweep} ${x2} ${y2} l ${nx} ${ny} m ${dx1} ${dy1} L ${x2 + nx} ${y2 + ny} l ${dx2} ${dy2}`
    },
    getHeightRank(node) {
      return Math.abs((node + this.size/2) % this.size - this.size/2)
    },
    getForcedTail(prev, hole) {
      let tail = -1
      for (let i = 0; i < this.size; i++) {
        if (i != prev && SimpleGraph.hasEdge(this.graph, hole, i)) {
          if (tail != -1) { return -1 }
          tail = i
        }
      }

      return tail
    },
    getXRank(node) {
      let a = (node + this.size/2) % this.size - this.size/2 // top half
      let b = this.size/2 - node // bottom half
      return Math.abs(a) < Math.abs(b) ? a : b
    },
    goForward() {
      if (this.ensureTail()) {
        if (this.canSpin && !this.won) {
          // continue going around the loop with the tail hidden
          this.showTail = this.won
          this.goForwardHelp()
        }
      } else {
        this.goForwardHelp()
        if (!this.reversed && this.reversing) {
          this.showTail = false // dead end
        }
      }
    },
    goForwardHelp() {
      this.trophyWasPushed = this.showTail
      let id = Permute.getValue(this.beads, this.tail) - 1
      this.beads = Permute.swap(this.beads, this.hole, this.tail)
      this.animations[id] = 1 + this.animations[id] % 2
      this.oldBeads[id] = this.tail
      this.trophyAlternate = !this.trophyAlternate
      this.oldHole = this.hole
      this.reversed = false
      this.showOldArrow = false
      this.backwardsInLoop = false
      this.continuingLoop = false
      if (this.reversing) {
        this.history.pop()
        if (this.history[0] == this.oldHole) {
          // reverse the loop
          this.history.reverse()
          this.history.push(this.history[0])
          this.backwardsInLoop = true
        } else {
          // not a loop
          this.reversed = true
          if (this.history.length >= 2) {
            this.tail = this.history[this.history.length - 2] // keep going back
          } else {
            this.tail = this.oldHole
          }

          return
        }
      } else {
        this.continuingLoop = this.history.length >= 3 &&
          this.oldHole == this.history[0] &&
          this.tail == this.history[1]
        this.history.push(this.tail)
      }

      // remove before loop
      for (let offset = this.history.length - 4; offset >= 0; offset--) {
        if (this.history[offset] == this.hole) {
          this.history = this.history.slice(offset)
          break
        }
      }

      this.tail = this.getNextTail(this.history)
    },
    getNextTail(history) {
      // first choice: continue the loop
      let end = history.length - 1
      let hole = history[end]
      if (history[0] == hole && end >= 3) {
        return history[1]
      }

      // second choice: new tail creates the longest possible loop
      let oldHole = history[end - 1]
      let longest = history.indexOf(history[0], 1) >= 0 ? 1 : 0
      for (let i = longest; i < end - 1; i++) {
        let tail = history[i]
        if (
          tail != oldHole && // going back shouldn't be the default.
                             // happens when old hole is start of loop.
          SimpleGraph.hasEdge(this.graph, hole, tail)
        ) { return tail }
      }

      // third choice: iterate clockwise and choose the first edge
      for (let i = 1; i < this.size; i++) {
        let tail = (hole + i) % this.size
        if (
          tail != oldHole && // going back shouldn't be the default
          SimpleGraph.hasEdge(this.graph, hole, tail)
        ) { return tail }
      }

      // fourth choice: go back (dead end)
      return oldHole
    },
    goBack() {
      if (this.history.length >= 2) {
        let newHole = this.history[this.history.length - 2]
        this.trophyWasPushed = this.showTail &&
          this.history[this.history.length - 2] == this.tail
        // always show tail when undoing win because winning hides tail.
        //
        // tutorial levels have dead ends which cause the tail to be hidden
        // even when using the keyboard. it's confusing if going back
        // doesn't cause the tail to be shown again.
        this.showTail = this.showTail || this.won || this.deadEnd

        this.oldHole = this.hole
        this.reversed = true
        if (!this.reversing) {
          this.trophyPushed = false
        }

        this.tail = this.hole
        let id = Permute.getValue(this.beads, newHole) - 1
        this.beads = Permute.swap(this.beads, newHole, this.tail)
        this.animations[id] = 1 + this.animations[id] % 2
        this.oldBeads[id] = newHole
        this.trophyAlternate = !this.trophyAlternate
        this.showOldArrow = false
        this.backwardsInLoop = false
        this.continuingLoop = false
        this.history.pop()
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
          this.backwardsInLoop = true
        }
      }
    },
    selectLeft() {
      if (this.ensureTail()) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = this.size - 1; i >= 0; i--) {
        let newTail = (this.tail + i) % this.size
        if (SimpleGraph.hasEdge(this.graph, this.hole, newTail)) {
          this.tail = newTail
          return
        }
      }
    },
    selectRight() {
      if (this.ensureTail()) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (SimpleGraph.hasEdge(this.graph, this.hole, newTail)) {
          this.tail = newTail
          return
        }
      }
    },
    ensureTail() {
      if (!this.showTail) {
        if (this.history.length <= 1 || !this.deadEnd) {
          this.showTail = true
        }

        this.resetButtons()
        return true
      }

      return false
    },
    onPointerDown(event) {
      this.focusIsClick = true
      if (event.button != 0) {
        return
      }

      let target = this.getClickTarget(event.offsetX, event.offsetY)
      this.resetButtons()
      this.clickingButton = target != null
      if (target != null && target >= 0) {
        if (target == this.hole) {
          if (this.history.length >= 2) {
            this.goBack()
            this.showOldArrow = true
          } else {
            this.showCross = true
          }
        } else if (SimpleGraph.hasEdge(this.graph, target, this.hole)) {
          this.tail = target
          this.goForwardHelp()
          this.showOldArrow = true
        } else {
          this.showCross = true
        }

        this.showTail = false
      } else if (target == -2) {
        if (this.history[0] == this.hole) {
          this.tail = this.history[1]
        } else {
          this.tail = this.getForcedTail(
            this.history[this.history.length - 2],
            this.hole,
          )
        }

        this.goForwardHelp()
        this.showTail = false
        this.spinButtonClicked = true
      } else if (target == -3) {
        this.goBack()
        this.showTail = false
        this.smallSpinButtonClicked = true
      }
    },
    clicked(event) {
      this.focusIsClick = false
      if (event.button == 0) {
        this.clickingButton = false
        if (this.canAnimate) {
          this.resetButtons()
        }
      }
    },
    getClickTarget(offsetX, offsetY) {
      let gameView = document.getElementById('game-view')
      let clientSize = Math.min(gameView.clientWidth, gameView.clientHeight)
      let x = (offsetX - 0.5 * gameView.clientWidth) * 286 / clientSize
      let y = (offsetY - 0.5 * gameView.clientHeight) * 286 / clientSize
      for (let i = 0; i < this.size; i++) {
        let dx = this.nodeXs[i] - x
        let dy = this.nodeYs[i] - y
        if (dx * dx + dy * dy < this.clickRadius * this.clickRadius) {
          return i
        }
      }

      if (this.canSpin) {
        let dx = 0 - x
        let dy = this.smallSpinButtonY - y
        if (
          dx * dx + dy * dy < this.smallClickRadius * this.smallClickRadius
        ) {
          return -3
        }

        dx = 0 - x
        dy = this.spinButtonY - y
        if (dx * dx + dy * dy < this.clickRadius * this.clickRadius) {
          return -2
        }
      }

      return null
    },
    buttonClicked() {
      if (!this.ensureTail()) {
        this.showTail = false
      }
    },
    onFocus(event) {
      if (!this.focusIsClick) {
        event.target.scrollIntoView(false)
      }

      this.focusIsClick = false
      if (!this.clickingButton) {
        this.ensureTail()
      }
    },
    onBlur() {
      this.focusIsClick = false
      this.showTail = false
      this.resetButtons()
    },
    resetButtons() {
      this.clickingButton = false
      this.showCross = false
      this.spinButtonClicked = false
      this.smallSpinButtonClicked = false
    },
    getIngress(center, egress) {
      let result = egress
      // calculations are easier with center = 0
      egress = (egress + this.size - center) % this.size
      // the entrance should be as close to 180 degrees from the exit as possible
      let nearSide = 2 * egress >= this.size ? 1 : -1
      for (let distance = 1; distance < this.size - 1; distance++) {
        // try near side first so it can be overridden by far side which is better
        for (let side = nearSide; Math.abs(side) == 1; side -= 2 * nearSide) {
          let ingress = egress + distance * side
          if (ingress > 0 && ingress < this.size) {
            // use real center for graph check
            let id = (ingress + center) % this.size
            if (SimpleGraph.hasEdge(this.graph, center, id)) {
              result = id
            }
          }
        }
      }

      return result
    }
  },
  watch: {
    state: {
      handler(newState, oldState) {
        this.won = false
        this.hasWon = false
        this.showTail = false
        this.beads = newState.beads
        this.oldBeads = new Array(this.size - 1)
        for (let i = 0; i < this.size - 1; i++) {
          this.oldBeads[i] = Permute.findValue(this.beads, i + 1)
        }

        this.animations = new Uint8Array(this.oldBeads.length)
        this.history = [...newState.history]
        this.oldHole = this.hole
        this.tail = this.getNextTail(this.history)
        this.showOldArrow = false
        this.backwardsInLoop = false
        this.continuingLoop = false
      },
      immediate: true,
    },
    graphId(newGraphId, oldGraphId) {
      this.won = false
      this.hasWon = false
      this.showTail = false
    },
    initialTail: {
      handler(newInitialTail, oldInitialTail) {
        if (newInitialTail != null) {
          this.tail = newInitialTail
        }
      },
      immediate: true,
    },
    canAnimate(newCanAnimate, oldCanAnimate) {
      if (newCanAnimate) {
        this.animations = new Uint8Array(this.oldBeads.length)
        this.showOldArrow = false
        this.backwardsInLoop = false
        this.continuingLoop = false
        this.trophyEnterPaused = true
        this.trophyExitPaused = true
      }
    },
    beads(newBeads, oldBeads) {
      let newWon = this.beads == 0
      this.justWon = false
      if (newWon != this.won) {
        if (newWon) {
          this.showTail = false
        } else {
          this.justWon = true
          this.hasWon = true
        }

        this.won = newWon
        this.$emit('update:won', newWon)
      }

      this.trophyPushed = this.showTail
      this.trophyEnterPaused = false
      this.trophyExitPaused = false
      this.$emit('update:state', { beads: this.beads, history: this.history })
    },
    tail(newTail, oldTail) {
      this.$emit('update:tail', newTail)
    },
    showTail(newShowTail, oldShowTail) {
      this.trophyEnterPaused = false
      if (newShowTail) {
        this.trophyPushed = true
      }
    },
  },
}
</script>

<template>
  <button
    :class="{game: true, canAnimate: canAnimate}"
    :autofocus="autofocus"
    @keydown.up.stop.prevent="goForward()"
    @keydown.down.stop.prevent="goBack()"
    @keydown.left.stop.prevent="selectLeft()"
    @keydown.right.stop.prevent="selectRight()"
    @keydown.w.stop.prevent="goForward()"
    @keydown.s.stop.prevent="goBack()"
    @keydown.a.stop.prevent="selectLeft()"
    @keydown.d.stop.prevent="selectRight()"
    @click="buttonClicked"
    @focus.native="onFocus"
    @blur.native="onBlur"
  >
    <svg id="game-view" viewBox="-143 -143 286 286" @pointerdown="onPointerDown" @click.stop.prevent="clicked" @pointerup="clicked">
      <defs>
        <!-- http://tsitsul.in/blog/coloropt/ -->
        <radialGradient r="0.55" id="checked-0"> <stop offset="77%" :stop-color="colorHex[0]" stop-opacity="0.25"/> <stop offset="96%" stop-opacity="0"/> </radialGradient>
        <radialGradient r="0.55" id="checked-1"> <stop offset="77%" :stop-color="colorHex[1]" stop-opacity="0.25"/> <stop offset="100%" stop-opacity="0"/> </radialGradient>
        <radialGradient r="0.55" id="checked-2"> <stop offset="77%" :stop-color="colorHex[2]" stop-opacity="0.25"/> <stop offset="96%" stop-opacity="0"/> </radialGradient>
        <radialGradient r="0.55" id="checked-3"> <stop offset="77%" :stop-color="colorHex[3]" stop-opacity="0.25"/> <stop offset="98%" stop-opacity="0"/> </radialGradient>
        <radialGradient r="0.55" id="checked-4"> <stop offset="77%" :stop-color="colorHex[4]" stop-opacity="0.25"/> <stop offset="96%" stop-opacity="0"/> </radialGradient>
        <radialGradient r="0.55" id="checked-5"> <stop offset="77%" :stop-color="colorHex[5]" stop-opacity="0.25"/> <stop offset="100%" stop-opacity="0"/> </radialGradient>
        <radialGradient r="0.55" id="checked-6"> <stop offset="77%" :stop-color="colorHex[6]" stop-opacity="0.25"/> <stop offset="97%" stop-opacity="0"/> </radialGradient>
        <image id="star" x="-6" y="-6" width="12" height="12" href="../assets/star.svg"/>
        <image id="star-small" x="-4" y="-4" width="8" height="8" href="../assets/star_small.svg"/>
        <image id="heart-bead" x="-6" y="-6" width="12" height="12" href="../assets/heart.svg"/>
        <image id="butterfly-bead" x="-6" y="-6" width="12" height="12" href="../assets/butterfly.svg"/>
        <image id="saturn-bead" x="-6" y="-6" width="12" height="12" href="../assets/saturn.svg"/>
        <image id="leaf-bead" x="-6" y="-6" width="12" height="12" href="../assets/leaf.svg"/>
        <image id="mushroom-bead" x="-6" y="-6" width="12" height="12" href="../assets/mushroom.svg"/>
        <image id="flower-bead" x="-6" y="-6" width="12" height="12" href="../assets/flower.svg"/>
        <image id="heart-outline" x="-4" y="-4" width="8" height="8" href="../assets/heart_outline.svg"/>
        <image id="butterfly-outline" x="-4" y="-4" width="8" height="8" href="../assets/butterfly_outline.svg"/>
        <image id="saturn-outline" x="-4" y="-4" width="8" height="8" href="../assets/saturn_outline.svg"/>
        <image id="leaf-outline" x="-4" y="-4" width="8" height="8" href="../assets/leaf_outline.svg"/>
        <image id="mushroom-outline" x="-4" y="-4" width="8" height="8" href="../assets/mushroom_outline.svg"/>
        <image id="flower-outline" x="-4" y="-4" width="8" height="8" href="../assets/flower_outline.svg"/>
      </defs>
      <g v-for="node in size">
        <circle
          v-if="node >= 2 ? Permute.getValue(beads, node - 1) == node - 1 : won"
          :fill="node >= 2 ? `url('#checked-${idColors[node - 2] + 1}')` : `url('#checked-0')`"
          :r="clickRadius * 1.3"
          :cx="nodeXs[node - 1]"
          :cy="nodeYs[node - 1]"
        />
      </g>
      <circle
        v-for="node in size"
        fill="var(--color-background)"
        :r="clickRadius"
        :cx="nodeXs[node - 1]"
        :cy="nodeYs[node - 1]"
        :class="{touchCircle: true, checked: node >= 2 ? Permute.getValue(beads, node - 1) == node - 1 : won}"
        :style="(node >= 2 ? Permute.getValue(beads, node - 1) == node - 1 : won) ? {stroke: node >= 2 ? colorHex[idColors[node - 2] + 1] : colorHex[0]} : {}"
      />
      <circle
        fill="var(--color-background)"
        :r="clickRadius"
        :cx="0"
        :cy="spinButtonY"
        :class="{touchCircle: true}"
      />
      <circle
        fill="var(--color-background)"
        :r="smallClickRadius"
        :cx="0"
        :cy="smallSpinButtonY"
        :class="{touchCircle: true}"
      />
      <mask id="trophy-exit-mask">
        <circle
          :cx="nodeXs[trophyExitStart]"
          :cy="nodeYs[trophyExitStart]"
          :r="clickRadius"
          fill="white"
        >
        </circle>
      </mask>
      <mask id="trophy-enter-mask">
        <circle
          :cx="nodeXs[trophyEnterEnd]"
          :cy="nodeYs[trophyEnterEnd]"
          :r="clickRadius"
          fill="white"
        >
        </circle>
      </mask>
      <g
        v-for="(edge, i) in edges"
        :key="`${edge.toString()},${size}`"
      >
        <circle
          v-if="backwardsInLoop ? i == 1 : i == 0"
          :cx="nodeXs[history[0]]"
          :cy="nodeYs[history[0]]"
          :r="terminatorRadius"
          :class="{ terminator: true, shown: edgeClasses[edge.toString()]['active'], hidden: edgeClasses[edge.toString()]['arrow'], delay: this.history.length == 2 }"
        />
        <circle
          v-if="backwardsInLoop ? i == 0 : i == 1"
          :cx="nodeXs[oldHole]"
          :cy="nodeYs[oldHole]"
          :r="terminatorRadius * 0.5"
          :class="{ oldTerminator: true, close: backwardsInLoop, delay: continuingLoop && !showOldArrow, alternate: trophyAlternate }"
        />
      </g>
      <g
        :style="{ 'offset-path': `path('${oldArrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
        :class="{headGroup: true, animate: showOldArrow, alternate: trophyAlternate}"
      >
        <path :d="headShadowPath" class="head shadow"/>
        <path :d="headPath" class="head"/>
      </g>
      <g
        v-if=showTail
        :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
      >
        <path :d="headShadowPath" class="head shadow"/>
        <path :d="headPath" class="head"/>
      </g>
      <g v-if="hasWon || (won && trophyAlternate)" :mask="trophyAlternate ? 'url(#trophy-enter-mask)' : 'url(#trophy-exit-mask)'">
        <use :href="(trophyAlternate ? won : justWon) ? '#star' : '#star-small'" :class="trophyAlternate ? trophyEnterClasses : trophyExitClasses"
          :style="{ 'transform': 'scale(2.7) rotate(90deg)', 'offset-path': trophyAlternate ? trophyEnterPath : trophyExitPath}"
        />
      </g>
      <g v-if="hasWon || (won && !trophyAlternate)" :mask="trophyAlternate ? 'url(#trophy-exit-mask)' : 'url(#trophy-enter-mask)'">
        <use :href="(trophyAlternate ? justWon : won) ? '#star' : '#star-small'" :class="trophyAlternate ? trophyExitClasses : trophyEnterClasses"
          :style="{ 'transform': 'scale(2.7) rotate(90deg)', 'offset-path': trophyAlternate ? trophyExitPath : trophyEnterPath}"
        />
      </g>
      <g
        :transform="`translate(${nodeXs[hole]}, ${nodeYs[hole]})`"
        :class="{crossGroup: true, ghost: !showCross}"
        :opacity="showCross ? 1 : 0"
      >
        <path :d="crossPath" class="cross shadow"/>
        <path :d="crossPath" class="cross"/>
      </g>
      <template v-if="canSpin">
        <g
          :style="{transform: `translate(0,${spinButtonY}px) scale(${clockwise ? 1 : -1},1)`}"
        >
          <g :class="{spinGroup: true, clicked: spinButtonClicked, ghost: !spinButtonClicked}">
            <path :d="spinPath" class="spinIcon shadow"/>
            <path :d="spinPath" class="spinIcon"/>
          </g>
        </g>
        <g
          :style="{transform: `translate(0,${smallSpinButtonY}px) scale(${clockwise ? -1 : 1},1)`}"
        >
          <g :class="{spinGroup: true, clicked: smallSpinButtonClicked, ghost: !smallSpinButtonClicked}">
            <path :d="smallSpinPath" class="spinIcon shadow"/>
            <path :d="smallSpinPath" class="spinIcon"/>
          </g>
        </g>
      </template>
      <Board
        :key="graphId"
        :graphId="graphId"
        :beads="beads"
        :history="history"
        :tail="showTail ? tail : -1"
        :controlLength="30"
        :radius="100"
      />
      <Goal
        v-for="i in size - 1"
        :size="size"
        :bead="i"
        :radius="100"
      />
    </svg>
  </button>
</template>

<style scoped>
button {
  background-color: inherit;
  border: none;
  font: inherit;
  padding: 0;
}
.game {
  aspect-ratio: 1;
  width: min(120%, 1.2 * max(100vh, 15rem), 42rem);
  margin-top: calc(0.5 * (max(100vh, 15rem) - min(120%, 1.2 * max(100vh, 15rem), 42rem)));
  margin-left: calc(0.5 * (100% - min(120%, 1.2 * max(100vh, 15rem), 42rem)));
  margin-bottom: min(0rem, 0.5 * (max(100vh, 15rem) - min(120%, 1.2 * max(100vh, 15rem), 42rem)));
  border: 2px solid #444444;
  border-radius: 2px;
  background-color: black;
}
.touchCircle {
  stroke: #444444;
  stroke-width: 1px;
}
.touchCircle.checked {
  stroke-width: 0.75;
  stroke-opacity: 1;
}
.terminator {
  opacity: 0;
  fill: var(--color-background);
}
.terminator.shown {
  opacity: 1;
}
.terminator.shown.hidden {
  opacity: 0;
}
.canAnimate .terminator.shown.delay {
  animation: delay 0.45s
}
@keyframes delay {
  from { opacity: 0; }
  to { opacity: 0; }
}
.oldTerminator {
  stroke: var(--color-background);
  stroke-width: 0;
  fill: none;
}
.canAnimate .oldTerminator.close {
  animation: close 0.45s ease 0.3s backwards
}
@keyframes close {
  from {
    r: calc(100% * 0.5 * v-bind(terminatorRadius) / 286);
    stroke-width: v-bind(terminatorRadius);
  }
  to {
    r: calc(100% * v-bind(terminatorRadius) / 286);
    stroke-width: 0;
  }
}
.canAnimate .oldTerminator.close.alternate {
  animation: close2 0.45s ease 0.3s backwards
}
@keyframes close2 {
  from {
    r: calc(100% * 0.5 * v-bind(terminatorRadius) / 286);
    stroke-width: v-bind(terminatorRadius);
  }
  to {
    r: calc(100% * v-bind(terminatorRadius) / 286);
    stroke-width: 0;
  }
}
.canAnimate .oldTerminator.delay {
  animation: oldDelay 0.45s ease 0.3s backwards
}
@keyframes oldDelay {
  from {
    r: calc(100% * 0.5 * v-bind(terminatorRadius) / 286);
    stroke-width: v-bind(terminatorRadius);
  }
  to {
    r: 0%;
    stroke-width: 0;
  }
}
.canAnimate .oldTerminator.delay.alternate {
  animation: oldDelay2 0.45s ease 0.3s backwards
}
@keyframes oldDelay2 {
  from {
    r: calc(100% * 0.5 * v-bind(terminatorRadius) / 286);
    stroke-width: v-bind(terminatorRadius);
  }
  to {
    r: 0%;
    stroke-width: 0;
  }
}
.head, .cross {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.head.shadow {
  stroke: none;
  fill: var(--color-background);
}
.headGroup {
  opacity: 0;
}
.canAnimate .headGroup.animate {
  animation: oldArrow 0.45s;
}
.canAnimate .headGroup.animate.alternate {
  animation: oldArrow2 0.45s;
}
@keyframes oldArrow {
  from { opacity: 1; }
  to { opacity: 1; }
}
@keyframes oldArrow2 {
  from { opacity: 1; }
  to { opacity: 1; }
}
.cross.shadow {
  stroke: var(--color-background);
  stroke-width: 12;
}
.canAnimate .crossGroup.ghost {
  transition: opacity 0s 0.35s;
}
.spinIcon {
  stroke: var(--color-text);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.spinIcon.shadow {
  stroke: var(--color-background);
  stroke-width: 9;
}
.spinGroup.clicked {
  transform: scale(calc(5/3));
}
.canAnimate .spinGroup.clicked {
  animation: revert 1s 0.35s forwards;
}
@keyframes revert {
  from { transform: scale(1); }
  to { transform: scale(1); }
}
.canAnimate .spinGroup.ghost {
  transition: transform 0s 0.05s;
}
.edge {
  fill: none;
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 4 12;
}
.canAnimate .edge {
  transition: d 0.5s;
}
.edge.arrow {
  stroke-dasharray: 8 8;
  stroke-dashoffset: 2;
}
.edge.active {
  stroke-dasharray: none;
}
.outline {
  stroke-width: 3;
  stroke: var(--color-text);
}
/*
tail onPath undo reverse offset-rotate
0    0                   -90deg
0    1           0       auto
0    1           1       reverse
1                        reverse
*/
.bead {
  offset-distance: 100%;
  offset-rotate: -90deg;
}
.bead.onPath {
  offset-rotate: auto;
}
.bead.onPath.reverse, .bead.tail {
  offset-rotate: reverse;
}
.canAnimate .bead.animate {
  animation: slide 0.75s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.canAnimate .bead.alternate {
  animation-name: slide2;
}
@keyframes slide2 {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.trophy {
  offset-rotate: auto;
  offset-distance: 100%;
}
.canAnimate .trophy.unpaused {
  animation: slide 0.75s ease forwards;
}
.canAnimate .trophy.wasPushed.unpaused {
  animation: wasPushed 0.75s ease forwards;
}
@keyframes wasPushed {
  from { offset-distance: calc(100% * 0.2); }
  to { offset-distance: 100%; }
}
.canAnimate .trophy.enter.unpaused {
  animation: slide2 0.75s ease forwards;
}
.trophy.enter.wasPushed {
  offset-distance: 0%;
}
.canAnimate .trophy.enter.wasPushed.unpaused {
  animation: unpushed 0.5s ease forwards;
}
@keyframes unpushed {
  from { offset-distance: calc(100% * 0.2); }
  to { offset-distance: 0%; }
}
.trophy.reverse {
  offset-rotate: reverse;
}
@keyframes pushed {
  from { offset-distance: 0%; }
  to { offset-distance: calc(100% * 0.2); }
}
.trophy.enter.pushed {
  offset-distance: calc(100% * 0.2);
}
.canAnimate .trophy.enter.pushed.unpaused {
  animation: pushed calc(0.75s * (1 - 0.2)) ease forwards;
}
</style>
