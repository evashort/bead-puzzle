import Permute from './Permute.js'
import base64js from 'base64-js'

export function bytesToNodeCount(bytes) {
    let lastIndex = bytes.length - 1
    for (; lastIndex > 0 && bytes[lastIndex] == 0; lastIndex--);
    let bitCount = 8 * lastIndex
    for (let byte = bytes[lastIndex]; byte > 0; byte >>= 1) {
        bitCount++
    }

    // https://oeis.org/A002024
    let n = Math.floor((Math.sqrt(8 * bitCount) + 1) / 2)
    return n + 1
}

export function applyLayout(bytes, layout) {
    let length = bytesToNodeCount(bytes)
    layout = Permute.fromIndex(layout, length)
    let byteCount = (length * (length - 1) / 2 + 7) >> 3
    let newBytes = new Uint8Array(byteCount)
    for (let b = 0; b < length; b++) {
        for (let a = 0; a < b; a++) {
            if (hasEdge(bytes, layout[a], layout[b])) {
                let bit = a + b * (b - 1) / 2
                newBytes[bit >> 3] |= (1 << (bit & 7))
            }
        }
    }

    return newBytes
}

export function hasEdge(bytes, a, b) {
    if (a == b) {
        return false
    }

    if (b < a) {
        [a, b] = [b, a]
    }

    let bit = a + b * (b - 1) / 2
    let byteIndex = bit >> 3
    return byteIndex < bytes.length && (
        bytes[byteIndex] & (1 << (bit & 7))
    ) != 0
}

export function* edges(bytes) {
    let a = 0, b = 1
    for (let byte of bytes) {
        for (let i = 1; i < 256; i *= 2) {
            if (byte & i) {
                yield [a, b]
            }

            a++
            if (a >= b) {
                a = 0
                b++
            }
        }
    }
}

export function* nodeEdges(bytes, a) {
    let bits = bytes.length * 8
    let bit = a * (a - 1) / 2
    for (let b = 0; b < a && bit < bits; b++) {
        if (bytes[bit >> 3] & (1 << (bit & 7))) {
            yield b
        }

        bit++
    }

    bit += a
    for (let b = a + 1; bit < bits; b++) {
        if (bytes[bit >> 3] & (1 << (bit & 7))) {
            yield b
        }

        bit += b
    }
}

export function fromString(string) {
    return base64js.toByteArray(string.split(".", 1)[0])
}

export function toString(bytes) {
    return base64js.fromByteArray(bytes)
}

export function oppositeEdge(bytes, a, b) {
    let n = bytesToNodeCount(bytes)
    let bestC = a
    let bestDistance = -Infinity
    // among the c with the highest distance, choose the lowest one greater
    // than b or the lowest one if none are greater than b. we do it this way
    // so that when this function is used to choose the next tail after a move,
    // the player can press the right arrow key to cycle through all the edges
    // without wrapping around to the other side of b.
    for (let c of nodeEdges(bytes, b)) {
        let distance = angleDistance(n, a, b, c)
        if (
            distance == bestDistance ? (c > b) > (bestC > b) :
            distance > bestDistance
        ) {
            bestC = c
            bestDistance = distance
        }
    }

    return bestC
}

function angleDistance(n, a, b, c) {
    if (a >= 0 && a != b) {
        // distance from a to c around the perimeter of the circle without
        // passing b
        let aToC = (c - a + n) % n
        let aToB = (b - a + n) % n
        return aToB < aToC ? n - aToC : aToC
    } else {
        // so that oppositeEdge returns the first c greater than b when a is
        // null, see comment in oppositeEdge
        return -1
    }
}

export function onlyPath(bytes, a, b) {
    let result = -1
    for (let c of nodeEdges(bytes, b)) {
      if (c == a) { continue }
      if (result >= 0) { return -1 }
      result = c
    }

    return result
}

var SimpleGraph = {
    bytesToNodeCount: bytesToNodeCount,
    applyLayout: applyLayout,
    hasEdge: hasEdge,
    edges: edges,
    nodeEdges: nodeEdges,
    fromString: fromString,
    toString: toString,
    oppositeEdge: oppositeEdge,
    onlyPath: onlyPath,
}

export default SimpleGraph
