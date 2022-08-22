<script setup>
import seedrandom from 'seedrandom'
</script>

<script>
export default {
  data() {
    let beadSet = new Set(this.startingBeads)
    let hole = 0
    for (; beadSet.has(hole); hole++) { }

    let dustDelays = new Float64Array(this.dustCount)
    // higher origin reduces numerical instability introduced by going fast
    let dustOrigin = 946713600000 // year 2000
    let now = Date.now()
    let dustIndex = Math.floor(
      (now - dustOrigin) * 0.001 / this.baseDustDuration * this.dustCount
    )
    for (let i = 0; i < this.dustCount; i++) {
      let j = dustIndex - i
      let startTime = j * this.baseDustDuration / this.dustCount
      dustDelays[j % this.dustCount] = startTime - (now - dustOrigin) * 0.001
    }

    return {
      beads: [...this.startingBeads],
      history: [hole, hole],
      chosenTail: null,
      holeClicked: false,
      ghostHole: null,
      animations: new Uint8Array(this.startingBeads.length),
      oldBeads: [...this.startingBeads],
      now: now,
      dustDelays: dustDelays,
      dustOrigin: dustOrigin,
      fast: false,
    }
  },
  props: {
    startingBeads: Array,
    edges: Array,
    baseDustDuration: Number,
    dustCount: Number,
  },
  created() {
    // https://newbedev.com/make-computed-vue-properties-dependent-on-current-time
    var self = this
    setInterval(function () {
      let oldDustIndex = self.dustIndex
      self.now = Date.now()
      let j = self.dustIndex
      if (j > oldDustIndex) {
        let startTime = j * self.dustDuration / self.dustCount
        self.dustDelays[j % self.dustCount] = startTime - 0.001 * (
          self.now - self.dustOrigin
        )
      }
    }, 100)
  },
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
    hole() {
      return this.history[this.history.length - 2]
    },
    tail() {
      return this.history[this.history.length - 1]
    },
    loopEnd() {
      if (this.hole == this.tail) {
        return this.history.length - 2
      }

      if (this.history.length <= 2) {
        return this.history.length - 1
      }

      if (this.tail == this.history[this.history.length - 3]) {
        return this.history.length - 2 // going back
      }

      if (this.hole == this.history[0] && this.tail == this.history[1]) {
        return this.history.length - 2 // continuing loop
      }

      return this.history.length - 1
    },
    loopStart() {
      let sentinel = this.history[this.loopEnd]
      for (let i = this.loopEnd - 2; i > 0; i--) {
        if (this.history[i] == sentinel) {
          return i
        }
      }

      return 0
    },
    historyIndices() {
      let result = new Uint16Array(this.size * this.size)
      for (let i = this.loopStart; i < this.loopEnd; i++) {
        let a = this.history[i]
        let b = this.history[i + 1]
        result[a * this.size + b] = result[b * this.size + a] = i + 1
      }

      return result
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
    tangents() {
      let count = this.loopEnd + 1 - this.loopStart
      let xs = new Float64Array(count)
      let ys = new Float64Array(count)
      if (this.history[this.loopStart] == this.history[this.loopEnd]) {
        let [x, y] = this.getTangent(
          this.history[this.loopEnd - 1],
          this.history[this.loopStart],
          this.history[this.loopStart + 1],
        )
        xs[0] = xs[count - 1] = x
        ys[0] = ys[count - 1] = y
      }

      for (let i = this.loopStart + 1; i < this.loopEnd; i++) {
        let [x, y] = this.getTangent(
          this.history[i - 1],
          this.history[i],
          this.history[i + 1],
        )
        xs[i - this.loopStart] = x
        ys[i - this.loopStart] = y
      }

      return [xs, ys]
    },
    edgePaths() {
      let controlLength = 30
      let edgePaths = {}
      let [dxs, dys] = this.tangents
      let offset = this.loopStart
      for (let a = 0; a < this.size; a++) {
        for (let b = a; b < this.size; b++) {
          let name = [a, b].toString()
          let x1 = this.nodeXs[a], y1 = this.nodeYs[a]
          if (a == b) {
            edgePaths[name] = `M ${x1} ${y1}`
            continue
          }

          let backName = [b, a].toString()
          let x2 = this.nodeXs[b], y2 = this.nodeYs[b]
          let i = this.historyIndices[a * this.size + b]
          if (i <= 0) {
            edgePaths[name] =
              `M ${x1} ${y1} C ${x1} ${y1}, ${x2} ${y2}, ${x2} ${y2}`
            edgePaths[backName] =
              `M ${x2} ${y2} C ${x2} ${y2}, ${x1} ${y1}, ${x1} ${y1}`
            continue
          }

          let dx1 = dxs[i - offset - 1], dy1 = dys[i - offset - 1]
          let dx2 = -dxs[i - offset], dy2 = -dys[i - offset]
          if ((this.history[i - 1] < this.history[i]) != (a < b)) {
            [dx1, dy1, dx2, dy2] = [dx2, dy2, dx1, dy1]
          }

          let x0 = x1 + dx1 * controlLength, y0 = y1 + dy1 * controlLength
          let x3 = x2 + dx2 * controlLength, y3 = y2 + dy2 * controlLength
          edgePaths[name] =
            `M ${x1} ${y1} C ${x0} ${y0}, ${x3} ${y3}, ${x2} ${y2}`
          edgePaths[backName] =
            `M ${x2} ${y2} C ${x3} ${y3}, ${x0} ${y0}, ${x1} ${y1}`
        }
      }

      return edgePaths
    },
    edgeTruncated() {
      let startNode = this.history[this.loopStart]
      if (this.history[this.loopEnd] == startNode) {
        return false
      }

      let next = this.history.indexOf(startNode, this.loopStart + 1)
      return next >= 0 && next < this.loopEnd
    },
    headRadius() {
      return 10
    },
    headHeight() {
      return this.headRadius * Math.sqrt(1.5)
    },
    headPath() {
      let r = this.headRadius, hr = 0.5 * this.headHeight
      return `M ${hr} ${-r} L ${-hr} ${0} L ${hr} ${r}`
    },
    showHead() {
      return this.hole != this.tail &&
        this.matrix[this.hole * this.size + this.tail]
    },
    crossRadius() {
      return 15
    },
    crossPath() {
      let d = this.crossRadius * Math.sqrt(0.5)
      return `M ${-d} ${-d} L ${d} ${d} M ${d} ${-d} L ${-d} ${d}`
    },
    showCross() {
      return (
        this.hole != this.tail &&
          !this.matrix[this.hole * this.size + this.tail]
      ) || (
        this.holeClicked && this.history.length <= 2
      )
    },
    arrowEdge() {
      let a = this.hole, b = this.tail
      if (this.ghostHole != null) {
        b = a
        a = this.ghostHole
      } else if (a == b && this.history.length >= 3) {
        a = this.history[this.history.length - 3]
      }

      return [a, b]
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
          return {
            bead: true,
            tail: node == this.tail && this.hole != this.tail,
            onPath: this.historyIndices[
              node * this.size + this.oldBeads[id]
            ] > 0,
            animate: this.animations[id] > 0,
            alternate: this.animations[id] % 2,
            reverse: this.animations[id] >= 3,
            undo: this.oldBeads[id] == this.hole,
            loop: this.hole == this.history[0],
          }
        },
        this,
      )
    },
    beadOffsetPaths() {
      return this.beads.map(
        function(node, id, beads) {
          let edge =
            this.historyIndices[node * this.size + this.oldBeads[id]] <= 0 &&
            node == this.tail ?
            [this.hole, this.tail] :
            [this.oldBeads[id], node]
          let path = this.edgePaths[edge.toString()]
          return `path('${path}')`
        },
        this,
      )
    },
    clickRadius() {
      return 42
    },
    smallClickRadius() {
      return 20
    },
    dustDuration() {
      return this.getDustDuration(this.fast)
    },
    dustIndex() {
      return this.getDustIndex(this.dustDuration)
    },
    dust() {
      let dust = new Array(this.dustCount)
      for (let i = 0; i < this.dustCount; i++) {
        let j = this.dustIndex - i
        let generator = new seedrandom(j)
        let angle = generator.quick() * 2 * Math.PI
        let distance = 80 * Math.sqrt(generator.quick())
        dust[j % this.dustCount] = {
          j: j,
          cx: distance * Math.cos(angle),
          cy: distance * Math.sin(angle),
          r: 3 + 5 * generator.quick(),
          color: this.getDustColor(j, generator)
        }
      }

      return dust
    },
  },
  methods: {
    getDustDuration(fast) {
      return this.baseDustDuration * (fast ? 0.02 : 1)
    },
    getDustIndex(dustDuration) {
      return Math.floor(
        (this.now - this.dustOrigin) * 0.001 / dustDuration * this.dustCount
      )
    },
    getDustColor(j, generator) {
      let duration = 20
      let uniformFraction = 0.3
      let realms = [
        {
          chartreuse: 4,
          yellow: 1,
        },
        {
          red: 1,
          orange: 2,
        },
        {
          lightskyblue: 1,
          fuchsia: 1,
        },
      ]
      let realmIndex = Math.floor(j / duration)
      let threshold = 1
      let phase = j % duration - uniformFraction * duration
      if (phase > 0) {
        let remaining = duration * (1 - uniformFraction)
        threshold = 0.5 * (1 + Math.cos(phase * Math.PI / remaining))
      }

      let sample = generator.quick()
      if (sample > threshold) {
        realmIndex++
        sample = (sample - threshold) / (1 - threshold)
      } else {
        sample /= threshold
      }
      let realm = realms[realmIndex % realms.length]
      sample *= Object.values(realm).reduce((a, b) => a + b)
      let color, weight
      for ([color, weight] of Object.entries(realm)) {
        sample -= weight
        if (sample < 0) {
          break
        }
      }

      return color
    },
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
    goForward() {
      if (this.ensureTail()) {
        if (this.history.length >= 4 && this.hole == this.history[0]) {
          // continue going around the loop with the tail hidden
          this.goForwardHelp()
          this.history.push(this.tail)
        }
      } else if (this.matrix[this.hole * this.size + this.tail]) {
        this.goForwardHelp()
        this.history.push(this.getNextTail(this.history, this.chosenTail))
        this.ghostHole = null
      }
    },
    goForwardHelp() {
      let id = this.beads.indexOf(this.tail)
      this.beads[id] = this.hole
      this.checkWin()
      this.animations[id] = 1 + this.animations[id] % 2
      this.oldBeads[id] = this.tail
      this.chosenTail = null
      this.holeClicked = false
      if (
        this.history.length >= 3 &&
        this.history[this.history.length - 3] == this.tail
      ) {
        let loop = this.history[0] == this.hole
        this.history.pop()
        this.history.pop()
        if (loop) {
          this.history.reverse()
          this.history.push(this.history[0])
        } else {
          this.animations[id] += 2
          this.chosenTail = this.hole // keep going back
        }
      }

      this.history = this.removeBeforeLoop(this.history)
    },
    removeBeforeLoop(history) {
      let hole = history[history.length - 1]
      for (let offset = history.length - 4; offset >= 0; offset--) {
        if (history[offset] == hole) {
          return history.slice(offset)
        }
      }

      return history
    },
    getNextTail(history, chosenTail) {
      // first choice: restore chosen tail
      if (chosenTail != null) {
        return chosenTail
      }

      let end = history.length - 1
      if (end >= 1 && history[end - 1] == history[end]) {
        end--
      }

      // second choice: continue the loop
      let hole = history[end]
      if (history[0] == hole && end >= 3) {
        return history[1]
      }

      // third choice: new tail creates the smallest possible loop
      let oldHole = history[end - 1]
      for (let i = end - 2; i >= 0; i--) {
        let tail = history[i]
        if (
          tail != oldHole && // going back shouldn't be the default.
                             // happens when old hole is start of loop.
          this.matrix[hole * this.size + tail]
        ) { return tail }
      }

      // fourth choice: iterate clockwise and choose the first edge
      for (let i = 1; i < this.size; i++) {
        let tail = (hole + i) % this.size
        if (
          tail != oldHole && // going back shouldn't be the default
          this.matrix[hole * this.size + tail]
        ) { return tail }
      }

      // fifth choice: dead end
      return hole
    },
    goBack() {
      this.holeClicked = false
      if (this.history.length > 2) {
        let hideTail = false
        if (this.hole == this.tail) {
          // tutorial levels have dead ends which cause the tail to be hidden
          // even when using the keyboard. it's confusing if going back
          // doesn't cause the tail to be shown again.
          let edges = 0
          for (let i = 0; i < this.size; i++) {
            edges += this.matrix[this.hole * this.size + i]
            if (edges > 1) {
              hideTail = true // not a dead end, ok to hide tail
              break
            }
          }
        }

        this.history.pop()
        let id = this.beads.indexOf(this.hole)
        this.beads[id] = this.tail
        this.checkWin()
        this.animations[id] = 3 + this.animations[id] % 2
        this.oldBeads[id] = this.hole
        if (this.history[0] == this.tail) {
          // ensure the entire loop is represented
          this.history.unshift(this.hole)
        }

        this.chosenTail = this.tail
        this.ghostHole = null
        if (hideTail) {
          this.history[this.history.length - 1] = this.hole
        }
      }
    },
    selectLeft() {
      if (this.ensureTail() && this.hole != this.tail) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = this.size - 1; i >= 0; i--) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          this.chosenTail = newTail
          this.holeClicked = false
          return
        }
      }
    },
    selectRight() {
      if (this.ensureTail() && this.hole != this.tail) {
        return
      }

      // iterate counterclockwise and choose the first edge
      for (let i = 1; i <= this.size; i++) {
        let newTail = (this.tail + i) % this.size
        if (this.matrix[this.hole * this.size + newTail]) {
          this.history[this.history.length - 1] = newTail
          this.chosenTail = newTail
          this.holeClicked = false
          return
        }
      }
    },
    ensureTail() {
      if (this.hole == this.tail) {
        if (this.holeClicked && this.history.length >= 3) {
          this.history[this.history.length - 1] =
            this.history[this.history.length - 3]
        } else {
          this.holeClicked = false
          this.ghostHole = null
          this.history[this.history.length - 1] =
            this.getNextTail(this.history, this.chosenTail)
        }

        return true
      }

      return false
    },
    onMouseDown(event) {
      let gameView = document.getElementById('game-view')
      let x = event.offsetX / gameView.clientWidth * 240 - 120
      let y = event.offsetY / gameView.clientHeight * 240 - 120
      this.holeClicked = false
      for (let i = 0; i < this.size; i++) {
        let dx = this.nodeXs[i] - x
        let dy = this.nodeYs[i] - y
        if (dx * dx + dy * dy < this.clickRadius * this.clickRadius) {
          if (i == this.hole) {
            this.holeClicked = true
            this.history[this.history.length - 1] = this.history.length >= 3 ?
              this.history[this.history.length - 3] : this.hole
          } else {
            this.history[this.history.length - 1] = i
            if (this.matrix[this.size * this.hole + i]) {
              this.chosenTail = i
            }
          }

          this.ghostHole = null
          return
        }
      }
    },
    clicked(event) {
      let i = this.holeClicked ? this.hole : this.tail
      if (!this.holeClicked && !this.matrix[this.size * this.hole + i]) {
        this.ghostHole = this.hole
        this.history[this.history.length - 1] = this.hole
        return
      }

      let gameView = document.getElementById('game-view')
      let x = event.offsetX / gameView.clientWidth * 240 - 120
      let y = event.offsetY / gameView.clientHeight * 240 - 120
      let dx = this.nodeXs[i] - x
      let dy = this.nodeYs[i] - y
      if (dx * dx + dy * dy >= this.clickRadius * this.clickRadius) {
        if (this.holeClicked) {
          this.history[this.history.length - 1] = this.hole
          this.holeClicked = false
        }

        return
      }

      let oldHole = this.hole
      if (this.holeClicked) {
        this.goBack()
        this.history[this.history.length - 1] = this.hole
      } else {
        this.goForwardHelp()
        this.history.push(this.tail)
      }

      this.ghostHole = oldHole
    },
    buttonClicked() {
      if (!this.ensureTail()) {
        this.history[this.history.length - 1] = this.hole
      }
    },
    onFocus() {
      if (!this.holeClicked) {
        this.ensureTail()
      }
    },
    onBlur() {
      this.holeClicked = false
      this.history[this.history.length - 1] = this.hole
    },
    checkWin() {
      for (let [id, node] of this.beads.entries()) {
        if (node != id + 1) {
          this.fast = false
          return
        }
      }

      this.fast = true
    },
  },
  watch: {
    startingBeads(newStartingBeads, oldStartingBeads) {
      this.beads = [...newStartingBeads]
      this.oldBeads = [...newStartingBeads]
      this.animations = new Uint8Array(this.beads.length)
      let beadSet = new Set(this.beads)
      let hole = 0
      for (; beadSet.has(hole); hole++) { }

      this.history = [hole, hole]
      this.chosenTail = null
      this.holeClicked = false
      this.ghostHole = null
      this.checkWin()
    },
    fast(newFast, oldFast) {
      let oldDuration = this.getDustDuration(oldFast)
      let newDuration = this.getDustDuration(newFast)
      let oldIndex = this.getDustIndex(oldDuration)
      let oldOrigin = this.dustOrigin
      this.now = Date.now()
      // change dustOrigin to keep dustIndex constant
      // dustIndex = (now - dustOrigin) / dustDuration
      // dustOrigin = now - dustIndex * newDuration
      let factor = newDuration / oldDuration
      this.dustOrigin = this.now * (1 - factor) + this.dustOrigin * factor
      for (let i = 0; i < this.dustCount; i++) {
        let j = oldIndex - i
        let startTime = j * oldDuration / this.dustCount
        let oldDelay = startTime - 0.001 * (this.now - oldOrigin)
        this.dustDelays[j % this.dustCount] = oldDelay * factor
      }
    }
  },
}
</script>

