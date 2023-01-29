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

export function bytesToEdges(bytes) {
    let edges = []
    let bitCount = 8 * bytes.length
    let x = 1, y = 0
    for (let bit = 0; bit < bitCount; bit++) {
        if (bytes[bit >> 3] & (1 << (bit & 7))) {
            edges.push([y, x])
        }

        y++
        if (y >= x) {
            y = 0
            x++
        }
    }

    return edges
}

var SimpleGraph = {
    bytesToNodeCount: bytesToNodeCount,
    bytesToEdges: bytesToEdges,
}

export default SimpleGraph
