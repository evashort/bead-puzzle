import Permute from './Permute.js'

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
    )
}

var SimpleGraph = {
    bytesToNodeCount: bytesToNodeCount,
    applyLayout: applyLayout,
    hasEdge: hasEdge,
}

export default SimpleGraph
