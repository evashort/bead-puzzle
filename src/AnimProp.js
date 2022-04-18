var tickers = new Set()
var intervalID = 0

function tickAll(now) {
  for (let ticker of tickers) {
    if (!ticker.tick(now)) {
      tickers.delete(ticker)
    }
  }

  if (tickers.size <= 0) {
    clearInterval(intervalID)
    intervalID = 0
  }
}

function requestTickAll() {
  window.requestAnimationFrame(tickAll)
}

function noCurve(t) {
  return t
}

export default class AnimProp {
  constructor(value, duration, curve=noCurve, speed=0, max=Infinity) {
    this.duration = duration
    this.curve = curve
    this.speed = speed
    this.max = max

    this.initial = value % this.max
    this.final = this.initial
    this.value = this.final
    this.start = 0
    this.stop = 0
  }

  set(value) {
    let now = performance.now()
    this.initial = this.getValue(now)
    this.final = value % this.max
    if (this.final + this.max - this.initial < this.initial - this.final) {
      this.final += this.max
    } else if (this.initial + this.max - this.final < this.final - this.initial) {
      this.initial += this.max
    }

    let distance = Math.abs(this.final - this.initial)
    let duration = this.duration
    if (distance < this.speed * this.duration) {
      duration = distance / this.speed
    }

    this.start = now
    this.stop = this.start + duration
    if (this.stop > this.start) {
      let oldSize = tickers.size
      tickers.add(this)
      if (oldSize <= 0) {
        intervalID = window.setInterval(requestTickAll, 16)
      }
    } else {
      this.value = this.final
    }
  }

  tick(now) {
    this.value = this.getValue(now)
    return now < this.stop
  }

  getValue(now) {
    if (now >= this.stop) {
      return this.final
    }

    let phase = this.curve((now - this.start) / (this.stop - this.start))
    let value = (this.initial * (1 - phase) + this.final * phase) % this.max
    return value
  }
}