<template>
  <button class="tabStop" @keydown.up.stop.prevent="goForward()" @keydown.down.stop.prevent="goBack()" @keydown.left.stop.prevent="selectLeft()" @keydown.right.stop.prevent="selectRight()" @click="buttonClicked" @focus.native="onFocus" @blur.native="onBlur">
    <svg class="gameView" id="game-view" viewBox="-120 -120 240 240" @mousedown="onMouseDown" @click.stop.prevent="clicked">
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
          :transform="`translate(${this.nodeXs[this.hole]}, ${this.nodeYs[this.hole]})`"
          fill="none"
          stroke="black"
          stroke-width="12"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <image id="check" x="-10" y="-10" width="20" height="20"
          href="../assets/checkmark.svg"
        />
      </defs>
      <circle
        v-for="node in size"
        fill="black"
        :r="clickRadius"
        :cx="nodeXs[node - 1]"
        :cy="nodeYs[node - 1]"
        :class="{touchCircle: true, active: this.matrix[size * hole + node - 1]}"
      />
      <circle
        fill="black"
        :r="clickRadius"
        :cx="0"
        :cy="15"
        :class="{touchCircle: true, active: this.history.length >= 4 && this.hole == this.history[0]}"
      />
      <circle
        fill="black"
        :r="smallClickRadius"
        :cx="0"
        :cy="smallClickRadius - clickRadius - 15"
        :class="{touchCircle: true, active: this.history.length >= 4 && this.hole == this.history[0]}"
      />
      <path
        :opacity="showHead ? 1 : 0"
        class="head"
        :d="headPath"
        :style="{ 'offset-path': `path('${arrowPath}')`, 'offset-distance': `${100 * 0.5 * headHeight / 160}%` }"
        :class="{ghost: ghostHole != null}"
        fill="none"
      />
      <path
        :opacity="showCross ? 1 : 0"
        class="head"
        :d="crossPath"
        :transform="`translate(${this.nodeXs[this.hole]}, ${this.nodeYs[this.hole]})`"
        :class="{ghost: ghostHole != null}"
        fill="none"
      />
      <circle
        :opacity="hole != tail ? 1 : 0"
        class="outline"
        :r="2 * beadRadius"
        fill="none"
        :cx="nodeXs[tail]"
        :cy="nodeYs[tail]"
        :class="{ghost: ghostHole != null}"
      />
      <g
        v-for="(mote, i) of dust"
        :class="{dust: true, alternate: Math.floor(mote.j / dustCount) % 2 != fast}"
        :style="{'animation-duration': `${dustDuration}s`, 'animation-delay': `${dustDelays[i]}s`}"
      >
        <circle
          :cx="mote.cx"
          :cy="mote.cy"
          :r="mote.r"
          :fill="mote.color"
          :style="{'transition-property': 'filter', 'transition-duration': '2s', 'filter': `brightness(${fast ? 100 : 50}%)`}"
          >
        </circle>
      </g>
      <mask id="cross-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use
          href="#cross-path"
          :opacity="showCross ? 1 : 0"
          :class="{ghost: ghostHole != null}"
        />
      </mask>
      <mask id="head-mask">
        <rect x="-130" y="-130" width="260" height="260" fill="white"></rect>
        <use
          href="#head-path"
          :opacity="showHead ? 1 : 0"
          :class="{ghost: ghostHole != null}"
        />
        <use
          href="#cross-path"
          :opacity="showCross ? 1 : 0"
          :class="{ghost: ghostHole != null}"
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
          :opacity="showHead ? 1 : 0"
          :class="{ghost: ghostHole != null}"
        />
        <use
          href="#cross-path"
          :opacity="showCross ? 1 : 0"
          :class="{ghost: ghostHole != null}"
        />
      </mask>
      <path
        v-for="edge of edges"
        :key="`${edge.toString()},${size}`"
        :class="{ edge: true, active: (x => x > 0 && x < this.history.length - 1)(historyIndices[edge[0] * size + edge[1]]), arrow: (edge[0] == hole && edge[1] == tail) || (edge[0] == tail && edge[1] == hole) }"
        :d="edgePaths[edge.toString()]"
        fill="none"
        v-bind:mask="(edge[0] == arrowEdge[0] && edge[1] == arrowEdge[1]) || (edge[0] == arrowEdge[1] && edge[1] == arrowEdge[0]) ? 'url(#cross-mask)' : (edge[0] == history[0] && edge[1] == history[1]) || (edge[0] == history[1] && edge[1] == history[0]) ? 'url(#truncate-mask)' : 'url(#head-mask)'"
      />
      <image v-if="size > 1" x="-5" y="-5" width="10" height="10" :class="beadClasses[0]"
        href="../assets/heart.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.7)', 'offset-path': beadOffsetPaths[0] }"
      />
      <image v-if="size > 2" x="-5" y="-5" width="10" height="10" :class="beadClasses[1]"
        href="../assets/butterfly.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.8)', 'offset-path': beadOffsetPaths[1] }"
      />
      <image v-if="size > 3" x="-5" y="-5" width="10" height="10" :class="beadClasses[2]"
        href="../assets/saturn.svg"
        :style="{ 'transform': 'rotate(90deg) scale(3.35)', 'offset-path': beadOffsetPaths[2] }"
      />
      <image v-if="size > 4" x="-5" y="-5" width="10" height="10" :class="beadClasses[3]"
        href="../assets/leaf.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.5)', 'offset-path': beadOffsetPaths[3] }"
      />
      <image v-if="size > 5" x="-5" y="-5" width="10" height="10" :class="beadClasses[4]"
        href="../assets/mushroom.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.6)', 'offset-path': beadOffsetPaths[4] }"
      />
      <image v-if="size > 6" x="-5" y="-5" width="10" height="10" :class="beadClasses[5]"
        href="../assets/flower.svg"
        :style="{ 'transform': 'rotate(90deg) scale(2.5)', 'offset-path': beadOffsetPaths[5] }"
      />
      <g v-if="size > 1" :transform="`translate(${goalXs[1]},${goalYs[1]})`">
        <image x="-3" y="-3" width="6" height="6"
          href="../assets/heart_outline.svg"
          :style="{ 'transform': `scale(2.7)` }"
        />
        <use :class="{ checkmark: true, checked: beads[0] == 1 }" href="#check"></use>
      </g>
      <g v-if="size > 2" :transform="`translate(${goalXs[2]},${goalYs[2]})`">
        <image x="-3" y="-3" width="6" height="6"
          href="../assets/butterfly_outline.svg"
          :style="{ 'transform': 'scale(2.8)' }"
        />
        <use :class="{ checkmark: true, checked: beads[1] == 2 }" href="#check"></use>
      </g>
      <g v-if="size > 3" :transform="`translate(${goalXs[3]},${goalYs[3]})`">
        <image x="-3" y="-3" width="6" height="6"
          href="../assets/saturn_outline.svg"
          :style="{ 'transform': 'scale(3.35)' }"
        />
        <use :class="{ checkmark: true, checked: beads[2] == 3 }" href="#check"></use>
      </g>
      <g v-if="size > 4" :transform="`translate(${goalXs[4]},${goalYs[4]})`">
        <image x="-3" y="-3" width="6" height="6"
          href="../assets/leaf_outline.svg"
          :style="{ 'transform': 'scale(2.5)' }"
        />
        <use :class="{ checkmark: true, checked: beads[3] == 4 }" href="#check"></use>
      </g>
      <g v-if="size > 5" :transform="`translate(${goalXs[5]},${goalYs[5]})`">
        <image x="-3" y="-3" width="6" height="6"
          href="../assets/mushroom_outline.svg"
          :style="{ 'transform': 'scale(2.6)' }"
        />
        <use :class="{ checkmark: true, checked: beads[4] == 5 }" href="#check"></use>
      </g>
      <g v-if="size > 6" :transform="`translate(${goalXs[6]},${goalYs[6]})`">
        <image x="-3" y="-3" width="6" height="6"
          href="../assets/flower_outline.svg"
          :style="{ 'transform': 'scale(2.5)' }"
        />
        <use :class="{ checkmark: true, checked: beads[5] == 6 }" href="#check"></use>
      </g>
    </svg>
  </button>
