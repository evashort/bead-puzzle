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

var SimpleGraph = {
    bytesToNodeCount: bytesToNodeCount,
    applyLayout: applyLayout,
    hasEdge: hasEdge,
    edges: edges,
    nodeEdges: nodeEdges,
    fromString: fromString,
    toString: toString,
}

export default SimpleGraph
