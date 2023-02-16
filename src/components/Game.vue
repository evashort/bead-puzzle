<script>
export default {
  data() {
    return {
      beads: [],
      won: false,
      history: [],
      showTail: false,
      showCross: false,
      // if clickTarget is null, clicking is treated as false no matter its
      // actual value
      clicking: false,
      clickTarget: null,
      /*
      animation legend:
      0 = static  forward primary
      1 = animate forward alternate
      2 = animate forward primary
      3 = animate reverse alternate
      4 = animate reverse primary

      6 = static  reverse primary
      */
      animations: new Uint8Array(0),
      oldBeads: [],

      // change triggers
      beadChanges: 0,

      // trophy state
      trophyAlternate: false,
      undoneHole: -1,
      trophyPushed: false,
      trophyWasPushed: false,
      justWon: false,
      hasWon: false,
    }
  },
  props: {
    startingBeads: Array,
    edges: Array,
    autofocus: Boolean,
  },
  emits: ['update:won', 'update:state'],
  computed: {
    size() {
      return this.startingBeads.length + 1
    },
    matrix() {
      let matrix = new Uint8Array(this.size * this.size)
      for (let [a, b] of this.edges) {
        matrix[a * this.size + b] = matrix[b * this.size + a] = 1
      }

      return matrix
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
    colorIds() {
      let colorIds = new Int8Array(6).fill(-1)
      for (let [id, color] of this.idColors.entries()) {
        colorIds[color] = id
      }

      return colorIds
    },
    hole() {
      return this.history[this.history.length - 2]
    },
    tail() {
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
      return this.history.length - 2
    },
    activeStart() {
      return this.history.length > 2 &&
        this.hole == this.history[0] && this.tail == this.history[1] && this.showTail ?
        0 : this.loopStart
    },
    deadEnd() {
      let edges = 0
      for (let i = 0; i < this.size; i++) {
        edges += this.matrix[this.hole * this.size + i]
        if (edges > 1) {
          return false
        }
      }

      return true
    },
    reversing() {
      return this.history.length >= 3 &&
        this.tail == this.history[this.history.length - 3]
    },
    nodeXs() {
      let xs = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        // avoid vertical edges because of rendering bug for masked paths
        xs[i] = 100 * Math.sin(2 * Math.PI * i / this.size + 0.02)
      }

      return xs
    },
    nodeYs() {
      let ys = new Float64Array(this.size)
      for (let i = 0; i < this.size; i++) {
        ys[i] = -100 * Math.cos(2 * Math.PI * i / this.size + 0.02)
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
    edgeTruncated() {
      let startNode = this.extra[this.loopStart]
      if (this.extra[this.loopEnd] == startNode) {
        return false
      }

      let next = this.extra.indexOf(startNode, this.loopStart + 1)
      return next >= 0 && next < this.loopEnd
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
    crossRadius() {
      return 18
    },
    crossPath() {
      let d = this.crossRadius * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    arrowEdge() {
      let a = this.hole, b = this.tail
      if (
        this.clickTarget != null && this.clickTarget >= 0 && !this.clicking
      ) {
        b = a
        a = this.clickTarget
      } else if (a == b && this.history.length >= 3) {
        a = this.history[this.history.length - 3]
      }

      if (this.matrix[a * this.size + b]) {
        return [a, b]
      }

      return[a, a]
    },
    arrowPath() {
      return this.edgePaths[this.arrowEdge.toString()]
    },
    beadRadius() {
      return 10
    },
    beadHeight() {
      return this.beadRadius * Math.sqrt(3)
    },
    beadClasses() {
      return this.beads.map(
        function(node, id, beads) {
          let historyIndex = this.extra.indexOf(node, this.activeStart)
          return {
            bead: true,
            tail: node == this.tail && this.showTail,
            onPath: historyIndex >= 0 && historyIndex <= this.activeEnd,
            animate: this.animations[id] % 6,
            alternate: this.animations[id] % 2,
            reverse: this.animations[id] >= 3,
            undo: this.oldBeads[id] == this.hole,
            moving: this.oldBeads[id] == this.hole ||
              this.oldBeads[id] == this.tail,
            ghost: this.clickTarget != null && !this.clicking,
          }
        },
        this,
      )
    },
    beadOffsetPaths() {
      return this.beads.map(
        function(node, id, beads) {
          let edge =
            node != this.extra[this.loopStart] &&
            node == this.tail &&
            this.showTail ?
            [this.hole, this.tail] :
            [this.oldBeads[id], node]
          let path = this.edgePaths[edge.toString()]
          return `path('${path}')`
        },
        this,
      )
    },
    trophyExitStart() {
      if (this.undoneHole >= 0) {
        return this.undoneHole
      } else if (this.history.length >= 3) {
        return this.history[this.history.length - 3]
      }

      return this.hole
    },
    trophyExitEnd() {
      if (this.history.length >= 3 && this.undoneHole == this.history[1]) {
        return this.history[2]
      } else if (this.undoneHole >= 0) {
        return this.getIngress(this.undoneHole, this.hole)
      } else if (this.history.length >= 4) {
        return this.history[this.history.length - 4]
      } else if (this.history.length >= 3) {
        let center = this.history[this.history.length - 3]
        return this.getIngress(center, this.hole)
      }

      return this.hole
    },
    trophyPushedStart() {
      return this.hole
    },
    trophyPushedEnd() {
      if (this.history.length >= 3) {
        if (this.hole == this.history[0]) {
          if (this.reversing) {
            return this.history[1]
          }

          return this.history[this.history.length - 3]
        } else if (this.reversing) {
          return this.getIngress(this.hole, this.history[this.history.length - 3])
        }

        return this.history[this.history.length - 3]
      }

      return this.getIngress(this.hole, this.tail)
    },
    trophyEnterStart() {
        if (this.undoneHole >= 0) {
        if (this.history.length >= 3) {
          return this.history[this.history.length - 3]
        } else {
          return this.getIngress(this.hole, this.undoneHole)
        }
      } else if (this.history.length >= 3) {
        if (this.history[0] == this.hole) {
          return this.history[1]
        }

        let egress = this.history[this.history.length - 3]
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
        reverse: this.undoneHole >= 0,
        wasPushed: this.trophyWasPushed,
      }
    },
    trophyEnterClasses() {
      return {
        trophy: true,
        enter: true,
        reverse: this.trophyPushed ?
          this.reversing :
          this.undoneHole >= 0,
        pushed: this.showTail,
        wasPushed: this.trophyPushed,
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
      if (this.history.length <= 2) {
        return this.showTail ? this.history : [this.hole]
      }

      let loop = [...this.history]
      loop.pop()
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
        loop.length == this.history.length - 1 &&
        !this.reversing &&
        this.showTail
      ) {
        loop.push(this.tail)
      }

      return loop
    },
    canSpin() {
      return this.history.length >= 3 && ( // must be 3 and not 4
        this.hole == this.history[0] || (
          this.extra[this.loopStart] == this.extra[this.loopEnd] && (
            this.extra.length > this.history.length ||
            this.getForcedTail(
              this.history[this.history.length - 3],
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
      let start = hole * this.size
      let tail = -1
      for (let i = 0; i < this.size; i++) {
        if (i != prev && this.matrix[start + i]) {
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
        if (this.undoneHole < 0 && this.reversing) {
          this.showTail = false // dead end
        }
      }
    },
    goForwardHelp() {
      this.trophyWasPushed = this.showTail
      let id = this.beads.indexOf(this.tail)
      this.beads[id] = this.hole
      this.beadChanges = (this.beadChanges + 1) % 1000
      this.animations[id] = 1 + this.animations[id] % 2
      this.oldBeads[id] = this.tail
      this.trophyAlternate = !this.trophyAlternate
      this.undoneHole = -1
      this.clickTarget = null
      if (this.reversing) {
        let loop = this.history[0] == this.hole
        this.undoneHole = this.hole
        this.history.pop()
        this.history.pop()
        if (loop) {
          this.history.reverse()
          this.history.push(this.history[0])
          this.undoneHole = -1
        } else {
          this.animations[id] += 2
          if (this.history.length >= 2) {
            this.history.push(this.hole) // keep going back
          } else {
            this.history.push(this.undoneHole)
          }

          return
        }
      }

      // remove before loop
      for (let offset = this.history.length - 4; offset >= 0; offset--) {
        if (this.history[offset] == this.tail) {
          this.history = this.history.slice(offset)
        }
      }

      this.history.push(this.getNextTail(this.history))
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
          this.matrix[hole * this.size + tail]
        ) { return tail }
      }

      // third choice: iterate clockwise and choose the first edge
      for (let i = 1; i < this.size; i++) {
        let tail = (hole + i) % this.size
        if (
          tail != oldHole && // going back shouldn't be the default
          this.matrix[hole * this.size + tail]
        ) { return tail }
      }

      // fourth choice: go back (dead end)
      return oldHole
    },
    goBack() {
      this.clickTarget = null
      if (this.history.length > 2) {
        this.trophyWasPushed = this.showTail
        // always show tail when undoing win because winning hides tail.
        //
        // tutorial levels have dead ends which cause the tail to be hidden
        // even when using the keyboard. it's confusing if going back
        // doesn't cause the tail to be shown again.
        this.showTail = this.showTail || this.won || this.deadEnd

        this.undoneHole = this.hole
        if (!this.reversing) {
          this.trophyPushed = false
        }

        this.history.pop()

        let id = this.beads.indexOf(this.hole)
        this.beads[id] = this.tail
        this.beadChanges = (this.beadChanges + 1) % 1000
        this.animations[id] = 3 + this.animations[id] % 2
        this.oldBeads[id] = this.hole
        this.trophyAlternate = !this.trophyAlternate
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
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
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          this.clickTarget = null
          // TODO: history changed (maybe)
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
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          this.clickTarget = null
          // TODO: history changed (maybe)
          return
        }
      }
    },
    ensureTail() {
      if (!this.showTail) {
        this.clickTarget = null
        if (this.history.length <= 2 || !this.deadEnd) {
          this.showTail = true
        }

        return true
      }

      return false
    },
    onMouseDown(event) {
      if (event.button != 0) {
        return
      }

      this.clickTarget = this.getClickTarget(event.offsetX, event.offsetY)
      this.clicking = true
      this.showCross = false
      if (this.clickTarget == this.hole && this.history.length <= 2) {
        this.clickTarget = -1
        this.showTail = false
        this.showCross = true
      } else if (this.clickTarget != null && this.clickTarget >= 0) {
        let newTail = this.clickTarget == this.hole ?
          this.history[this.history.length - 3] : this.clickTarget
        this.showTail = this.matrix[this.size * this.hole + newTail]
        if (this.showTail) {
          this.history[this.history.length - 1] = newTail
          // TODO: history changed (maybe)
        } else {
          this.clickTarget = -1
          this.showCross = true
        }
      } else if (this.clickTarget == -2 || this.clickTarget == -3) {
        this.showTail = false
      }
    },
    clicked(event) {
      if (event.button != 0) {
        return
      }

      this.clicking = false
      let newTarget = this.getClickTarget(event.offsetX, event.offsetY)
      if (this.clickTarget == -1) {
      } else if (newTarget != this.clickTarget) {
        this.clicking = true
      } else if (this.clickTarget == this.hole && this.reversing) {
        let oldTarget = this.hole
        this.goBack()
        this.clickTarget = oldTarget
        this.showTail = false
      } else if (this.clickTarget != null && this.clickTarget == this.tail) {
        let oldTarget = this.hole
        this.goForwardHelp()
        this.clickTarget = oldTarget
        this.showTail = false
      } else if (this.clickTarget == -2 && this.canSpin) {
        if (this.history[0] == this.hole) {
          this.history[this.history.length - 1] = this.history[1]
        } else {
          this.history[this.history.length - 1] = this.getForcedTail(
            this.history[this.history.length - 3],
            this.hole,
          )
        }
        this.goForwardHelp()
        this.clickTarget = -2
      } else if (this.clickTarget == -3 && this.canSpin) {
        this.goBack()
        this.showTail = false
        this.clickTarget = -3
      }
    },
    getClickTarget(offsetX, offsetY) {
      let gameView = document.getElementById('game-view')
      let clientSize = Math.min(gameView.clientWidth, gameView.clientHeight)
      let x = (offsetX - 0.5 * gameView.clientWidth) * 240 / clientSize
      let y = (offsetY - 0.5 * gameView.clientHeight) * 240 / clientSize
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
    onFocus() {
      if (
        this.clickTarget != -2 && this.clickTarget != -1 &&
          this.clickTarget != -3
      ) {
        this.ensureTail()
      }
    },
    onBlur() {
      this.clickTarget = null
      this.showTail = false
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
            // use real center for matrix check
            let id = (ingress + center) % this.size
            if (this.matrix[center * this.size + id]) {
              result = id
            }
          }
        }
      }

      return result
    }
  },
  watch: {
    startingBeads: {
      handler(newStartingBeads, oldStartingBeads) {
        this.won = false
        this.hasWon = false
        this.showTail = false
        this.beads = [...newStartingBeads]
        this.beadChanges = (this.beadChanges + 1) % 1000
        this.oldBeads = [...newStartingBeads]
        this.animations = new Uint8Array(this.beads.length)
        let beadSet = new Set(this.beads)
        let hole = 0
        for (; beadSet.has(hole); hole++) { }

        this.history = [hole]
        this.history.push(this.getNextTail(this.history))
        this.clickTarget = null
      },
      immediate: true,
    },
    beadChanges(newBeadChanges, oldBeadChanges) {
      let newWon = true
      for (let [id, node] of this.beads.entries()) {
        if (node != id + 1) { newWon = false }
      }

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
      this.$emit('update:state', { beads: this.beads })
    },
    showTail(newShowTail, oldShowTail) {
      if (newShowTail) {
        this.trophyPushed = true
      }
    }
  },
}
</script>

<template>
  <button
    class="game"
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
    <svg id="game-view" viewBox="-143 -143 286 286" @mousedown="onMouseDown" @click.stop.prevent="clicked">
      <defs>
        <path
          id="head-path"
          :d="headPath"
          :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
          fill="none"
          stroke="black"
          stroke-width="12"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          id="cross-path"
          :d="crossPath"
          :transform="`translate(${nodeXs[hole]}, ${nodeYs[hole]})`"
          fill="none"
          stroke="black"
          stroke-width="12"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- http://tsitsul.in/blog/coloropt/ -->
        <radialGradient r="0.55" id="checked-0"> <stop offset="75%" stop-color="black"/> <stop offset="100%" stop-color="#cacaca"/> </radialGradient>
        <radialGradient r="0.55" id="checked-1"> <stop offset="70%" stop-color="black"/> <stop offset="100%" stop-color="#b51d14"/> </radialGradient>
        <radialGradient r="0.55" id="checked-2"> <stop offset="75%" stop-color="black"/> <stop offset="100%" stop-color="#ddb310"/> </radialGradient>
        <radialGradient r="0.55" id="checked-3"> <stop offset="72%" stop-color="black"/> <stop offset="100%" stop-color="#00b25d"/> </radialGradient>
        <radialGradient r="0.55" id="checked-4"> <stop offset="75%" stop-color="black"/> <stop offset="100%" stop-color="#00beff"/> </radialGradient>
        <radialGradient r="0.55" id="checked-5"> <stop offset="70%" stop-color="black"/> <stop offset="100%" stop-color="#4053d3"/> </radialGradient>
        <radialGradient r="0.55" id="checked-6"> <stop offset="74%" stop-color="black"/> <stop offset="100%" stop-color="#fb49b0"/> </radialGradient>
        <image id="star" x="-6" y="-6" width="12" height="12" href="../assets/star.svg"></image>
        <image id="star-small" x="-4" y="-4" width="8" height="8" href="../assets/star_small.svg"></image>
      </defs>
      <circle
        v-for="node in size"
        :fill="node >= 2 && beads[node - 2] == node - 1 ? `url('#checked-${idColors[node - 2] + 1}')` : won ? `url('#checked-0')` : 'black'"
        :r="clickRadius"
        :cx="nodeXs[node - 1]"
        :cy="nodeYs[node - 1]"
        :class="{touchCircle: true, checked: node >= 2 ? beads[node - 2] == node - 1 : won}"
      />
      <circle
        fill="black"
        :r="clickRadius"
        :cx="0"
        :cy="spinButtonY"
        :class="{touchCircle: true}"
      />
      <circle
        fill="black"
        :r="smallClickRadius"
        :cx="0"
        :cy="smallSpinButtonY"
        :class="{touchCircle: true}"
      />
      <path
        :opacity="showTail ? 1 : 0"
        class="head"
        :d="headPath"
        :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
        :class="{ghost: clickTarget != null && !clicking}"
        fill="none"
      />
      <mask id="cross-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use
          href="#cross-path"
          :opacity="showCross && clicking ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
      </mask>
      <mask id="head-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use
          href="#head-path"
          :opacity="showTail ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
        <!-- replace with black shape and make sure it covers the trophy -->
        <use
          href="#cross-path"
          :opacity="showCross && clicking ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
      </mask>
      <mask id="truncate-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <circle
          :cx="nodeXs[history[0]]"
          :cy="nodeYs[history[0]]"
          :r="edgeTruncated ? 25 : 0"
          fill="black"
          :style="{'transition': 'r 0.5s'}">
        </circle>
        <use
          href="#head-path"
          :opacity="showTail ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
        <use
          href="#cross-path"
          :opacity="showCross && clicking ? 1 : 0"
          :class="{ghost: clickTarget != null && !clicking}"
        />
      </mask>
      <mask id="trophy-exit-mask">
        <circle
          :cx="nodeXs[this.trophyExitStart]"
          :cy="nodeYs[this.trophyExitStart]"
          :r="clickRadius"
          fill="white"
        >
        </circle>
      </mask>
      <mask id="trophy-enter-mask">
        <circle
          :cx="nodeXs[this.trophyEnterEnd]"
          :cy="nodeYs[this.trophyEnterEnd]"
          :r="clickRadius"
          fill="white"
        >
        </circle>
      </mask>
      <path
        v-for="edge of edges"
        :key="`${edge.toString()},${size}`"
        :class="edgeClasses[edge.toString()]"
        :d="edgePaths[edge.toString()]"
        fill="none"
        v-bind:mask="(edge[0] == arrowEdge[0] && edge[1] == arrowEdge[1]) || (edge[0] == arrowEdge[1] && edge[1] == arrowEdge[0]) ? 'url(#cross-mask)' : (edge[0] == history[0] && edge[1] == history[1]) || (edge[0] == history[1] && edge[1] == history[0]) ? 'url(#truncate-mask)' : 'url(#head-mask)'"
      />
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
      <path
        :opacity="showCross && clicking ? 1 : 0"
        class="head"
        :d="crossPath"
        :transform="`translate(${nodeXs[hole]}, ${nodeYs[hole]})`"
        :class="{ghost: clickTarget != null && !clicking}"
        fill="none"
      />
      <template v-if="canSpin">
        <g
          :style="{transform: `translate(0,${spinButtonY}px) scale(${clockwise ? 1 : -1},1) scale(${clicking && clickTarget == -2 ? activeBeadScale : normalBeadScale})`}"
          :class="{spinIconGhost: clickTarget == -2 && !clicking}"
        >
          <path :d="spinPath" class="spinIcon shadow"/>
          <path :d="spinPath" class="spinIcon"/>
        </g>
        <g
          :style="{transform: `translate(0,${smallSpinButtonY}px) scale(${clockwise ? -1 : 1},1) scale(${clicking && clickTarget == -3 ? activeBeadScale : normalBeadScale})`}"
          :class="{spinIconGhost: clickTarget == -3 && !clicking}"
        >
          <path :d="smallSpinPath" class="spinIcon shadow"/>
          <path :d="smallSpinPath" class="spinIcon"/>
        </g>
      </template>
      <image v-if="colorIds[0] >= 0" x="-6" y="-6" width="12" height="12" :class="beadClasses[colorIds[0]]"
        href="../assets/heart.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.7) scale(${tail == beads[colorIds[0]] && showTail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[colorIds[0]] }"
      />
      <image v-if="colorIds[1] >= 0" x="-6" y="-6" width="12" height="12" :class="beadClasses[colorIds[1]]"
        href="../assets/butterfly.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.8) scale(${tail == beads[colorIds[1]] && showTail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[colorIds[1]] }"
      />
      <image v-if="colorIds[2] >= 0" x="-6" y="-6" width="12" height="12" :class="beadClasses[colorIds[2]]"
        href="../assets/saturn.svg"
        :style="{ 'transform': `rotate(90deg) scale(3.35) scale(${tail == beads[colorIds[2]] && showTail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[colorIds[2]] }"
      />
      <image v-if="colorIds[3] >= 0" x="-6" y="-6" width="12" height="12" :class="beadClasses[colorIds[3]]"
        href="../assets/leaf.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.5) scale(${tail == beads[colorIds[3]] && showTail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[colorIds[3]] }"
      />
      <image v-if="colorIds[4] >= 0" x="-6" y="-6" width="12" height="12" :class="beadClasses[colorIds[4]]"
        href="../assets/mushroom.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.6) scale(${tail == beads[colorIds[4]] && showTail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[colorIds[4]] }"
      />
      <image v-if="colorIds[5] >= 0" x="-6" y="-6" width="12" height="12" :class="beadClasses[colorIds[5]]"
        href="../assets/flower.svg"
        :style="{ 'transform': `rotate(90deg) scale(2.5) scale(${tail == beads[colorIds[5]] && showTail ? activeBeadScale : normalBeadScale})`, 'offset-path': beadOffsetPaths[colorIds[5]] }"
      />
      <g v-if="colorIds[0] >= 0" :transform="`translate(${goalXs[colorIds[0] + 1]},${goalYs[colorIds[0] + 1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/heart_outline.svg"
          :style="{ 'transform': 'scale(2.7)' }"
        />
      </g>
      <g v-if="colorIds[1] >= 0" :transform="`translate(${goalXs[colorIds[1] + 1]},${goalYs[colorIds[1] + 1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/butterfly_outline.svg"
          :style="{ 'transform': 'scale(2.8)' }"
        />
      </g>
      <g v-if="colorIds[2] >= 0" :transform="`translate(${goalXs[colorIds[2] + 1]},${goalYs[colorIds[2] + 1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/saturn_outline.svg"
          :style="{ 'transform': 'scale(3.35)' }"
        />
      </g>
      <g v-if="colorIds[3] >= 0" :transform="`translate(${goalXs[colorIds[3] + 1]},${goalYs[colorIds[3] + 1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/leaf_outline.svg"
          :style="{ 'transform': 'scale(2.5)' }"
        />
      </g>
      <g v-if="colorIds[4] >= 0" :transform="`translate(${goalXs[colorIds[4] + 1]},${goalYs[colorIds[4] + 1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/mushroom_outline.svg"
          :style="{ 'transform': 'scale(2.6)' }"
        />
      </g>
      <g v-if="colorIds[5] >= 0" :transform="`translate(${goalXs[colorIds[5] + 1]},${goalYs[colorIds[5] + 1]})`">
        <image x="-4" y="-4" width="8" height="8"
          href="../assets/flower_outline.svg"
          :style="{ 'transform': 'scale(2.5)' }"
        />
      </g>
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
}
.touchCircle {
  stroke: var(--color-text);
  stroke-width: 0.5;
  stroke-opacity: 0.25;
}
.touchCircle.checked {
  stroke-width: 0.75;
  stroke-opacity: 1;
}
.head {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.ghost {
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
  stroke: black;
  stroke-width: 9;
}
.spinIconGhost {
  transition: transform 0s 0.05s;
}
.edge {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  transition: d 0.5s;
  stroke-dasharray: 4 12;
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
1    0      0            reverse
1           1    0       auto
1           1    1       reverse
1    1      0            auto
*/
.bead {
  offset-distance: 100%;
  offset-rotate: -90deg;
}
.bead.onPath {
  offset-rotate: auto;
}
.bead.onPath.reverse {
  offset-rotate: reverse;
}
.bead.animate {
  animation: slide 0.75s ease forwards;
}
@keyframes slide {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.bead.alternate {
  animation-name: slide2;
}
@keyframes slide2 {
  from { offset-distance: 0%; }
  to { offset-distance: 100%; }
}
.bead.tail {
  offset-rotate: reverse;
}
.bead.tail.onPath {
  offset-rotate: auto;
}
.bead.tail.undo {
  offset-rotate: auto;
}
.bead.tail.undo.reverse {
  offset-rotate: reverse;
}
.bead.ghost {
  transition: transform 0s 0.35s;
}
.bead.ghost.moving {
  /* this timing function approximates a delay, since actual delay caused
   * beads to stay BIG sometimes due to browser bug
   */
  transition: transform 0.06s cubic-bezier(1,0,1,0);
}
.trophy {
  offset-rotate: auto;
  animation: slide 0.75s ease forwards;
}
.trophy.wasPushed {
  animation: wasPushed 0.75s ease forwards;
}
@keyframes wasPushed {
  from { offset-distance: calc(100% * 0.2); }
  to { offset-distance: 100%; }
}
.trophy.enter {
  animation: slide2 0.75s ease forwards;
}
.trophy.enter.wasPushed {
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
  animation: pushed calc(0.75s * (1 - 0.2)) ease forwards;
}
</style>