</template>

<style scoped>
.tabStop {
  background-color: inherit;
  border: none;
  font: inherit;
  padding: 0;
}
.gameView {
  width: 40rem;
  height: 40rem;
}
.touchCircle {
  stroke: var(--color-text);
  stroke-width: 0.5;
  stroke-opacity: 0.25;
}
.head {
  stroke: var(--color-text);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
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
.ghost {
  transition: opacity 0s 0.35s, cx 0s 0.5s, cy 0s 0.5s;
}
/*
tail onPath undo loop reverse offset-rotate
0    0                        -90deg
0    1                0       auto
0    1                1       reverse
1    0      0                 reverse
1           1    0    0       auto
1           1    0    1       reverse
1           1    1            reverse
1    1      0                 auto
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
  animation-name: slide2
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
.bead.tail.undo.loop {
  offset-rotate: reverse;
}
.checkmark {
  opacity: 0;
  transition-property: opacity;
  transition-delay: 0s;
}
.checkmark.checked {
  opacity: 1;
  transition-delay: 0.35s;
}
.dust {
  animation-name: dustFade;
  animation-fill-mode: forwards;
}
.dust.alternate {
  animation-name: dustFade2;
}
@keyframes dustFade {
  from { opacity: 0.00785; }
  3% { opacity: 0.00785; }
  10% { opacity: 0.01; }
  45% { opacity: 1; }
  65% { opacity: 1; }
  90% { opacity: 0.01; }
  97% { opacity: 0; }
  to { opacity: 0; }
}
@keyframes dustFade2 {
  from { opacity: 0.00785; }
  3% { opacity: 0.00785; }
  10% { opacity: 0.01; }
  45% { opacity: 1; }
  65% { opacity: 1; }
  90% { opacity: 0.01; }
  97% { opacity: 0; }
  to { opacity: 0; }
}
</style>
